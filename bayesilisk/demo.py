from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from .catalog import attention_composite_scenarios
from .constants import VERSION
from .model_proposals import (
    SCENARIO_PROPOSER_PROMPT_VERSION,
    validate_model_scenario_proposals,
)
from .playwright_adapter import build_context_from_probe_results
from .reporting import build_contextual_report, build_report, issue_payloads


CLASSIFICATION_LEGEND: dict[str, str] = {
    "breakage.easy": (
        "An invariant fails in a direct, high-signal path. This is usually obvious once the route or state is tested."
    ),
    "breakage.hard-to-find": (
        "An invariant fails only after context narrows the search to a cross-role, cross-module, stale-state, "
        "or unusual workflow path. It is still a deterministic failure; the label describes discoverability, "
        "not uncertainty."
    ),
    "control-confirmed": (
        "A control path behaved as expected and increases confidence that the verifier is not blindly reporting noise."
    ),
    "finding.candidate-breakage": (
        "An invariant failed, but the posterior score or evidence basis is not strong enough for an automatic issue. "
        "Keep it as a probe until a local verifier, browser evidence, or human review confirms it."
    ),
}


DEMO_FIXTURE_SOURCE = "bayesilisk/demo.py::DEMO_PROBES"
DEMO_FIXTURE_KIND = "synthetic-local-fixture"


DEMO_PROBES: tuple[dict[str, str], ...] = (
    {
        "actorRole": "manager",
        "actualStatus": "200",
        "domain": "Travel",
        "expectedStatus": "409",
        "fixtureId": "travel-expense-before-funding",
        "invariantId": "travel.funding_before_expense",
        "meaning": "Should reject expense review before travel funding is approved.",
        "route": "/demo/wizard/expense-review",
        "source": "seeded-workflow-fixture",
        "title": "Wizard accepts expense review before travel funding approval",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "Travel",
        "expectedStatus": "409",
        "fixtureId": "travel-itinerary-expense-mismatch",
        "invariantId": "travel.expense_items_match_itinerary",
        "meaning": "Should reject expense review when itinerary and expense dates do not match.",
        "route": "/demo/checkout/review",
        "source": "seeded-workflow-fixture",
        "title": "Checkout review accepts itinerary and expense mismatch",
    },
    {
        "actorRole": "employee",
        "actualStatus": "200",
        "domain": "Expenses",
        "expectedStatus": "409",
        "fixtureId": "expense-duplicate-stale-submit",
        "invariantId": "modules.expense_approval_requires_module_and_receipt",
        "meaning": "Should reject duplicate or stale expense submission state.",
        "route": "/demo/retry/expense-submit",
        "source": "seeded-workflow-fixture",
        "title": "Retry after back navigation creates duplicate submission",
    },
    {
        "actorRole": "support",
        "actualStatus": "200",
        "domain": "HR",
        "expectedStatus": "403",
        "fixtureId": "support-hr-document-shortcut",
        "invariantId": "hr.documents_customer_role_boundary",
        "meaning": "Should deny support access to customer HR documents.",
        "route": "/api/hr/documents",
        "source": "seeded-workflow-fixture",
        "title": "Support actor reaches HR document route",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "Billing",
        "expectedStatus": "403",
        "fixtureId": "billing-export-feature-off",
        "invariantId": "billing.export_requires_role_and_module",
        "meaning": "Should deny billing export when the feature/module boundary is closed.",
        "route": "/api/billing/exports",
        "source": "seeded-workflow-fixture",
        "title": "Feature flag off but billing export path remains exposed",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "DMS",
        "expectedStatus": "403",
        "fixtureId": "foreign-tenant-receipt",
        "invariantId": "dms.tenant_process_boundary",
        "meaning": "Should reject a receipt document from another tenant.",
        "route": "/api/dms/documents/foreign-receipt",
        "source": "seeded-workflow-fixture",
        "title": "Foreign-tenant receipt is accepted during expense review",
    },
    {
        "actorRole": "employee",
        "actualStatus": "200",
        "domain": "Expenses",
        "expectedStatus": "403",
        "fixtureId": "employee-self-review",
        "invariantId": "roles.employee_self_review_forbidden",
        "meaning": "Should deny an employee approving their own claim.",
        "route": "/api/expense-claims/self/review",
        "source": "seeded-workflow-fixture",
        "title": "Employee self-review is accepted",
    },
    {
        "actorRole": "support",
        "actualStatus": "200",
        "domain": "Support",
        "expectedStatus": "403",
        "fixtureId": "expired-support-takeover",
        "invariantId": "support.takeover_session_required",
        "meaning": "Should deny support access after takeover expiry.",
        "route": "/api/support/takeover/expense-review",
        "source": "seeded-workflow-fixture",
        "title": "Expired support takeover still reaches a workflow",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "Expenses",
        "expectedStatus": "403",
        "fixtureId": "expense-missing-receipt",
        "invariantId": "modules.expense_approval_requires_module_and_receipt",
        "meaning": "Should reject approval when required receipt evidence is missing.",
        "route": "/api/expense-claims/missing-receipt/review",
        "source": "seeded-workflow-fixture",
        "title": "Expense approval succeeds without required receipt",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "Travel",
        "expectedStatus": "409",
        "fixtureId": "non-chronological-itinerary",
        "invariantId": "travel.itinerary_chronology",
        "meaning": "Should reject a travel itinerary with impossible date ordering.",
        "route": "/api/travel/itineraries/non-chronological",
        "source": "seeded-workflow-fixture",
        "title": "Non-chronological itinerary is accepted",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "domain": "Billing",
        "expectedStatus": "200",
        "fixtureId": "billing-export-control",
        "invariantId": "billing.export_requires_role_and_module",
        "meaning": "Control: finance with billing enabled should export successfully.",
        "route": "/api/billing/exports",
        "source": "seeded-control-fixture",
        "title": "Billing export control remains allowed",
    },
    {
        "actorRole": "hr_manager",
        "actualStatus": "200",
        "domain": "HR",
        "expectedStatus": "200",
        "fixtureId": "hr-document-control",
        "invariantId": "hr.documents_customer_role_boundary",
        "meaning": "Control: customer HR manager should reach HR documents.",
        "route": "/api/hr/documents",
        "source": "seeded-control-fixture",
        "title": "HR manager document control remains allowed",
    },
)


def demo_html() -> str:
    rows = []
    for index, probe in enumerate(DEMO_PROBES, start=1):
        rows.append(
            f"""
            <tr
              data-bayesilisk-probe
              data-title="{probe['title']}"
              data-actor-role="{probe['actorRole']}"
              data-domain="{probe['domain']}"
              data-fixture-id="{probe['fixtureId']}"
              data-meaning="{probe['meaning']}"
              data-route="{probe['route']}"
              data-source="{probe['source']}"
              data-invariant-id="{probe['invariantId']}"
              data-expected-status="{probe['expectedStatus']}"
              data-actual-status="{probe['actualStatus']}"
              data-api-path="/api/probe/{index}"
              data-fixture-source="{DEMO_FIXTURE_SOURCE}"
            >
              <td>{probe['title']}</td>
              <td><code>{probe['domain']}</code></td>
              <td><code>{probe['actorRole']}</code></td>
              <td><code>{probe['route']}</code></td>
              <td>{probe['meaning']}</td>
              <td><code>{probe['source']}</code></td>
              <td><code>{probe['expectedStatus']}</code></td>
              <td><code data-observed-status>pending</code></td>
              <td><button type="button" data-run-probe>Run</button></td>
            </tr>
            """
        )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bayesilisk Workflow Pressure Demo</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.45;
      }}
      body {{
        margin: 0;
        background: #f5f7fb;
        color: #162033;
      }}
      main {{
        margin: 0 auto;
        max-width: 1440px;
        padding: 28px 20px 44px;
      }}
      h1 {{
        font-size: 28px;
        margin: 0 0 8px;
      }}
      .notice {{
        background: #fff7da;
        border: 1px solid #dcc36b;
        color: #3d3212;
        margin: 0 0 18px;
        padding: 12px 14px;
      }}
      p {{
        color: #526070;
        margin: 0 0 18px;
      }}
      table {{
        background: #ffffff;
        border: 1px solid #d9e0ea;
        border-collapse: collapse;
        width: 100%;
      }}
      th, td {{
        border-bottom: 1px solid #e7ebf2;
        padding: 9px 10px;
        text-align: left;
        vertical-align: middle;
      }}
      th {{
        background: #edf2f8;
        color: #344055;
        font-size: 13px;
        font-weight: 700;
      }}
      code {{
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
        font-size: 13px;
      }}
      button {{
        background: #15658e;
        border: 0;
        border-radius: 6px;
        color: #ffffff;
        cursor: pointer;
        font: inherit;
        font-weight: 700;
        min-width: 72px;
        padding: 8px 12px;
      }}
      [data-observed-status] {{
        font-variant-numeric: tabular-nums;
        font-weight: 700;
      }}
    </style>
  </head>
  <body>
    <main>
      <h1>Bayesilisk Workflow Pressure Demo</h1>
      <div class="notice">
        Synthetic local fixture app. These rows are not imported from an existing customer app.
        They are defined in <code>{DEMO_FIXTURE_SOURCE}</code>; Bayesilisk then adds generated and
        model-style scenarios and checks everything with deterministic invariants.
      </div>
      <p>
        Twelve product-like workflow fixtures across Travel, Expenses, Billing, HR, Support, and DMS:
        stale state, impossible ordering, duplicate submission, feature-flag exposure, tenant boundaries,
        controls, and role lanes. The browser observes the fixture app; Bayesilisk judges deterministic
        invariants from the resulting context.
      </p>
      <table aria-label="Bayesilisk workflow pressure probes">
        <thead>
          <tr>
            <th>Scenario pressure</th>
            <th>Domain</th>
            <th>Actor</th>
            <th>Route or workflow</th>
            <th>Guard</th>
            <th>Fixture source</th>
            <th>Expected</th>
            <th>Observed</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {"".join(rows)}
        </tbody>
      </table>
    </main>
    <script>
      for (const button of document.querySelectorAll("[data-run-probe]")) {{
        button.addEventListener("click", async () => {{
          const row = button.closest("[data-bayesilisk-probe]");
          const response = await fetch(`${{row.dataset.apiPath}}?status=${{row.dataset.actualStatus}}`);
          row.querySelector("[data-observed-status]").textContent = String(response.status);
        }});
      }}
    </script>
  </body>
</html>
"""


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            body = demo_html().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path.startswith("/api/probe/"):
            status = int(parse_qs(parsed.query).get("status", ["200"])[0])
            body = json.dumps({"status": status, "demo": "bayesilisk"}).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def log_message(self, format: str, *args: Any) -> None:
        return


@contextmanager
def demo_server() -> Any:
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def run_playwright_probe(
    url: str,
    *,
    headless: bool,
    hold_ms: int,
    step_delay_ms: int,
    timeout_ms: int,
) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed; rerun with --no-playwright for deterministic local evidence.") from exc

    results: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            network_responses: list[dict[str, Any]] = []
            page.on("response", lambda response: network_responses.append({"status": response.status, "url": response.url}))
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            probes = page.locator("[data-bayesilisk-probe]")
            for index in range(probes.count()):
                probe = probes.nth(index)
                probe.locator("[data-run-probe]").click(timeout=timeout_ms)
                status = probe.locator("[data-observed-status]")
                deadline = time.monotonic() + (timeout_ms / 1000)
                observed = status.inner_text(timeout=timeout_ms).strip()
                while observed == "pending" and time.monotonic() < deadline:
                    page.wait_for_timeout(50)
                    observed = status.inner_text(timeout=timeout_ms).strip()
                results.append(
                    {
                        "actorRole": probe.get_attribute("data-actor-role"),
                        "domain": probe.get_attribute("data-domain"),
                        "expectedStatus": probe.get_attribute("data-expected-status"),
                        "failureDetail": "",
                        "fixtureId": probe.get_attribute("data-fixture-id"),
                        "fixtureSource": probe.get_attribute("data-fixture-source"),
                        "invariantId": probe.get_attribute("data-invariant-id"),
                        "networkResponses": network_responses[-12:],
                        "observedStatus": observed,
                        "route": probe.get_attribute("data-route"),
                        "selector": f"[data-bayesilisk-probe] >> nth={index}",
                        "source": probe.get_attribute("data-source"),
                        "targetUrl": url,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "title": probe.get_attribute("data-title"),
                    }
                )
                if step_delay_ms:
                    page.wait_for_timeout(step_delay_ms)
            if hold_ms:
                page.wait_for_timeout(hold_ms)
        finally:
            browser.close()
    return results


def fallback_probe_results(url: str) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "actorRole": probe["actorRole"],
            "domain": probe["domain"],
            "expectedStatus": probe["expectedStatus"],
            "failureDetail": "deterministic local fallback; Playwright not used",
            "fixtureId": probe["fixtureId"],
            "fixtureSource": DEMO_FIXTURE_SOURCE,
            "invariantId": probe["invariantId"],
            "networkResponses": [{"status": int(probe["actualStatus"]), "url": f"{url}{probe['route'].lstrip('/')}"}],
            "observedStatus": probe["actualStatus"],
            "route": probe["route"],
            "selector": f"demo-probe-{index}",
            "source": probe["source"],
            "targetUrl": url,
            "timestamp": timestamp,
            "title": probe["title"],
        }
        for index, probe in enumerate(DEMO_PROBES, start=1)
    ]


def canned_model_proposal(attention: dict[str, Any]) -> dict[str, Any]:
    selected = [plane for plane in attention.get("selectedPlaneIds", []) if isinstance(plane, str)]
    generated = attention_composite_scenarios(selected, 1)
    if generated:
        scenario = generated[0]
        target = selected[0]
        return {
            "fragments": list(scenario.fragment_ids),
            "invariants": list(scenario.invariant_ids),
            "targetPlane": target,
            "title": f"Canned model-style proposal: {scenario.title}",
        }
    return {
        "fragments": ["role.finance", "module.expenses_off", "route.expense_approve", "expense.receipt_missing"],
        "invariants": ["modules.expense_approval_requires_module_and_receipt"],
        "targetPlane": "modules.expense_approval_requires_module_and_receipt",
        "title": "Canned model-style proposal: disabled module still approves an expense",
    }


def classification_counts(findings: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for finding in findings:
        classification = str(finding.get("classification", "unknown"))
        counts[classification] = counts.get(classification, 0) + 1
    return dict(sorted(counts.items()))


def demo_chain(report: dict[str, Any], model_proposal: dict[str, Any], *, seed: int) -> dict[str, Any]:
    attention = report["grassmannAttention"]
    provider = {
        "baseUrlClass": "not-used",
        "modelName": "canned-local-demo",
        "promptHash": "local-demo",
        "promptVersion": SCENARIO_PROPOSER_PROMPT_VERSION,
        "provider": "demo-canned",
        "source": "local-demo-fixture",
        "sourceContext": attention.get("source", "none"),
    }
    bad_proposal = {
        "fragments": ["workflow.step_ordering.unknown"],
        "invariants": ["workflow.impossible_step_order"],
        "targetPlane": "workflow.impossible_step_order",
        "title": "Canned rejected proposal: invented wizard invariant",
    }
    accepted, rejected = validate_model_scenario_proposals(
        [model_proposal, bad_proposal],
        attention,
        provider=provider,
    )
    model_report = build_report(
        seed,
        generated_count=max(1, len(accepted)),
        grassmann={**attention, "selectedPlaneIds": []},
        limit=None,
        model_scenarios=accepted,
    )
    model_findings = [
        finding
        for finding in model_report["findings"]
        if isinstance(finding.get("generationBasis"), str)
        and finding["generationBasis"].startswith("weak-model-proposal:")
    ]
    payloads = issue_payloads(report, limit=1)
    verdict = next((finding for finding in report["findings"] if finding["observedResult"] == "fail"), report["findings"][0])
    return {
        "deterministicVerdict": {
            "classification": verdict["classification"],
            "invariantId": verdict["invariantId"],
            "observedResult": verdict["observedResult"],
            "riskScore": verdict["riskScore"],
            "scenarioId": verdict["scenarioId"],
        },
        "grassmannPlane": report["selectedByGrassmannAttention"][0] if report["selectedByGrassmannAttention"] else {},
        "issuePayload": payloads[0] if payloads else {},
        "modelProposal": {
            "acceptedCount": len(accepted),
            "acceptedScenarioIds": [scenario.id for scenario in accepted],
            "deterministicFindingCount": len(model_findings),
            "deterministicResultCounts": classification_counts(model_findings),
            "mode": "canned-local-optional",
            "rejectedCount": len(rejected),
            "rejectedReasons": [item["reason"] for item in rejected],
        },
        "playwrightEvidence": report["observedByPlaywright"][0] if report["observedByPlaywright"] else {},
        "reportSummary": {
            "classificationCounts": classification_counts(report["findings"]),
            "findingCount": len(report["findings"]),
            "generatedScenarioCount": report["generatedScenarioCount"],
            "invariantCount": len(report["invariants"]),
            "rankedProbeCount": len(report.get("rankedProbes", [])),
        },
    }


def explain_status_delta(expected: Any, observed: Any) -> str:
    try:
        expected_status = int(expected)
        observed_status = int(observed)
    except (TypeError, ValueError):
        return "status evidence was malformed; normalized before use"
    if expected_status == observed_status:
        return "control matched expectation"
    if expected_status == 409 and 200 <= observed_status < 300:
        return "workflow should reject inconsistent state, but the app accepted it"
    if expected_status == 403 and 200 <= observed_status < 300:
        return "role/module boundary should deny access, but the app allowed it"
    if expected_status >= 400 and 200 <= observed_status < 300:
        return "negative-path guard expected an error, but the app returned success"
    return f"expected HTTP {expected_status}, observed HTTP {observed_status}"


def evidence_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for fact in report.get("observedByPlaywright", []):
        expected = fact.get("expectedStatus")
        observed = fact.get("observedStatus")
        rows.append(
            {
                "actorRole": fact.get("actorRole", "unknown"),
                "expectedStatus": expected,
                "invariantId": fact.get("invariantId", "unknown"),
                "observedStatus": observed,
                "passed": fact.get("passed") is True,
                "route": fact.get("route", "unknown"),
                "title": fact.get("title", "Observed probe"),
                "whyItMatters": explain_status_delta(expected, observed),
            }
        )
    return rows


def run_demo(args: argparse.Namespace) -> dict[str, Any]:
    if args.no_playwright:
        url = "http://127.0.0.1/local-bayesilisk-demo/"
        mode = "fallback: Playwright disabled by --no-playwright"
        results = fallback_probe_results(url)
    else:
        with demo_server() as url:
            mode = "playwright"
            try:
                results = run_playwright_probe(
                    url,
                    headless=not args.headed,
                    hold_ms=args.hold_seconds * 1000,
                    step_delay_ms=args.step_delay_ms,
                    timeout_ms=max(1000, args.timeout_ms),
                )
            except RuntimeError as exc:
                mode = f"fallback: {exc}"
                results = fallback_probe_results(url)

    context = build_context_from_probe_results(results, source="bayesilisk-demo", target=url)
    runtime_config = {"enableScenarioProposer": bool(args.enable_scenario_proposer)}
    report = build_contextual_report(
        args.seed,
        context=context,
        generated_count=args.generated_count,
        limit=args.limit,
        runtime_config=runtime_config,
    )
    model_proposal = canned_model_proposal(report["grassmannAttention"])
    return {
        "appUrl": url,
        "chain": demo_chain(report, model_proposal, seed=args.seed),
        "classificationLegend": CLASSIFICATION_LEGEND,
        "demo": "workflow-pressure",
        "evidence": evidence_rows(report),
        "fixtureKind": DEMO_FIXTURE_KIND,
        "fixtureSource": DEMO_FIXTURE_SOURCE,
        "playwrightMode": mode,
        "playwrightProbe": context["playwrightProbe"],
        "recordingCommand": "bayesilisk-demo --recording",
        "tool": VERSION,
    }


def render_text(payload: dict[str, Any]) -> str:
    chain = payload["chain"]
    issue = chain["issuePayload"]
    summary = chain["reportSummary"]
    verdict = chain["deterministicVerdict"]
    evidence = payload.get("evidence", [])
    failed = [row for row in evidence if not row.get("passed")]
    passed = [row for row in evidence if row.get("passed")]
    lines = [
        "Bayesilisk local workflow pressure demo",
        "",
        "Fixture provenance:",
        f"- kind: {payload['fixtureKind']}",
        f"- source: {payload['fixtureSource']}",
        "- these workflows are synthetic local fixtures, not claims about an existing app",
        "- to test a real app, instrument its page with data-bayesilisk-probe rows and run tools/playwright_probe.py --url <url>",
        "",
        "What this proves:",
        "- Playwright is only the sensor: it clicks a local fixture or caller-provided app and records expected vs observed status.",
        "- Grassmann attention is only the router: it selects where to spend verifier budget.",
        "- Catalog and attention-generated scenarios expand the search space beyond the seeded browser clicks.",
        "- The scenario proposer lane is not trusted: one local model-style proposal is accepted, one invented target is rejected.",
        "- Bayesilisk is the judge: deterministic invariants produce the verdict and issue payload.",
        "",
        "Scale of this local run:",
        (
            f"- browser fixtures: {payload['playwrightProbe']['resultCount']} user actions "
            f"({payload['playwrightProbe']['failedCount']} failing, {payload['playwrightProbe']['passedCount']} controls)"
        ),
        f"- deterministic rules: {summary['invariantCount']} invariants",
        f"- generated scenarios: {summary['generatedScenarioCount']} catalog/attention composites",
        f"- ranked findings inspected: {summary['findingCount']} with {summary['classificationCounts']}",
        f"- ranked follow-up probes: {summary['rankedProbeCount']}",
        "",
        f"App: {payload['appUrl']}",
        (
            "Browser evidence: "
            f"{payload['playwrightMode']} observed {payload['playwrightProbe']['failedCount']} failing probes "
            f"out of {payload['playwrightProbe']['resultCount']}."
        ),
    ]
    for index, row in enumerate(failed[:5], start=1):
        lines.append(
            "  "
            f"{index}. {row['title']} | actor={row['actorRole']} | route={row['route']} | "
            f"expected={row['expectedStatus']} observed={row['observedStatus']} | invariant={row['invariantId']}"
        )
        lines.append(f"     meaning: {row['whyItMatters']}")
    if passed:
        lines.append("  controls:")
        for row in passed[:3]:
            lines.append(
                "     "
                f"{row['title']} | actor={row['actorRole']} | expected={row['expectedStatus']} "
                f"observed={row['observedStatus']}"
            )
    lines.extend(
        [
            "",
            "Classification legend:",
            *[
                f"  {classification}: {meaning}"
                for classification, meaning in sorted(payload["classificationLegend"].items())
            ],
            "",
            "Attention routing:",
            (
                "  selected="
                f"{chain['grassmannPlane'].get('invariantId', 'none')} "
                f"score={chain['grassmannPlane'].get('attentionScore', 0)}"
            ),
            "  reasons=" + ", ".join(chain["grassmannPlane"].get("reasons", [])),
            "",
            "Untrusted proposal lane:",
            (
                "  "
                f"{chain['modelProposal']['mode']} accepted={chain['modelProposal']['acceptedCount']} "
                f"rejected={chain['modelProposal']['rejectedCount']} "
                f"rejectedReasons={chain['modelProposal']['rejectedReasons']}"
            ),
            (
                "  acceptedScenarioIds="
                + ", ".join(chain["modelProposal"].get("acceptedScenarioIds", []))
            ),
            (
                "  deterministicChecksOnAcceptedProposal="
                f"{chain['modelProposal']['deterministicFindingCount']} findings "
                f"{chain['modelProposal']['deterministicResultCounts']}"
            ),
            "  Accepted proposals still have to pass schema/id validation and deterministic invariant checks.",
            "",
            "Deterministic verdict:",
            (
                "  "
                f"{verdict['observedResult']} {verdict['classification']} "
                f"invariant={verdict['invariantId']} risk={verdict['riskScore']}"
            ),
            f"  scenario={verdict['scenarioId']}",
            "  classificationMeaning="
            + payload["classificationLegend"].get(verdict["classification"], "No definition available."),
            "",
            "Issue-ready output:",
            f"  title={issue.get('title', 'none')}",
            f"  fingerprint={issue.get('fingerprint', 'none')}",
            f"  dedupeState={issue.get('dedupeState', 'none')}",
            "",
            "Recording command:",
            f"  {payload['recordingCommand']}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local Bayesilisk workflow pressure demo.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable demo output.")
    parser.add_argument("--seed", type=int, default=150, help="Deterministic report seed.")
    parser.add_argument("--generated-count", type=int, default=8, help="Generated scenario count.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum findings included in the demo report.")
    parser.add_argument("--no-playwright", action="store_true", help="Use deterministic local probe evidence instead of launching Chromium.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
    parser.add_argument(
        "--recording",
        action="store_true",
        help="Open headed Chromium, slow probe clicks, and hold the browser briefly for screen recording.",
    )
    parser.add_argument("--hold-seconds", type=int, default=0, help="Seconds to keep headed Chromium open after probes.")
    parser.add_argument("--step-delay-ms", type=int, default=0, help="Delay between browser probe clicks.")
    parser.add_argument("--timeout-ms", type=int, default=5000, help="Per-navigation and per-probe timeout in ms.")
    parser.add_argument("--enable-scenario-proposer", action="store_true", help="Also call the configured scenario proposer provider.")
    args = parser.parse_args()
    if args.recording:
        args.headed = True
        args.step_delay_ms = max(args.step_delay_ms, 450)
        args.hold_seconds = max(args.hold_seconds, 10)
    return args


def main() -> int:
    args = parse_args()
    payload = run_demo(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
