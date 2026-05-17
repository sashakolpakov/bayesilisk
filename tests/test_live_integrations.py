from __future__ import annotations

import importlib
import json
import os
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.live_playwright
def test_live_playwright_demo_probe_end_to_end(tmp_path: Path) -> None:
    pytest.importorskip("playwright.sync_api")
    probe = importlib.import_module("tools.playwright_probe")
    adapter = importlib.import_module("bayesilisk.playwright_adapter")
    reporting = importlib.import_module("bayesilisk.reporting")

    try:
        results = probe.run_browser_probe(probe.demo_url(), headless=True)
    except Exception as exc:
        pytest.skip(f"Playwright browser is unavailable: {exc}")

    context = adapter.build_context_from_probe_results(
        results,
        source="live-playwright-demo",
        target=probe.demo_url(),
    )
    report = reporting.build_contextual_report(150, generated_count=4, context=context)

    assert context["playwrightProbe"]["resultCount"] >= 1
    assert report["contextSummary"]["source"] == "live-playwright-demo"
    assert report["grassmannAttention"]["selectedPlaneIds"]
    assert any("playwright-evidence" in finding.get("attentionReasons", []) for finding in report["findings"])


@pytest.mark.live_ollama
def test_live_ollama_scenario_proposer_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    if os.environ.get("BAYESILISK_LIVE_OLLAMA") != "1":
        pytest.skip("set BAYESILISK_LIVE_OLLAMA=1 to run live Ollama scenario proposer test")

    reporting = importlib.import_module("bayesilisk.reporting")
    monkeypatch.setenv("BAYESILISK_USE_OLLAMA_SCENARIO_MODEL", "1")
    monkeypatch.setenv(
        "BAYESILISK_OLLAMA_SCENARIO_MODEL",
        os.environ.get("BAYESILISK_OLLAMA_SCENARIO_MODEL", "qwen2.5-coder:3b"),
    )
    model = os.environ.get("BAYESILISK_OLLAMA_SCENARIO_MODEL", "qwen2.5-coder:3b")
    base_url = os.environ.get("BAYESILISK_OLLAMA_BASE_URL", os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
    try:
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/chat",
            data=json.dumps(
                {
                    "model": model,
                    "messages": [{"role": "user", "content": "Return JSON only: {}"}],
                    "stream": False,
                    "options": {"num_predict": 1, "temperature": 0.0},
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(
            request,
            timeout=float(os.environ.get("BAYESILISK_OLLAMA_WARMUP_TIMEOUT", "30")),
        ) as response:
            response.read()
    except Exception as exc:
        pytest.skip(f"Ollama scenario proposer warm-up unavailable: {exc}")
    monkeypatch.setenv("BAYESILISK_OLLAMA_SCENARIO_TIMEOUT", os.environ.get("BAYESILISK_OLLAMA_SCENARIO_TIMEOUT", "20"))

    context = {
        "source": "live-ollama-scenario-proposer",
        "agentNotes": ["support takeover and HR documents boundary need scenario proposal coverage"],
        "repositoryFacts": [
            {
                "source": "microsoft-playwright",
                "actorRole": "support",
                "route": "/api/hr/documents",
                "expectedStatus": 403,
                "observedStatus": 200,
                "invariantId": "hr.documents_customer_role_boundary",
                "passed": False,
            }
        ],
    }
    report = reporting.build_contextual_report(150, generated_count=4, context=context)
    generation = report["weakModelScenarioGeneration"]

    if generation.get("error"):
        pytest.skip(f"Ollama scenario proposer unavailable: {generation['error']}")

    assert generation["enabled"] is True
    assert generation["source"] == "ollama-chat"
    assert generation["acceptedCount"] + generation["rejectedCount"] >= 1
