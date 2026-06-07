"""Lightweight, dependency-free validation for motif packs.

Mirrors the manual-validation style used in connector_orchestration.py rather
than pulling in jsonschema, keeping the core zero-dependency. The JSON Schema in
schemas/motif-pack.schema.json is the human/editor reference; this module is the
runtime gate.
"""

from __future__ import annotations

import re
from typing import Any

PACK_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
MOTIF_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
TOKEN_RE = re.compile(
    r"^(principal|session|scope|resource|identifier|state|boundary|capability|evidence)"
    r"\.[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)?$"
)
TIERS = {"core", "premium"}
KINDS = {"param-mutation", "workflow-sequence"}
SEVERITIES = {"low", "medium", "high", "critical"}
CONFIDENCES = {"deterministic", "heuristic"}


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _status_ok(value: Any) -> bool:
    return _is_int(value) and 100 <= value <= 599


def _validate_expected_behavior(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}.expectedBehavior is required and must be an object")
        return
    if not _status_ok(value.get("status")):
        errors.append(f"{prefix}.expectedBehavior.status must be an integer 100-599")
    alt = value.get("alt", [])
    if alt and (not isinstance(alt, list) or not all(_status_ok(item) for item in alt)):
        errors.append(f"{prefix}.expectedBehavior.alt must be a list of status integers")


def _validate_token(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict) or not TOKEN_RE.match(_str(value.get("token"))):
        errors.append(f"{prefix} must be an ABAG token object with a valid `token`")


def _validate_motif(motif: Any, index: int, seen: set[str], errors: list[str], warnings: list[str]) -> None:
    prefix = f"motifs[{index}]"
    if not isinstance(motif, dict):
        errors.append(f"{prefix} must be an object")
        return
    motif_id = _str(motif.get("motifId"))
    if not MOTIF_ID_RE.match(motif_id):
        errors.append(f"{prefix}.motifId is missing or malformed")
    elif motif_id in seen:
        errors.append(f"{prefix}.motifId `{motif_id}` is duplicated")
    else:
        seen.add(motif_id)

    kind = _str(motif.get("kind"))
    if kind not in KINDS:
        errors.append(f"{prefix}.kind must be one of {sorted(KINDS)}")
    if not _str(motif.get("family")):
        errors.append(f"{prefix}.family is required")
    if _str(motif.get("severity")) not in SEVERITIES:
        errors.append(f"{prefix}.severity must be one of {sorted(SEVERITIES)}")
    if _str(motif.get("confidence")) not in CONFIDENCES:
        errors.append(f"{prefix}.confidence must be one of {sorted(CONFIDENCES)}")
    if not _str(motif.get("rationale")):
        errors.append(f"{prefix}.rationale is required")
    _validate_expected_behavior(motif.get("expectedBehavior"), prefix, errors)

    if kind == "param-mutation":
        applies = motif.get("appliesTo")
        if not isinstance(applies, dict) or not (_str(applies.get("paramKind")) or applies.get("tokens")):
            errors.append(f"{prefix}.appliesTo needs a paramKind and/or tokens")
        mutation = motif.get("mutation")
        if not isinstance(mutation, dict) or not _str(mutation.get("id")):
            errors.append(f"{prefix}.mutation.id is required for param-mutation motifs")
    elif kind == "workflow-sequence":
        requires = motif.get("requiresTokens")
        if not isinstance(requires, list) or not requires:
            errors.append(f"{prefix}.requiresTokens must be a non-empty list for workflow-sequence motifs")
        else:
            for token_index, token in enumerate(requires):
                _validate_token(token, f"{prefix}.requiresTokens[{token_index}]", errors)
        if not isinstance(motif.get("pattern"), list) or not motif.get("pattern"):
            warnings.append(f"{prefix}.pattern is empty; sequence motifs read better with a step pattern")


def validate_pack(pack: Any) -> dict[str, Any]:
    """Validate a motif pack structure. Returns {accepted, errors, warnings}."""
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(pack, dict):
        return {"accepted": False, "errors": ["pack must be a JSON object"], "warnings": []}

    if not PACK_ID_RE.match(_str(pack.get("packId"))):
        errors.append("packId is missing or malformed")
    if not _str(pack.get("version")):
        errors.append("version is required")
    tier = _str(pack.get("tier"))
    if tier not in TIERS:
        errors.append(f"tier must be one of {sorted(TIERS)}")
    if tier == "premium" and not _str(pack.get("signature")):
        warnings.append("premium pack has no signature; it cannot be loaded without one")

    motifs = pack.get("motifs")
    if not isinstance(motifs, list) or not motifs:
        errors.append("motifs must be a non-empty list")
    else:
        seen: set[str] = set()
        for index, motif in enumerate(motifs):
            _validate_motif(motif, index, seen, errors, warnings)

    return {"accepted": not errors, "errors": errors, "warnings": warnings}
