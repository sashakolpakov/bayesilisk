# Quick Start

Bayesilisk runs locally and uses deterministic scenario data by default. A fixed seed plus the same inputs produces the same report.

## Install

From the repository root:

```sh
python3 -m pip install -e '.[dev]'
```

For browser probing with Microsoft Playwright:

```sh
python3 -m pip install -e '.[dev,playwright]'
python3 -m playwright install chromium
```

For documentation work:

```sh
python3 -m pip install -r docs/requirements.txt
```

## Run the Verifier

```sh
python3 -m bayesilisk --seed 150 --format json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --generated-count 16 --format json
```

The installed console entry point is equivalent:

```sh
bayesilisk --seed 150 --format json
```

## Run With Context

Context is caller-provided JSON. It can include issue text, agent notes, repository facts, Playwright observations, muted fingerprints, confirmed fingerprints, and prior adjustments.

```sh
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --format json
```

Only `ready-for-issue` failed findings should be opened automatically:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --issue-payloads
```

## Run the Playwright Demo

The bundled demo target is static and local. It intentionally contains mismatched route outcomes so Bayesilisk can receive browser evidence without contacting production systems.

```sh
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format markdown
```

## Enable Optional Ollama Layers

Embeddings add a plane-similarity signal to Grassmann attention:

```sh
BAYESILISK_USE_OLLAMA_EMBEDDINGS=1 \
BAYESILISK_OLLAMA_MODEL=nomic-embed-text \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

The scenario proposer model suggests extra candidate scenarios. Bayesilisk validates those proposals before they enter the finite-state verifier:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

The same controls are available as explicit CLI flags:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json \
  --enable-embeddings \
  --embedding-model nomic-embed-text \
  --enable-scenario-proposer \
  --scenario-model gemma4:e2b \
  --scenario-proposal-limit 3 \
  --attention-threshold 0.4 \
  --attention-selection-limit 3 \
  --ollama-base-url http://localhost:11434
```

Reports include `effectiveConfiguration`, so a tester can see which attention,
embedding, model, proposal-limit, and base-URL-class settings were actually used.

## Test

```sh
python3 -m pytest
```

GitHub CI deliberately runs the deterministic suite and docs build without
Ollama, hosted model APIs, Playwright browsers, or local-only services:

```sh
python3 -m pytest -m "not live_playwright and not live_ollama"
sphinx-build -b html docs docs/_build/html
```

Live checks are opt-in local verification commands. They are useful before
promotion or release work, but they are not required for the deterministic
verifier to prove report compatibility:

```sh
python3 -m pytest tests/test_live_integrations.py -m live_playwright -rs
BAYESILISK_LIVE_OLLAMA=1 python3 -m pytest tests/test_live_integrations.py -m live_ollama -rs
```

## Build Documentation

```sh
sphinx-build -b html docs docs/_build/html
```
