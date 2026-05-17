from __future__ import annotations

import importlib
import io
import json
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs" / "bayesilisk.md"
DESIGN = REPO_ROOT / "DESIGN.md"
README = REPO_ROOT / "README.md"
REPORTS_DOC = REPO_ROOT / "docs" / "reports.md"
PYPROJECT = REPO_ROOT / "pyproject.toml"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def run_bayesilisk(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "bayesilisk", *args],
        check=True,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def test_bayesilisk_json_report_is_seeded_and_reproducible() -> None:
    first = run_bayesilisk("--seed", "150", "--format", "json")
    second = run_bayesilisk("--seed", "150", "--format", "json")

    assert first.stdout == second.stdout
    report = json.loads(first.stdout)

    assert report["tool"] == "bayesilisk.v1.2"
    assert report["seed"] == 150
    assert report["deterministic"] is True
    assert report["productionAccess"] is False
    assert report["generatedScenarioCount"] == 8
    assert "harder-to-find-after-easy-breakages" in report["prioritizationPolicy"]
    assert {"confirmedBreakages", "candidateProbes", "hardToFindModes", "controls"} <= set(report["sections"])
    assert set(report["domains"]) == {
        "Travel",
        "Expenses",
        "Billing",
        "HR",
        "Support",
        "DMS",
        "module entitlements",
    }

    invariant_ids = {invariant["id"] for invariant in report["invariants"]}
    assert {
        "roles.route_matrix_allowed",
        "roles.employee_self_review_forbidden",
        "modules.expense_approval_requires_module_and_receipt",
        "dms.tenant_process_boundary",
        "support.takeover_session_required",
        "billing.export_requires_role_and_module",
        "hr.documents_customer_role_boundary",
        "travel.itinerary_chronology",
        "travel.funding_before_expense",
        "travel.expense_items_match_itinerary",
    } <= invariant_ids
    assert "finance" in report["roleRouteMatrix"]["/api/expense-claims/{claimId}/review"]

    findings = report["findings"]
    assert findings == sorted(findings, key=lambda item: (-item["riskScore"], item["posteriorMode"], item["id"]))
    assert {"pass", "fail"} <= {finding["observedResult"] for finding in findings}
    assert {"mundane", "creative", "intentionally-inconsistent", "round-up"} <= {
        finding["scenarioTone"] for finding in findings
    }
    assert {
        "mundane.travel_funding_to_multimodal_expense",
        "mundane.hr_document_by_hr_manager",
        "mundane.manager_reviews_employee_expense",
        "roundup.billing_export_disabled_module",
        "creative.support_active_hr_document_shortcut",
        "inconsistent.dms_wrong_process_receipt",
        "roundup.travel_expense_before_late_funding",
        "inconsistent.travel_missing_airplane_leg",
        "roundup.travel_funding_unapproved_multimodal_expense",
        "inconsistent.travel_air_train_leg_mismatch",
    } <= {finding["scenarioId"] for finding in findings}
    assert any(finding["generatedScenario"] for finding in findings)
    assert any(finding["scenarioTone"].startswith("generated") for finding in findings)
    assert {"breakage.easy", "breakage.hard-to-find", "control-confirmed"} <= {
        finding["classification"] for finding in findings
    }
    assert {
        "harder-to-find-after-easy-breakages",
        "highest-fault-probability",
        "posterior-control-confidence",
    } <= {finding["posteriorMode"] for finding in findings}

    for finding in findings:
        assert finding["fingerprint"].startswith("bayesilisk:")
        assert finding["dedupeKey"].startswith(finding["fingerprint"])
        assert finding["issueReadiness"] in {
            "do-not-open-muted",
            "no-issue-control",
            "probe-only",
            "ready-for-issue",
            "regression-watch",
        }
        assert finding["observationBasis"]["tags"]
        assert 0 < finding["riskScore"] < 1
        assert finding["posteriorProbability"] == finding["riskScore"]
        assert finding["classification"]
        assert finding["posteriorMode"]
        assert finding["fragments"]
        assert finding["subScenarios"]
        assert any(entry["completeAlone"] is False for entry in finding["subScenarios"])
        assert "actorRole" in finding["accessPattern"]
        assert "routes" in finding["accessPattern"]
        assert finding["expectedInvariant"]
        assert finding["suggestedIssueTitle"].startswith("Bayesilisk ")
        assert "Reproduce with `python3 -m bayesilisk --seed <seed> --format json`" in finding[
            "suggestedIssueBody"
        ]


def test_expanded_catalog_catches_distinct_bad_spots() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    report = bayesilisk.build_report(150, generated_count=0)
    findings = report["findings"]

    wrong_process = next(
        finding
        for finding in findings
        if finding["scenarioId"] == "inconsistent.dms_wrong_process_receipt"
        and finding["invariantId"] == "dms.tenant_process_boundary"
    )
    assert wrong_process["observedResult"] == "fail"
    assert "does not match" in wrong_process["observation"]

    active_support_takeover = next(
        finding
        for finding in findings
        if finding["scenarioId"] == "creative.support_active_hr_document_shortcut"
        and finding["invariantId"] == "support.takeover_session_required"
    )
    active_support_hr = next(
        finding
        for finding in findings
        if finding["scenarioId"] == "creative.support_active_hr_document_shortcut"
        and finding["invariantId"] == "hr.documents_customer_role_boundary"
    )
    assert active_support_takeover["observedResult"] == "pass"
    assert active_support_hr["observedResult"] == "fail"

    late_funding = next(
        finding
        for finding in findings
        if finding["scenarioId"] == "roundup.travel_expense_before_late_funding"
        and finding["invariantId"] == "travel.funding_before_expense"
    )
    assert late_funding["observedResult"] == "fail"
    assert "before funding approval" in late_funding["observation"]

    missing_airplane_leg = next(
        finding
        for finding in findings
        if finding["scenarioId"] == "inconsistent.travel_missing_airplane_leg"
        and finding["invariantId"] == "travel.expense_items_match_itinerary"
    )
    assert missing_airplane_leg["observedResult"] == "fail"
    assert "transport modes are not covered" in missing_airplane_leg["observation"]


def test_focused_modules_expose_expected_boundaries() -> None:
    attention = importlib.import_module("bayesilisk.attention")
    catalog = importlib.import_module("bayesilisk.catalog")
    cli = importlib.import_module("bayesilisk.cli")
    config = importlib.import_module("bayesilisk.config")
    context = importlib.import_module("bayesilisk.context")
    invariants = importlib.import_module("bayesilisk.invariants")
    model_proposals = importlib.import_module("bayesilisk.model_proposals")
    reporting = importlib.import_module("bayesilisk.reporting")

    assert catalog.FRAGMENTS
    assert catalog.SCENARIOS
    assert invariants.route_matrix_allowed
    assert attention.grassmann_attention
    assert model_proposals.validate_model_scenario_proposals
    assert reporting.build_contextual_report
    assert config.effective_runtime_config()["scenarioProvider"]
    assert context.context_summary({"agentNotes": ["expense route"]})["textSignalCount"] == 1
    assert cli.main

    engine_path = REPO_ROOT / "bayesilisk" / "engine.py"
    assert len(engine_path.read_text(encoding="utf-8").splitlines()) <= 40
    for module_path in (REPO_ROOT / "bayesilisk").glob("*.py"):
        if module_path.name in {"engine.py", "__init__.py"}:
            continue
        assert "from .engine import" not in module_path.read_text(encoding="utf-8")


def test_scenario_catalog_has_valid_references_and_invariant_coverage() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    fragment_ids = {fragment.id for fragment in bayesilisk.FRAGMENTS}
    invariant_ids = {invariant.id for invariant in bayesilisk.INVARIANTS}

    for scenario in bayesilisk.SCENARIOS:
        assert scenario.fragment_ids
        assert scenario.invariant_ids
        assert set(scenario.fragment_ids) <= fragment_ids
        assert set(scenario.invariant_ids) <= invariant_ids

    report = bayesilisk.build_report(150, generated_count=0)
    scenario_ids = {finding["scenarioId"] for finding in report["findings"]}
    assert {scenario.id for scenario in bayesilisk.SCENARIOS} <= scenario_ids

    invariant_results: dict[str, set[str]] = {}
    for finding in report["findings"]:
        invariant_results.setdefault(finding["invariantId"], set()).add(finding["observedResult"])

    for invariant_id in invariant_ids:
        assert invariant_results[invariant_id] == {"fail", "pass"}


def test_bayesilisk_markdown_and_output_files_include_issue_ready_findings(tmp_path: Path) -> None:
    json_path = tmp_path / "bayesilisk.json"
    markdown_path = tmp_path / "bayesilisk.md"

    json_run = run_bayesilisk("--seed", "150", "--format", "json", "--limit", "2", "--output", str(json_path))
    markdown_run = run_bayesilisk(
        "--seed",
        "150",
        "--format",
        "markdown",
        "--limit",
        "2",
        "--output",
        str(markdown_path),
    )

    assert json_run.stdout == ""
    assert markdown_run.stdout == ""

    report = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert len(report["findings"]) == 2
    assert "# Bayesilisk Report" in markdown
    assert "- Seed: `150`" in markdown
    assert "- Production access: `false`" in markdown
    assert "## Sections" in markdown
    assert "Fingerprint:" in markdown
    assert "Classification:" in markdown
    assert "Issue readiness:" in markdown
    assert "Posterior mode:" in markdown
    assert "Observation basis:" in markdown
    assert "Access pattern:" in markdown
    assert "Sub-scenarios:" in markdown
    assert "Suggested issue body:" in markdown
    assert "Expected invariant:" in markdown
    assert "Risk score:" in markdown


def test_bayesilisk_observation_history_dampens_fixed_findings(tmp_path: Path) -> None:
    baseline = json.loads(run_bayesilisk("--seed", "150", "--format", "json").stdout)
    fixed_finding = next(finding for finding in baseline["findings"] if finding["observedResult"] == "fail")
    observation_path = tmp_path / "observations.json"
    observation_path.write_text(
        json.dumps(
            {
                "source": "unit-test-history",
                "fixedFingerprints": [fixed_finding["fingerprint"]],
            }
        ),
        encoding="utf-8",
    )

    adjusted = json.loads(
        run_bayesilisk("--seed", "150", "--format", "json", "--observations", str(observation_path)).stdout
    )
    adjusted_finding = next(
        finding for finding in adjusted["findings"] if finding["fingerprint"] == fixed_finding["fingerprint"]
    )

    assert adjusted_finding["riskScore"] < fixed_finding["riskScore"]
    assert adjusted_finding["issueReadiness"] == "regression-watch"
    assert "fixed-regression-watch" in adjusted_finding["observationBasis"]["tags"]


def test_bayesilisk_context_promotes_related_modes_and_dedupes_existing_payloads() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    baseline = bayesilisk.build_report(150, limit=8, generated_count=8)
    existing = next(finding for finding in baseline["findings"] if finding["issueReadiness"] == "ready-for-issue")
    context = {
        "source": "unit-test-agent-tracker-context",
        "agentNotes": [
            "Verifier saw HR documents process context metadata, support takeover, tenant DMS, travel expense receipts, "
            "and role permission 403 gaps on develop-usa.",
        ],
        "issues": [
            {
                "number": 999,
                "state": "open",
                "title": "Existing Bayesilisk finding",
                "body": f"Already tracked fingerprint `{existing['fingerprint']}`.",
            }
        ],
        "pullRequests": [{"number": 170, "state": "open", "title": "Bayesilisk verifier hardening"}],
    }

    report = bayesilisk.build_contextual_report(150, generated_count=8, context=context)
    context_summary = report["contextSummary"]

    assert context_summary["source"] == "unit-test-agent-tracker-context"
    assert context_summary["agentNoteCount"] == 1
    assert context_summary["issueCount"] == 1
    assert context_summary["pullRequestCount"] == 1
    assert existing["fingerprint"] in context_summary["fingerprints"]
    assert context_summary["priorAdjustments"]["dms.tenant_process_boundary"] > 0
    assert context_summary["priorAdjustments"]["hr.documents_customer_role_boundary"] > 0

    muted = next(finding for finding in report["findings"] if finding["fingerprint"] == existing["fingerprint"])
    assert muted["issueReadiness"] == "do-not-open-muted"
    assert "muted-known-non-issue" in muted["observationBasis"]["tags"]
    assert report["rankedProbes"]
    assert report["issuePayloads"]
    assert all(payload["fingerprint"] != existing["fingerprint"] for payload in report["issuePayloads"])


def test_playwright_probe_context_promotes_browser_observed_route_failures() -> None:
    adapter = importlib.import_module("bayesilisk.playwright_adapter")
    bayesilisk = importlib.import_module("bayesilisk.engine")
    context = adapter.build_context_from_probe_results(
        [
            {
                "actorRole": "support",
                "expectedStatus": 403,
                "invariantId": "hr.documents_customer_role_boundary",
                "observedStatus": 200,
                "route": "/api/hr/documents",
                "title": "Expired support shortcut reaches HR documents",
            },
            {
                "actorRole": "finance",
                "expectedStatus": 200,
                "invariantId": "billing.export_requires_role_and_module",
                "observedStatus": 200,
                "route": "/api/billing/exports",
                "title": "Finance billing export remains allowed",
            },
        ],
        target="file:///tmp/playwright-target.html",
    )

    assert context["source"] == "playwright-probe"
    assert context["playwrightProbe"]["failedCount"] == 1
    assert context["playwrightProbe"]["passedCount"] == 1
    assert context["priorAdjustments"]["hr.documents_customer_role_boundary"] == 0.06
    assert "Microsoft Playwright observed route permission behavior" in context["agentNotes"][0]
    assert context["repositoryFacts"][0]["source"] == "microsoft-playwright"

    report = bayesilisk.build_contextual_report(150, limit=12, context=context)
    observations = bayesilisk.context_observations(context)
    assert report["contextSummary"]["source"] == "playwright-probe"
    assert observations["priorAdjustments"]["hr.documents_customer_role_boundary"] == 0.06
    attention = report["grassmannAttention"]
    assert attention["boundedFeedback"] is True
    assert attention["embeddingMode"] == "grassmann-style-anchor-plane-proxy"
    assert "hr.documents_customer_role_boundary" in attention["selectedPlaneIds"]
    assert attention["planes"][0]["attentionScore"] > 0
    assert any("playwright-evidence" in plane["reasons"] for plane in attention["planes"])
    assert report["observedByPlaywright"]
    assert report["observedByPlaywright"][0]["source"] == "microsoft-playwright"
    assert report["selectedByGrassmannAttention"]
    assert report["proposedByModel"]["enabled"] is False
    assert report["verifiedByBayesilisk"]
    assert any(
        finding["generatedScenario"]
        and finding["generationBasis"].startswith("grassmann-attention:")
        for finding in report["findings"]
    )
    assert all("attentionScore" in finding for finding in report["findings"])
    assert report["rankedProbes"]


def test_fixed_or_muted_context_decays_attention_without_hiding_failures() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    context = {
        "source": "unit-test-muted-attention",
        "mutedInvariantIds": ["hr.documents_customer_role_boundary"],
        "repositoryFacts": [
            {
                "actorRole": "support",
                "expectedStatus": 403,
                "invariantId": "hr.documents_customer_role_boundary",
                "observedStatus": 200,
                "passed": False,
                "route": "/api/hr/documents",
                "source": "microsoft-playwright",
            }
        ],
    }
    undecayed = bayesilisk.grassmann_attention(
        {key: value for key, value in context.items() if key != "mutedInvariantIds"}
    )
    decayed = bayesilisk.grassmann_attention(context)
    undecayed_plane = next(
        plane for plane in undecayed["planes"] if plane["invariantId"] == "hr.documents_customer_role_boundary"
    )
    decayed_plane = next(
        plane for plane in decayed["planes"] if plane["invariantId"] == "hr.documents_customer_role_boundary"
    )

    assert decayed_plane["decayForFixedOrMuted"] == 0.2
    assert decayed_plane["attentionScore"] < undecayed_plane["attentionScore"]
    assert "fixed-or-muted-attention-decay" in decayed_plane["reasons"]

    report = bayesilisk.build_contextual_report(150, generated_count=0, context=context)
    assert any(
        finding["invariantId"] == "hr.documents_customer_role_boundary"
        and finding["observedResult"] == "fail"
        for finding in report["findings"]
    )


def test_playwright_context_preserves_probe_evidence_metadata() -> None:
    adapter = importlib.import_module("bayesilisk.playwright_adapter")
    context = adapter.build_context_from_probe_results(
        [
            {
                "actorRole": "support",
                "artifactPaths": ["/tmp/bayesilisk/probe-01-screenshot.png", "/tmp/bayesilisk/trace.zip"],
                "expectedStatus": 403,
                "failureDetail": "observed 200 while expecting 403",
                "invariantId": "hr.documents_customer_role_boundary",
                "networkResponses": [{"status": 200, "url": "https://example.test/api/hr/documents"}],
                "observedStatus": 200,
                "route": "/api/hr/documents",
                "selector": "[data-bayesilisk-probe] >> nth=0",
                "targetUrl": "https://example.test/demo",
                "timestamp": "2026-05-16T00:00:00+00:00",
                "title": "Support reaches HR documents",
            }
        ],
        target="https://example.test/demo",
    )
    fact = context["repositoryFacts"][0]

    assert context["playwrightProbe"]["artifactCount"] == 2
    assert fact["artifactPaths"] == ["/tmp/bayesilisk/probe-01-screenshot.png", "/tmp/bayesilisk/trace.zip"]
    assert fact["failureDetail"] == "observed 200 while expecting 403"
    assert fact["networkResponses"] == [{"status": 200, "url": "https://example.test/api/hr/documents"}]
    assert fact["selector"] == "[data-bayesilisk-probe] >> nth=0"
    assert fact["targetUrl"] == "https://example.test/demo"
    assert fact["timestamp"] == "2026-05-16T00:00:00+00:00"


def test_grassmann_attention_biases_generation_without_overriding_verdicts() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    context = {
        "source": "unit-test-travel-plane",
        "repositoryFacts": [
            {
                "actorRole": "finance",
                "expectedStatus": 403,
                "invariantId": "travel.expense_items_match_itinerary",
                "observedStatus": 200,
                "passed": False,
                "route": "/api/expense-claims/{claimId}/review",
                "source": "microsoft-playwright",
                "title": "Airfare accepted without matching itinerary leg",
            }
        ],
    }

    baseline = bayesilisk.build_report(150, generated_count=8)
    contextual = bayesilisk.build_contextual_report(150, generated_count=8, context=context)

    assert "travel.expense_items_match_itinerary" in contextual["grassmannAttention"]["selectedPlaneIds"]
    assert not any(
        finding["generationBasis"].startswith("grassmann-attention:")
        for finding in baseline["findings"]
    )
    attention_findings = [
        finding
        for finding in contextual["findings"]
        if finding["scenarioId"] == "generated.attention.01.travel_expense_items_match_itinerary"
    ]
    assert attention_findings
    chronology = next(
        finding for finding in attention_findings if finding["invariantId"] == "travel.itinerary_chronology"
    )
    transport_match = next(
        finding
        for finding in attention_findings
        if finding["invariantId"] == "travel.expense_items_match_itinerary"
    )
    assert chronology["observedResult"] == "pass"
    assert transport_match["observedResult"] == "fail"
    assert transport_match["attentionScore"] > 0
    assert "playwright-evidence" in transport_match["attentionReasons"]


def test_generated_failure_minimization_covers_travel_dms_support_and_hr() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    selected_planes = [
        "travel.expense_items_match_itinerary",
        "dms.tenant_process_boundary",
        "support.takeover_session_required",
        "hr.documents_customer_role_boundary",
    ]
    report = bayesilisk.build_report(
        150,
        generated_count=4,
        grassmann={
            "embeddingMode": "unit-test",
            "planes": [
                {
                    "attentionScore": 0.8,
                    "invariantId": invariant_id,
                    "reasons": ["unit-test-minimization"],
                }
                for invariant_id in selected_planes
            ],
            "selectedPlaneIds": selected_planes,
        },
    )

    def minimized_fragment_ids(scenario_id: str, invariant_id: str) -> list[str]:
        finding = next(
            finding
            for finding in report["findings"]
            if finding["scenarioId"] == scenario_id and finding["invariantId"] == invariant_id
        )
        assert finding["observedResult"] == "fail"
        assert finding["originalScenario"]["fragmentIds"] == [fragment["id"] for fragment in finding["fragments"]]
        assert finding["minimizedReproducer"]["preservedInvariantFailure"] is True
        assert finding["minimizedReproducer"]["minimizedFragmentCount"] < finding["minimizedReproducer"][
            "originalFragmentCount"
        ]
        assert finding["observation"] == finding["minimizedReproducer"]["observation"]
        assert set(finding["minimizedReproducer"]["removedFragmentIds"]) < set(finding["originalScenario"]["fragmentIds"])
        return finding["minimizedReproducer"]["fragmentIds"]

    assert minimized_fragment_ids(
        "generated.attention.01.travel_expense_items_match_itinerary",
        "travel.expense_items_match_itinerary",
    ) == ["expense.airfare", "travel.legs_missing_airplane"]
    assert minimized_fragment_ids(
        "generated.attention.02.dms_tenant_process_boundary",
        "dms.tenant_process_boundary",
    ) == ["dms.foreign_tenant_document"]
    assert minimized_fragment_ids(
        "generated.attention.03.support_takeover_session_required",
        "support.takeover_session_required",
    ) == ["role.support_takeover_expired"]
    assert minimized_fragment_ids(
        "generated.attention.04.hr_documents_customer_role_boundary",
        "hr.documents_customer_role_boundary",
    ) == ["role.support_takeover_expired", "hr.payroll_file_route"]

    payloads = bayesilisk.issue_payloads(report)
    payload = next(
        payload
        for payload in payloads
        if payload["scenarioId"] == "generated.attention.01.travel_expense_items_match_itinerary"
        and payload["invariantId"] == "travel.expense_items_match_itinerary"
    )
    assert payload["originalScenario"]["fragmentIds"] != payload["minimizedReproducer"]["fragmentIds"]
    assert "Original generated scenario:" in payload["body"]
    assert "Minimized reproducer:" in payload["body"]


def test_weak_model_proposals_are_schema_validated_before_becoming_scenarios() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    attention = {
        "selectedPlaneIds": ["hr.documents_customer_role_boundary"],
        "planes": [],
    }
    proposals = [
        {
            "title": "Weak model proposes support HR document probe",
            "targetPlane": "hr.documents_customer_role_boundary",
            "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
            "invariants": [
                "support.takeover_session_required",
                "hr.documents_customer_role_boundary",
            ],
        },
        {
            "title": "Rejected invented route",
            "targetPlane": "hr.documents_customer_role_boundary",
            "fragments": ["role.support_takeover_active", "route.invented"],
            "invariants": ["hr.documents_customer_role_boundary"],
        },
    ]

    provider = {
        "baseUrlClass": "loopback",
        "modelName": "gemma4:e2b",
        "promptHash": "prompt-hash-for-test",
        "promptVersion": "scenario-proposer.v1",
        "provider": "ollama",
        "source": "ollama-chat",
        "sourceContext": "unit-test",
    }
    scenarios, rejected = bayesilisk.validate_model_scenario_proposals(proposals, attention, provider=provider)
    assert len(scenarios) == 1
    assert scenarios[0].id.startswith("generated.model.01.hr_documents_customer_role_boundary")
    assert scenarios[0].generation_basis == "weak-model-proposal:hr.documents_customer_role_boundary"
    assert scenarios[0].provenance["provider"] == "ollama"
    assert scenarios[0].provenance["modelName"] == "gemma4:e2b"
    assert scenarios[0].provenance["baseUrlClass"] == "loopback"
    assert scenarios[0].provenance["promptHash"] == "prompt-hash-for-test"
    assert scenarios[0].provenance["proposalHash"]
    assert rejected[0]["reason"] == "unknown-fragment-id"
    assert rejected[0]["proposalHash"]

    report = bayesilisk.build_report(
        150,
        generated_count=1,
        grassmann={
            "embeddingMode": "unit-test",
            "planes": [
                {
                    "attentionScore": 0.8,
                    "invariantId": "hr.documents_customer_role_boundary",
                    "reasons": ["unit-test-model-proposal"],
                }
            ],
            "selectedPlaneIds": [],
            "weakModelScenarioGeneration": {"enabled": True, "acceptedCount": 1},
        },
        model_scenarios=scenarios,
    )
    model_findings = [
        finding
        for finding in report["findings"]
        if finding["scenarioId"] == scenarios[0].id
    ]
    assert model_findings
    assert any(finding["observedResult"] == "fail" for finding in model_findings)
    assert all(finding["generationBasis"].startswith("weak-model-proposal:") for finding in model_findings)
    assert all(finding["modelProvenance"]["proposalHash"] == scenarios[0].provenance["proposalHash"] for finding in model_findings)

    payloads = bayesilisk.issue_payloads(report)
    model_payloads = [payload for payload in payloads if payload["scenarioId"] == scenarios[0].id]
    assert model_payloads
    assert all(payload["modelProvenance"]["provider"] == "ollama" for payload in model_payloads)
    hr_payload = next(
        payload for payload in model_payloads if payload["invariantId"] == "hr.documents_customer_role_boundary"
    )
    assert hr_payload["originalScenario"]["fragmentIds"] == [
        "role.support_takeover_active",
        "hr.payroll_file_route",
    ]
    assert hr_payload["minimizedReproducer"]["fragmentIds"] == [
        "role.support_takeover_active",
        "hr.payroll_file_route",
    ]
    assert hr_payload["minimizedReproducer"]["preservedInvariantFailure"] is True


def test_scenario_proposer_config_precedence_and_report_redaction(monkeypatch: pytest.MonkeyPatch) -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    monkeypatch.setenv("BAYESILISK_SCENARIO_PROVIDER", "openai-compatible")
    monkeypatch.setenv("BAYESILISK_SCENARIO_API_KEY_ENV", "BAYESILISK_UNIT_SCENARIO_KEY")
    monkeypatch.setenv("BAYESILISK_UNIT_SCENARIO_KEY", "sk-unit-secret")
    monkeypatch.setenv("BAYESILISK_SCENARIO_BASE_URL", "https://llm.example.test/v1")

    config = bayesilisk.effective_runtime_config({})
    report_config = bayesilisk.report_runtime_config(config)

    assert config["scenarioProvider"] == "openai-compatible"
    assert config["scenarioApiKey"] == "sk-unit-secret"
    assert report_config["scenarioProvider"] == "openai-compatible"
    assert report_config["scenarioApiKeyConfigured"] is True
    assert report_config["scenarioBaseUrlClass"] == "remote-host"
    assert "sk-unit-secret" not in json.dumps(report_config)

    override = bayesilisk.effective_runtime_config({"scenarioProvider": "ollama", "scenarioApiKey": "override-secret"})
    override_report = bayesilisk.report_runtime_config(override)
    assert override["scenarioProvider"] == "ollama"
    assert override["scenarioApiKey"] == "override-secret"
    assert override_report["scenarioProvider"] == "ollama"
    assert "override-secret" not in json.dumps(override_report)


def test_openai_compatible_provider_requires_api_key() -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    attention = {
        "source": "unit-test",
        "selectedPlaneIds": ["hr.documents_customer_role_boundary"],
        "planes": [],
    }

    scenarios, generation = bayesilisk.weak_model_scenarios(
        attention,
        runtime_config={
            "enableScenarioProposer": True,
            "scenarioProvider": "openai-compatible",
            "scenarioBaseUrl": "https://llm.example.test/v1",
            "scenarioApiKey": "",
        },
    )

    assert scenarios == []
    assert generation["provider"] == "openai-compatible"
    assert generation["error"] == "missing-api-key"
    assert generation["acceptedCount"] == 0


def test_provider_auth_failures_and_unavailable_ollama_are_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    model_proposals = importlib.import_module("bayesilisk.model_proposals")
    attention = {
        "source": "unit-test",
        "selectedPlaneIds": ["hr.documents_customer_role_boundary"],
        "planes": [],
    }

    def auth_failure(*args: object, **kwargs: object) -> dict[str, object]:
        raise urllib.error.HTTPError("https://llm.example.test/v1", 401, "Unauthorized Bearer sk-secret", {}, None)

    monkeypatch.setattr(model_proposals, "_openai_compatible_chat_json", auth_failure)
    _, auth_generation = bayesilisk.weak_model_scenarios(
        attention,
        runtime_config={
            "enableScenarioProposer": True,
            "scenarioProvider": "openai-compatible",
            "scenarioBaseUrl": "https://llm.example.test/v1",
            "scenarioApiKey": "sk-secret",
        },
    )
    assert auth_generation["error"] == "provider-authentication-failed"
    assert "sk-secret" not in json.dumps(auth_generation)

    def unavailable(*args: object, **kwargs: object) -> dict[str, object]:
        raise OSError("connection refused Bearer sk-ollama-leak")

    monkeypatch.setattr(model_proposals, "_ollama_chat_json", unavailable)
    _, ollama_generation = bayesilisk.weak_model_scenarios(
        attention,
        runtime_config={"enableScenarioProposer": True, "scenarioProvider": "ollama"},
    )
    assert ollama_generation["provider"] == "ollama"
    assert "connection refused" in ollama_generation["error"]
    assert "sk-ollama-leak" not in json.dumps(ollama_generation)


def test_provider_output_remains_untrusted_and_redacted(monkeypatch: pytest.MonkeyPatch) -> None:
    bayesilisk = importlib.import_module("bayesilisk.engine")
    model_proposals = importlib.import_module("bayesilisk.model_proposals")
    attention = {
        "source": "unit-test",
        "selectedPlaneIds": ["hr.documents_customer_role_boundary"],
        "planes": [],
    }

    def fake_chat(*args: object, **kwargs: object) -> dict[str, object]:
        return {
            "scenarios": [
                {
                    "title": "Provider proposes support HR probe",
                    "targetPlane": "hr.documents_customer_role_boundary",
                    "fragments": ["role.support_takeover_active", "hr.payroll_file_route"],
                    "invariants": ["support.takeover_session_required", "hr.documents_customer_role_boundary"],
                },
                {
                    "title": "Provider leaks in rejected proposal",
                    "targetPlane": "hr.documents_customer_role_boundary",
                    "fragments": ["role.support_takeover_active", "route.invented"],
                    "invariants": ["hr.documents_customer_role_boundary"],
                    "apiKey": "sk-provider-secret",
                    "headers": {"Authorization": "Bearer sk-provider-secret"},
                },
            ]
        }

    monkeypatch.setattr(model_proposals, "_openai_compatible_chat_json", fake_chat)
    scenarios, generation = bayesilisk.weak_model_scenarios(
        attention,
        runtime_config={
            "enableScenarioProposer": True,
            "scenarioProvider": "openai-compatible",
            "scenarioBaseUrl": "https://llm.example.test/v1",
            "scenarioApiKey": "sk-config-secret",
        },
    )

    assert len(scenarios) == 1
    assert generation["acceptedCount"] == 1
    assert generation["rejected"][0]["reason"] == "unknown-fragment-id"
    serialized = json.dumps(generation)
    assert "sk-provider-secret" not in serialized
    assert "sk-config-secret" not in serialized
    assert "[REDACTED]" in serialized


def test_bayesilisk_cli_context_can_emit_issue_payloads(tmp_path: Path) -> None:
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "source": "unit-test-cli-context",
                "agentNotes": ["travel expense itinerary and support takeover permission probe"],
            }
        ),
        encoding="utf-8",
    )

    report = json.loads(
        run_bayesilisk("--seed", "150", "--format", "json", "--limit", "3", "--context", str(context_path)).stdout
    )
    payloads = json.loads(
        run_bayesilisk(
            "--seed",
            "150",
            "--limit",
            "3",
            "--context",
            str(context_path),
            "--issue-payloads",
        ).stdout
    )

    assert report["contextSummary"]["source"] == "unit-test-cli-context"
    assert report["rankedProbes"]
    assert payloads
    assert {"title", "body", "fingerprint", "dedupeState", "labels"} <= set(payloads[0])
    assert payloads[0]["dedupeState"] == "new"
    assert payloads[0]["issuePayloadSource"] == "verifiedByBayesilisk"


def test_bayesilisk_demo_command_shows_full_loop_without_playwright() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bayesilisk.demo", "--no-playwright", "--json"],
        check=True,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    chain = payload["chain"]

    assert payload["demo"] == "workflow-pressure"
    assert payload["playwrightMode"].startswith("fallback:")
    assert payload["playwrightProbe"]["failedCount"] >= 4
    assert chain["playwrightEvidence"]["source"] == "microsoft-playwright"
    assert chain["grassmannPlane"]["invariantId"]
    assert chain["modelProposal"]["mode"] == "canned-local-optional"
    assert chain["modelProposal"]["acceptedCount"] == 1
    assert chain["modelProposal"]["rejectedReasons"] == ["unknown-target-plane"]
    assert chain["deterministicVerdict"]["observedResult"] == "fail"
    assert chain["issuePayload"]["issuePayloadSource"] == "verifiedByBayesilisk"


def test_bayesilisk_cli_reports_effective_runtime_configuration() -> None:
    report = json.loads(
        run_bayesilisk(
            "--seed",
            "150",
            "--limit",
            "1",
            "--enable-embeddings",
            "--embedding-model",
            "unit-embed",
            "--enable-scenario-proposer",
            "--scenario-provider",
            "ollama",
            "--scenario-model",
            "unit-scenario",
            "--scenario-base-url",
            "https://llm.example.test/v1",
            "--scenario-proposal-limit",
            "5",
            "--attention-threshold",
            "0.9",
            "--attention-selection-limit",
            "2",
            "--ollama-base-url",
            "http://localhost:11435",
        ).stdout
    )
    config = report["effectiveConfiguration"]

    assert config["attentionSelectionLimit"] == 2
    assert config["attentionThreshold"] == 0.9
    assert config["embeddingModel"] == "unit-embed"
    assert config["embeddingsEnabled"] is True
    assert config["ollamaBaseUrlClass"] == "loopback"
    assert config["scenarioApiKeyConfigured"] is False
    assert config["scenarioBaseUrlClass"] == "remote-host"
    assert config["scenarioModel"] == "unit-scenario"
    assert config["scenarioProposalLimit"] == 5
    assert config["scenarioProposerEnabled"] is True
    assert config["scenarioProvider"] == "ollama"


def test_bayesilisk_mcp_server_lists_tools_and_returns_ranked_context() -> None:
    server = importlib.import_module("bayesilisk.mcp_server")

    initialize = server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    tools = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    call = server.handle_request(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "bayesilisk.rank_context",
                "arguments": {
                    "seed": 150,
                    "limit": 2,
                    "context": {
                        "agentNotes": ["HR documents DMS tenant scope and travel expense itinerary probe"],
                    },
                    "attentionThreshold": 0.9,
                    "attentionSelectionLimit": 1,
                    "enableEmbeddings": False,
                    "enableScenarioProposer": False,
                    "embeddingModel": "mcp-embed",
                    "scenarioProvider": "ollama",
                    "scenarioModel": "mcp-scenario",
                },
            },
        }
    )

    assert initialize["result"]["serverInfo"]["version"] == "bayesilisk.v1.2"
    assert {tool["name"] for tool in tools["result"]["tools"]} == {
        "bayesilisk.issue_payloads",
        "bayesilisk.rank_context",
        "bayesilisk.run",
    }
    payload = json.loads(call["result"]["content"][0]["text"])
    assert payload["tool"] == "bayesilisk.v1.2"
    assert payload["contextSummary"]["textSignalCount"] >= 1
    assert len(payload["rankedProbes"]) == 2
    assert payload["effectiveConfiguration"]["attentionThreshold"] == 0.9
    assert payload["effectiveConfiguration"]["attentionSelectionLimit"] == 1
    assert payload["effectiveConfiguration"]["embeddingModel"] == "mcp-embed"
    assert payload["effectiveConfiguration"]["scenarioModel"] == "mcp-scenario"
    assert payload["effectiveConfiguration"]["scenarioProvider"] == "ollama"

    raw = io.BytesIO()
    server.write_message(raw, {"jsonrpc": "2.0", "id": 4, "result": {"ok": True}})
    raw.seek(0)
    assert server.read_message(raw) == {"jsonrpc": "2.0", "id": 4, "result": {"ok": True}}


def test_bayesilisk_documentation_pins_no_production_access_and_report_contract() -> None:
    document = DOC.read_text(encoding="utf-8")

    for fragment in (
        "no production access",
        "Rule invariants",
        "Bayesian prioritization",
        "Scenario fragments",
        "Report Contract",
        "breakage/finding classification",
        "posterior mode",
        "fingerprint",
        "issue readiness",
        "observation history",
        "MCP tool server",
        "Microsoft Playwright bridge",
        "Grassmann attention",
        "tools/playwright_probe.py --demo",
        "Context ingestion",
        "bayesilisk.rank_context",
        "bayesilisk.issue_payloads",
        "rental car, train, and airplane",
        "Permission/role matrix",
        "python3 -m bayesilisk --seed 150 --format json",
        "must not connect to production systems",
        "must not",
        "internal platform claims",
    ):
        assert fragment in document


def test_design_document_pins_trust_boundaries() -> None:
    design = DESIGN.read_text(encoding="utf-8")

    for fragment in (
        "scenario facts -> invariant checks -> pass/fail -> Bayesian ranking",
        "observedByPlaywright",
        "selectedByGrassmannAttention",
        "proposedByModel",
        "verifiedByBayesilisk",
        "Playwright is the sensor.",
        "Grassmann is the router.",
        "The scenario proposer model is the proposer.",
        "Bayesilisk is the judge.",
        "No embedding, Grassmann score, model output, issue text, or Playwright observation may directly decide",
        "attentionScore",
        "riskScore",
        "Model output is untrusted candidate input.",
    ):
        assert fragment in design


def test_readme_pins_ci_trust_signals_and_product_motto() -> None:
    readme = README.read_text(encoding="utf-8")
    pyproject = PYPROJECT.read_text(encoding="utf-8")

    for fragment in (
        "actions/workflows/ci.yml/badge.svg",
        "Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the Oracle.",
        'python3 -m pytest -m "not live_playwright and not live_ollama"',
        "sphinx-build -b html docs docs/_build/html",
        "Live browser/model checks are local opt-in tests",
        "BAYESILISK_LIVE_OLLAMA=1",
        "without Ollama",
        "without granting a model authority",
        "--enable-embeddings",
        "--enable-scenario-proposer",
        "--scenario-provider",
        "--scenario-proposal-limit",
        "effectiveConfiguration",
        "ollamaBaseUrl",
        "bayesilisk-demo",
    ):
        assert fragment in readme
    assert 'bayesilisk-demo = "bayesilisk.demo:main"' in pyproject


def test_proof_artifacts_are_linked_and_explain_trust_boundaries() -> None:
    readme = README.read_text(encoding="utf-8")
    reports = REPORTS_DOC.read_text(encoding="utf-8")

    for path in (
        REPO_ROOT / "docs" / "assets" / "bayesilisk-proof-loop.gif",
        REPO_ROOT / "docs" / "examples" / "example-report.json",
        REPO_ROOT / "docs" / "examples" / "example-issue-payloads.json",
    ):
        assert path.exists()
        assert path.stat().st_size > 0

    for fragment in (
        "docs/assets/bayesilisk-proof-loop.gif",
        "docs/examples/example-report.json",
        "docs/examples/example-issue-payloads.json",
        "Why This Is Not a Black Box",
        "Model Unavailable? Still Works",
        "Playwright evidence -> Grassmann attention -> model proposal -> Bayesilisk verification -> issue payload",
        "Model output remains untrusted candidate input.",
        "Only `verifiedByBayesilisk` contains deterministic invariant results",
    ):
        assert fragment in readme

    for fragment in (
        "Example JSON report",
        "Example GitHub issue payloads",
        "Why This Is Not a Black Box",
        "Model Unavailable? Still Works",
        "The issue-worthy result must come from `verifiedByBayesilisk`.",
        "does not require Ollama",
    ):
        assert fragment in reports
