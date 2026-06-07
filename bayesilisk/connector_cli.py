"""User-friendly `bayesilisk connector` subcommands.

This is the terminal-facing front end for the connector loop that previously
existed only over MCP/Codex. It is a thin wrapper: every check and expansion is
delegated to :mod:`bayesilisk.connector_orchestration` and
:mod:`bayesilisk.probe_proposals` so the CLI and the agent path share identical
deterministic behavior.

    connector init      scaffold a starter source/observed context
    connector validate  lint a source or observed context with clear diagnostics
    connector propose   expand proposal rules (loud, never a silent empty list)
    connector verify    run deterministic verification over observed evidence
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .connector_orchestration import (
    local_provenance,
    observed_fact_template,
    source_context_template,
    validate_observed_context,
    validate_source_context,
    verify_connector_outputs,
)
from .connector_loop import advance as loop_advance
from .connector_scan import load_spec, scan_openapi
from .motifs import available_motifs, bind_motifs, load_packs
from .probe_proposals import generate_probe_proposals
from .reporting import markdown_report

ACTION_GRAPH_TEMPLATE = {
    "actions": [
        {
            "actionId": "create-resource",
            "produces": [
                {"token": "resource.public_id", "resourceType": "generic_resource", "refines": "resource.id"},
                {"token": "state.active", "resourceType": "generic_resource", "refines": "resource.state.active"},
            ],
        },
        {
            "actionId": "retire-resource",
            "requires": [
                {"token": "resource.public_id", "resourceType": "generic_resource", "refines": "resource.id"}
            ],
            "produces": [
                {"token": "state.revoked", "resourceType": "generic_resource", "refines": "resource.state.retired"}
            ],
        },
        {"actionId": "open-resource-route", "requires": []},
    ],
    "sequenceRules": [
        {
            "ruleId": "retired-resource-replay",
            "invariantId": "app.retired_resource_rejected",
            "expectedBehavior": {"status": 410},
            "requiresState": [
                {"token": "state.revoked", "resourceType": "generic_resource"}
            ],
            "goal": {
                "action": "open-resource-route",
                "paramBindings": {
                    "resourceId": {"token": "resource.public_id", "resourceType": "generic_resource", "refines": "resource.id"}
                },
            },
            "maxDepth": 4,
            "title": "Retired resource replay is rejected",
        }
    ],
}


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def _emit(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content if content.endswith("\n") else content + "\n")
    else:
        output.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _dump(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _print_diagnostics(label: str, validation: dict[str, Any]) -> None:
    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])
    if validation.get("accepted", not errors):
        _eprint(f"OK: {label} accepted")
    else:
        _eprint(f"FAIL: {label} rejected")
    for error in errors:
        _eprint(f"  error: {error}")
    for warning in warnings:
        _eprint(f"  warning: {warning}")


def _cmd_init(args: argparse.Namespace) -> int:
    kind = args.kind
    context: dict[str, Any] = {}
    if kind in {"source", "both"}:
        context = source_context_template()
        context.setdefault("agentNotes", []).append(
            "Replace placeholder ids/routes/proposalRules with source-backed values, then run "
            "`bayesilisk connector validate`."
        )
        if args.with_action_graph:
            context["connectorActionGraph"] = ACTION_GRAPH_TEMPLATE
    if kind == "observed":
        context = {
            "source": "connector-observation",
            "agentNotes": [
                "observedStatus and passed must come from real local execution, not from prose."
            ],
            "priorAdjustments": {},
            "repositoryFacts": [observed_fact_template()],
        }
    elif kind == "both":
        context["repositoryFacts"] = [*context.get("repositoryFacts", []), observed_fact_template()]
    _emit(_dump(context), args.output)
    if args.output is not None:
        _eprint(f"wrote {kind} connector skeleton to {args.output}")
        _eprint("next: bayesilisk connector validate " + str(args.output))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    context = _load_json(args.context)
    if not isinstance(context, dict):
        _eprint("FAIL: context file is not a JSON object")
        return 1
    if args.observed:
        plan = _load_json(args.plan) if args.plan else None
        validation = validate_observed_context(context, scenario_plan_payload=plan)
        _print_diagnostics("observed context", validation)
        _eprint(f"  observed facts: {validation.get('observedFactCount', 0)}")
        return 0 if validation["accepted"] else 1
    validation = validate_source_context(context)
    _print_diagnostics("source context", validation)
    _eprint(f"  source facts: {validation['factCount']}  proposals: {validation['proposalCount']}")
    if validation["declaredActions"]:
        _eprint("  declared actions: " + ", ".join(validation["declaredActions"]))
    return 0 if validation["accepted"] else 1


def _packs_from_args(args: argparse.Namespace) -> list[str]:
    return [str(path) for path in (getattr(args, "pack", None) or [])]


def _motifs_from_args(args: argparse.Namespace) -> list[dict[str, Any]]:
    return available_motifs(
        license_token=getattr(args, "license", None),
        extra_packs=_packs_from_args(args),
    )


def _cmd_propose(args: argparse.Namespace) -> int:
    context = _load_json(args.context)
    if not isinstance(context, dict):
        _eprint("FAIL: context file is not a JSON object")
        return 1
    if getattr(args, "bind_motifs", False):
        motifs = _motifs_from_args(args)
        context = bind_motifs(context, motifs)
        _eprint(f"bound {len(motifs)} motif(s) from {len(_packs_from_args(args)) + 1} pack source(s)")
    limit = args.limit if args.limit is not None else 24
    proposals = generate_probe_proposals(context, limit=limit)
    _emit(_dump(proposals), args.output)
    if not proposals:
        # The key fix over `--probe-proposals-output`: never silently emit [].
        validation = validate_source_context(context)
        _eprint("WARNING: 0 probe proposals generated.")
        for warning in validation["warnings"] or [
            "add proposalRules, proposalGates, or connectorActionGraph.sequenceRules"
        ]:
            _eprint(f"  {warning}")
        return 1
    _eprint(f"generated {len(proposals)} probe proposal(s)")
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    source_context = _load_json(args.source) if args.source else {}
    observed_context = _load_json(args.observed)
    if not isinstance(observed_context, dict):
        _eprint("FAIL: --observed file is not a JSON object")
        return 1
    if args.provenance:
        provenance = _load_json(args.provenance)
    else:
        prov_payload = local_provenance(source_context if isinstance(source_context, dict) else {})
        if not prov_payload["validation"]["accepted"]:
            _print_diagnostics("local provenance", prov_payload["validation"])
            return 1
        provenance = prov_payload["provenance"]
    plan = _load_json(args.plan) if args.plan else {}
    result = verify_connector_outputs(
        {
            "sourceContext": source_context if isinstance(source_context, dict) else {},
            "observedContext": observed_context,
            "provenance": provenance,
            "scenarioPlan": plan,
            "seed": args.seed,
            "includeIssuePayloads": True,
        }
    )
    validation = result["observationValidation"]
    _print_diagnostics("observed context", validation)
    if not validation["accepted"]:
        return 1
    if args.issue_payloads:
        _emit(_dump(result["issuePayloads"]), args.output)
        _eprint(f"emitted {len(result['issuePayloads'])} issue payload(s)")
    elif args.format == "markdown" and result["report"]:
        _emit(markdown_report(result["report"]), args.output)
    else:
        _emit(_dump(result["report"]), args.output)
    verified = result["ledgers"]["verifiedByBayesilisk"]
    _eprint(f"verified findings: {len(verified)}")
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    spec = load_spec(args.spec)
    context = scan_openapi(spec)
    fact_count = len(context["repositoryFacts"])
    if args.bind_motifs:
        motifs = _motifs_from_args(args)
        context = bind_motifs(context, motifs)
        _eprint(f"scanned {fact_count} route(s); bound {len(motifs)} motif(s)")
    else:
        _eprint(f"scanned {fact_count} route(s); pass --bind-motifs to add probe rules")
    _emit(_dump(context), args.output)
    if args.output is not None:
        _eprint("next: bayesilisk connector validate " + str(args.output))
    return 0


def _cmd_motifs(args: argparse.Namespace) -> int:
    packs = load_packs(license_token=getattr(args, "license", None), extra_packs=_packs_from_args(args))
    if args.show:
        for motif in _motifs_from_args(args):
            if motif.get("motifId") == args.show:
                _emit(_dump(motif), None)
                return 0
        _eprint(f"no unlocked motif `{args.show}` found")
        return 1
    for pack in packs:
        lock = "unlocked" if pack["unlocked"] else "LOCKED"
        _eprint(f"[{lock}] {pack['packId']} ({pack['tier']}, v{pack['version']}) - {pack['motifCount']} motif(s): {pack['reason']}")
        if not pack["valid"]:
            for error in pack["errors"]:
                _eprint(f"    error: {error}")
        for motif in pack["motifs"]:
            status = motif.get("expectedBehavior", {}).get("status")
            _eprint(f"    - {motif['motifId']} [{motif['kind']}, {motif.get('severity')}] -> {status}")
    return 0


def _cmd_loop(args: argparse.Namespace) -> int:
    state = _load_json(args.state) if args.state.exists() else None
    result = loop_advance(
        state,
        spec=load_spec(args.spec) if args.spec else None,
        source_context=_load_json(args.source) if args.source else None,
        observed_context=_load_json(args.observed) if args.observed else None,
        packs=_packs_from_args(args),
        license_token=getattr(args, "license", None),
        max_rounds=args.max_rounds,
        max_dry_rounds=args.max_dry_rounds,
    )
    args.state.write_text(_dump(result["state"]) + "\n", encoding="utf-8")
    _eprint(f"[{result['phase']}] round {result['round']}")
    _eprint(result["nextAction"])
    if "newFindingCount" in result:
        _eprint(f"  new findings: {result['newFindingCount']} | total issue payloads: {len(result.get('issuePayloads', []))}")
    _emit(_dump({key: value for key, value in result.items() if key != "state"}), args.output)
    return 1 if result["phase"] == "blocked" else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bayesilisk connector",
        description="Author, lint, and verify Bayesilisk connectors from the terminal.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="Scaffold a starter connector context JSON.")
    init_parser.add_argument("--kind", choices=("source", "observed", "both"), default="source")
    init_parser.add_argument("--with-action-graph", action="store_true", help="Include a connectorActionGraph example.")
    init_parser.add_argument("--output", type=Path, default=None, help="Write to a file instead of stdout.")
    init_parser.set_defaults(func=_cmd_init)

    validate_parser = sub.add_parser("validate", help="Lint a source or observed connector context.")
    validate_parser.add_argument("context", type=Path, help="Path to the context JSON.")
    validate_parser.add_argument("--observed", action="store_true", help="Validate as observed evidence, not source.")
    validate_parser.add_argument("--plan", type=Path, default=None, help="Optional scenario plan to cross-check actions.")
    validate_parser.set_defaults(func=_cmd_validate)

    propose_parser = sub.add_parser("propose", help="Expand source-context proposal rules into probe proposals.")
    propose_parser.add_argument("context", type=Path, help="Path to the source-context JSON.")
    propose_parser.add_argument("--limit", type=int, default=None, help="Maximum proposals.")
    propose_parser.add_argument("--bind-motifs", action="store_true", help="Bind motif-library probes before expanding.")
    propose_parser.add_argument("--pack", type=Path, action="append", help="Extra motif pack file/dir (repeatable).")
    propose_parser.add_argument("--license", default=None, help="License token or path (or set BAYESILISK_LICENSE).")
    propose_parser.add_argument("--output", type=Path, default=None, help="Write to a file instead of stdout.")
    propose_parser.set_defaults(func=_cmd_propose)

    scan_parser = sub.add_parser("scan", help="Scan an OpenAPI spec into a draft source context.")
    scan_parser.add_argument("spec", type=Path, help="Path to an OpenAPI JSON (or YAML with the [scan] extra).")
    scan_parser.add_argument("--bind-motifs", action="store_true", help="Bind motif-library probes to the scanned routes.")
    scan_parser.add_argument("--pack", type=Path, action="append", help="Extra motif pack file/dir (repeatable).")
    scan_parser.add_argument("--license", default=None, help="License token or path (or set BAYESILISK_LICENSE).")
    scan_parser.add_argument("--output", type=Path, default=None, help="Write to a file instead of stdout.")
    scan_parser.set_defaults(func=_cmd_scan)

    motifs_parser = sub.add_parser("motifs", help="List or show motif-library packs and motifs.")
    motifs_parser.add_argument("--show", default=None, help="Print one motif by id (must be unlocked).")
    motifs_parser.add_argument("--pack", type=Path, action="append", help="Extra motif pack file/dir (repeatable).")
    motifs_parser.add_argument("--license", default=None, help="License token or path (or set BAYESILISK_LICENSE).")
    motifs_parser.set_defaults(func=_cmd_motifs)

    loop_parser = sub.add_parser("loop", help="Advance the closed connector loop one step (agent-driven).")
    loop_parser.add_argument("--state", type=Path, required=True, help="Loop state JSON (created if missing).")
    loop_parser.add_argument("--spec", type=Path, default=None, help="OpenAPI spec to scan on the first step.")
    loop_parser.add_argument("--source", type=Path, default=None, help="Source context JSON to start from instead of a spec.")
    loop_parser.add_argument("--observed", type=Path, default=None, help="Observed-context JSON from connector execution.")
    loop_parser.add_argument("--pack", type=Path, action="append", help="Extra motif pack file/dir (repeatable).")
    loop_parser.add_argument("--license", default=None, help="License token or path (or set BAYESILISK_LICENSE).")
    loop_parser.add_argument("--max-rounds", type=int, default=None, help="Round cap (default 6).")
    loop_parser.add_argument("--max-dry-rounds", type=int, default=None, help="Stop after K dry rounds (default 2).")
    loop_parser.add_argument("--output", type=Path, default=None, help="Write the step result JSON to a file instead of stdout.")
    loop_parser.set_defaults(func=_cmd_loop)

    verify_parser = sub.add_parser("verify", help="Run deterministic verification over observed evidence.")
    verify_parser.add_argument("--source", type=Path, default=None, help="Source-context JSON (for explanation).")
    verify_parser.add_argument("--observed", type=Path, required=True, help="Observed-evidence JSON.")
    verify_parser.add_argument("--plan", type=Path, default=None, help="Optional scenario plan JSON.")
    verify_parser.add_argument("--provenance", type=Path, default=None, help="Provenance JSON; a local one is built if omitted.")
    verify_parser.add_argument("--seed", type=int, default=150, help="Deterministic ordering seed.")
    verify_parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Report format.")
    verify_parser.add_argument("--issue-payloads", action="store_true", help="Emit only issue payloads.")
    verify_parser.add_argument("--output", type=Path, default=None, help="Write to a file instead of stdout.")
    verify_parser.set_defaults(func=_cmd_verify)

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
