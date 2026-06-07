"""Bind motifs to a source context.

A motif is a template. The binder matches motifs against an app's declared facts,
params, ABAG tokens, and (optionally) a connector action graph, then emits the
deterministic `proposalRules` / `connectorActionGraph.sequenceRules` that
`bayesilisk.probe_proposals.generate_probe_proposals` already knows how to expand
and the verifier already knows how to check. Nothing here decides a verdict.

Because the proposal engine carries one expected status per fact, each matched
param-mutation motif produces a derived source fact (a copy of the host fact with
the motif's expected status and a single proposal rule) rather than mutating the
original. Binding is deterministic: sorted iteration, no randomness.
"""

from __future__ import annotations

import copy
from typing import Any


def _str(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _token_strings(value: Any) -> set[str]:
    """Collect ABAG token strings from a string, a token object, or a list of either."""
    tokens: set[str] = set()
    if isinstance(value, str):
        if _str(value):
            tokens.add(_str(value))
    elif isinstance(value, dict):
        token = _str(value.get("token") or value.get("kind"))
        if token:
            tokens.add(token)
    elif isinstance(value, list):
        for item in value:
            tokens |= _token_strings(item)
    return tokens


def _param_tokens(param: dict[str, Any], fact: dict[str, Any]) -> set[str]:
    tokens = _token_strings(param.get("tokens")) | _token_strings(param.get("token"))
    tokens |= _token_strings(fact.get("tokens"))
    return tokens


def _source_facts(context: dict[str, Any]) -> list[dict[str, Any]]:
    facts = context.get("repositoryFacts")
    if not isinstance(facts, list):
        return []
    out: list[dict[str, Any]] = []
    for fact in facts:
        if not isinstance(fact, dict):
            continue
        has_route = isinstance(fact.get("routePattern"), str) and fact["routePattern"].strip()
        has_observed = isinstance(fact.get("observedStatus"), int) and not isinstance(fact.get("observedStatus"), bool)
        if has_route and not has_observed:
            out.append(fact)
    return out


def _matches_param(motif: dict[str, Any], param: dict[str, Any], param_tokens: set[str]) -> bool:
    applies = motif.get("appliesTo")
    if not isinstance(applies, dict):
        return False
    kind = _str(applies.get("paramKind"))
    if kind and kind == _str(param.get("kind")):
        return True
    motif_tokens = {t for t in (applies.get("tokens") or []) if isinstance(t, str)}
    return bool(motif_tokens & param_tokens)


def _render(template: str, param_name: str, fallback: str) -> str:
    text = _str(template)
    if not text:
        return fallback
    return text.replace("{param}", param_name)


def _derived_fact(fact: dict[str, Any], param: dict[str, Any], motif: dict[str, Any]) -> dict[str, Any]:
    param_name = _str(param.get("name"))
    mutation = motif.get("mutation") if isinstance(motif.get("mutation"), dict) else {}
    mutation_id = _str(mutation.get("id")) or _str(motif.get("motifId"))
    expected = motif.get("expectedBehavior", {})
    derived = copy.deepcopy(fact)
    derived["invariantId"] = _str(fact.get("invariantId")) or f"external.{_str(motif.get('motifId')).replace('-', '_')}"
    derived["expectedBehavior"] = {"status": expected.get("status")}
    derived.pop("expectedStatus", None)
    derived["proposalRules"] = {
        param_name: [
            {
                "id": mutation_id,
                "value": _render(mutation.get("valueTemplate", ""), param_name, mutation_id),
                "title": _str(mutation.get("title")) or mutation_id.replace("-", " "),
            }
        ]
    }
    derived["title"] = f"{_str(motif.get('family'))}: {_str(motif.get('motifId'))} ({param_name})"
    derived["motifId"] = _str(motif.get("motifId"))
    derived["motifFamily"] = _str(motif.get("family"))
    derived["motifSeverity"] = _str(motif.get("severity"))
    derived["motifConfidence"] = _str(motif.get("confidence"))
    if motif.get("references"):
        derived["motifReferences"] = motif["references"]
    if isinstance(expected.get("alt"), list):
        derived["expectedStatusAlternatives"] = expected["alt"]
    return derived


def _graph_produced_tokens(context: dict[str, Any]) -> set[str]:
    graph = context.get("connectorActionGraph")
    if not isinstance(graph, dict):
        return set()
    tokens: set[str] = set()
    for action in graph.get("actions", []) if isinstance(graph.get("actions"), list) else []:
        if isinstance(action, dict):
            tokens |= _token_strings(action.get("produces"))
    return tokens


def _sequence_rule(motif: dict[str, Any], context: dict[str, Any]) -> dict[str, Any] | None:
    graph = context.get("connectorActionGraph")
    if not isinstance(graph, dict):
        return None
    produced = _graph_produced_tokens(context)
    required = _token_strings(motif.get("requiresTokens"))
    if not required or not required.issubset(produced):
        return None
    actions = [a for a in graph.get("actions", []) if isinstance(a, dict)]
    goal_binding = motif.get("goalBinding") if isinstance(motif.get("goalBinding"), dict) else {}
    goal_token = _token_strings(goal_binding.get("token"))
    # Prefer an action that consumes the goal-binding token as the terminal action.
    goal_action = ""
    for action in actions:
        if goal_token & _token_strings(action.get("requires")):
            goal_action = _str(action.get("actionId") or action.get("id"))
            break
    if not goal_action and actions:
        goal_action = _str(actions[-1].get("actionId") or actions[-1].get("id"))
    if not goal_action:
        return None
    rule: dict[str, Any] = {
        "ruleId": f"motif.{_str(motif.get('motifId'))}",
        "invariantId": f"external.{_str(motif.get('motifId')).replace('-', '_')}",
        "expectedBehavior": {"status": motif.get("expectedBehavior", {}).get("status")},
        "requiresState": [{"token": t} for t in sorted(required) if t.startswith("state.")],
        "goal": {"action": goal_action},
        "maxDepth": 5,
        "title": f"{_str(motif.get('family'))}: {_str(motif.get('motifId'))}",
    }
    param = _str(goal_binding.get("param"))
    if param and goal_binding.get("token"):
        rule["goal"]["paramBindings"] = {param: goal_binding["token"]}
    return rule


def bind_motifs(source_context: dict[str, Any], motifs: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a copy of source_context augmented with motif-derived proposals."""
    if not isinstance(source_context, dict):
        return {}
    context = copy.deepcopy(source_context)
    param_motifs = sorted(
        (m for m in motifs if m.get("kind") == "param-mutation"),
        key=lambda m: _str(m.get("motifId")),
    )
    sequence_motifs = sorted(
        (m for m in motifs if m.get("kind") == "workflow-sequence"),
        key=lambda m: _str(m.get("motifId")),
    )

    derived_facts: list[dict[str, Any]] = []
    for fact in _source_facts(context):
        params = [p for p in fact.get("params", []) if isinstance(p, dict) and _str(p.get("name"))]
        for param in params:
            param_tokens = _param_tokens(param, fact)
            for motif in param_motifs:
                if _matches_param(motif, param, param_tokens):
                    derived_facts.append(_derived_fact(fact, param, motif))

    if derived_facts:
        existing = context.get("repositoryFacts")
        context["repositoryFacts"] = [*(existing if isinstance(existing, list) else []), *derived_facts]

    if sequence_motifs and isinstance(context.get("connectorActionGraph"), dict):
        graph = context["connectorActionGraph"]
        rules = graph.get("sequenceRules")
        rules = list(rules) if isinstance(rules, list) else []
        existing_rule_ids = {_str(r.get("ruleId")) for r in rules if isinstance(r, dict)}
        for motif in sequence_motifs:
            rule = _sequence_rule(motif, context)
            if rule and rule["ruleId"] not in existing_rule_ids:
                rules.append(rule)
        graph["sequenceRules"] = rules

    notes = context.get("agentNotes")
    note = f"Bound {len(derived_facts)} motif-derived probe rule(s) from the Bayesilisk motif library."
    context["agentNotes"] = [*(notes if isinstance(notes, list) else []), note]
    return context
