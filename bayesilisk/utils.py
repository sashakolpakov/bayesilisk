from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.parse
from typing import Any

from .constants import SENSITIVE_FIELD_PATTERN

def _slug_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")[:48] or "proposal"


def _extract_json_object(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
        if isinstance(payload, dict):
            return payload
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return {}
    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


SCENARIO_PROPOSER_PROMPT_VERSION = "scenario-proposer.v1"


def _safe_url_class(base_url: str) -> str:
    parsed = urllib.parse.urlparse(base_url)
    host = (parsed.hostname or "").lower()
    if host in {"localhost", "127.0.0.1", "::1"}:
        return "loopback"
    if host.startswith("10.") or host.startswith("192.168.") or re.match(r"^172\.(1[6-9]|2\d|3[0-1])\.", host):
        return "private-network"
    if not host:
        return "unknown"
    return "remote-host"


def _safe_hostname_class(base_url: str) -> str:
    return _safe_url_class(base_url)


def _safe_hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _redact_secrets(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            key_text = str(key)
            if SENSITIVE_FIELD_PATTERN.search(key_text):
                redacted[key_text] = "[REDACTED]"
            else:
                redacted[key_text] = _redact_secrets(value)
        return redacted
    if isinstance(payload, list):
        return [_redact_secrets(item) for item in payload]
    if isinstance(payload, str):
        return re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+", r"\1[REDACTED]", payload)
    return payload


def _safe_error(exc: Exception) -> str:
    if isinstance(exc, urllib.error.HTTPError) and exc.code in {401, 403}:
        return "provider-authentication-failed"
    return str(_redact_secrets(str(exc)))


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _invariant_id_set(payload: dict[str, Any] | None, *keys: str) -> set[str]:
    from .invariants import INVARIANTS

    if not isinstance(payload, dict):
        return set()
    invariant_ids = {invariant.id for invariant in INVARIANTS}
    found: set[str] = set()
    for key in keys:
        values = payload.get(key, [])
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, str) and value in invariant_ids:
                found.add(value)
    return found
