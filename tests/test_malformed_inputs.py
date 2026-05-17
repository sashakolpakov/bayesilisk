from __future__ import annotations

import importlib


def test_malformed_context_and_observations_do_not_crash_report_building() -> None:
    context_module = importlib.import_module("bayesilisk.context")
    reporting = importlib.import_module("bayesilisk.reporting")

    for malformed_context in (None, "agent note text", ["not", "an", "object"], 42):
        summary = context_module.context_summary(malformed_context)
        report = reporting.build_contextual_report(
            150,
            limit=2,
            generated_count=0,
            observations=["bad-observation-shape"],
            context=malformed_context,
        )

        assert summary["source"] == "none"
        assert report["contextSummary"]["source"] == "none"
        assert len(report["findings"]) == 2
        assert report["rankedProbes"]


def test_malformed_context_objects_ignore_unknown_ids_and_invalid_status_values() -> None:
    attention_module = importlib.import_module("bayesilisk.attention")
    context_module = importlib.import_module("bayesilisk.context")
    context = {
        "source": 123,
        "agentNotes": "support takeover route 403",
        "issues": {"one": {"body": "tracked bayesilisk:0123456789abcdef"}},
        "repositoryFacts": [
            None,
            "bad-fact",
            {
                "actorRole": ["support"],
                "expectedStatus": "not-a-status",
                "invariantId": "hr.documents_customer_role_boundary",
                "observedStatus": {"status": 200},
                "passed": "false",
                "route": 123,
                "source": "microsoft-playwright",
            },
            {
                "expectedStatus": 403,
                "invariantId": "unknown.invariant",
                "observedStatus": 200,
                "source": "microsoft-playwright",
            },
        ],
        "priorAdjustments": {
            "hr.documents_customer_role_boundary": "high",
            "travel.funding_before_expense": 0.25,
        },
        "mutedInvariantIds": ["unknown.invariant", "hr.documents_customer_role_boundary", 17],
    }

    observations = context_module.context_observations(context)
    attention = attention_module.grassmann_attention(context)
    invalid_status_plane = next(
        plane for plane in attention["planes"] if plane["invariantId"] == "hr.documents_customer_role_boundary"
    )
    unknown_plane = [plane for plane in attention["planes"] if plane["invariantId"] == "unknown.invariant"]

    assert observations["priorAdjustments"]["travel.funding_before_expense"] == 0.25
    assert "hr.documents_customer_role_boundary" not in observations["priorAdjustments"]
    assert invalid_status_plane["testedCount"] == 0
    assert invalid_status_plane["decayForFixedOrMuted"] == 0.2
    assert unknown_plane == []


def test_malformed_playwright_probe_results_are_normalized_and_bounded() -> None:
    adapter = importlib.import_module("bayesilisk.playwright_adapter")
    reporting = importlib.import_module("bayesilisk.reporting")
    context = adapter.build_context_from_probe_results(
        [
            None,
            "not-a-result",
            {
                "actorRole": {"role": "support"},
                "expectedStatus": True,
                "invariantId": "unknown.invariant",
                "observedStatus": "200",
                "route": 123,
                "title": ["bad-title"],
            },
            {
                "actorRole": "support",
                "expectedStatus": "403",
                "invariantId": "hr.documents_customer_role_boundary",
                "observedStatus": "200",
                "route": "/api/hr/documents",
                "title": "Support reaches HR documents",
            },
            {
                "actorRole": "admin",
                "expectedStatus": "200",
                "invariantId": "hr.documents_customer_role_boundary",
                "observedStatus": 200,
                "route": "/api/hr/documents",
                "title": "Admin reaches HR documents",
            },
        ],
        target=123,
    )

    assert context["playwrightProbe"]["resultCount"] == 5
    assert context["playwrightProbe"]["failedCount"] == 4
    assert context["playwrightProbe"]["passedCount"] == 1
    assert context["priorAdjustments"] == {"hr.documents_customer_role_boundary": 0.06}
    assert context["repositoryFacts"][0]["invariantId"] == "unknown"
    assert context["repositoryFacts"][2]["expectedStatus"] is None
    assert context["repositoryFacts"][2]["route"] == "123"

    report = reporting.build_contextual_report(150, limit=3, generated_count=0, context=context)
    assert report["contextSummary"]["source"] == "playwright-probe"
    assert report["observedByPlaywright"]


def test_model_proposal_validation_rejects_mutations_and_accepts_one_valid_candidate() -> None:
    model_proposals = importlib.import_module("bayesilisk.model_proposals")
    valid = {
        "title": "Valid support HR document proposal",
        "targetPlane": "hr.documents_customer_role_boundary",
        "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
        "invariants": ["support.takeover_session_required", "hr.documents_customer_role_boundary"],
    }
    proposals = [
        None,
        {"targetPlane": "hr.documents_customer_role_boundary", "fragments": valid["fragments"], "invariants": valid["invariants"]},
        {"title": 404, "targetPlane": "hr.documents_customer_role_boundary", "fragments": valid["fragments"], "invariants": valid["invariants"]},
        {"title": "Unknown target", "targetPlane": "invented.plane", "fragments": valid["fragments"], "invariants": valid["invariants"]},
        {"title": "Unknown fragment", "targetPlane": "hr.documents_customer_role_boundary", "fragments": ["role.support_takeover_active", "route.invented"], "invariants": ["hr.documents_customer_role_boundary"]},
        {"title": "Unknown invariant", "targetPlane": "hr.documents_customer_role_boundary", "fragments": valid["fragments"], "invariants": ["invented.invariant"]},
        {"title": "Non-string fragment", "targetPlane": "hr.documents_customer_role_boundary", "fragments": ["role.support_takeover_active", 7], "invariants": ["hr.documents_customer_role_boundary"]},
        {"title": "Too many fragments", "targetPlane": "hr.documents_customer_role_boundary", "fragments": ["role.support_takeover_active"] * 13, "invariants": ["hr.documents_customer_role_boundary"]},
        {"title": "Too many invariants", "targetPlane": "hr.documents_customer_role_boundary", "fragments": valid["fragments"], "invariants": ["hr.documents_customer_role_boundary"] * 7},
        {"title": "Target not included", "targetPlane": "hr.documents_customer_role_boundary", "fragments": valid["fragments"], "invariants": ["support.takeover_session_required"]},
        valid,
        dict(valid),
    ]

    scenarios, rejected = model_proposals.validate_model_scenario_proposals(
        proposals,
        {"selectedPlaneIds": ["unknown.plane", 17]},
        provider={"provider": "unit-test"},
    )
    reasons = [item["reason"] for item in rejected]

    assert len(scenarios) == 1
    assert scenarios[0].generation_basis == "weak-model-proposal:hr.documents_customer_role_boundary"
    assert "invalid-proposal-object" in reasons
    assert "missing-title" in reasons
    assert "unknown-target-plane" in reasons
    assert "unknown-fragment-id" in reasons
    assert "unknown-invariant-id" in reasons
    assert "invalid-fragment-count" in reasons
    assert "invalid-invariant-count" in reasons
    assert "target-plane-not-in-invariants" in reasons
    assert "duplicate-proposal" in reasons
