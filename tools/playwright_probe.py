#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from bayesilisk.playwright_adapter import build_context_from_probe_results


def demo_url() -> str:
    return (REPO_ROOT / "demo" / "playwright_target.html").resolve().as_uri()


def run_browser_probe(url: str, *, headless: bool = True) -> list[dict[str, Any]]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Microsoft Playwright is not installed. Install with "
            "`python3 -m pip install -e '.[playwright]'` and then run "
            "`python3 -m playwright install chromium`."
        ) from exc

    results: list[dict[str, Any]] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            probes = page.locator("[data-bayesilisk-probe]")
            count = probes.count()
            for index in range(count):
                probe = probes.nth(index)
                probe.locator("[data-run-probe]").click()
                observed = probe.locator("[data-observed-status]").inner_text().strip()
                results.append(
                    {
                        "actorRole": probe.get_attribute("data-actor-role"),
                        "expectedStatus": probe.get_attribute("data-expected-status"),
                        "invariantId": probe.get_attribute("data-invariant-id"),
                        "observedStatus": observed,
                        "route": probe.get_attribute("data-route"),
                        "title": probe.get_attribute("data-title"),
                    }
                )
        finally:
            browser.close()
    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bayesilisk route probes through Microsoft Playwright.")
    parser.add_argument("--url", default=None, help="Target URL with Bayesilisk probe elements.")
    parser.add_argument("--demo", action="store_true", help="Use the bundled static demo target.")
    parser.add_argument("--output", type=Path, default=None, help="Write Bayesilisk context JSON to this path.")
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible browser window.")
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
        results = run_browser_probe(url, headless=not args.headed)
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
