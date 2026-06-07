"""Turn an OpenAPI spec into a draft Bayesilisk source context.

This is the deterministic L1 extractor: it discovers an app's surface (routes,
parameters, operations) so the motif library can auto-apply probes. It does not
decide expected behavior beyond what the spec documents; motifs supply the
adversarial expectations when bound. JSON specs work with zero dependencies;
YAML requires the optional `[scan]` extra (pyyaml).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

HTTP_METHODS = ("get", "post", "put", "patch", "delete")

_ID_RE = re.compile(r"(^id$|_id$|Id$|uid$|uuid$|guid$)", re.IGNORECASE)
_TENANT_RE = re.compile(r"(tenant|org|organization|account|workspace|company)", re.IGNORECASE)
_TOKEN_RE = re.compile(r"(token|secret|nonce|otp|apikey|api_key)", re.IGNORECASE)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "operation"


def infer_param_kind(name: str, schema: dict[str, Any] | None) -> tuple[str, list[str]]:
    """Infer a Bayesilisk param kind + ABAG tokens from an OpenAPI parameter."""
    schema = schema if isinstance(schema, dict) else {}
    fmt = str(schema.get("format", "")).lower()
    if _TENANT_RE.search(name):
        return "tenant-id", ["scope.tenant"]
    if _TOKEN_RE.search(name):
        return "token", ["identifier.single_use_token"]
    if _ID_RE.search(name) or fmt in {"uuid", "uri"}:
        return "id", ["resource.id"]
    schema_type = str(schema.get("type", "")).lower()
    if schema_type in {"integer", "number"}:
        return "number", []
    return "string", []


def _parameters(operation: dict[str, Any], path_item: dict[str, Any]) -> list[dict[str, Any]]:
    raw = [p for p in path_item.get("parameters", []) if isinstance(p, dict)]
    raw += [p for p in operation.get("parameters", []) if isinstance(p, dict)]
    params: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in raw:
        name = str(entry.get("name", "")).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        location = str(entry.get("in", "query")).strip() or "query"
        if location not in {"path", "query"}:
            continue  # only path/query params are probe-mutable here
        kind, tokens = infer_param_kind(name, entry.get("schema"))
        param: dict[str, Any] = {
            "name": name,
            "kind": kind,
            "location": location,
            "required": bool(entry.get("required", location == "path")),
        }
        if tokens:
            param["tokens"] = tokens
        params.append(param)
    return params


def _documented_denial(operation: dict[str, Any]) -> int | None:
    responses = operation.get("responses")
    if not isinstance(responses, dict):
        return None
    codes: list[int] = []
    for code in responses:
        try:
            value = int(code)
        except (TypeError, ValueError):
            continue
        if 400 <= value < 500:
            codes.append(value)
    for preferred in (404, 403, 401, 409, 410):
        if preferred in codes:
            return preferred
    return min(codes) if codes else None


def scan_openapi(spec: dict[str, Any]) -> dict[str, Any]:
    """Build a draft source context (repositoryFacts) from an OpenAPI document."""
    facts: list[dict[str, Any]] = []
    paths = spec.get("paths") if isinstance(spec.get("paths"), dict) else {}
    for route in sorted(paths):
        path_item = paths[route]
        if not isinstance(path_item, dict):
            continue
        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if not isinstance(operation, dict):
                continue
            params = _parameters(operation, path_item)
            if not params:
                continue  # nothing to mutate
            action = _slug(str(operation.get("operationId") or f"{method}-{route}"))
            title = str(operation.get("summary") or f"{method.upper()} {route}").strip()
            fact: dict[str, Any] = {
                "source": "openapi-scan",
                "title": title,
                "invariantId": f"external.{action.replace('-', '_')}",
                "routePattern": route,
                "params": params,
                "availableActions": [action],
                "path": route,
                "httpMethod": method.upper(),
            }
            denial = _documented_denial(operation)
            if denial is not None:
                fact["expectedBehavior"] = {"status": denial}
            facts.append(fact)
    title = ""
    if isinstance(spec.get("info"), dict):
        title = str(spec["info"].get("title", "")).strip()
    return {
        "source": "openapi-scan",
        "agentNotes": [
            f"Draft source context scanned from OpenAPI{f' ({title})' if title else ''}; "
            "review params, then bind motifs to add probe rules.",
        ],
        "repositoryFacts": facts,
    }


def load_spec(path: Path) -> dict[str, Any]:
    """Load an OpenAPI spec. JSON is zero-dep; YAML needs the [scan] extra."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:  # pragma: no cover - exercised only without the extra
            raise SystemExit("YAML specs require the optional extra: pip install 'bayesilisk[scan]'") from exc
        spec = yaml.safe_load(text)
    else:
        spec = json.loads(text)
    if not isinstance(spec, dict):
        raise SystemExit("OpenAPI spec must be a JSON/YAML object")
    return spec
