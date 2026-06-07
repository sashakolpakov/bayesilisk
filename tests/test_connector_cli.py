from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run_connector(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bayesilisk", "connector", *args],
        check=check,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_connector_init_scaffolds_a_validatable_context(tmp_path: Path) -> None:
    context_path = tmp_path / "source-context.json"
    run_connector("init", "--kind", "source", "--with-action-graph", "--output", str(context_path))
    context = json.loads(context_path.read_text(encoding="utf-8"))
    assert context["repositoryFacts"][0]["proposalRules"]
    assert "connectorActionGraph" in context

    validate = run_connector("validate", str(context_path))
    assert validate.returncode == 0
    assert "OK: source context accepted" in validate.stderr

    propose = run_connector("propose", str(context_path))
    proposals = json.loads(propose.stdout)
    assert len(proposals) >= 1


def test_connector_validate_flags_unsafe_and_silent_contexts(tmp_path: Path) -> None:
    # Missing proposalRules: accepted, but loudly warned (not silent).
    norules = tmp_path / "norules.json"
    norules.write_text(
        json.dumps(
            {
                "source": "x",
                "repositoryFacts": [
                    {
                        "source": "repository-scan",
                        "title": "t",
                        "invariantId": "app.x",
                        "routePattern": "/r/{id}",
                        "expectedBehavior": {"status": 404},
                        "availableActions": ["a"],
                        "params": [{"name": "id"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    validate = run_connector("validate", str(norules))
    assert validate.returncode == 0
    assert "no proposalRules" in validate.stderr

    propose = run_connector("propose", str(norules), check=False)
    assert propose.returncode == 1
    assert "0 probe proposals" in propose.stderr
    assert json.loads(propose.stdout) == []

    # Forbidden verifier-only field + production URL: rejected.
    bad = tmp_path / "bad.json"
    bad.write_text(
        json.dumps(
            {
                "source": "x",
                "repositoryFacts": [
                    {
                        "source": "s",
                        "title": "t",
                        "invariantId": "app.x",
                        "routePattern": "https://app.production.example/r",
                        "expectedBehavior": {"status": 404},
                        "proposalRules": {"id": [{"id": "u", "value": "v"}]},
                        "availableActions": ["a"],
                        "params": [{"name": "id"}],
                        "passed": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    rejected = run_connector("validate", str(bad), check=False)
    assert rejected.returncode == 1
    assert "verifier-only fields" in rejected.stderr
    assert "production URL" in rejected.stderr


def _write_source_and_observed(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / "src.json"
    observed = tmp_path / "obs.json"
    source.write_text(
        json.dumps(
            {
                "source": "source-context",
                "repositoryFacts": [
                    {
                        "availableActions": ["open-resource-action"],
                        "expectedBehavior": {"status": 404},
                        "invariantId": "external.resource_unknown_target_rejected",
                        "params": [{"name": "targetId", "kind": "id", "location": "query"}],
                        "proposalRules": {"targetId": [{"id": "unknown-id", "value": "missing-target"}]},
                        "routePattern": "/resource/{resourceId}/action?targetId={targetId}",
                        "source": "repository-scan",
                        "title": "Resource action rejects unknown target",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    observed.write_text(
        json.dumps(
            {
                "source": "observed-context",
                "repositoryFacts": [
                    {
                        "actorRole": "operator",
                        "artifactPaths": [],
                        "expectedStatus": 404,
                        "failureDetail": "Unknown target id opened the protected action.",
                        "invariantId": "external.resource_unknown_target_rejected",
                        "networkResponses": [
                            {"status": 200, "url": "http://localhost:3000/resource/123/action?targetId=missing-target"}
                        ],
                        "observedStatus": 200,
                        "passed": False,
                        "route": "/resource/{resourceId}/action?targetId={targetId}",
                        "selector": "connector:open-resource-action",
                        "source": "connector-observation",
                        "targetUrl": "http://localhost:3000/resource/123/action?targetId=missing-target",
                        "timestamp": "2026-05-30T00:00:00Z",
                        "title": "Resource action rejects unknown target",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return source, observed


def test_connector_verify_emits_payloads_and_rejects_inconsistent_facts(tmp_path: Path) -> None:
    source, observed = _write_source_and_observed(tmp_path)
    issues_path = tmp_path / "issues.json"
    verify = run_connector(
        "verify",
        "--source",
        str(source),
        "--observed",
        str(observed),
        "--issue-payloads",
        "--output",
        str(issues_path),
    )
    assert verify.returncode == 0
    payloads = json.loads(issues_path.read_text(encoding="utf-8"))
    assert payloads
    assert payloads[0]["issuePayloadSource"] == "verifiedByBayesilisk"

    # passed inconsistent with observedStatus == expectedStatus must be rejected.
    bad_observed = json.loads(observed.read_text(encoding="utf-8"))
    bad_observed["repositoryFacts"][0]["passed"] = True
    bad_path = tmp_path / "obs_bad.json"
    bad_path.write_text(json.dumps(bad_observed), encoding="utf-8")
    rejected = run_connector("verify", "--source", str(source), "--observed", str(bad_path), check=False)
    assert rejected.returncode == 1
    assert "must equal observedStatus == expectedStatus" in rejected.stderr


def test_flat_cli_invocation_is_unchanged() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bayesilisk", "--seed", "150", "--format", "json"],
        check=True,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    report = json.loads(result.stdout)
    assert report["tool"].startswith("bayesilisk.")
    assert report["seed"] == 150


def test_mcp_connector_quickstart_returns_ordered_loop() -> None:
    server = importlib.import_module("bayesilisk.mcp_server")
    tools = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = [tool["name"] for tool in tools["result"]["tools"]]
    assert "connector_quickstart" in names

    call = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "connector_quickstart", "arguments": {}},
        }
    )
    quickstart = json.loads(call["result"]["content"][0]["text"])
    steps = [entry["tool"] for entry in quickstart["loop"]]
    assert steps == [
        "interview_connector_need",
        "establish_provenance",
        "connector_prompt_packet",
        "scenario_plan",
        "verify_connector_outputs",
        "fix_packet",
    ]
    assert quickstart["sourceContextTemplate"]["repositoryFacts"]
