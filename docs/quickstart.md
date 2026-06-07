# Quick Start

Bayesilisk runs locally and uses deterministic scenario data by default. A fixed seed plus the same inputs produces the same report.

## Install

Install directly from GitHub:

```sh
python3 -m pip install 'git+https://github.com/sashakolpakov/bayesilisk.git'
```

Or clone and install editable for development:

```sh
git clone https://github.com/sashakolpakov/bayesilisk.git
cd bayesilisk
python3 -m pip install -e .
```

From an existing repository checkout:

```sh
python3 -m pip install -e .
```

For development work:

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

## MCP Setup

After installation, start the local stdio MCP server with:

```sh
bayesilisk-mcp
```

The module entry point is equivalent when run from a checkout:

```sh
python3 -m bayesilisk.mcp_server
```

By default the MCP server writes only MCP JSON-RPC frames on `stdout` and stays
quiet on `stderr`. Set `BAYESILISK_MCP_BANNER=1` when running it manually if
you want the ASCII startup banner.

Codex example:

```toml
[mcp_servers.bayesilisk]
command = "bayesilisk-mcp"
args = []
startup_timeout_sec = 60
tool_timeout_sec = 120
```

For a project-local config inside a Bayesilisk checkout, use an explicit
checkout path. An absolute Python path is safest if Codex does not inherit your
interactive shell `PATH`.

```toml
[mcp_servers.bayesilisk]
command = "python3"
args = ["-m", "bayesilisk.mcp_server"]
cwd = "/absolute/path/to/bayesilisk"
startup_timeout_sec = 60
tool_timeout_sec = 120
```

See {doc}`codex-mcp` for the full Codex connector workflow.

Other coding agents should use the same launch command in their MCP config:

- installed package: `bayesilisk-mcp`
- checkout/module form: `python3 -m bayesilisk.mcp_server`

## Run The Local Verifier

```sh
python3 -m bayesilisk --seed 150 --format json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --generated-count 16 --format json
```

The installed console entry point is equivalent:

```sh
bayesilisk --seed 150 --format json
```

## Probe Your Own App

To probe a target app, use the connector subcommands rather than hand-writing
context. Scan an API description, bind the motif library, and run the guided
loop:

```sh
bayesilisk connector scan openapi.json --bind-motifs --output source-context.json
bayesilisk connector validate source-context.json
bayesilisk connector propose source-context.json
bayesilisk connector motifs                 # list motif packs/motifs
```

For a fully automated, agent-driven cycle against a locally-running app, use the
stateless controller:

```sh
bayesilisk connector loop --state loop.json --spec openapi.json
# write/run the connector, capture observed-context.json, then:
bayesilisk connector loop --state loop.json --observed observed-context.json
```

See {doc}`connector-quickstart`, {doc}`motifs`, and {doc}`connector-loop`.

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

The bundled workflow demo is local-only. It contains twelve synthetic
product-like user actions across Travel, Expenses, Billing, HR, Support, and
DMS. Some are controls and some intentionally contain stale state, impossible
ordering, duplicate submission, feature-flag exposure, tenant-boundary, and role
lane failures so Bayesilisk can receive browser evidence without contacting
production systems.

```sh
bayesilisk-demo
bayesilisk-demo --recording
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format markdown
```

`bayesilisk-demo --recording` opens headed Chromium, slows the probe clicks, and
holds the browser briefly for screen recording. The transcript explains the
trust boundary: Playwright observes, Grassmann routes, the scenario proposer lane
is untrusted, generated catalog/attention scenarios expand coverage, and
Bayesilisk's deterministic invariants judge. A
`breakage.hard-to-find` verdict is still a deterministic invariant failure; the
label means it required cross-role, cross-module, stale-state, or unusual
workflow context to surface. The transcript also defines `breakage.easy`,
`finding.candidate-breakage`, and `control-confirmed`, and it translates status
pairs such as `expected=409 observed=200` into the product meaning: a workflow
that should reject inconsistent state returned success.

The transcript has two parts: a general multi-fixture verifier run, then a
hard-to-find drill-down. The drill-down shows a route-matrix failure that is not
the first obvious browser symptom; it requires connecting support takeover
state, HR document access, route permissions, and module context before the
deterministic verifier emits an issue-ready finding. It also shows a seeded
sweep order. Changing `--seed` can make the same buried failure appear earlier
or later, while remaining reproducible for that seed.

The demo rows are synthetic fixtures from `bayesilisk/demo.py::DEMO_PROBES`, not
claims about an existing product. To test a real app, expose probe rows in that
app and point Playwright at it:

```sh
python3 tools/playwright_probe.py --url http://localhost:3000/probe-page \
  --output /tmp/bayesilisk-real-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-real-context.json --format markdown
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
