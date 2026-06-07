from __future__ import annotations

from typing import Any

from .constants import VERSION
from .probe_proposals import generate_probe_proposals
from .reporting import build_contextual_report, issue_payloads
from .utils import _safe_hash

DEFAULT_CREATED_AT = "1970-01-01T00:00:00Z"
FORBIDDEN_DRAFT_FIELDS = {
    "issueReadiness",
    "observedResult",
    "observedStatus",
    "passed",
    "riskScore",
    "verifiedByBayesilisk",
}
LOCAL_FIXTURE_SCOPES = {"dev", "local", "staging"}
PRODUCTION_MARKERS = ("customer-data", "live-customer", "prod.", "prod-", "production")


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text or default


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    return [_text(item) for item in _list(value) if _text(item)]


def _validation(
    *,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    errors = errors or []
    return {
        "accepted": not errors,
        "errors": errors,
        "warnings": warnings or [],
    }


def _bounded_int(value: Any, *, default: int, minimum: int = 1, maximum: int = 50) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _contains_production_marker(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(marker in lowered for marker in PRODUCTION_MARKERS)


def _is_production_url(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    return _contains_production_marker(value)


def _tool_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {"tool": VERSION, **payload}


def _hash_id(prefix: str, payload: Any, length: int = 12) -> str:
    return f"{prefix}.{_safe_hash(payload)[:length]}"


def connector_boundaries() -> list[str]:
    """Shared non-negotiable connector boundaries (CLI, MCP, prompt packet)."""
    return [
        "Do not modify Bayesilisk core for this app connector.",
        "Do not let an LLM write observedStatus.",
        "Do not let an LLM write passed.",
        "Do not open issues from connector output alone.",
        "Run connector actions only against local, dev, or staging fixtures.",
        "Use Bayesilisk issue payloads or verified reports before creating fix briefs.",
    ]


def source_context_template() -> dict[str, Any]:
    """A fresh starter source-context fact set with explicit proposal rules."""
    return {
        "agentNotes": [],
        "playwrightProbe": {"artifactCount": 0, "failedCount": 0, "passedCount": 0, "resultCount": 0, "target": None},
        "priorAdjustments": {},
        "repositoryFacts": [
            {
                "availableActions": ["connector-action-name"],
                "expectedBehavior": {"description": "source-backed expectation", "status": 404},
                "invariantId": "app.invariant_id",
                "params": [{"kind": "id", "location": "query", "name": "resourceId", "required": True}],
                "proposalRules": {"resourceId": [{"id": "unknown-id", "value": "missing-resourceId"}]},
                "routePattern": "/resource/{resourceId}",
                "source": "repository-scan",
                "title": "Source-backed connector expectation",
            }
        ],
        "source": "codex-bayesilisk-source-context",
    }


def observed_fact_template() -> dict[str, Any]:
    """A fresh observed-fact template; placeholders for connector-produced fields."""
    return {
        "actorRole": "local-test-actor",
        "artifactPaths": [],
        "expectedStatus": 404,
        "failureDetail": "<concrete failure detail from connector execution>",
        "invariantId": "app.invariant_id",
        "networkResponses": [],
        "observedStatus": "<must come from Playwright/API execution>",
        "passed": "<must be deterministic comparison after execution>",
        "route": "/resource/{resourceId}",
        "selector": "connector:connector-action-name",
        "source": "connector-observation",
        "targetUrl": "http://localhost:3000/resource/missing-resourceId",
        "timestamp": "<ISO-8601 execution timestamp>",
        "title": "Observed local connector result",
    }


def local_provenance(source_context: dict[str, Any], *, created_at: str | None = None) -> dict[str, Any]:
    """Build a minimal local-only provenance for terminal-driven verification.

    Lets a human run `connector verify` without the full agent provenance
    handshake while keeping the same production/credential guards.
    """
    source = _text(_dict(source_context).get("source"), "cli-connector")
    return establish_provenance(
        {
            "connectorNeed": {"source": source, "productionAccessAllowed": False},
            "createdAt": created_at or DEFAULT_CREATED_AT,
            "executionBoundary": {
                "allowedBaseUrls": ["http://localhost"],
                "credentialPolicy": "no-production-credentials",
                "target": "local fixtures",
            },
            "sourceClaims": [
                {"kind": "repo", "providedBy": "human", "value": source or "local connector source context"}
            ],
        }
    )


def connector_quickstart(arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Single self-describing entry point for agents building a connector.

    The agent-side equivalent of `bayesilisk connector init`: returns the ordered
    tool loop, the required source/observed fields, the boundaries, and
    copy-paste templates so a coding agent can drive the whole flow without
    re-reading the docs.
    """
    return _tool_payload(
        {
            "loop": [
                {"step": 1, "tool": "interview_connector_need", "purpose": "Normalize the request and ask bounded follow-ups."},
                {"step": 2, "tool": "establish_provenance", "purpose": "Record source claims and a local-only execution boundary."},
                {"step": 3, "tool": "connector_prompt_packet", "purpose": "Get a bounded spec for writing the connector in the app repo."},
                {"step": 4, "tool": "scenario_plan", "purpose": "Expand source context into a bounded probe plan."},
                {"step": 5, "tool": "verify_connector_outputs", "purpose": "Deterministically verify observed evidence; emit issue payloads."},
                {"step": 6, "tool": "fix_packet", "purpose": "Emit a repair brief from verified findings only."},
            ],
            "cliEquivalent": [
                "bayesilisk connector init --kind both --with-action-graph",
                "bayesilisk connector validate <source-context.json>",
                "bayesilisk connector propose <source-context.json>",
                "bayesilisk connector verify --source <s.json> --observed <o.json>",
            ],
            "boundaries": connector_boundaries(),
            "sourceContextTemplate": source_context_template(),
            "observedFactTemplate": observed_fact_template(),
            "requiredObservedFactFields": [
                "actorRole", "artifactPaths", "expectedStatus", "failureDetail", "invariantId",
                "networkResponses", "observedStatus", "passed", "route", "selector", "source",
                "targetUrl", "timestamp", "title",
            ],
        }
    )


def interview_connector_need(arguments: dict[str, Any]) -> dict[str, Any]:
    request_text = _text(arguments.get("requestText"))
    known_answers = _dict(arguments.get("knownAnswers"))
    max_questions = _bounded_int(arguments.get("maxQuestions"), default=5, maximum=8)
    errors: list[str] = []
    warnings: list[str] = []

    if not request_text:
        errors.append("requestText is required")
    if known_answers.get("productionAccessAllowed") is True:
        errors.append("productionAccessAllowed must be false")

    app_name = _text(known_answers.get("appName")) or None
    app_repo_path = _text(known_answers.get("appRepoPath")) or None
    target_area = _text(known_answers.get("targetArea")) or None
    test_framework = _text(known_answers.get("testFramework"), "unknown")
    fixture_scope = _text(known_answers.get("fixtureScope"), "unknown").lower()
    desired_output = _text(known_answers.get("desiredOutput")) or None
    risk_motifs = _strings(known_answers.get("riskMotifs"))

    if fixture_scope == "production":
        errors.append("fixtureScope must not be production")
    if fixture_scope not in LOCAL_FIXTURE_SCOPES and fixture_scope != "unknown":
        warnings.append(f"fixtureScope `{fixture_scope}` is not one of local, dev, or staging")

    question_specs = [
        (
            "app_name",
            app_name,
            "What application should the connector target?",
            "Connector packets need a stable app identity.",
        ),
        (
            "app_repo",
            app_repo_path,
            "Which local app or test repo path should Codex inspect?",
            "Connector code must live outside Bayesilisk core.",
        ),
        (
            "target_area",
            target_area,
            "Which workflow, route family, panel, or security boundary should this connector probe first?",
            "Bayesilisk needs a bounded connector scope.",
        ),
        (
            "fixture_scope",
            fixture_scope if fixture_scope in LOCAL_FIXTURE_SCOPES else None,
            "Will probes run only against local, dev, or staging fixtures?",
            "Bayesilisk must avoid production systems and customer data.",
        ),
        (
            "desired_output",
            desired_output,
            "Should Codex create source context, connector code, a scenario plan, verification output, or a fix brief?",
            "The prompt packet depends on the next artifact Codex should produce.",
        ),
        (
            "test_framework",
            None if test_framework == "unknown" else test_framework,
            "Does this repo already use Playwright, Cypress, API tests, or another harness?",
            "The connector should reuse existing local test fixtures where possible.",
        ),
        (
            "risk_motifs",
            risk_motifs,
            "Which risk motifs matter most, such as auth, tenant boundary, stale token, duplicate submit, or workflow order?",
            "Scenario plans should start from explicit invariants and observable probe points.",
        ),
    ]
    questions = [
        {"id": question_id, "question": question, "whyNeeded": why_needed}
        for question_id, known, question, why_needed in question_specs
        if not known
    ][:max_questions]

    required_ready_fields = [
        app_name,
        target_area,
        desired_output,
        fixture_scope if fixture_scope in LOCAL_FIXTURE_SCOPES else None,
    ]
    readiness = "needs-interview"
    if all(required_ready_fields):
        readiness = "ready-for-provenance"
    if all(required_ready_fields) and app_repo_path:
        readiness = "ready-for-prompt"

    connector_need = {
        "appName": app_name,
        "appRepoPath": app_repo_path,
        "desiredOutput": desired_output,
        "fixtureScope": None if fixture_scope == "unknown" else fixture_scope,
        "productionAccessAllowed": False,
        "readiness": readiness if not errors else "needs-interview",
        "requestText": request_text,
        "riskMotifs": risk_motifs,
        "targetArea": target_area,
        "testFramework": None if test_framework == "unknown" else test_framework,
    }
    return _tool_payload(
        {
            "connectorNeed": connector_need,
            "questions": questions,
            "validation": _validation(errors=errors, warnings=warnings),
        }
    )


def establish_provenance(arguments: dict[str, Any]) -> dict[str, Any]:
    connector_need = _dict(arguments.get("connectorNeed"))
    source_claims = [claim for claim in _list(arguments.get("sourceClaims")) if isinstance(claim, dict)]
    execution_boundary = _dict(arguments.get("executionBoundary"))
    errors: list[str] = []
    warnings: list[str] = []

    if not connector_need:
        errors.append("connectorNeed is required")
    if not source_claims:
        errors.append("at least one sourceClaim is required")
    if not execution_boundary:
        errors.append("executionBoundary is required")

    allowed_base_urls = _strings(execution_boundary.get("allowedBaseUrls"))
    credential_policy = _text(execution_boundary.get("credentialPolicy"), "unknown")
    target = _text(execution_boundary.get("target"), "unknown")
    if any(_is_production_url(url) for url in allowed_base_urls):
        errors.append("allowedBaseUrls must not include production URLs")
    if _contains_production_marker(target):
        errors.append("executionBoundary.target must not be production")
    if "production" in credential_policy.lower() and "no-production" not in credential_policy.lower():
        errors.append("credentialPolicy must prohibit production credentials")

    normalized_claims: list[dict[str, Any]] = []
    for claim in source_claims:
        normalized = {
            "hash": _text(claim.get("hash")) or None,
            "kind": _text(claim.get("kind"), "human-note"),
            "lineEnd": claim.get("lineEnd") if _is_int(claim.get("lineEnd")) else None,
            "lineStart": claim.get("lineStart") if _is_int(claim.get("lineStart")) else None,
            "path": _text(claim.get("path")) or None,
            "providedBy": _text(claim.get("providedBy"), "human"),
            "value": _text(claim.get("value")),
        }
        if not normalized["value"]:
            errors.append("sourceClaim.value is required")
        if normalized["providedBy"] == "codex" and not any(
            normalized.get(key) for key in ("hash", "path")
        ) and normalized["kind"] not in {"repo", "route", "test"}:
            warnings.append("Codex-only source claim has no file, test, route, repo, or hash anchor")
        normalized_claims.append(normalized)

    normalized_claims.sort(key=lambda item: (item["kind"], item["path"] or "", item["value"]))
    normalized_boundary = {
        "allowedBaseUrls": allowed_base_urls,
        "credentialPolicy": credential_policy,
        "disallowedBaseUrls": _strings(execution_boundary.get("disallowedBaseUrls")),
        "target": target,
    }
    connector_need_hash = _safe_hash(connector_need)[:16]
    provenance_seed = {
        "connectorNeedHash": connector_need_hash,
        "executionBoundary": normalized_boundary,
        "sourceClaims": normalized_claims,
    }
    provenance = {
        "connectorNeedHash": connector_need_hash,
        "createdAt": _text(arguments.get("createdAt"), DEFAULT_CREATED_AT),
        "createdBy": "establish_provenance",
        "executionBoundary": normalized_boundary,
        "provenanceId": _hash_id("prov", provenance_seed, 16),
        "sourceClaims": normalized_claims,
    }
    return _tool_payload({"provenance": provenance, "validation": _validation(errors=errors, warnings=warnings)})


def connector_prompt_packet(arguments: dict[str, Any]) -> dict[str, Any]:
    connector_need = _dict(arguments.get("connectorNeed"))
    provenance = _dict(arguments.get("provenance"))
    style = _text(arguments.get("style"), "starter-kit")
    target_language = _text(arguments.get("targetLanguage"), "unknown")
    include_examples = bool(arguments.get("includeExamples", True))
    errors: list[str] = []

    provenance_id = _text(provenance.get("provenanceId"))
    if not connector_need:
        errors.append("connectorNeed is required")
    if not provenance_id:
        errors.append("accepted provenance with provenanceId is required")

    boundaries = connector_boundaries()
    codex_task = (
        "Create an app-specific Bayesilisk connector in the target app or test repo. "
        "Read local tests, routes, schemas, and fixture helpers; write source context with explicit "
        "expected statuses, proposalRules/proposalGates or connectorActionGraph sequenceRules, and a "
        "connector action mapping. Do not edit Bayesilisk core. Execute observed facts only through "
        "real local fixture, browser, or API actions."
    )
    source_context_template_value = source_context_template()
    observed_fact_template_value = observed_fact_template()
    packet_seed = {
        "connectorNeed": connector_need,
        "includeExamples": include_examples,
        "provenanceId": provenance_id,
        "style": style,
        "targetLanguage": target_language,
    }
    prompt_packet = {
        "codexTask": codex_task,
        "includeExamples": include_examples,
        "observedFactTemplate": observed_fact_template_value,
        "packetId": _hash_id("connector-prompt", packet_seed, 16),
        "provenanceId": provenance_id,
        "requiredOutputs": [
            "source context JSON",
            "connector action mapping",
            "local fixture execution instructions",
            "observed context JSON contract",
        ],
        "sourceContextTemplate": source_context_template_value,
        "style": style,
        "systemBoundaries": boundaries,
        "targetLanguage": target_language,
    }
    return _tool_payload({"promptPacket": prompt_packet, "validation": _validation(errors=errors)})


def _forbidden_field_paths(value: Any, *, path: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key in FORBIDDEN_DRAFT_FIELDS:
                paths.append(next_path)
            paths.extend(_forbidden_field_paths(item, path=next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            paths.extend(_forbidden_field_paths(item, path=f"{path}[{index}]"))
    return paths


def _declared_connector_actions(source_context: dict[str, Any]) -> set[str]:
    actions: set[str] = set()
    for fact in _list(source_context.get("repositoryFacts")):
        if not isinstance(fact, dict):
            continue
        for action in _strings(fact.get("availableActions")):
            actions.add(action)
    graph = _dict(source_context.get("connectorActionGraph"))
    for action in _list(graph.get("actions")):
        if isinstance(action, dict) and _text(action.get("actionId")):
            actions.add(_text(action.get("actionId")))
    return actions


def _proposal_actions(proposal: dict[str, Any]) -> set[str]:
    actions: set[str] = set()
    action = _text(proposal.get("connectorAction"))
    if action:
        actions.add(action)
    for step in _list(proposal.get("sequenceSteps")):
        if isinstance(step, dict) and _text(step.get("connectorAction")):
            actions.add(_text(step.get("connectorAction")))
    return actions


def scenario_plan(arguments: dict[str, Any]) -> dict[str, Any]:
    source_context = _dict(arguments.get("sourceContext"))
    provenance = _dict(arguments.get("provenance"))
    draft_plan = _dict(arguments.get("draftPlan"))
    limit = _bounded_int(arguments.get("limit"), default=24, maximum=100)
    errors: list[str] = []
    warnings: list[str] = []
    rejected_scenarios: list[dict[str, Any]] = []

    provenance_id = _text(provenance.get("provenanceId"))
    if not provenance_id:
        errors.append("accepted provenance with provenanceId is required")
    if not source_context:
        errors.append("sourceContext is required")

    forbidden_paths = _forbidden_field_paths(draft_plan)
    if forbidden_paths:
        errors.append("draftPlan contains verifier-only fields: " + ", ".join(forbidden_paths))

    generated = generate_probe_proposals(source_context, limit=limit) if source_context else []
    declared_actions = _declared_connector_actions(source_context)
    for scenario in _list(draft_plan.get("scenarios")):
        if not isinstance(scenario, dict):
            continue
        action = _text(scenario.get("connectorAction"))
        title = _text(scenario.get("title"), "draft scenario")
        if action and action not in declared_actions:
            rejected_scenarios.append({"reason": f"unknown connectorAction `{action}`", "title": title})
        if not _is_int(scenario.get("expectedStatus")):
            rejected_scenarios.append({"reason": "missing integer expectedStatus", "title": title})

    if not generated and not errors:
        warnings.append("sourceContext produced no proposals; add proposalRules, proposalGates, or connectorActionGraph.sequenceRules")

    plan_seed = {"generated": generated, "provenanceId": provenance_id, "source": source_context.get("source")}
    accepted_scenarios = generated if not errors else []
    scenario_plan_payload = {
        "acceptedScenarios": accepted_scenarios,
        "executionInstructions": [
            "Connector executes connectorAction against local fixtures and writes observed facts.",
            "Observed facts must be produced by Playwright/API execution, not by Codex prose.",
            "Call verify_connector_outputs after connector execution.",
        ],
        "generatedProposals": generated,
        "planId": _hash_id("scenario-plan", plan_seed, 16),
        "provenanceId": provenance_id or None,
        "rejectedScenarios": rejected_scenarios,
    }
    return _tool_payload(
        {
            "scenarioPlan": scenario_plan_payload,
            "validation": _validation(errors=errors, warnings=warnings),
        }
    )


def _expected_status_present(fact: dict[str, Any]) -> bool:
    behavior = _dict(fact.get("expectedBehavior"))
    return _is_int(behavior.get("status")) or _is_int(fact.get("expectedStatus"))


def validate_source_context(source_context: dict[str, Any]) -> dict[str, Any]:
    """Lint a connector source context before proposal generation.

    Reuses the same proposal expansion (`generate_probe_proposals`), forbidden
    verifier-only field detection, and production-marker guards used elsewhere so
    a terminal author gets the diagnostics that were previously MCP-only. The key
    fix over `--probe-proposals-output` is a loud warning when zero proposals
    would be generated instead of a silent empty list.
    """
    errors: list[str] = []
    warnings: list[str] = []
    source_context = _dict(source_context)
    facts = [fact for fact in _list(source_context.get("repositoryFacts")) if isinstance(fact, dict)]
    if not source_context:
        errors.append("source context is empty or not an object")
    elif not facts and not _dict(source_context.get("connectorActionGraph")):
        errors.append("source context has no repositoryFacts and no connectorActionGraph")

    forbidden_paths = _forbidden_field_paths(source_context)
    if forbidden_paths:
        errors.append("source context contains verifier-only fields: " + ", ".join(forbidden_paths))

    declared_actions = _declared_connector_actions(source_context)
    for index, fact in enumerate(facts):
        prefix = f"repositoryFacts[{index}]"
        route_pattern = fact.get("routePattern")
        has_route = isinstance(route_pattern, str) and route_pattern.strip()
        has_observed = _is_int(fact.get("expectedStatus")) and _is_int(fact.get("observedStatus"))
        if _is_production_url(route_pattern) or _is_production_url(fact.get("targetUrl")):
            errors.append(f"{prefix} references a production URL")
        if has_observed:
            continue  # observed-evidence fact, not a source fact; verified elsewhere
        if not has_route:
            warnings.append(f"{prefix} has no routePattern; it will not produce route proposals")
            continue
        if not _expected_status_present(fact):
            warnings.append(f"{prefix} has no expectedBehavior.status or expectedStatus; no proposals will be generated")
        has_rules = isinstance(fact.get("proposalRules"), dict) and fact["proposalRules"]
        has_gate = isinstance(source_context.get("proposalGates"), list) and source_context["proposalGates"]
        if not has_rules and not has_gate:
            warnings.append(
                f"{prefix} has no proposalRules and no proposalGates; "
                "add proposalRules, proposalGates, or a connectorActionGraph sequence rule"
            )

    proposals = generate_probe_proposals(source_context) if facts or _dict(source_context.get("connectorActionGraph")) else []
    if not proposals and not errors:
        warnings.append(
            "no probe proposals would be generated; add proposalRules, proposalGates, "
            "or connectorActionGraph.sequenceRules so Bayesilisk has something to expand"
        )
    return {
        "accepted": not errors,
        "errors": errors,
        "warnings": warnings,
        "declaredActions": sorted(declared_actions),
        "proposalCount": len(proposals),
        "factCount": len(facts),
    }


def _observed_facts(observed_context: dict[str, Any]) -> list[dict[str, Any]]:
    return [fact for fact in _list(observed_context.get("repositoryFacts")) if isinstance(fact, dict)]


def _scenario_plan_actions(plan: dict[str, Any]) -> set[str]:
    payload = _dict(plan.get("scenarioPlan")) or plan
    actions: set[str] = set()
    for key in ("acceptedScenarios", "generatedProposals"):
        for proposal in _list(payload.get(key)):
            if isinstance(proposal, dict):
                actions.update(_proposal_actions(proposal))
    return actions


def _merge_contexts(source_context: dict[str, Any], observed_context: dict[str, Any]) -> dict[str, Any]:
    merged = {**source_context, **observed_context}
    merged["source"] = _text(observed_context.get("source"), _text(source_context.get("source"), "connector-verification"))
    merged["agentNotes"] = [
        *_strings(source_context.get("agentNotes")),
        *_strings(observed_context.get("agentNotes")),
    ] or ["Connector output verified by Bayesilisk MCP."]
    merged["priorAdjustments"] = {
        **_dict(source_context.get("priorAdjustments")),
        **_dict(observed_context.get("priorAdjustments")),
    }
    merged["repositoryFacts"] = [
        *[fact for fact in _list(source_context.get("repositoryFacts")) if isinstance(fact, dict)],
        *_observed_facts(observed_context),
    ]
    if "playwrightProbe" not in merged:
        result_count = len(_observed_facts(observed_context))
        failed_count = sum(1 for fact in _observed_facts(observed_context) if fact.get("passed") is False)
        merged["playwrightProbe"] = {
            "artifactCount": 0,
            "failedCount": failed_count,
            "passedCount": max(result_count - failed_count, 0),
            "resultCount": result_count,
            "target": "local connector fixtures",
        }
    return merged


def _validate_observed_context(
    observed_context: dict[str, Any],
    *,
    scenario_plan_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    forbidden_author_fields_found: list[str] = []
    facts = _observed_facts(observed_context)
    required = [
        "actorRole",
        "artifactPaths",
        "expectedStatus",
        "failureDetail",
        "invariantId",
        "networkResponses",
        "observedStatus",
        "passed",
        "route",
        "selector",
        "source",
        "targetUrl",
        "timestamp",
        "title",
    ]
    if not facts:
        errors.append("observedContext.repositoryFacts must contain at least one observed fact")
    allowed_actions = _scenario_plan_actions(scenario_plan_payload or {})
    forbidden_observed_fields = FORBIDDEN_DRAFT_FIELDS - {"observedStatus", "passed"}
    for index, fact in enumerate(facts):
        prefix = f"observedContext.repositoryFacts[{index}]"
        for field in sorted(forbidden_observed_fields):
            if field in fact:
                errors.append(f"{prefix}.{field} is verifier-only and must not appear in observed facts")
                forbidden_author_fields_found.append(f"{prefix}.{field}")
        for key in required:
            if key not in fact:
                errors.append(f"{prefix}.{key} is required")
        expected = fact.get("expectedStatus")
        observed = fact.get("observedStatus")
        passed = fact.get("passed")
        if not _is_int(expected):
            errors.append(f"{prefix}.expectedStatus must be an integer")
        if not _is_int(observed):
            errors.append(f"{prefix}.observedStatus must be an integer")
        if not isinstance(passed, bool):
            errors.append(f"{prefix}.passed must be a boolean")
        if _is_int(expected) and _is_int(observed) and isinstance(passed, bool) and passed != (observed == expected):
            errors.append(f"{prefix}.passed must equal observedStatus == expectedStatus")
        target_url = _text(fact.get("targetUrl"))
        if _is_production_url(target_url):
            errors.append(f"{prefix}.targetUrl must not point at production")
        selector = _text(fact.get("selector"))
        if allowed_actions and selector.startswith("connector:"):
            selector_action = selector.split(":", 1)[1]
            if selector_action not in allowed_actions:
                errors.append(f"{prefix}.selector action `{selector_action}` is not in scenarioPlan")
        if fact.get("source") in {"codex", "model", "llm"}:
            errors.append(f"{prefix}.source must be a connector execution source, not `{fact.get('source')}`")
    return {
        "accepted": not errors,
        "errors": errors,
        "forbiddenAuthorFieldsFound": forbidden_author_fields_found,
        "observedFactCount": len(facts),
        "warnings": warnings,
    }


def validate_observed_context(
    observed_context: dict[str, Any],
    *,
    scenario_plan_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Public wrapper around observed-context validation for the CLI/agents."""
    return _validate_observed_context(observed_context, scenario_plan_payload=scenario_plan_payload)


def verify_connector_outputs(arguments: dict[str, Any]) -> dict[str, Any]:
    source_context = _dict(arguments.get("sourceContext"))
    observed_context = _dict(arguments.get("observedContext"))
    provenance = _dict(arguments.get("provenance"))
    plan = _dict(arguments.get("scenarioPlan"))
    seed = _bounded_int(arguments.get("seed"), default=150, maximum=10_000_000)
    limit_arg = arguments.get("limit", 10)
    limit = None if limit_arg is None else _bounded_int(limit_arg, default=10, maximum=100)
    include_issue_payloads = bool(arguments.get("includeIssuePayloads", True))
    validation = _validate_observed_context(observed_context, scenario_plan_payload=plan)
    if not _text(provenance.get("provenanceId")):
        validation["accepted"] = False
        validation["errors"].append("accepted provenance with provenanceId is required")
    if not observed_context:
        validation["accepted"] = False
        validation["errors"].append("observedContext is required")

    ledgers = {
        "observedByPlaywright": _observed_facts(observed_context),
        "proposedByModel": [],
        "selectedByGrassmannAttention": [],
        "verifiedByBayesilisk": [],
    }
    if not validation["accepted"]:
        return _tool_payload(
            {
                "issuePayloads": [],
                "ledgers": ledgers,
                "observationValidation": validation,
                "report": None,
            }
        )

    context = _merge_contexts(source_context, observed_context)
    report = build_contextual_report(seed, limit=limit, context=context)
    payloads = issue_payloads(report, context=context, limit=limit) if include_issue_payloads else []
    ledgers = {
        "observedByPlaywright": _observed_facts(observed_context),
        "proposedByModel": report.get("proposedByModel", []),
        "selectedByGrassmannAttention": report.get("selectedByGrassmannAttention", []),
        "verifiedByBayesilisk": report.get("verifiedByBayesilisk", []),
    }
    return _tool_payload(
        {
            "issuePayloads": payloads,
            "ledgers": ledgers,
            "observationValidation": validation,
            "report": report,
        }
    )


def fix_packet(arguments: dict[str, Any]) -> dict[str, Any]:
    verified_report = _dict(arguments.get("verifiedReport"))
    if "report" in verified_report and isinstance(verified_report["report"], dict):
        verified_report = verified_report["report"]
    supplied_payloads = [item for item in _list(arguments.get("issuePayloads")) if isinstance(item, dict)]
    provenance = _dict(arguments.get("provenance"))
    max_findings = _bounded_int(arguments.get("maxFindings"), default=3, maximum=10)
    brief_style = _text(arguments.get("briefStyle"), "concise")
    errors: list[str] = []

    provenance_id = _text(provenance.get("provenanceId"))
    if not provenance_id:
        errors.append("accepted provenance with provenanceId is required")
    if not verified_report:
        errors.append("verifiedReport is required")

    payload_by_fingerprint = {
        _text(payload.get("fingerprint")): payload
        for payload in supplied_payloads
        if _text(payload.get("fingerprint"))
    }
    ready_findings = [
        finding
        for finding in _list(verified_report.get("findings"))
        if isinstance(finding, dict)
        and finding.get("observedResult") == "fail"
        and finding.get("issueReadiness") == "ready-for-issue"
    ]
    if not ready_findings and supplied_payloads:
        ready_findings = [
            {
                "accessPattern": {},
                "dedupeKey": payload.get("dedupeKey"),
                "fingerprint": payload.get("fingerprint"),
                "invariantId": payload.get("invariantId"),
                "observation": payload.get("body"),
                "scenarioId": payload.get("scenarioId"),
                "suggestedIssueTitle": payload.get("title"),
            }
            for payload in supplied_payloads
        ]
    findings = []
    for finding in ready_findings[:max_findings]:
        fingerprint = _text(finding.get("fingerprint"))
        issue_payload = payload_by_fingerprint.get(fingerprint, {})
        invariant_id = _text(finding.get("invariantId"))
        title = _text(issue_payload.get("title") or finding.get("suggestedIssueTitle"), "Bayesilisk verified finding")
        observed_evidence = {
            "accessPattern": finding.get("accessPattern", {}),
            "classification": finding.get("classification"),
            "fingerprint": fingerprint,
            "observation": finding.get("observation"),
            "originalScenario": finding.get("originalScenario"),
            "scenarioId": finding.get("scenarioId"),
        }
        fix_brief = (
            f"Patch the target app so verified invariant `{invariant_id}` holds for fingerprint `{fingerprint}`. "
            "Rerun the connector and Bayesilisk; treat the fix as credible only after verified evidence changes."
        )
        if brief_style == "detailed" and issue_payload.get("body"):
            fix_brief = f"{fix_brief}\n\nVerified issue payload:\n{issue_payload['body']}"
        findings.append(
            {
                "artifactPaths": [],
                "codexGuardrails": [
                    "Patch only app code/tests.",
                    "Do not edit Bayesilisk core for this app finding.",
                    "Do not cite unverified connector output as issue-ready.",
                    "Rerun the connector and Bayesilisk after the patch.",
                ],
                "dedupeKey": finding.get("dedupeKey") or issue_payload.get("dedupeKey"),
                "fingerprint": fingerprint,
                "fixBrief": fix_brief,
                "issueTitle": title,
                "observedEvidence": observed_evidence,
                "verifiedInvariantId": invariant_id,
            }
        )
    if not findings and not errors:
        errors.append("verifiedReport contains no ready-for-issue findings")
    packet_seed = {"findings": findings, "provenanceId": provenance_id}
    return _tool_payload(
        {
            "fixPacket": {
                "findings": [] if errors else findings,
                "packetId": _hash_id("fix-packet", packet_seed, 16),
                "provenanceId": provenance_id or None,
                "source": "verifiedByBayesilisk",
            },
            "validation": _validation(errors=errors),
        }
    )
