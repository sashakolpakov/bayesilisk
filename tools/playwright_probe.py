#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bayesilisk.playwright_adapter import artifact_path, build_context_from_probe_results


def demo_url() -> str:
    return (REPO_ROOT / "demo" / "playwright_target.html").resolve().as_uri()


def run_browser_probe(
    url: str,
    *,
    artifacts_dir: Path | None = None,
    headless: bool = True,
    retries: int = 0,
    screenshot: bool = False,
    timeout_ms: int = 5000,
    trace: bool = False,
) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Microsoft Playwright is not installed. Install with "
            "`python3 -m pip install -e '.[playwright]'` and then run "
            "`python3 -m playwright install chromium`."
        ) from exc

    results: list[dict[str, Any]] = []
    if artifacts_dir is not None:
        artifacts_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            network_responses: list[dict[str, Any]] = []
            page.on(
                "response",
                lambda response: network_responses.append(
                    {
                        "status": response.status,
                        "url": response.url,
                    }
                ),
            )
            if trace and artifacts_dir is not None:
                page.context.tracing.start(screenshots=True, snapshots=True, sources=True)
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            probes = page.locator("[data-bayesilisk-probe]")
            count = probes.count()
            for index in range(count):
                probe = probes.nth(index)
                selector = f"[data-bayesilisk-probe] >> nth={index}"
                artifact_paths: list[str] = []
                failure_detail = ""
                observed = ""
                for attempt in range(retries + 1):
                    try:
                        probe.locator("[data-run-probe]").click(timeout=timeout_ms)
                        observed = probe.locator("[data-observed-status]").inner_text(timeout=timeout_ms).strip()
                        break
                    except Exception as exc:
                        failure_detail = f"attempt {attempt + 1} failed: {exc}"
                        if attempt >= retries:
                            observed = ""
                expected_status = probe.get_attribute("data-expected-status")
                if screenshot and artifacts_dir is not None:
                    screenshot_path = artifact_path(artifacts_dir, index, "screenshot.png")
                    probe.screenshot(path=screenshot_path)
                    artifact_paths.append(screenshot_path)
                results.append(
                    {
                        "actorRole": probe.get_attribute("data-actor-role"),
                        "artifactPaths": artifact_paths,
                        "expectedStatus": expected_status,
                        "failureDetail": failure_detail,
                        "invariantId": probe.get_attribute("data-invariant-id"),
                        "networkResponses": network_responses[-12:],
                        "observedStatus": observed,
                        "route": probe.get_attribute("data-route"),
                        "selector": selector,
                        "targetUrl": url,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "title": probe.get_attribute("data-title"),
                    }
                )
            if trace and artifacts_dir is not None:
                trace_path = artifacts_dir / "trace.zip"
                page.context.tracing.stop(path=str(trace_path))
                for result in results:
                    result.setdefault("artifactPaths", []).append(str(trace_path))
        finally:
            browser.close()
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bayesilisk route probes through Microsoft Playwright.")
    parser.add_argument("--url", default=None, help="Target URL with Bayesilisk probe elements.")
    parser.add_argument("--demo", action="store_true", help="Use the bundled static demo target.")
    parser.add_argument("--output", type=Path, default=None, help="Write Bayesilisk context JSON to this path.")
    parser.add_argument("--artifacts-dir", type=Path, default=None, help="Directory for screenshots and traces.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
    parser.add_argument("--retries", type=int, default=0, help="Probe retry count after a probe-level failure.")
    parser.add_argument("--screenshot", action="store_true", help="Capture a screenshot for each probe.")
    parser.add_argument("--timeout-ms", type=int, default=5000, help="Per-navigation and per-probe timeout in ms.")
    parser.add_argument("--trace", action="store_true", help="Capture a Playwright trace.zip artifact.")
    parser.add_argument(
        "--fail-on-target-failure",
        action="store_true",
        help="Exit 1 when the target has an observed permission mismatch.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    url = args.url
    if args.demo or url is None:
        url = demo_url()

    try:
        results = run_browser_probe(
            url,
            artifacts_dir=args.artifacts_dir,
            headless=not args.headed,
            retries=max(0, args.retries),
            screenshot=args.screenshot,
            timeout_ms=max(1000, args.timeout_ms),
            trace=args.trace,
        )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    context = build_context_from_probe_results(results, source="playwright-probe", target=url)
    content = json.dumps(context, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(content, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding="utf-8")

    if args.fail_on_target_failure and context["playwrightProbe"]["failedCount"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
