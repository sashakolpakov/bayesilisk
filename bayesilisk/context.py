from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .constants import CONTEXT_COLLECTION_KEYS, CONTEXT_INVARIANT_KEYWORDS, FINGERPRINT_PATTERN
from .types import Invariant, Scenario

def load_observations(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_context(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _context_items(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _context_items(nested)
    elif isinstance(value, list | tuple):
        for nested in value:
            yield from _context_items(nested)


def _context_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, int | float | bool):
        yield str(value)
    elif isinstance(value, dict):
        for nested in value.values():
            yield from _context_strings(nested)
    elif isinstance(value, list | tuple):
        for nested in value:
            yield from _context_strings(nested)


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list | tuple | set):
        return []
    return sorted({item for item in value if isinstance(item, str)})


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _count_context_collection(context: dict[str, Any], key: str) -> int:
    value = context.get(key)
    if isinstance(value, list | tuple):
        return len(value)
    if isinstance(value, dict):
        return len(value)
    return 0


def _context_prior_adjustments(text: str) -> tuple[dict[str, float], dict[str, int]]:
    lower = text.lower()
    keyword_hits: dict[str, int] = {}
    adjustments: dict[str, float] = {}
    for invariant_id, keywords in CONTEXT_INVARIANT_KEYWORDS.items():
        hits = sum(lower.count(keyword) for keyword in keywords)
        if hits <= 0:
            continue
        keyword_hits[invariant_id] = hits
        adjustments[invariant_id] = round(min(0.18, 0.018 * hits), 6)
    return adjustments, keyword_hits


def context_summary(context: dict[str, Any] | None) -> dict[str, Any]:
    context = _dict_or_empty(context)
    text_values = list(_context_strings(context))
    text = "\n".join(text_values)
    fingerprints = sorted(set(FINGERPRINT_PATTERN.findall(text)))
    prior_adjustments, keyword_hits = _context_prior_adjustments(text)
    return {
        "source": context.get("source", "mcp-context" if context else "none"),
        "agentNoteCount": _count_context_collection(context, "agentNotes"),
        "issueCount": _count_context_collection(context, "issues")
        + _count_context_collection(context, "openIssues"),
        "pullRequestCount": _count_context_collection(context, "pullRequests")
        + _count_context_collection(context, "prs"),
        "repositoryFactCount": _count_context_collection(context, "repositoryFacts"),
        "textSignalCount": len([value for value in text_values if value.strip()]),
        "fingerprints": fingerprints,
        "keywordHits": keyword_hits,
        "priorAdjustments": prior_adjustments,
    }


def context_observations(context: dict[str, Any] | None) -> dict[str, Any]:
    summary = context_summary(context)
    context = _dict_or_empty(context)
    muted = set(summary["fingerprints"])
    muted.update(_string_list(context.get("mutedFingerprints")))
    fixed = set(_string_list(context.get("fixedFingerprints")))
    confirmed = set(_string_list(context.get("confirmedFingerprints")))
    explicit_adjustments = context.get("priorAdjustments", {})
    prior_adjustments = dict(summary["priorAdjustments"])
    if isinstance(explicit_adjustments, dict):
        for invariant_id, delta in explicit_adjustments.items():
            if isinstance(invariant_id, str) and isinstance(delta, int | float):
                prior_adjustments[invariant_id] = round(float(delta), 6)
    scenario_adjustments = context.get("scenarioAdjustments", {})
    if not isinstance(scenario_adjustments, dict):
        scenario_adjustments = {}
    return {
        "source": summary["source"],
        "fixedFingerprints": sorted(fixed),
        "confirmedFingerprints": sorted(confirmed),
        "mutedFingerprints": sorted(muted),
        "priorAdjustments": prior_adjustments,
        "scenarioAdjustments": scenario_adjustments,
    }


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _context_plane_facts(context: dict[str, Any] | None) -> list[dict[str, Any]]:
    facts: list[dict[str, Any]] = []
    context = _dict_or_empty(context)
    if not context:
        return facts
    for item in _context_items(context):
        if not isinstance(item, dict):
            continue
        invariant_id = item.get("invariantId")
        if not isinstance(invariant_id, str):
            continue
        passed = item.get("passed")
        if not isinstance(passed, bool):
            expected_status = _int_or_none(item.get("expectedStatus"))
            observed_status = _int_or_none(item.get("observedStatus"))
            if expected_status is None or observed_status is None:
                continue
            passed = expected_status == observed_status
        facts.append(
            {
                "actorRole": item.get("actorRole"),
                "invariantId": invariant_id,
                "passed": passed,
                "route": item.get("route"),
                "source": item.get("source", context.get("source", "context")),
            }
        )
    return facts


def merge_observations(base: dict[str, Any] | None, incoming: dict[str, Any] | None) -> dict[str, Any]:
    base = _dict_or_empty(base)
    incoming = _dict_or_empty(incoming)
    merged = dict(base)
    merged["source"] = incoming.get("source") or base.get("source", "none")
    for key in ("fixedFingerprints", "confirmedFingerprints", "mutedFingerprints"):
        merged[key] = sorted(set(_string_list(base.get(key))) | set(_string_list(incoming.get(key))))
    for key in ("priorAdjustments", "scenarioAdjustments"):
        merged_values = {}
        if isinstance(base.get(key), dict):
            merged_values.update(base[key])
        if isinstance(incoming.get(key), dict):
            merged_values.update(incoming[key])
        merged[key] = merged_values
    return merged


def observation_basis(
    fingerprint: str,
    scenario: Scenario,
    invariant: Invariant,
    observations: dict[str, Any],
) -> dict[str, Any]:
    fixed = set(observations.get("fixedFingerprints", []))
    confirmed = set(observations.get("confirmedFingerprints", []))
    muted = set(observations.get("mutedFingerprints", []))
    invariant_adjustments = observations.get("priorAdjustments", {})
    scenario_adjustments = observations.get("scenarioAdjustments", {})

    prior_delta = 0.0
    tags: list[str] = []
    if fingerprint in fixed:
        prior_delta -= 0.28
        tags.append("fixed-regression-watch")
    if fingerprint in confirmed:
        prior_delta += 0.18
        tags.append("confirmed-local-breakage")
    if fingerprint in muted:
        prior_delta -= 0.45
        tags.append("muted-known-non-issue")
    if invariant.id in invariant_adjustments:
        prior_delta += float(invariant_adjustments[invariant.id])
        tags.append(f"invariant-adjustment:{invariant.id}")
    if scenario.id in scenario_adjustments:
        prior_delta += float(scenario_adjustments[scenario.id])
        tags.append(f"scenario-adjustment:{scenario.id}")
    return {
        "source": observations.get("source", "none"),
        "tags": tags or ["fresh-prior"],
        "priorDelta": round(prior_delta, 6),
    }
