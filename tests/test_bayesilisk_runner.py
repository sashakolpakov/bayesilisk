from __future__ import annotations

import importlib
import io
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "bayesilisk.md"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run_bayesilisk(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bayesilisk", *args],
        check=True,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_bayesilisk_json_report_is_seeded_and_reproducible() -> None:
    first = run_bayesilisk("--seed", "150", "--format", "json")
    second = run_bayesilisk("--seed", "150", "--format", "json")

    assert first.stdout == second.stdout
    report = json.loads(first.stdout)

    assert report["tool"] == "bayesilisk.v1.2"
    assert report["seed"] == 150
    assert report["deterministic"] is True
    assert report["productionAccess"] is False
    assert report["generatedScenarioCount"] == 8
    assert "harder-to-find-after-easy-breakages" in report["prioritizationPolicy"]
    assert {"confirmedBreakages", "candidateProbes", "hardToFindModes", "controls"} <= set(report["sections"])
    assert set(report["domains"]) == {
        "Travel",
        "Expenses",
        "Billing",
        "HR",
        "Support",
        "DMS",
        "module entitlements",
    }

    invariant_ids = {invariant["id"] for invariant in report["invariants"]}
    assert {
        "roles.route_matrix_allowed",
        "roles.employee_self_review_forbidden",
        "modules.expense_approval_requires_module_and_receipt",
        "dms.tenant_process_boundary",
        "support.takeover_session_required",
        "billing.export_requires_role_and_module",
        "hr.documents_customer_role_boundary",
        "travel.itinerary_chronology",
        "travel.funding_before_expense",
        "travel.expense_items_match_itinerary",
    } <= invariant_ids
    assert "finance" in report["roleRouteMatrix"]["/api/expense-claims/{claimId}/review"]

    findings = report["findings"]
    assert findings == sorted(findings, key=lambda item: (-item["riskScore"], item["posteriorMode"], item["id"]))
    assert {"pass", "fail"} <= {finding["observedResult"] for finding in findings}
    assert {"mundane", "creative", "intentionally-inconsistent", "round-up"} <= {
        finding["scenarioTone"] for finding in findings
    }
    assert {
        "mundane.travel_funding_to_multimodal_expense",
        "roundup.travel_funding_unapproved_multimodal_expense",
        "inconsistent.travel_air_train_leg_mismatch",
    } <= {finding["scenarioId"] for finding in findings}
    assert any(finding["generatedScenario"] for finding in findings)
    assert any(finding["scenarioTone"].startswith("generated") for finding in findings)
    assert {"breakage.easy", "breakage.hard-to-find", "control-confirmed"} <= {
        finding["classification"] for finding in findings
    }
    assert {
        "harder-to-find-after-easy-breakages",
        "highest-fault-probability",
        "posterior-control-confidence",
    } <= {finding["posteriorMode"] for finding in findings}

    for finding in findings:
        assert finding["fingerprint"].startswith("bayesilisk:")
        assert finding["dedupeKey"].startswith(finding["fingerprint"])
        assert finding["issueReadiness"] in {
            "do-not-open-muted",
            "no-issue-control",
            "probe-only",
            "ready-for-issue",
            "regression-watch",
        }
        assert finding["observationBasis"]["tags"]
        assert 0 < finding["riskScore"] < 1
        assert finding["posteriorProbability"] == finding["riskScore"]
        assert finding["classification"]
        assert finding["posteriorMode"]
        assert finding["fragments"]
        assert finding["subScenarios"]
        assert any(entry["completeAlone"] is False for entry in finding["subScenarios"])
        assert "actorRole" in finding["accessPattern"]
        assert "routes" in finding["accessPattern"]
        assert finding["expectedInvariant"]
        assert finding["suggestedIssueTitle"].startswith("Bayesilisk ")
        assert "Reproduce with `python3 -m bayesilisk --seed <seed> --format json`" in finding[
            "suggestedIssueBody"
        ]


def test_bayesilisk_markdown_and_output_files_include_gitea_ready_findings(tmp_path: Path) -> None:
    json_path = tmp_path / "bayesilisk.json"
    markdown_path = tmp_path / "bayesilisk.md"

    json_run = run_bayesilisk("--seed", "150", "--format", "json", "--limit", "2", "--output", str(json_path))
    markdown_run = run_bayesilisk(
        "--seed",
        "150",
        "--format",
        "markdown",
        "--limit",
        "2",
        "--output",
        str(markdown_path),
    )

    assert json_run.stdout == ""
    assert markdown_run.stdout == ""

    report = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert len(report["findings"]) == 2
    assert "# Bayesilisk Report" in markdown
    assert "- Seed: `150`" in markdown
    assert "- Production access: `false`" in markdown
    assert "## Sections" in markdown
    assert "Fingerprint:" in markdown
    assert "Classification:" in markdown
    assert "Issue readiness:" in markdown
    assert "Posterior mode:" in markdown
    assert "Observation basis:" in markdown
    assert "Access pattern:" in markdown
    assert "Sub-scenarios:" in markdown
    assert "Suggested Gitea issue body:" in markdown
    assert "Expected invariant:" in markdown
    assert "Risk score:" in markdown


def test_bayesilisk_observation_history_dampens_fixed_findings(tmp_path: Path) -> None:
    baseline = json.loads(run_bayesilisk("--seed", "150", "--format", "json").stdout)
    fixed_finding = next(finding for finding in baseline["findings"] if finding["observedResult"] == "fail")
    observation_path = tmp_path / "observations.json"
    observation_path.write_text(
        json.dumps(
            {
                "source": "unit-test-history",
                "fixedFingerprints": [fixed_finding["fingerprint"]],
            }
        ),
        encoding="utf-8",
    )

    adjusted = json.loads(
        run_bayesilisk("--seed", "150", "--format", "json", "--observations", str(observation_path)).stdout
    )
    adjusted_finding = next(
        finding for finding in adjusted["findings"] if finding["fingerprint"] == fixed_finding["fingerprint"]
    )

    assert adjusted_finding["riskScore"] < fixed_finding["riskScore"]
    assert adjusted_finding["issueReadiness"] == "regression-watch"
    assert "fixed-regression-watch" in adjusted_finding["observationBasis"]["tags"]


def test_bayesilisk_context_promotes_related_modes_and_dedupes_existing_payloads() -> None:
    bayesilisk = importlib.import_module("bayesilisk.bayesilisk")
    baseline = bayesilisk.build_report(150, limit=8, generated_count=8)
    existing = next(finding for finding in baseline["findings"] if finding["issueReadiness"] == "ready-for-issue")
    context = {
        "source": "unit-test-agent-gitea-context",
        "agentNotes": [
            "Verifier saw HR documents process context metadata, support takeover, tenant DMS, travel expense receipts, "
            "and role permission 403 gaps on develop-usa.",
        ],
        "issues": [
            {
                "number": 999,
                "state": "open",
                "title": "Existing Bayesilisk finding",
                "body": f"Already tracked fingerprint `{existing['fingerprint']}`.",
            }
        ],
        "pullRequests": [{"number": 170, "state": "open", "title": "Bayesilisk verifier hardening"}],
    }

    report = bayesilisk.build_contextual_report(150, generated_count=8, context=context)
    context_summary = report["contextSummary"]

    assert context_summary["source"] == "unit-test-agent-gitea-context"
    assert context_summary["agentNoteCount"] == 1
    assert context_summary["issueCount"] == 1
    assert context_summary["pullRequestCount"] == 1
    assert existing["fingerprint"] in context_summary["fingerprints"]
    assert context_summary["priorAdjustments"]["dms.tenant_process_boundary"] > 0
    assert context_summary["priorAdjustments"]["hr.documents_customer_role_boundary"] > 0

    muted = next(finding for finding in report["findings"] if finding["fingerprint"] == existing["fingerprint"])
    assert muted["issueReadiness"] == "do-not-open-muted"
    assert "muted-known-non-issue" in muted["observationBasis"]["tags"]
    assert report["rankedProbes"]
    assert report["issuePayloads"]
    assert all(payload["fingerprint"] != existing["fingerprint"] for payload in report["issuePayloads"])


def test_bayesilisk_cli_context_can_emit_gitea_issue_payloads(tmp_path: Path) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "source": "unit-test-cli-context",
                "agentNotes": ["travel expense itinerary and support takeover permission probe"],
            }
        ),
        encoding="utf-8",
    )

    report = json.loads(
        run_bayesilisk("--seed", "150", "--format", "json", "--limit", "3", "--context", str(context_path)).stdout
    )
    payloads = json.loads(
        run_bayesilisk(
            "--seed",
            "150",
            "--limit",
            "3",
            "--context",
            str(context_path),
            "--issue-payloads",
        ).stdout
    )

    assert report["contextSummary"]["source"] == "unit-test-cli-context"
    assert report["rankedProbes"]
    assert payloads
    assert {"title", "body", "fingerprint", "dedupeState", "labels"} <= set(payloads[0])
    assert payloads[0]["dedupeState"] == "new"


def test_bayesilisk_mcp_server_lists_tools_and_returns_ranked_context() -> None:
    server = importlib.import_module("bayesilisk.mcp_server")

    initialize = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    tools = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    call = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "bayesilisk.rank_context",
                "arguments": {
                    "seed": 150,
                    "limit": 2,
                    "context": {
                        "agentNotes": ["HR documents DMS tenant scope and travel expense itinerary probe"],
                    },
                },
            },
        }
    )

    assert initialize["result"]["serverInfo"]["version"] == "bayesilisk.v1.2"
    assert {tool["name"] for tool in tools["result"]["tools"]} == {
        "bayesilisk.issue_payloads",
        "bayesilisk.rank_context",
        "bayesilisk.run",
    }
    payload = json.loads(call["result"]["content"][0]["text"])
    assert payload["tool"] == "bayesilisk.v1.2"
    assert payload["contextSummary"]["textSignalCount"] >= 1
    assert len(payload["rankedProbes"]) == 2

    raw = io.BytesIO()
    server.write_message(raw, {"jsonrpc": "2.0", "id": 4, "result": {"ok": True}})
    raw.seek(0)
    assert server.read_message(raw) == {"jsonrpc": "2.0", "id": 4, "result": {"ok": True}}


def test_bayesilisk_documentation_pins_no_production_access_and_report_contract() -> None:
    document = DOC.read_text(encoding="utf-8")

    for fragment in (
        "no production access",
        "Rule invariants",
        "Bayesian prioritization",
        "Scenario fragments",
        "Report Contract",
        "breakage/finding classification",
        "posterior mode",
        "fingerprint",
        "issue readiness",
        "observation history",
        "MCP tool server",
        "Context ingestion",
        "bayesilisk.rank_context",
        "bayesilisk.issue_payloads",
        "rental car, train, and airplane",
        "Permission/role matrix",
        "python3 -m bayesilisk --seed 150 --format json",
        "must not connect to production systems",
        "must not",
        "internal platform claims",
    ):
        assert fragment in document
