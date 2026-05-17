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
from .reporting import build_contextual_report, issue_payloads


DEMO_PROBES: tuple[dict[str, str], ...] = (
    {
        "actorRole": "manager",
        "actualStatus": "200",
        "expectedStatus": "409",
        "invariantId": "travel.funding_before_expense",
        "route": "/demo/wizard/expense-review",
        "title": "Wizard accepts expense review before travel funding approval",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "expectedStatus": "409",
        "invariantId": "travel.expense_items_match_itinerary",
        "route": "/demo/checkout/review",
        "title": "Checkout review accepts itinerary and expense mismatch",
    },
    {
        "actorRole": "employee",
        "actualStatus": "200",
        "expectedStatus": "409",
        "invariantId": "modules.expense_approval_requires_module_and_receipt",
        "route": "/demo/retry/expense-submit",
        "title": "Retry after back navigation creates duplicate submission",
    },
    {
        "actorRole": "support",
        "actualStatus": "200",
        "expectedStatus": "403",
        "invariantId": "hr.documents_customer_role_boundary",
        "route": "/api/hr/documents",
        "title": "Support actor reaches HR document route",
    },
    {
        "actorRole": "finance",
        "actualStatus": "200",
        "expectedStatus": "403",
        "invariantId": "billing.export_requires_role_and_module",
        "route": "/api/billing/exports",
        "title": "Feature flag off but billing export path remains exposed",
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
              data-route="{probe['route']}"
              data-invariant-id="{probe['invariantId']}"
              data-expected-status="{probe['expectedStatus']}"
              data-actual-status="{probe['actualStatus']}"
              data-api-path="/api/probe/{index}"
            >
              <td>{probe['title']}</td>
              <td><code>{probe['actorRole']}</code></td>
              <td><code>{probe['route']}</code></td>
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
        max-width: 1120px;
        padding: 28px 20px 44px;
      }}
      h1 {{
        font-size: 28px;
        margin: 0 0 8px;
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
        padding: 11px 12px;
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
      <p>
        Local brittle product workflows: stale state, impossible ordering, duplicate submission,
        feature-flag exposure, and one auth lane. The browser observes behavior; Bayesilisk judges it.
      </p>
      <table aria-label="Bayesilisk workflow pressure probes">
        <thead>
          <tr>
            <th>Scenario pressure</th>
            <th>Actor</th>
            <th>Route or workflow</th>
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


def run_playwright_probe(url: str, *, headless: bool, timeout_ms: int) -> list[dict[str, Any]]:
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
                        "expectedStatus": probe.get_attribute("data-expected-status"),
                        "failureDetail": "",
                        "invariantId": probe.get_attribute("data-invariant-id"),
                        "networkResponses": network_responses[-12:],
                        "observedStatus": observed,
                        "route": probe.get_attribute("data-route"),
                        "selector": f"[data-bayesilisk-probe] >> nth={index}",
                        "targetUrl": url,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "title": probe.get_attribute("data-title"),
                    }
                )
        finally:
            browser.close()
    return results


def fallback_probe_results(url: str) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "actorRole": probe["actorRole"],
            "expectedStatus": probe["expectedStatus"],
            "failureDetail": "deterministic local fallback; Playwright not used",
            "invariantId": probe["invariantId"],
            "networkResponses": [{"status": int(probe["actualStatus"]), "url": f"{url}{probe['route'].lstrip('/')}"}],
            "observedStatus": probe["actualStatus"],
            "route": probe["route"],
            "selector": f"demo-probe-{index}",
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


def demo_chain(report: dict[str, Any], model_proposal: dict[str, Any]) -> dict[str, Any]:
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
            "mode": "canned-local-optional",
            "rejectedCount": len(rejected),
            "rejectedReasons": [item["reason"] for item in rejected],
        },
        "playwrightEvidence": report["observedByPlaywright"][0] if report["observedByPlaywright"] else {},
    }


def run_demo(args: argparse.Namespace) -> dict[str, Any]:
    if args.no_playwright:
        url = "http://127.0.0.1/local-bayesilisk-demo/"
        mode = "fallback: Playwright disabled by --no-playwright"
        results = fallback_probe_results(url)
    else:
        with demo_server() as url:
            mode = "playwright"
            try:
                results = run_playwright_probe(url, headless=not args.headed, timeout_ms=max(1000, args.timeout_ms))
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
        "chain": demo_chain(report, model_proposal),
        "demo": "workflow-pressure",
        "playwrightMode": mode,
        "playwrightProbe": context["playwrightProbe"],
        "tool": VERSION,
    }


def render_text(payload: dict[str, Any]) -> str:
    chain = payload["chain"]
    issue = chain["issuePayload"]
    return "\n".join(
        [
            "Bayesilisk local workflow pressure demo",
            f"App: {payload['appUrl']}",
            f"Playwright evidence: {payload['playwrightMode']} with {payload['playwrightProbe']['failedCount']} mismatches",
            f"Grassmann plane: {chain['grassmannPlane'].get('invariantId', 'none')}",
            (
                "Model proposal: "
                f"{chain['modelProposal']['mode']} accepted={chain['modelProposal']['acceptedCount']} "
                f"rejected={chain['modelProposal']['rejectedCount']}"
            ),
            (
                "Deterministic verdict: "
                f"{chain['deterministicVerdict']['observedResult']} "
                f"{chain['deterministicVerdict']['classification']} "
                f"{chain['deterministicVerdict']['invariantId']}"
            ),
            f"Issue payload: {issue.get('title', 'none')}",
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local Bayesilisk workflow pressure demo.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable demo output.")
    parser.add_argument("--seed", type=int, default=150, help="Deterministic report seed.")
    parser.add_argument("--generated-count", type=int, default=8, help="Generated scenario count.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum findings included in the demo report.")
    parser.add_argument("--no-playwright", action="store_true", help="Use deterministic local probe evidence instead of launching Chromium.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
    parser.add_argument("--timeout-ms", type=int, default=5000, help="Per-navigation and per-probe timeout in ms.")
    parser.add_argument("--enable-scenario-proposer", action="store_true", help="Also call the configured scenario proposer provider.")
    return parser.parse_args()


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
