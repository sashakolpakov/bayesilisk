from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, BinaryIO

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from bayesilisk.config import effective_runtime_config  # type: ignore[no-redef]
    from bayesilisk.engine import VERSION  # type: ignore[no-redef]
    from bayesilisk.reporting import (  # type: ignore[no-redef]
        build_contextual_report,
        issue_payloads,
        ranked_probes,
    )
else:
    from .config import effective_runtime_config
    from .engine import VERSION
    from .reporting import build_contextual_report, issue_payloads, ranked_probes

PROTOCOL_VERSION = "2024-11-05"

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
        "name": "bayesilisk.run",
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
        "name": "bayesilisk.rank_context",
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
        "name": "bayesilisk.issue_payloads",
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
)


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
    name = params.get("name")
    arguments = params.get("arguments", {})
    if not isinstance(arguments, dict):
        return _error_response(request_id, -32602, "arguments must be an object")
    try:
        report = _report_from_arguments(arguments)
        if name == "bayesilisk.run":
            payload = report
        elif name == "bayesilisk.rank_context":
            payload = {
                "contextSummary": report["contextSummary"],
                "effectiveConfiguration": report["effectiveConfiguration"],
                "rankedProbes": ranked_probes(report, limit=arguments.get("limit", 10)),
                "sections": report["sections"],
                "tool": report["tool"],
            }
        elif name == "bayesilisk.issue_payloads":
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
        else:
            return _error_response(request_id, -32602, f"unknown tool: {name}")
    except Exception as exc:
        return _error_response(request_id, -32000, str(exc))
    return {"jsonrpc": "2.0", "id": request_id, "result": _tool_content(payload)}


def read_message(stream: BinaryIO) -> dict[str, Any] | None:
    headers: dict[str, str] = {}
    while True:
        line = stream.readline()
        if line == b"":
            return None
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
    return json.loads(payload.decode("utf-8"))


def write_message(stream: BinaryIO, message: dict[str, Any]) -> None:
    payload = json.dumps(message, separators=(",", ":"), sort_keys=True).encode("utf-8")
    stream.write(f"Content-Length: {len(payload)}\r\n\r\n".encode("ascii"))
    stream.write(payload)
    stream.flush()


def main() -> int:
    while True:
        message = read_message(sys.stdin.buffer)
        if message is None:
            return 0
        response = handle_request(message)
        if response is not None:
            write_message(sys.stdout.buffer, response)


if __name__ == "__main__":
    raise SystemExit(main())
