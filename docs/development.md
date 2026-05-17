# Development

## Repository Layout

```text
bayesilisk/
  bayesilisk.py          finite-state verifier, attention, reports, CLI
  demo.py                local workflow pressure demo command
  playwright_adapter.py  Playwright observation adapter
  mcp_server.py          stdio MCP server
demo/
  playwright_target.html local browser-probe target
docs/
  *.md                   Sphinx/MyST documentation
tests/
  test_bayesilisk_runner.py
tools/
  playwright_probe.py    demo and target Playwright probe
```

## Test Policy

Run:

```sh
python3 -m pytest
```

The required CI path is deterministic and service-free:

```sh
python3 -m pytest -m "not live_playwright and not live_ollama"
sphinx-build -b html docs docs/_build/html
```

The tests should cover:

- every catalog scenario references valid fragments and invariants;
- every invariant has at least one passing control and one failing bad-spot case;
- Playwright context affects attention but does not override deterministic results;
- model-proposed scenarios are validated before use;
- issue payloads are deduped and only emitted for ready failed findings.

Live integrations are opt-in. They are marked so CI can skip them on GitHub,
where no browser binaries or local scenario proposer model are assumed to exist:

```sh
python3 -m pytest -m live_playwright
BAYESILISK_LIVE_OLLAMA=1 BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b python3 -m pytest -m live_ollama
```

Default CI runs deterministic tests and builds the Sphinx docs only. It does not
require Ollama, hosted model APIs, Playwright browsers, API keys, or local hidden
state.

## Docs Policy

Build docs locally before changing the public documentation:

```sh
python3 -m pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

The GitHub Pages workflow builds the same Sphinx site on pushes to `main`.

## Public Language

Use “scenario proposer model” in user-facing documentation. The current code still emits some `weakModelScenarioGeneration` and `weak-model-proposal:*` fields for compatibility with earlier report contracts.

## Boundaries

Do not add code that:

- connects Bayesilisk to production systems;
- treats embeddings as pass/fail evidence;
- treats model output as trusted;
- opens tracker issues directly from the verifier;
- hides deterministic failures because attention is low.
