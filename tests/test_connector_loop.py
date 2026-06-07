from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bayesilisk.connector_loop import advance  # noqa: E402

SPEC = {
    "openapi": "3.0.0",
    "info": {"title": "Loop Demo"},
    "paths": {
        "/bookings/{bookingId}": {
            "get": {
                "operationId": "getBooking",
                "parameters": [{"name": "bookingId", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {}, "404": {}},
            }
        }
    },
}


def _observed_from(result: dict, *, passed: bool) -> dict:
    """Build an observed context that fails (or passes) the first proposed probe."""
    proposal = result["proposals"][0]
    expected = proposal["expectedStatus"]
    observed_status = expected if passed else 200 if expected != 200 else 500
    return {
        "source": "connector-observation",
        "repositoryFacts": [
            {
                "actorRole": proposal.get("actorRole") or "operator",
                "artifactPaths": [],
                "expectedStatus": expected,
                "failureDetail": "observed during local execution",
                "invariantId": proposal["invariantId"],
                "networkResponses": [],
                "observedStatus": observed_status,
                "passed": observed_status == expected,
                "route": proposal["routePattern"],
                "selector": "connector:" + proposal["connectorAction"],
                "source": "connector-observation",
                "targetUrl": "http://localhost:3000/bookings/x",
                "timestamp": "2026-06-07T00:00:00Z",
                "title": proposal["title"],
            }
        ],
    }


def test_loop_starts_from_spec_and_awaits_connector() -> None:
    result = advance(None, spec=SPEC)
    assert result["phase"] == "await-connector"
    assert result["proposals"]
    assert result["boundContext"]["repositoryFacts"]
    assert "connector" in result["nextAction"].lower()
    assert result["loopId"]


def test_loop_verifies_repairs_then_converges() -> None:
    start = advance(None, spec=SPEC, max_dry_rounds=1)
    observed = _observed_from(start, passed=False)

    first = advance(start["state"], observed_context=observed)
    assert first["phase"] == "repair"
    assert first["newFindingCount"] >= 1
    assert first["issuePayloads"]
    assert first.get("fixPacket")

    # Same observed evidence again -> no new fingerprints -> dry round -> converged (maxDryRounds=1).
    second = advance(first["state"], observed_context=observed)
    assert second["phase"] == "converged"
    assert second["newFindingCount"] == 0
    # No duplicate accumulation.
    fingerprints = [f["fingerprint"] for f in second["state"]["readyFindings"]]
    assert len(fingerprints) == len(set(fingerprints))


def test_loop_blocks_on_invalid_observed() -> None:
    start = advance(None, spec=SPEC)
    bad = _observed_from(start, passed=False)
    bad["repositoryFacts"][0]["passed"] = True  # inconsistent with observedStatus != expectedStatus
    result = advance(start["state"], observed_context=bad)
    assert result["phase"] == "blocked"
    assert any("passed" in e for e in result["observationValidation"]["errors"])


def test_loop_round_cap_stops() -> None:
    start = advance(None, spec=SPEC, max_rounds=1, max_dry_rounds=9)
    result = advance(start["state"], observed_context=_observed_from(start, passed=True))
    assert result["round"] == 1
    assert result["phase"] == "converged"  # hit the round cap


def test_loop_is_deterministic() -> None:
    a = advance(None, spec=SPEC)
    b = advance(None, spec=SPEC)
    assert json.dumps(a["state"], sort_keys=True) == json.dumps(b["state"], sort_keys=True)


def test_mcp_connector_loop_roundtrip() -> None:
    server = importlib.import_module("bayesilisk.mcp_server")

    def call(arguments: dict) -> dict:
        response = server.handle_request(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "connector_loop", "arguments": arguments}}
        )
        return json.loads(response["result"]["content"][0]["text"])

    start = call({"spec": SPEC})
    assert start["phase"] == "await-connector"
    observed = _observed_from(start, passed=False)
    nxt = call({"state": start["state"], "observedContext": observed, "maxDryRounds": 1})
    assert nxt["phase"] in {"repair", "converged"}
    assert nxt["issuePayloads"]
