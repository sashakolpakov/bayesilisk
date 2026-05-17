from __future__ import annotations

import argparse
import json
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from .constants import VERSION
from .playwright_adapter import build_context_from_probe_results
from .reporting import build_contextual_report, issue_payloads


PROBE_SOURCE = "bayesilisk/realistic_demo.py::REALISTIC_PROBES"


REALISTIC_PROBES: tuple[dict[str, Any], ...] = (
    {
        "id": "hr-support-active-shortcut",
        "title": "Support takeover reaches HR document",
        "actorRole": "support",
        "expectedStatus": 403,
        "invariantId": "hr.documents_customer_role_boundary",
        "route": "/api/hr/documents",
        "request": {
            "actor": "sara-support",
            "documentTenant": "acme",
            "route": "/api/hr/documents",
            "takeover": "active",
            "targetEmployee": "emp-002",
            "tenant": "acme",
        },
        "why": "Support has a takeover session, but that must not become a customer HR role.",
    },
    {
        "id": "hr-manager-control",
        "title": "HR manager reaches HR document",
        "actorRole": "hr_manager",
        "expectedStatus": 200,
        "invariantId": "hr.documents_customer_role_boundary",
        "route": "/api/hr/documents",
        "request": {
            "actor": "helen-hr",
            "documentTenant": "acme",
            "route": "/api/hr/documents",
            "targetEmployee": "emp-002",
            "tenant": "acme",
        },
        "why": "Control: customer HR should be allowed to read an HR document.",
    },
    {
        "id": "billing-disabled-preview-export",
        "title": "Finance exports billing with module disabled",
        "actorRole": "finance",
        "expectedStatus": 403,
        "invariantId": "billing.export_requires_role_and_module",
        "route": "/api/billing/exports",
        "request": {
            "actor": "fran-finance",
            "exportMode": "preview",
            "route": "/api/billing/exports",
            "tenant": "beta",
        },
        "why": "Finance role is not enough when the billing module is disabled for the tenant.",
    },
    {
        "id": "billing-finance-control",
        "title": "Finance exports billing with module enabled",
        "actorRole": "finance",
        "expectedStatus": 200,
        "invariantId": "billing.export_requires_role_and_module",
        "route": "/api/billing/exports",
        "request": {
            "actor": "fran-finance",
            "exportMode": "full",
            "route": "/api/billing/exports",
            "tenant": "acme",
        },
        "why": "Control: finance plus billing entitlement should export.",
    },
    {
        "id": "employee-self-review",
        "title": "Employee approves own expense through manager hint",
        "actorRole": "employee",
        "expectedStatus": 403,
        "invariantId": "roles.employee_self_review_forbidden",
        "route": "/api/expense-claims/{claimId}/review",
        "request": {
            "actor": "erin-employee",
            "claimOwner": "emp-001",
            "decision": "approve",
            "managerHint": True,
            "receiptStatus": "approved",
            "route": "/api/expense-claims/{claimId}/review",
            "tenant": "acme",
        },
        "why": "A UI hint must not turn an employee into their own manager.",
    },
    {
        "id": "manager-expense-control",
        "title": "Manager approves employee expense with receipt",
        "actorRole": "manager",
        "expectedStatus": 200,
        "invariantId": "modules.expense_approval_requires_module_and_receipt",
        "route": "/api/expense-claims/{claimId}/review",
        "request": {
            "actor": "marta-manager",
            "claimOwner": "emp-002",
            "decision": "approve",
            "receiptStatus": "approved",
            "route": "/api/expense-claims/{claimId}/review",
            "tenant": "acme",
        },
        "why": "Control: manager, enabled expenses module, and approved receipt should pass.",
    },
    {
        "id": "foreign-tenant-receipt",
        "title": "Foreign tenant DMS receipt is accepted",
        "actorRole": "finance",
        "expectedStatus": 403,
        "invariantId": "dms.tenant_process_boundary",
        "route": "/api/dms/documents",
        "request": {
            "actor": "fran-finance",
            "documentProcess": "travel_expense",
            "documentTenant": "beta",
            "route": "/api/dms/documents",
            "tenant": "acme",
        },
        "why": "Receipt documents must not cross tenant boundaries.",
    },
    {
        "id": "expired-support-takeover",
        "title": "Expired support takeover is denied",
        "actorRole": "support",
        "expectedStatus": 403,
        "invariantId": "support.takeover_session_required",
        "route": "/api/support/takeover/expense-review",
        "request": {
            "actor": "sara-support",
            "route": "/api/support/takeover/expense-review",
            "takeover": "expired",
            "tenant": "acme",
        },
        "why": "Control: expired takeover should be denied.",
    },
)


USERS: dict[str, dict[str, str]] = {
    "erin-employee": {"employeeId": "emp-001", "role": "employee"},
    "fran-finance": {"employeeId": "emp-fin", "role": "finance"},
    "helen-hr": {"employeeId": "emp-hr", "role": "hr_manager"},
    "marta-manager": {"employeeId": "emp-manager", "role": "manager"},
    "sara-support": {"employeeId": "emp-support", "role": "support"},
}

TENANT_MODULES: dict[str, dict[str, bool]] = {
    "acme": {"billing": True, "expenses": True, "hr": True, "travel": True},
    "beta": {"billing": False, "expenses": True, "hr": True, "travel": False},
}


def realistic_status(probe: dict[str, Any]) -> int:
    request = probe["request"]
    actor = USERS[request["actor"]]
    role = actor["role"]
    route = request["route"]
    modules = TENANT_MODULES[request["tenant"]]

    if route == "/api/hr/documents":
        if role in {"admin", "hr_manager", "owner"} and request["documentTenant"] == request["tenant"]:
            return 200
        if role == "support" and request.get("takeover") == "active":
            return 200  # Intentional bug: takeover bypasses customer HR role.
        return 403

    if route == "/api/billing/exports":
        if role not in {"admin", "finance", "owner"}:
            return 403
        if modules.get("billing"):
            return 200
        if request.get("exportMode") == "preview":
            return 200  # Intentional bug: preview path skips module entitlement.
        return 403

    if route == "/api/expense-claims/{claimId}/review":
        if not modules.get("expenses"):
            return 403
        if request.get("receiptStatus") != "approved":
            return 403
        if actor["employeeId"] == request.get("claimOwner"):
            if request.get("managerHint"):
                return 200  # Intentional bug: UI hint is trusted as authorization.
            return 403
        if role in {"admin", "finance", "manager", "owner"}:
            return 200
        return 403

    if route == "/api/dms/documents":
        if request.get("documentTenant") == request["tenant"] and request.get("documentProcess") == "travel_expense":
            return 200
        if role == "finance" and request.get("documentProcess") == "travel_expense":
            return 200  # Intentional bug: finance can attach a foreign tenant receipt.
        return 403

    if route == "/api/support/takeover/expense-review":
        if role == "support" and request.get("takeover") == "active":
            return 200
        return 403

    return 404


def probe_page() -> str:
    rows = []
    for probe in REALISTIC_PROBES:
        rows.append(
            f"""
            <tr
              data-bayesilisk-probe
              data-title="{probe['title']}"
              data-actor-role="{probe['actorRole']}"
              data-route="{probe['route']}"
              data-invariant-id="{probe['invariantId']}"
              data-expected-status="{probe['expectedStatus']}"
            >
              <td>{probe['title']}</td>
              <td><code>{probe['actorRole']}</code></td>
              <td><code>{probe['route']}</code></td>
              <td>{probe['why']}</td>
              <td><code>{probe['expectedStatus']}</code></td>
              <td><code data-observed-status>pending</code></td>
              <td><button type="button" data-run-probe data-probe-id="{probe['id']}">Run</button></td>
            </tr>
            """
        )
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Bayesilisk Realistic App Probe Harness</title>
    <style>
      :root {{
        color-scheme: light;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.45;
      }}
      body {{
        margin: 0;
        background: #f6f7f9;
        color: #182233;
      }}
      main {{
        margin: 0 auto;
        max-width: 1320px;
        padding: 28px 20px 44px;
      }}
      h1 {{
        font-size: 28px;
        margin: 0 0 8px;
      }}
      p {{
        color: #566273;
        margin: 0 0 18px;
      }}
      table {{
        background: #fff;
        border: 1px solid #d8dee8;
        border-collapse: collapse;
        width: 100%;
      }}
      th, td {{
        border-bottom: 1px solid #e6eaf1;
        padding: 10px;
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
        background: #155f88;
        border: 0;
        border-radius: 6px;
        color: #fff;
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
      <h1>Realistic Permission Probe Harness</h1>
      <p>
        This is a small local app with users, tenants, module flags, support takeover state,
        HR documents, DMS receipts, and expense approvals. Buttons call real local permission
        handlers; Playwright only records expected versus observed status.
      </p>
      <table aria-label="Realistic app Bayesilisk probes">
        <thead>
          <tr>
            <th>Probe</th>
            <th>Actor</th>
            <th>Route</th>
            <th>Rule intent</th>
            <th>Expected</th>
            <th>Observed</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </main>
    <script>
      for (const button of document.querySelectorAll("[data-run-probe]")) {{
        button.addEventListener("click", async () => {{
          const row = button.closest("[data-bayesilisk-probe]");
          const response = await fetch(`/internal/run-probe?id=${{encodeURIComponent(button.dataset.probeId)}}`);
          row.querySelector("[data-observed-status]").textContent = String(response.status);
        }});
      }}
    </script>
  </body>
</html>
"""


class RealisticHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/internal/bayesilisk-probes"}:
            body = probe_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/internal/run-probe":
            probe_id = parse_qs(parsed.query).get("id", [""])[0]
            probe = next((item for item in REALISTIC_PROBES if item["id"] == probe_id), None)
            status = realistic_status(probe) if probe else 404
            body = json.dumps({"probe": probe_id, "status": status}).encode("utf-8")
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
def realistic_server() -> Any:
    server = ThreadingHTTPServer(("127.0.0.1", 0), RealisticHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/internal/bayesilisk-probes"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def fallback_results(target: str) -> list[dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    return [
        {
            "actorRole": probe["actorRole"],
            "expectedStatus": probe["expectedStatus"],
            "failureDetail": "local permission handler fallback; Playwright not used",
            "invariantId": probe["invariantId"],
            "networkResponses": [{"status": realistic_status(probe), "url": f"{target}#{probe['id']}"}],
            "observedStatus": realistic_status(probe),
            "route": probe["route"],
            "selector": f"realistic-probe-{index}",
            "targetUrl": target,
            "timestamp": timestamp,
            "title": probe["title"],
        }
        for index, probe in enumerate(REALISTIC_PROBES)
    ]


def run_browser_probe(url: str, *, headless: bool, hold_ms: int, step_delay_ms: int, timeout_ms: int) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright is not installed; rerun with --no-playwright.") from exc

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
                if step_delay_ms:
                    page.wait_for_timeout(step_delay_ms)
            if hold_ms:
                page.wait_for_timeout(hold_ms)
        finally:
            browser.close()
    return results


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for finding in report["findings"]:
        counts[finding["classification"]] = counts.get(finding["classification"], 0) + 1
    return {
        "classificationCounts": dict(sorted(counts.items())),
        "findingCount": len(report["findings"]),
        "issuePayloadCount": len(report.get("issuePayloads", [])),
        "rankedProbeCount": len(report.get("rankedProbes", [])),
    }


def run_demo(args: argparse.Namespace) -> dict[str, Any]:
    if args.no_playwright:
        target = "http://127.0.0.1/realistic-app/internal/bayesilisk-probes"
        mode = "fallback: local permission handlers without browser"
        results = fallback_results(target)
    else:
        with realistic_server() as target:
            mode = "playwright"
            try:
                results = run_browser_probe(
                    target,
                    headless=not args.headed,
                    hold_ms=args.hold_seconds * 1000,
                    step_delay_ms=args.step_delay_ms,
                    timeout_ms=max(1000, args.timeout_ms),
                )
            except RuntimeError as exc:
                mode = f"fallback: {exc}"
                results = fallback_results(target)

    context = build_context_from_probe_results(results, source="realistic-app-demo", target=target)
    if args.context_output:
        args.context_output.parent.mkdir(parents=True, exist_ok=True)
        args.context_output.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = build_contextual_report(args.seed, context=context, generated_count=args.generated_count, limit=args.limit)
    report["issuePayloads"] = issue_payloads(report, limit=3)
    return {
        "contextOutput": str(args.context_output) if args.context_output else None,
        "demo": "realistic-app-permission-harness",
        "mode": mode,
        "probeCount": context["playwrightProbe"]["resultCount"],
        "probeFailures": context["playwrightProbe"]["failedCount"],
        "probePasses": context["playwrightProbe"]["passedCount"],
        "reportSummary": summarize(report),
        "target": target,
        "tool": VERSION,
        "topFindings": [
            {
                "classification": finding["classification"],
                "invariantId": finding["invariantId"],
                "issueReadiness": finding["issueReadiness"],
                "observation": finding["observation"],
                "riskScore": finding["riskScore"],
                "scenarioId": finding["scenarioId"],
            }
            for finding in report["findings"][:5]
        ],
    }


def render_text(payload: dict[str, Any]) -> str:
    lines = [
        "Bayesilisk realistic app integration demo",
        "",
        "What is real here:",
        "- the app exposes /internal/bayesilisk-probes with data-bayesilisk-probe rows",
        "- each button calls a local permission handler with users, tenants, modules, takeover state, and documents",
        "- Playwright records expected versus observed status; Bayesilisk turns that into context",
        "- Bayesilisk expands the scenario space and checks deterministic invariants",
        "",
        f"Target: {payload['target']}",
        f"Mode: {payload['mode']}",
        f"Probe harness: {payload['probeFailures']} failing observations, {payload['probePasses']} controls, {payload['probeCount']} total",
        f"Verifier findings: {payload['reportSummary']['findingCount']} ranked findings {payload['reportSummary']['classificationCounts']}",
        f"Issue payloads: {payload['reportSummary']['issuePayloadCount']}",
        "",
        "Top deterministic findings:",
    ]
    for index, finding in enumerate(payload["topFindings"], start=1):
        lines.append(
            "  "
            f"{index}. {finding['classification']} | {finding['invariantId']} | "
            f"risk={finding['riskScore']} | {finding['issueReadiness']}"
        )
        lines.append(f"     scenario={finding['scenarioId']}")
        lines.append(f"     observed={finding['observation']}")
    if payload["contextOutput"]:
        lines.extend(["", f"Context written to: {payload['contextOutput']}"])
    lines.extend(
        [
            "",
            "Equivalent real-app flow:",
            "  python3 tools/playwright_probe.py --url http://localhost:3000/internal/bayesilisk-probes --output /tmp/bayesilisk-context.json --headed --screenshot --trace --artifacts-dir /tmp/bayesilisk-artifacts",
            "  python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --format markdown",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the realistic local app permission harness demo.")
    parser.add_argument("--context-output", type=Path, default=None, help="Write captured Bayesilisk context JSON.")
    parser.add_argument("--generated-count", type=int, default=8, help="Generated scenario count.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
    parser.add_argument("--hold-seconds", type=int, default=0, help="Seconds to hold headed Chromium open after probes.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable demo output.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum findings included in the report.")
    parser.add_argument("--no-playwright", action="store_true", help="Use local permission handlers without launching Chromium.")
    parser.add_argument("--recording", action="store_true", help="Open headed Chromium, slow clicks, and hold for recording.")
    parser.add_argument("--seed", type=int, default=150, help="Deterministic report seed.")
    parser.add_argument("--serve-only", action="store_true", help="Serve the realistic probe app and print its URL.")
    parser.add_argument("--step-delay-ms", type=int, default=0, help="Delay between browser probe clicks.")
    parser.add_argument("--timeout-ms", type=int, default=5000, help="Per-navigation and per-probe timeout in ms.")
    args = parser.parse_args()
    if args.recording:
        args.headed = True
        args.step_delay_ms = max(args.step_delay_ms, 450)
        args.hold_seconds = max(args.hold_seconds, 10)
    return args


def main() -> int:
    args = parse_args()
    if args.serve_only:
        with realistic_server() as target:
            print("Bayesilisk realistic probe app")
            print(f"URL: {target}")
            print("Run from another terminal:")
            print(f"  python3 tools/playwright_probe.py --url {target} --output /tmp/bayesilisk-context.json --headed")
            print("  python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --format markdown")
            try:
                while True:
                    time.sleep(3600)
            except KeyboardInterrupt:
                return 0
    payload = run_demo(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_text(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
