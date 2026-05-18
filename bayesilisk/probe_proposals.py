from __future__ import annotations

from typing import Any

from .utils import _safe_hash, _slug_id

DEFAULT_PROPOSAL_LIMIT = 24


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _status(value: Any) -> int | None:
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


def _source_facts(context: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(context, dict):
        return []
    facts = context.get("repositoryFacts", [])
    if not isinstance(facts, list):
        return []
    return [
        fact
        for fact in facts
        if isinstance(fact, dict)
        and isinstance(fact.get("routePattern"), str)
        and not (isinstance(fact.get("expectedStatus"), int) and isinstance(fact.get("observedStatus"), int))
    ]


def _expected_status(fact: dict[str, Any]) -> int | None:
    behavior = fact.get("expectedBehavior")
    if isinstance(behavior, dict):
        status = _status(behavior.get("status"))
        if status is not None:
            return status
    status = _status(fact.get("expectedStatus"))
    if status is not None:
        return status
    return None


def _actions(fact: dict[str, Any]) -> list[str]:
    actions = fact.get("availableActions")
    if not isinstance(actions, list):
        return []
    return [_string(action) for action in actions if _string(action)]


def _params(fact: dict[str, Any]) -> list[dict[str, Any]]:
    params = fact.get("params")
    if not isinstance(params, list):
        return []
    return [param for param in params if isinstance(param, dict) and _string(param.get("name"))]


def _normalize_mutation(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str):
        mutation_id = _string(value)
        return {"mutationId": mutation_id} if mutation_id else None
    if not isinstance(value, dict):
        return None
    mutation_id = _string(value.get("id") or value.get("mutationId"))
    if not mutation_id:
        return None
    normalized = {"mutationId": mutation_id}
    if "value" in value:
        normalized["value"] = value["value"]
    if "mutatedValue" in value:
        normalized["value"] = value["mutatedValue"]
    if isinstance(value.get("title"), str):
        normalized["title"] = value["title"]
    return normalized


def _proposal_rules(fact: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rules = fact.get("proposalRules")
    if not isinstance(rules, dict):
        return {}
    normalized: dict[str, list[dict[str, Any]]] = {}
    for param_name, mutations in rules.items():
        name = _string(param_name)
        if not name:
            continue
        if isinstance(mutations, str):
            mutations = [mutations]
        if not isinstance(mutations, list):
            continue
        normalized_mutations = [_normalize_mutation(mutation) for mutation in mutations]
        normalized[name] = [mutation for mutation in normalized_mutations if mutation is not None]
    return normalized


def _context_gates(context: dict[str, Any] | None) -> list[dict[str, Any]]:
    gates = context.get("proposalGates") if isinstance(context, dict) else None
    if not isinstance(gates, list):
        return []
    return [gate for gate in gates if isinstance(gate, dict) and _string(gate.get("gateId"))]


def _gate_rules(gates: list[dict[str, Any]], fact: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    invariant_id = _string(fact.get("invariantId"))
    merged: dict[str, list[dict[str, Any]]] = {}
    for gate in gates:
        invariant_ids = gate.get("invariantIds")
        if isinstance(invariant_ids, list) and invariant_id not in {_string(item) for item in invariant_ids}:
            continue
        rules = gate.get("rules")
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            param_name = _string(rule.get("param"))
            mutations = rule.get("mutations")
            if isinstance(mutations, str):
                mutations = [mutations]
            if not param_name or not isinstance(mutations, list):
                continue
            normalized_mutations = [_normalize_mutation(mutation) for mutation in mutations]
            merged[param_name] = [mutation for mutation in normalized_mutations if mutation is not None]
    return merged


def generate_probe_proposals(context: dict[str, Any] | None, *, limit: int = DEFAULT_PROPOSAL_LIMIT) -> list[dict[str, Any]]:
    proposals: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    gates = _context_gates(context)
    for fact in _source_facts(context):
        invariant_id = _string(fact.get("invariantId"), "external.connector_probe")
        route_pattern = _string(fact.get("routePattern"))
        actions = _actions(fact)
        params = _params(fact)
        fact_rules = _proposal_rules(fact)
        gate_rules = _gate_rules(gates, fact)
        rules = fact_rules or gate_rules
        expected_status = _expected_status(fact)
        if not rules or expected_status is None:
            continue
        proposal_gate = "fact-proposal-rules" if fact_rules else "context-proposal-gate"
        for action in actions:
            for param in params:
                param_name = _string(param.get("name"))
                if param_name not in rules:
                    continue
                for mutation in rules[param_name]:
                    mutation_id = _string(mutation.get("mutationId"))
                    key = (action, invariant_id, route_pattern, f"{param_name}:{mutation_id}")
                    if key in seen:
                        continue
                    seen.add(key)
                    title = (
                        f"{_string(fact.get('title'), invariant_id)}: "
                        f"{_string(mutation.get('title'), mutation_id.replace('-', ' '))} for {param_name}"
                    )
                    proposal_hash = _safe_hash(key)[:10]
                    mutated_params = {}
                    if "value" in mutation:
                        mutated_params[param_name] = mutation["value"]
                    proposals.append(
                        {
                            "actorRole": _string(fact.get("actorRole"), "unknown"),
                            "connectorAction": action,
                            "expectedStatus": expected_status,
                            "invariantId": invariant_id,
                            "mutationId": mutation_id,
                            "mutatedParams": mutated_params,
                            "nearbyTests": fact.get("nearbyTests", []) if isinstance(fact.get("nearbyTests"), list) else [],
                            "path": fact.get("path"),
                            "proposalId": f"probe.{len(proposals) + 1:02d}.{_slug_id(invariant_id)}.{proposal_hash}",
                            "proposalGate": proposal_gate,
                            "rationale": "Bayesilisk expanded app-provided proposal rules; connector must execute real app behavior.",
                            "routePattern": route_pattern,
                            "sourceParam": param_name,
                            "sourceText": _string(fact.get("sourceText") or fact.get("text")),
                            "title": title,
                        }
                    )
                    if len(proposals) >= limit:
                        return proposals
    return proposals
