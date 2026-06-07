"""L3 closed connector loop: a stateless next-step controller.

Bayesilisk cannot execute an arbitrary app (auth, fixtures, browser) and must
never let a model decide the verdict. So the loop does every *deterministic* step
(scan -> bind motifs -> validate -> verify -> fix) and tracks convergence, then
hands the agent the exact next action for the one step it cannot do: write and run
the connector. The agent drives by calling `advance` repeatedly, passing the
returned state back in each time; Bayesilisk holds no session.

Determinism: no clocks or RNG; ids derive from content hashes; fingerprints are
sorted. Convergence: stop after `maxDryRounds` consecutive rounds with no new
verified ready-for-issue fingerprint, or when `maxRounds` is reached.
"""

from __future__ import annotations

import copy
from typing import Any, Iterable

from .connector_orchestration import (
    fix_packet,
    local_provenance,
    scenario_plan,
    validate_source_context,
    verify_connector_outputs,
)
from .connector_scan import scan_openapi
from .motifs import available_motifs, bind_motifs
from .probe_proposals import generate_probe_proposals
from .utils import _safe_hash

DEFAULT_MAX_ROUNDS = 6
DEFAULT_MAX_DRY_ROUNDS = 2

# Phases
START = "start"
AWAIT_CONNECTOR = "await-connector"
AWAIT_EXECUTION = "await-execution"
REPAIR = "repair"
BLOCKED = "blocked"
CONVERGED = "converged"


def init_state(*, max_rounds: int = DEFAULT_MAX_ROUNDS, max_dry_rounds: int = DEFAULT_MAX_DRY_ROUNDS) -> dict[str, Any]:
    return {
        "loopId": None,
        "round": 0,
        "phase": START,
        "sourceContext": None,
        "boundContext": None,
        "provenance": None,
        "scenarioPlan": None,
        "seenFingerprints": [],
        "readyFindings": [],
        "issuePayloads": [],
        "dryRounds": 0,
        "maxRounds": max(1, int(max_rounds)),
        "maxDryRounds": max(1, int(max_dry_rounds)),
    }


def _result(state: dict[str, Any], next_action: str, **outputs: Any) -> dict[str, Any]:
    payload = {"loopId": state["loopId"], "state": state, "phase": state["phase"], "round": state["round"], "nextAction": next_action}
    payload.update({key: value for key, value in outputs.items() if value is not None})
    return payload


def _ready_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        finding
        for finding in report.get("findings", [])
        if isinstance(finding, dict)
        and finding.get("observedResult") == "fail"
        and finding.get("issueReadiness") == "ready-for-issue"
    ]


def advance(
    state: dict[str, Any] | None,
    *,
    spec: dict[str, Any] | None = None,
    source_context: dict[str, Any] | None = None,
    observed_context: dict[str, Any] | None = None,
    packs: Iterable[str] = (),
    license_token: str | None = None,
    max_rounds: int | None = None,
    max_dry_rounds: int | None = None,
    seed: int = 150,
) -> dict[str, Any]:
    """Advance the loop one step. Pure: returns a fresh state + the step outputs."""
    state = copy.deepcopy(state) if state else init_state()
    if max_rounds is not None:
        state["maxRounds"] = max(1, int(max_rounds))
    if max_dry_rounds is not None:
        state["maxDryRounds"] = max(1, int(max_dry_rounds))

    # Phase 1: establish a bound source context if we do not have one yet.
    if not state.get("sourceContext"):
        context = source_context if isinstance(source_context, dict) else (scan_openapi(spec) if isinstance(spec, dict) else None)
        if context is None:
            state["phase"] = START
            return _result(state, "Provide an OpenAPI spec or a source context to begin (--spec or --source).")
        motifs = available_motifs(license_token=license_token, extra_packs=packs)
        bound = bind_motifs(context, motifs)
        validation = validate_source_context(bound)
        proposals = generate_probe_proposals(bound)
        prov = local_provenance(bound)
        if not prov["validation"]["accepted"]:
            state["phase"] = BLOCKED
            return _result(state, "Local provenance was rejected: " + "; ".join(prov["validation"]["errors"][:5]))
        plan = scenario_plan({"provenance": prov["provenance"], "sourceContext": bound})
        state["sourceContext"] = bound
        state["boundContext"] = bound
        state["provenance"] = prov["provenance"]
        state["scenarioPlan"] = plan["scenarioPlan"]
        state["loopId"] = _safe_hash({"source": bound.get("source"), "proposals": [p.get("proposalId") for p in proposals]})[:16]
        state["phase"] = AWAIT_CONNECTOR
        next_action = (
            f"Write a connector that maps these {len(proposals)} proposed probe(s) to real local "
            "fixture/browser/API actions, execute it against local/dev/staging only, then re-run the "
            "loop with the observed-context.json it produces."
        )
        return _result(
            state,
            next_action,
            boundContext=bound,
            boundMotifCount=len(motifs),
            proposals=proposals,
            sourceValidation=validation,
        )

    # Phase 2: we have a source context; we need observed evidence to advance.
    if not isinstance(observed_context, dict):
        return _result(
            state,
            "Execute the connector against local fixtures and re-run the loop with --observed observed-context.json.",
        )

    result = verify_connector_outputs(
        {
            "sourceContext": state["sourceContext"],
            "observedContext": observed_context,
            "provenance": state["provenance"],
            "scenarioPlan": state["scenarioPlan"],
            "seed": seed,
            "includeIssuePayloads": True,
        }
    )
    state["round"] += 1
    validation = result["observationValidation"]
    if not validation["accepted"]:
        state["phase"] = BLOCKED
        return _result(
            state,
            "Observed evidence was rejected; fix it and re-run: " + "; ".join(validation["errors"][:5]),
            observationValidation=validation,
        )

    report = result.get("report") or {}
    payload_by_fingerprint = {p.get("fingerprint"): p for p in result.get("issuePayloads", []) if isinstance(p, dict)}
    seen = set(state["seenFingerprints"])
    new_findings = [f for f in _ready_findings(report) if f.get("fingerprint") and f["fingerprint"] not in seen]

    fix = None
    if new_findings:
        state["dryRounds"] = 0
        for finding in new_findings:
            fingerprint = finding["fingerprint"]
            seen.add(fingerprint)
            state["readyFindings"].append(
                {
                    "fingerprint": fingerprint,
                    "invariantId": finding.get("invariantId"),
                    "title": finding.get("suggestedIssueTitle"),
                    "round": state["round"],
                }
            )
            if fingerprint in payload_by_fingerprint:
                state["issuePayloads"].append(payload_by_fingerprint[fingerprint])
        state["seenFingerprints"] = sorted(seen)
        fix = fix_packet(
            {"verifiedReport": report, "issuePayloads": result.get("issuePayloads", []), "provenance": state["provenance"]}
        ).get("fixPacket")
    else:
        state["dryRounds"] += 1

    converged = state["dryRounds"] >= state["maxDryRounds"] or state["round"] >= state["maxRounds"]
    if converged:
        state["phase"] = CONVERGED
        next_action = (
            f"Converged after {state['round']} round(s) with {len(state['issuePayloads'])} verified issue "
            "payload(s). Open issues from the accumulated issuePayloads; act only on verified output."
        )
    elif new_findings:
        state["phase"] = REPAIR
        next_action = (
            f"{len(new_findings)} new verified finding(s). Apply the fix briefs (or widen motif coverage), "
            "re-execute the connector, and re-run the loop with the new observed-context.json."
        )
    else:
        state["phase"] = AWAIT_EXECUTION
        next_action = (
            "No new findings this round. Expand probe coverage or fixtures, re-execute, and re-run the loop "
            "with the new observed-context.json."
        )
    return _result(
        state,
        next_action,
        observationValidation=validation,
        report=report,
        fixPacket=fix,
        issuePayloads=state["issuePayloads"],
        newFindingCount=len(new_findings),
    )
