# Integrations

Bayesilisk integrations are optional. The deterministic CLI remains usable with standard-library Python only.

## Microsoft Playwright

The Playwright bridge turns browser observations into Bayesilisk context JSON.

Install:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
```

Run the local demo:

```sh
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

Capture evidence artifacts:

```sh
python3 tools/playwright_probe.py --demo \
  --artifacts-dir /tmp/bayesilisk-artifacts \
  --screenshot \
  --trace \
  --output /tmp/bayesilisk-playwright-context.json
```

The probe looks for rows marked with `data-bayesilisk-probe`. Each row should provide:

- `data-title`;
- `data-actor-role`;
- `data-route`;
- `data-invariant-id`;
- `data-expected-status`;
- clickable child `data-run-probe`;
- status child `data-observed-status`.

Playwright is the sensor. Bayesilisk remains the judge.

## Ollama Embeddings

Embeddings add a similarity signal to Grassmann attention:

```sh
BAYESILISK_USE_OLLAMA_EMBEDDINGS=1 \
BAYESILISK_OLLAMA_MODEL=nomic-embed-text \
python3 -m bayesilisk --seed 150 --context /tmp/context.json --format json
```

If Ollama is unavailable, the dependency-free anchor-plane proxy is still used.

## Scenario Proposer Model

The proposer model is configured through Ollama today:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/context.json --format json
```

The provider abstraction and API-key handling are tracked as a follow-up issue. The design requires that provider output stay untrusted and schema-validated.

Live verification is opt-in:

```sh
python3 -m pytest -m live_playwright
BAYESILISK_LIVE_OLLAMA=1 BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b python3 -m pytest -m live_ollama
```

The GitHub CI workflow skips live Playwright and live Ollama tests by default,
because it does not assume installed browsers or a local model service.

## MCP Server

Bayesilisk includes a stdio MCP tool server:

```sh
python3 -m bayesilisk.mcp_server
```

Tools:

- `bayesilisk.run`: run a contextual report;
- `bayesilisk.rank_context`: return ranked failed probes from supplied context;
- `bayesilisk.issue_payloads`: return deduped issue payloads for ready failed findings.

The MCP server runs locally and does not mutate issue trackers or production systems.

## GitHub Issues

The repository uses GitHub Issues for public planning. Bayesilisk itself emits issue-ready payloads, but creating issues is intentionally left to a caller-controlled workflow.
