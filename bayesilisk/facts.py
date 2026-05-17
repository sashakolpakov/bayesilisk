from __future__ import annotations

import hashlib
import json
from typing import Any

from .constants import (
    BOOLEAN_AND_FACT_KEYS,
    BOOLEAN_OR_FACT_KEYS,
    HR_DOCUMENT_ROUTE,
    LIST_FACT_KEYS,
    NUMERIC_SUM_FACT_KEYS,
    VERSION,
)
from .invariants import has_route
from .types import Fragment, Invariant, Scenario

def merge_unique(existing: list[Any], incoming: list[Any]) -> list[Any]:
    merged = list(existing)
    for item in incoming:
        if item not in merged:
            merged.append(item)
    return merged


def merge_facts(fragments: list[Fragment]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    modules: dict[str, bool] = {}
    conflicts: list[dict[str, Any]] = []

    for fragment in fragments:
        for key, value in fragment.facts.items():
            if key == "modules":
                modules.update(value)
            elif key in LIST_FACT_KEYS:
                facts[key] = merge_unique(facts.get(key, []), value)
            elif key in BOOLEAN_OR_FACT_KEYS:
                facts[key] = bool(facts.get(key, False) or value)
            elif key in BOOLEAN_AND_FACT_KEYS:
                facts[key] = bool(facts.get(key, True) and value)
            elif key in NUMERIC_SUM_FACT_KEYS:
                facts[key] = int(facts.get(key, 0)) + int(value)
            elif key in facts and facts[key] != value:
                conflicts.append(
                    {
                        "fragmentId": fragment.id,
                        "key": key,
                        "previous": facts[key],
                        "incoming": value,
                    }
                )
                facts[key] = value
            else:
                facts[key] = value
    if modules:
        facts["modules"] = modules
    if conflicts:
        facts["factConflicts"] = conflicts
    return facts


def sub_scenarios(fragments: list[Fragment]) -> list[dict[str, Any]]:
    return [
        {
            "id": f"subscenario.{index}.{fragment.id}",
            "fragmentId": fragment.id,
            "domain": fragment.domain,
            "kind": fragment.kind,
            "completeAlone": fragment.complete_alone,
            "summary": fragment.summary,
        }
        for index, fragment in enumerate(fragments, start=1)
    ]


def access_pattern(facts: dict[str, Any]) -> dict[str, Any]:
    data_signals = {
        key: facts[key]
        for key in (
            "allRequiredReceiptsUsable",
            "documentTenantMatches",
            "itineraryCoversExpenseDates",
            "segmentsChronological",
            "targetEmployeeId",
            "transportModesCoveredByItinerary",
        )
        if key in facts
    }
    return {
        "actorRole": facts.get("actorRole", "unknown"),
        "businessFlow": facts.get("businessFlow", []),
        "decision": facts.get("decision"),
        "expenseCategories": facts.get("expenseCategories", []),
        "modules": facts.get("modules", {}),
        "routes": facts.get("routes", []),
        "transportModes": facts.get("transportModes", []),
        "dataSignals": data_signals,
    }


def scenario_fragment_payload(fragments: list[Fragment]) -> list[dict[str, Any]]:
    return [
        {
            "completeAlone": fragment.complete_alone,
            "domain": fragment.domain,
            "id": fragment.id,
            "kind": fragment.kind,
            "summary": fragment.summary,
        }
        for fragment in fragments
    ]


def scenario_reproducer_payload(
    scenario: Scenario,
    fragments: list[Fragment],
    observation: str | None = None,
) -> dict[str, Any]:
    facts = merge_facts(fragments)
    payload = {
        "accessPattern": access_pattern(facts),
        "fragmentIds": [fragment.id for fragment in fragments],
        "fragments": scenario_fragment_payload(fragments),
        "generatedScenario": scenario.generated,
        "generationBasis": scenario.generation_basis,
        "scenarioId": scenario.id,
        "scenarioTitle": scenario.title,
        "scenarioTone": scenario.tone,
        "subScenarios": sub_scenarios(fragments),
    }
    if observation is not None:
        payload["observation"] = observation
    return payload


def _preserves_minimization_context(
    original_facts: dict[str, Any],
    candidate_facts: dict[str, Any],
    invariant: Invariant,
) -> bool:
    if invariant.id in {
        "roles.route_matrix_allowed",
        "support.takeover_session_required",
        "hr.documents_customer_role_boundary",
    }:
        original_actor = original_facts.get("actorRole")
        if original_actor is not None and candidate_facts.get("actorRole") != original_actor:
            return False
    if invariant.id == "hr.documents_customer_role_boundary" and has_route(original_facts, HR_DOCUMENT_ROUTE):
        return has_route(candidate_facts, HR_DOCUMENT_ROUTE)
    return True


def minimize_failing_generated_scenario(
    scenario: Scenario,
    invariant: Invariant,
    fragments: list[Fragment],
    original_observation: str,
) -> dict[str, Any] | None:
    if not scenario.generated:
        return None
    original_facts = merge_facts(fragments)
    passed, observation = invariant.evaluator(original_facts)
    if passed or observation != original_observation:
        return None

    minimized = list(fragments)
    changed = True
    while changed:
        changed = False
        for index in range(len(minimized)):
            candidate = [fragment for candidate_index, fragment in enumerate(minimized) if candidate_index != index]
            if not candidate:
                continue
            candidate_facts = merge_facts(candidate)
            if not _preserves_minimization_context(original_facts, candidate_facts, invariant):
                continue
            candidate_passed, candidate_observation = invariant.evaluator(candidate_facts)
            if not candidate_passed and candidate_observation == original_observation:
                minimized = candidate
                changed = True
                break

    removed_ids = [fragment.id for fragment in fragments if fragment not in minimized]
    payload = scenario_reproducer_payload(scenario, minimized, observation=original_observation)
    payload.update(
        {
            "invariantId": invariant.id,
            "minimized": len(minimized) < len(fragments),
            "minimizedFragmentCount": len(minimized),
            "originalFragmentCount": len(fragments),
            "preservedInvariantFailure": True,
            "removedFragmentIds": removed_ids,
        }
    )
    return payload


def finding_fingerprint(scenario: Scenario, invariant: Invariant, fragments: list[Fragment]) -> str:
    payload = {
        "fragments": [fragment.id for fragment in fragments],
        "invariant": invariant.id,
        "scenario": scenario.id,
        "tool": VERSION,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    return f"bayesilisk:{digest[:16]}"
