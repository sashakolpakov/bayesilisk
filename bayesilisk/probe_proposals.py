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
    sequence_limit = max(limit - len(proposals), 0)
    if sequence_limit:
        proposals.extend(generate_sequence_proposals(context, limit=sequence_limit))
    return proposals


def _unique_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _string(value)
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _token_aliases(value: Any) -> list[str]:
    if isinstance(value, str):
        return [_string(value)] if _string(value) else []
    if not isinstance(value, dict):
        return []
    aliases: list[str] = []
    concrete = _string(value.get("refines") or value.get("appToken") or value.get("id"))
    if concrete:
        aliases.append(concrete)
    token = _string(value.get("token") or value.get("kind"))
    resource_type = _string(value.get("resourceType") or value.get("resource"))
    if token and resource_type:
        aliases.append(f"{token}:{resource_type}")
    if token:
        aliases.append(token)
    return _unique_strings(aliases)


def _token_display_id(value: Any) -> str:
    aliases = _token_aliases(value)
    return aliases[0] if aliases else ""


def _list_of_token_display_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return _unique_strings([_token_display_id(item) for item in value])


def _list_of_token_keys(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    keys: list[str] = []
    for item in value:
        keys.extend(_token_aliases(item))
    return _unique_strings(keys)


def _abag_token(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    token = _string(value.get("token") or value.get("kind"))
    if not token:
        return None
    normalized = {"token": token}
    for key in ("refines", "resourceType", "description"):
        text = _string(value.get(key))
        if text:
            normalized[key] = text
    return normalized


def _list_of_abag_tokens(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    return [token for item in value if (token := _abag_token(item)) is not None]


def _action_graph(context: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(context, dict):
        return {}
    graph = context.get("connectorActionGraph")
    return graph if isinstance(graph, dict) else {}


def _graph_actions(graph: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    raw_actions = graph.get("actions")
    if not isinstance(raw_actions, list):
        return [], {}
    actions: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}
    for raw_action in raw_actions:
        if not isinstance(raw_action, dict):
            continue
        action_id = _string(raw_action.get("actionId") or raw_action.get("id"))
        if not action_id or action_id in by_id:
            continue
        requires_tokens = _list_of_abag_tokens(raw_action.get("requires"))
        produces_tokens = _list_of_abag_tokens(raw_action.get("produces"))
        action = {
            **raw_action,
            "actionId": action_id,
            "requires": _list_of_token_display_ids(raw_action.get("requires")),
            "produces": _list_of_token_display_ids(raw_action.get("produces")),
            "_requiresKeys": _list_of_token_keys(raw_action.get("requires")),
            "_producesKeys": _list_of_token_keys(raw_action.get("produces")),
        }
        if requires_tokens:
            action["requiresTokens"] = requires_tokens
        if produces_tokens:
            action["producesTokens"] = produces_tokens
        actions.append(action)
        by_id[action_id] = action
    return actions, by_id


def _sequence_rules(graph: dict[str, Any]) -> list[dict[str, Any]]:
    rules = graph.get("sequenceRules")
    if not isinstance(rules, list):
        return []
    normalized = []
    for rule in rules:
        if isinstance(rule, dict) and _string(rule.get("ruleId") or rule.get("id")):
            normalized.append(rule)
    return normalized


def _goal(rule: dict[str, Any]) -> dict[str, Any]:
    goal = rule.get("goal")
    return goal if isinstance(goal, dict) else {}


def _raw_param_bindings(goal: dict[str, Any], rule: dict[str, Any]) -> dict[str, Any]:
    raw_bindings = goal.get("paramBindings")
    if raw_bindings is None:
        raw_bindings = rule.get("paramBindings")
    if not isinstance(raw_bindings, dict):
        return {}
    return raw_bindings


def _param_bindings(goal: dict[str, Any], rule: dict[str, Any]) -> dict[str, str]:
    raw_bindings = _raw_param_bindings(goal, rule)
    bindings: dict[str, str] = {}
    for name, source in raw_bindings.items():
        param_name = _string(name)
        source_name = _token_display_id(source)
        if param_name and source_name:
            bindings[param_name] = source_name
    return bindings


def _param_binding_keys(goal: dict[str, Any], rule: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    for source in _raw_param_bindings(goal, rule).values():
        keys.extend(_token_aliases(source))
    return _unique_strings(keys)


def _param_binding_tokens(goal: dict[str, Any], rule: dict[str, Any]) -> dict[str, dict[str, str]]:
    tokens: dict[str, dict[str, str]] = {}
    for name, source in _raw_param_bindings(goal, rule).items():
        param_name = _string(name)
        token = _abag_token(source)
        if param_name and token is not None:
            tokens[param_name] = token
    return tokens


def _producer_for(actions: list[dict[str, Any]], token: str) -> dict[str, Any] | None:
    for action in actions:
        if token in action["_producesKeys"]:
            return action
    return None


def _topological_action_order(plan: list[dict[str, Any]], terminal_action_id: str) -> list[dict[str, Any]] | None:
    remaining = [action for action in plan if action["actionId"] != terminal_action_id]
    terminal = next((action for action in plan if action["actionId"] == terminal_action_id), None)
    ordered: list[dict[str, Any]] = []
    produced: set[str] = set()

    while remaining:
        progressed = False
        for action in list(remaining):
            if all(token in produced for token in action["_requiresKeys"]):
                ordered.append(action)
                produced.update(action["_producesKeys"])
                remaining.remove(action)
                progressed = True
        if not progressed:
            return None

    if terminal is not None:
        if not all(token in produced for token in terminal["_requiresKeys"]):
            return None
        ordered.append(terminal)
    return ordered


def _build_sequence(
    *,
    actions: list[dict[str, Any]],
    by_id: dict[str, dict[str, Any]],
    rule: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, str]] | None:
    goal = _goal(rule)
    terminal_action_id = _string(goal.get("action") or rule.get("terminalAction"))
    terminal = by_id.get(terminal_action_id)
    if terminal is None:
        return None

    bindings = _param_bindings(goal, rule)
    required: list[str] = []
    for token in [*terminal["_requiresKeys"], *_list_of_token_keys(rule.get("requiresState")), *_param_binding_keys(goal, rule)]:
        if token not in required:
            required.append(token)

    plan: list[dict[str, Any]] = []
    produced: set[str] = set()
    added_actions: set[str] = set()
    max_depth = _status(rule.get("maxDepth")) or 5

    while True:
        missing = [token for token in required if token not in produced]
        if not missing:
            break
        if len(plan) >= max_depth:
            return None
        producer = _producer_for(actions, missing[0])
        if producer is None:
            return None
        action_id = producer["actionId"]
        if action_id in added_actions:
            return None
        for token in producer["_requiresKeys"]:
            if token not in required:
                required.append(token)
        produced.update(producer["_producesKeys"])
        added_actions.add(action_id)
        plan.append(producer)

    if terminal_action_id not in added_actions:
        plan.append(terminal)
    if len(plan) > max_depth:
        return None
    ordered = _topological_action_order(plan, terminal_action_id)
    if ordered is None:
        return None
    return ordered, bindings


def generate_sequence_proposals(context: dict[str, Any] | None, *, limit: int = DEFAULT_PROPOSAL_LIMIT) -> list[dict[str, Any]]:
    graph = _action_graph(context)
    actions, by_id = _graph_actions(graph)
    if not actions:
        return []

    proposals: list[dict[str, Any]] = []
    seen: set[tuple[str, str, tuple[str, ...], tuple[tuple[str, str], ...]]] = set()
    for rule in _sequence_rules(graph):
        invariant_id = _string(rule.get("invariantId"), "external.connector_sequence_rule")
        expected_status = _expected_status(rule)
        if expected_status is None:
            continue
        built = _build_sequence(actions=actions, by_id=by_id, rule=rule)
        if built is None:
            continue
        sequence, bindings = built
        action_ids = tuple(action["actionId"] for action in sequence)
        key = (
            _string(rule.get("ruleId") or rule.get("id")),
            invariant_id,
            action_ids,
            tuple(sorted(bindings.items())),
        )
        if key in seen:
            continue
        seen.add(key)
        proposal_hash = _safe_hash(key)[:10]
        sequence_steps = []
        binding_tokens = _param_binding_tokens(_goal(rule), rule)
        for index, action in enumerate(sequence, start=1):
            is_terminal = index == len(sequence)
            step = {
                "connectorAction": action["actionId"],
                "params": bindings if is_terminal else {},
                "produces": action["produces"],
                "requires": action["requires"],
                "stepId": f"step.{index:02d}.{_slug_id(action['actionId'])}",
            }
            if action.get("requiresTokens"):
                step["requiresTokens"] = action["requiresTokens"]
            if action.get("producesTokens"):
                step["producesTokens"] = action["producesTokens"]
            if is_terminal and binding_tokens:
                step["paramBindingTokens"] = binding_tokens
            sequence_steps.append(step)
        proposals.append(
            {
                "expectedStatus": expected_status,
                "invariantId": invariant_id,
                "proposalGate": "connector-action-graph",
                "proposalId": f"sequence.{len(proposals) + 1:02d}.{_slug_id(invariant_id)}.{proposal_hash}",
                "proposalKind": "workflow-sequence",
                "rationale": "Bayesilisk composed connector-declared actions into a bounded deterministic workflow sequence.",
                "sequenceRuleId": _string(rule.get("ruleId") or rule.get("id")),
                "sequenceSteps": sequence_steps,
                "title": _string(rule.get("title"), invariant_id),
            }
        )
        if len(proposals) >= limit:
            return proposals
    return proposals
