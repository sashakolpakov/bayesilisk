# Integrations

Bayesilisk integrations are optional. The deterministic CLI remains usable with standard-library Python only.

For app-specific adapters, see {doc}`connectors`. Connector code belongs in the
target app or test repo. Test teams should not patch Bayesilisk core to support
one application.

## Microsoft Playwright

The Playwright bridge turns browser observations into Bayesilisk context JSON.

Install:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
```

Run the local demo:

```sh
bayesilisk-demo
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

`bayesilisk-demo` serves an intentionally brittle local workflow app and prints
this chain:

```text
Playwright evidence
  -> Grassmann plane
  -> optional model-style proposal
  -> deterministic verdict
  -> issue payload
```

It can run with `--no-playwright` when a tester wants deterministic local
evidence without launching Chromium.

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

The default proposer provider is Ollama:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/context.json --format json
```

The provider boundary is explicit. `BAYESILISK_SCENARIO_PROVIDER` defaults to
`ollama`; `openai-compatible` is available for hosted Chat Completions style
endpoints. API keys come from `BAYESILISK_SCENARIO_API_KEY`, provider-specific
environment variables, or the variable named by `BAYESILISK_SCENARIO_API_KEY_ENV`.
Reports include provider/model/proposal provenance and key-presence booleans,
but never raw keys or sensitive headers. Provider output stays untrusted and
schema-validated.
Configuration precedence is explicit CLI/MCP arguments, then environment
variables, then defaults.

Environment variables are not required for reproducible runs. The CLI also
accepts explicit controls:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/context.json \
  --enable-embeddings \
  --embedding-model nomic-embed-text \
  --enable-scenario-proposer \
  --scenario-provider ollama \
  --scenario-model gemma4:e2b \
  --scenario-proposal-limit 3 \
  --attention-threshold 0.4 \
  --attention-selection-limit 3 \
  --ollama-base-url http://localhost:11434
```

Reports include `effectiveConfiguration`, so a tester can see which attention,
embedding, provider, model, proposal-limit, key-presence, and base-URL-class
settings were actually used.

Live verification is opt-in:

```sh
python3 -m pytest -m live_playwright
BAYESILISK_LIVE_OLLAMA=1 BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b python3 -m pytest -m live_ollama
```

The GitHub CI workflow skips live Playwright and live Ollama tests by default,
because it does not assume installed browsers or a local model service.

## MCP Server

Bayesilisk includes a local stdio MCP tool server:

```sh
bayesilisk-mcp
```

From a checkout, the module form is equivalent:

```sh
python3 -m bayesilisk.mcp_server
```

By default the server writes only MCP JSON-RPC frames on `stdout` and stays
quiet on `stderr`. Set `BAYESILISK_MCP_BANNER=1` when running it manually if
you want the ASCII startup banner.

Verifier tools:

- `run`: run a contextual report.
- `rank_context`: return ranked failed probes from supplied context.
- `issue_payloads`: return deduped issue payloads for ready failed
  findings.
- `propose_probes`: expand connector-supplied rules and action
  graphs into probe proposals.

Codex orchestration tools:

- `interview_connector_need`;
- `establish_provenance`;
- `connector_prompt_packet`;
- `scenario_plan`;
- `verify_connector_outputs`;
- `fix_packet`.

The MCP tools accept the same control names as JSON arguments:
`enableEmbeddings`, `embeddingModel`, `enableScenarioProposer`,
`scenarioProvider`, `scenarioModel`, `scenarioProposalLimit`,
`scenarioBaseUrl`, `scenarioApiKeyEnv`, `attentionThreshold`,
`attentionSelectionLimit`, and `ollamaBaseUrl`.

The MCP server runs locally and does not mutate issue trackers or production systems.

For Codex configuration and connector onboarding, see {doc}`codex-mcp`.

## Coding Agent Loop

A Codex-style agent can use Bayesilisk MCP as the cheap local drill layer:

1. Call `interview_connector_need`.
2. Call `establish_provenance`.
3. Call `connector_prompt_packet`.
4. Write connector code and source context in the target app or test repo.
5. Call `scenario_plan` or `propose_probes`.
6. Run the app-specific connector against local fixtures.
7. Call `verify_connector_outputs`.
8. Call `fix_packet` only for verified issue-ready findings.

If a local model/API is configured, pass `enableScenarioProposer=true` plus
`scenarioProvider`, `scenarioModel`, and base URL/API-key settings to
`run`. Model proposals stay untrusted; Bayesilisk validates them
before deterministic verification.

## GitHub Issues

The repository uses GitHub Issues for public planning. Bayesilisk itself emits issue-ready payloads, but creating issues is intentionally left to a caller-controlled workflow.
