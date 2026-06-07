from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, BinaryIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from bayesilisk.config import effective_runtime_config  # type: ignore[no-redef]
    from bayesilisk.connector_orchestration import (  # type: ignore[no-redef]
        connector_prompt_packet,
        connector_quickstart,
        establish_provenance,
        fix_packet,
        interview_connector_need,
        scenario_plan,
        verify_connector_outputs,
    )
    from bayesilisk.connector_loop import advance as loop_advance  # type: ignore[no-redef]
    from bayesilisk.constants import VERSION  # type: ignore[no-redef]
    from bayesilisk.motifs import (  # type: ignore[no-redef]
        available_motifs,
        bind_motifs,
        load_packs,
    )
    from bayesilisk.probe_proposals import generate_probe_proposals  # type: ignore[no-redef]
    from bayesilisk.reporting import (  # type: ignore[no-redef]
        build_contextual_report,
        issue_payloads,
        ranked_probes,
    )
else:
    from .config import effective_runtime_config
    from .connector_loop import advance as loop_advance
    from .connector_orchestration import (
        connector_prompt_packet,
        connector_quickstart,
        establish_provenance,
        fix_packet,
        interview_connector_need,
        scenario_plan,
        verify_connector_outputs,
    )
    from .constants import VERSION
    from .motifs import available_motifs, bind_motifs, load_packs
    from .probe_proposals import generate_probe_proposals
    from .reporting import build_contextual_report, issue_payloads, ranked_probes

PROTOCOL_VERSION = "2024-11-05"
DEBUG_LOG_ENV = "BAYESILISK_MCP_DEBUG"
WIRE_MODE = "framed"
BAYESILISK_ASCII_LOGO = r"""
       __
  _.-'  `-..__
 /  _   _    _`-.
|  (o) (o)  / \  \
 \    __   /   |  |
  `-.___)-'   /  /
      /      /_.'
     /__/`--'
"""

RUNTIME_CONFIG_SCHEMA: dict[str, Any] = {
    "attentionSelectionLimit": {"type": "integer", "default": 4},
    "attentionThreshold": {"type": "number", "default": 0.35},
    "enableEmbeddings": {"type": "boolean", "default": False},
    "enableScenarioProposer": {"type": "boolean", "default": False},
    "embeddingModel": {"type": "string", "default": "nomic-embed-text"},
    "ollamaBaseUrl": {"type": "string", "default": "http://localhost:11434"},
    "scenarioApiKey": {"type": "string"},
    "scenarioApiKeyEnv": {"type": "string"},
    "scenarioBaseUrl": {"type": "string"},
    "scenarioModel": {"type": "string", "default": "gemma4:e2b"},
    "scenarioProposalLimit": {"type": "integer", "default": 3},
    "scenarioProvider": {"type": "string", "default": "ollama"},
}

TOOLS: tuple[dict[str, Any], ...] = (
    {
        "name": "run",
        "description": "Run Bayesilisk with optional agent/tracker context and return the full contextual report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {"type": "integer", "default": 150},
                "limit": {"type": ["integer", "null"], "default": None},
                "generatedCount": {"type": "integer", "default": 8},
                "context": {"type": "object"},
                "observations": {"type": "object"},
                **RUNTIME_CONFIG_SCHEMA,
            },
        },
    },
    {
        "name": "rank_context",
        "description": "Rank likely fault probes from supplied repository, tracker, and agent context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {"type": "integer", "default": 150},
                "limit": {"type": ["integer", "null"], "default": 10},
                "generatedCount": {"type": "integer", "default": 8},
                "context": {"type": "object"},
                "observations": {"type": "object"},
                **RUNTIME_CONFIG_SCHEMA,
            },
        },
    },
    {
        "name": "issue_payloads",
        "description": "Return deduped issue payloads for confirmed local invariant failures.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "seed": {"type": "integer", "default": 150},
                "limit": {"type": ["integer", "null"], "default": 10},
                "generatedCount": {"type": "integer", "default": 8},
                "context": {"type": "object"},
                "observations": {"type": "object"},
                "includeExisting": {"type": "boolean", "default": False},
                **RUNTIME_CONFIG_SCHEMA,
            },
        },
    },
    {
        "name": "propose_probes",
        "description": "Expand context-supplied connector proposal rules and action graphs into app-agnostic probe proposals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {"type": "object"},
                "limit": {"type": ["integer", "null"], "default": 24},
            },
        },
    },
    {
        "name": "list_motifs",
        "description": "List motif-library packs and unlocked motifs (the app-agnostic library of authorization/data-boundary probes). Premium packs show as locked without a license.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "license": {"type": "string"},
                "packs": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
    {
        "name": "bind_motifs",
        "description": "Bind motif-library probes to a connector source context, returning an augmented context (proposalRules + sequenceRules) plus the expanded proposals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sourceContext": {"type": "object"},
                "license": {"type": "string"},
                "packs": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": ["integer", "null"], "default": 24},
            },
            "required": ["sourceContext"],
        },
    },
    {
        "name": "connector_loop",
        "description": "Advance the closed connector loop one step: does all deterministic work (scan/bind/validate/verify/fix), tracks convergence, and returns the exact next action for the agent's execute step. Pass the returned state back in each call.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "state": {"type": "object"},
                "spec": {"type": "object"},
                "sourceContext": {"type": "object"},
                "observedContext": {"type": "object"},
                "packs": {"type": "array", "items": {"type": "string"}},
                "license": {"type": "string"},
                "maxRounds": {"type": "integer"},
                "maxDryRounds": {"type": "integer"},
            },
        },
    },
    {
        "name": "connector_quickstart",
        "description": "Start here for connectors: returns the ordered tool loop, boundaries, and copy-paste source/observed templates. Agent-side equivalent of `bayesilisk connector init`.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "interview_connector_need",
        "description": "Connector loop step 1/6: normalize a connector request and return bounded follow-up questions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requestText": {"type": "string"},
                "knownAnswers": {"type": "object"},
                "maxQuestions": {"type": "integer", "default": 5},
            },
            "required": ["requestText"],
        },
    },
    {
        "name": "establish_provenance",
        "description": "Connector loop step 2/6: create a caller-supplied provenance packet for connector source and execution boundaries. Call after interview_connector_need.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "connectorNeed": {"type": "object"},
                "createdAt": {"type": "string"},
                "executionBoundary": {"type": "object"},
                "sourceClaims": {"type": "array"},
            },
            "required": ["connectorNeed", "executionBoundary", "sourceClaims"],
        },
    },
    {
        "name": "connector_prompt_packet",
        "description": "Connector loop step 3/6: emit a bounded prompt/spec packet that tells Codex how to create an app-specific connector safely. Call after establish_provenance.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "connectorNeed": {"type": "object"},
                "includeExamples": {"type": "boolean", "default": True},
                "provenance": {"type": "object"},
                "style": {"type": "string", "default": "starter-kit"},
                "targetLanguage": {"type": "string", "default": "unknown"},
            },
            "required": ["connectorNeed", "provenance"],
        },
    },
    {
        "name": "scenario_plan",
        "description": "Connector loop step 4/6: build a bounded connector scenario plan from source context, proposal rules, action graphs, and optional drafts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "draftPlan": {"type": "object"},
                "limit": {"type": "integer", "default": 24},
                "provenance": {"type": "object"},
                "sourceContext": {"type": "object"},
            },
            "required": ["provenance", "sourceContext"],
        },
    },
    {
        "name": "verify_connector_outputs",
        "description": "Connector loop step 5/6: validate connector observations and run deterministic Bayesilisk verification over accepted local evidence. Call after the connector executes the scenario_plan.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "includeIssuePayloads": {"type": "boolean", "default": True},
                "limit": {"type": ["integer", "null"], "default": 10},
                "observedContext": {"type": "object"},
                "provenance": {"type": "object"},
                "scenarioPlan": {"type": "object"},
                "seed": {"type": "integer", "default": 150},
                "sourceContext": {"type": "object"},
            },
            "required": ["observedContext", "provenance"],
        },
    },
    {
        "name": "fix_packet",
        "description": "Connector loop step 6/6: emit a Codex repair brief from verified Bayesilisk findings or issue payloads only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "briefStyle": {"type": "string", "default": "concise"},
                "issuePayloads": {"type": "array"},
                "maxFindings": {"type": "integer", "default": 3},
                "provenance": {"type": "object"},
                "verifiedReport": {"type": "object"},
            },
            "required": ["provenance", "verifiedReport"],
        },
    },
)


def _canonical_tool_name(name: Any) -> str | None:
    if not isinstance(name, str):
        return None
    if name.startswith("bayesilisk."):
        return name.removeprefix("bayesilisk.")
    return name


def _debug_log(message: str) -> None:
    log_path = os.environ.get(DEBUG_LOG_ENV)
    if not log_path:
        return
    with Path(log_path).open("a", encoding="utf-8") as handle:
        handle.write(f"{message}\n")


def _tool_content(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, indent=2, sort_keys=True),
            }
        ],
        "isError": False,
    }


def _error_response(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _report_from_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    seed = int(arguments.get("seed", 150))
    generated_count = int(arguments.get("generatedCount", arguments.get("generated_count", 8)))
    limit = arguments.get("limit")
    if limit is not None:
        limit = int(limit)
    context = arguments.get("context", {})
    observations = arguments.get("observations", {})
    if not isinstance(context, dict):
        raise ValueError("context must be an object")
    if not isinstance(observations, dict):
        raise ValueError("observations must be an object")
    runtime_config = {
        key: arguments[key]
        for key in RUNTIME_CONFIG_SCHEMA
        if key in arguments
    }
    return build_contextual_report(
        seed,
        limit=limit,
        generated_count=generated_count,
        observations=observations,
        context=context,
        runtime_config=effective_runtime_config(runtime_config),
    )


def handle_request(message: dict[str, Any]) -> dict[str, Any] | None:
    request_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})
    if method == "notifications/initialized":
        return None
    if request_id is None and method not in {"notifications/initialized"}:
        return None
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "bayesilisk", "version": VERSION},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": list(TOOLS)}}
    if method != "tools/call":
        return _error_response(request_id, -32601, f"unknown method: {method}")

    if not isinstance(params, dict):
        return _error_response(request_id, -32602, "params must be an object")
    requested_name = params.get("name")
    name = _canonical_tool_name(requested_name)
    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return _error_response(request_id, -32602, "arguments must be an object")
    try:
        if name == "run":
            report = _report_from_arguments(arguments)
            payload = report
        elif name == "rank_context":
            report = _report_from_arguments(arguments)
            payload = {
                "contextSummary": report["contextSummary"],
                "effectiveConfiguration": report["effectiveConfiguration"],
                "rankedProbes": ranked_probes(report, limit=arguments.get("limit", 10)),
                "sections": report["sections"],
                "tool": report["tool"],
            }
        elif name == "issue_payloads":
            report = _report_from_arguments(arguments)
            payload = {
                "contextSummary": report["contextSummary"],
                "effectiveConfiguration": report["effectiveConfiguration"],
                "issuePayloads": issue_payloads(
                    report,
                    context=arguments.get("context", {}),
                    limit=arguments.get("limit", 10),
                    include_existing=bool(arguments.get("includeExisting", False)),
                ),
                "tool": report["tool"],
            }
        elif name == "propose_probes":
            context = arguments.get("context", {})
            if not isinstance(context, dict):
                raise ValueError("context must be an object")
            limit = arguments.get("limit", 24)
            if limit is not None:
                limit = int(limit)
            proposals = generate_probe_proposals(context, limit=limit or 24)
            payload = {
                "proposalCount": len(proposals),
                "proposals": proposals,
                "tool": VERSION,
            }
        elif name == "list_motifs":
            extra_packs = arguments.get("packs", []) or []
            packs = load_packs(license_token=arguments.get("license"), extra_packs=extra_packs)
            payload = {
                "packs": [{key: pack[key] for key in ("packId", "version", "tier", "title", "unlocked", "reason", "motifCount")} for pack in packs],
                "motifs": available_motifs(license_token=arguments.get("license"), extra_packs=extra_packs),
                "tool": VERSION,
            }
        elif name == "bind_motifs":
            source_context = arguments.get("sourceContext", {})
            if not isinstance(source_context, dict):
                raise ValueError("sourceContext must be an object")
            extra_packs = arguments.get("packs", []) or []
            motifs = available_motifs(license_token=arguments.get("license"), extra_packs=extra_packs)
            bound = bind_motifs(source_context, motifs)
            limit = arguments.get("limit", 24)
            limit = int(limit) if limit is not None else 24
            payload = {
                "boundContext": bound,
                "boundMotifCount": len(motifs),
                "proposals": generate_probe_proposals(bound, limit=limit),
                "tool": VERSION,
            }
        elif name == "connector_loop":
            payload = loop_advance(
                arguments.get("state"),
                spec=arguments.get("spec"),
                source_context=arguments.get("sourceContext"),
                observed_context=arguments.get("observedContext"),
                packs=arguments.get("packs", []) or [],
                license_token=arguments.get("license"),
                max_rounds=arguments.get("maxRounds"),
                max_dry_rounds=arguments.get("maxDryRounds"),
            )
        elif name == "connector_quickstart":
            payload = connector_quickstart(arguments)
        elif name == "interview_connector_need":
            payload = interview_connector_need(arguments)
        elif name == "establish_provenance":
            payload = establish_provenance(arguments)
        elif name == "connector_prompt_packet":
            payload = connector_prompt_packet(arguments)
        elif name == "scenario_plan":
            payload = scenario_plan(arguments)
        elif name == "verify_connector_outputs":
            payload = verify_connector_outputs(arguments)
        elif name == "fix_packet":
            payload = fix_packet(arguments)
        else:
            return _error_response(request_id, -32602, f"unknown tool: {requested_name}")
    except Exception as exc:
        return _error_response(request_id, -32000, str(exc))
    return {"jsonrpc": "2.0", "id": request_id, "result": _tool_content(payload)}


def read_message(stream: BinaryIO) -> dict[str, Any] | None:
    global WIRE_MODE
    headers: dict[str, str] = {}
    while True:
        line = stream.readline()
        if line == b"":
            return None
        if line.lstrip().startswith(b"{"):
            WIRE_MODE = "jsonl"
            return json.loads(line.decode("utf-8"))
        if line in {b"\r\n", b"\n"}:
            break
        name, _, value = line.decode("ascii").partition(":")
        headers[name.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    payload = stream.read(length)
    if not payload:
        return None
    WIRE_MODE = "framed"
    return json.loads(payload.decode("utf-8"))


def write_message(stream: BinaryIO, message: dict[str, Any]) -> None:
    payload = json.dumps(message, separators=(",", ":"), sort_keys=True).encode("utf-8")
    if WIRE_MODE == "jsonl":
        stream.write(payload + b"\n")
    else:
        stream.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
        stream.write(payload)
    stream.flush()


def write_startup_banner(stream: Any) -> None:
    stream.write(f"{BAYESILISK_ASCII_LOGO.strip()}\n\nBayesilisk MCP\nBill is awake\n{VERSION}\n")
    stream.flush()


def main() -> int:
    _debug_log(f"start executable={sys.executable} cwd={Path.cwd()}")
    if os.environ.get("BAYESILISK_MCP_BANNER") == "1":
        write_startup_banner(sys.stderr)
    while True:
        message = read_message(sys.stdin.buffer)
        if message is None:
            _debug_log("stdin closed")
            return 0
        _debug_log(f"request method={message.get('method')} id={message.get('id')}")
        response = handle_request(message)
        if response is not None:
            if "error" in response:
                _debug_log(f"response error={response['error']}")
            else:
                _debug_log(f"response method={message.get('method')} id={response.get('id')}")
            write_message(sys.stdout.buffer, response)


if __name__ == "__main__":
    raise SystemExit(main())
