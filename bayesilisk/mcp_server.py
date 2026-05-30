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
        establish_provenance,
        fix_packet,
        interview_connector_need,
        scenario_plan,
        verify_connector_outputs,
    )
    from bayesilisk.constants import VERSION  # type: ignore[no-redef]
    from bayesilisk.probe_proposals import generate_probe_proposals  # type: ignore[no-redef]
    from bayesilisk.reporting import (  # type: ignore[no-redef]
        build_contextual_report,
        issue_payloads,
        ranked_probes,
    )
else:
    from .config import effective_runtime_config
    from .connector_orchestration import (
        connector_prompt_packet,
        establish_provenance,
        fix_packet,
        interview_connector_need,
        scenario_plan,
        verify_connector_outputs,
    )
    from .constants import VERSION
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
        "name": "interview_connector_need",
        "description": "Normalize a Codex connector request and return bounded follow-up questions.",
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
        "description": "Create a caller-supplied provenance packet for connector source and execution boundaries.",
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
        "description": "Emit a bounded prompt/spec packet that tells Codex how to create an app-specific connector safely.",
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
        "description": "Build a bounded connector scenario plan from source context, proposal rules, action graphs, and optional drafts.",
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
        "description": "Validate connector observations and run deterministic Bayesilisk verification over accepted local evidence.",
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
        "description": "Emit a Codex repair brief from verified Bayesilisk findings or issue payloads only.",
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
