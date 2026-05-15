from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BAYESILISK = REPO_ROOT / "tools" / "bayesilisk" / "bayesilisk.py"
DOC = REPO_ROOT / "docs" / "bayesilisk.md"


def run_bayesilisk(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(BAYESILISK), *args],
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

    assert report["tool"] == "bayesilisk.v1"
    assert report["seed"] == 150
    assert report["deterministic"] is True
    assert report["productionAccess"] is False
    assert "harder-to-find-after-easy-breakages" in report["prioritizationPolicy"]
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
        "roundup.travel_funding_unapproved_multimodal_expense",
        "inconsistent.travel_air_train_leg_mismatch",
    } <= {finding["scenarioId"] for finding in findings}
    assert {"breakage.easy", "breakage.hard-to-find", "control-confirmed"} <= {
        finding["classification"] for finding in findings
    }
    assert {
        "harder-to-find-after-easy-breakages",
        "highest-fault-probability",
        "posterior-control-confidence",
    } <= {finding["posteriorMode"] for finding in findings}

    for finding in findings:
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
        assert "Reproduce with `python tools/bayesilisk/bayesilisk.py --seed <seed> --format json`" in finding[
            "suggestedIssueBody"
        ]


def test_bayesilisk_markdown_and_output_files_include_gitea_ready_findings(tmp_path: Path) -> None:
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
    assert "Classification:" in markdown
    assert "Posterior mode:" in markdown
    assert "Access pattern:" in markdown
    assert "Sub-scenarios:" in markdown
    assert "Suggested Gitea issue body:" in markdown
    assert "Expected invariant:" in markdown
    assert "Risk score:" in markdown


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
        "rental car, train, and airplane",
        "Permission/role matrix",
        "python tools/bayesilisk/bayesilisk.py --seed 150 --format json",
        "must not connect to production systems",
        "must not",
        "internal platform claims",
    ):
        assert fragment in document
