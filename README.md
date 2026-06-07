# Bayesilisk

[![CI](https://github.com/sashakolpakov/bayesilisk/actions/workflows/ci.yml/badge.svg)](https://github.com/sashakolpakov/bayesilisk/actions/workflows/ci.yml)
[![Docs](https://github.com/sashakolpakov/bayesilisk/actions/workflows/pages.yml/badge.svg)](https://sashakolpakov.github.io/bayesilisk/)

<p align="center">
  <img src="logo/bayesilisk_logo.png" alt="Bayesilisk logo" width="220">
</p>

**Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the Oracle.**

Bayesilisk is a deterministic verifier for authorization, route, entitlement,
and data-boundary testing. It separates scenario proposal from verification:
connectors declare a bounded application surface, Bayesilisk expands and checks
candidate probes, and only deterministic verification over returned evidence can
produce issue-ready findings.

The current architecture has two operating routes:

- `local`: you run the verifier and connector loop directly from the CLI against
  local fixtures, API descriptions, browser evidence, or caller-provided
  context;
- `mcp/agent-bound`: a coding agent such as Codex uses the local MCP server to
  interview for connector requirements, draft connector artifacts, plan
  scenarios, and verify connector outputs, while Bayesilisk remains the
  deterministic oracle.

Bayesilisk is local-first. It does not inspect production systems or live
customer data, and it does not allow a model, connector, or Playwright trace to
declare a bug by itself.

## What Bayesilisk Does

Bayesilisk is for teams that want broader scenario coverage than ordinary E2E
suites, without delegating correctness to an LLM. A connector publishes the
search surface:

- routes;
- actions;
- identifiers and state facts;
- invariants;
- mutation schemas;
- optional typed workflow rules through an Abstract Bayesilisk Action Graph
  (ABAG).

Bayesilisk then:

1. expands that declared surface into candidate probes;
2. validates candidates against deterministic contracts;
3. optionally prioritizes them with Grassmann-style attention and a Bayesian
   score;
4. accepts observed evidence only after connector execution;
5. verifies expected-versus-observed behavior deterministically.

The trust boundary is strict:

```text
scenario proposal -> contract validation -> connector execution -> deterministic verification
```

Models may help propose where to look. They do not decide pass/fail, issue
readiness, or truth.

See [docs/architecture.md](docs/architecture.md) and the
[manuscript](manuscript/main.tex) ([PDF](manuscript/main.pdf)).

## Quick Start

### 1. Install

Install directly from GitHub:

```sh
python3 -m pip install 'git+https://github.com/sashakolpakov/bayesilisk.git'
```

Or clone and install editable:

```sh
git clone https://github.com/sashakolpakov/bayesilisk.git
cd bayesilisk
python3 -m pip install -e .
```

From an existing checkout:

```sh
python3 -m pip install -e .
```

Development extras:

```sh
python3 -m pip install -e '.[dev]'
```

Optional browser probing:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
```

### 2. Codex Setup First

If you want Bayesilisk through Codex, start here.

Run the local MCP server:

```sh
bayesilisk-mcp
```

From a checkout, the module form is equivalent:

```sh
python3 -m bayesilisk.mcp_server
```

Then add Bayesilisk to Codex config:

```toml
[mcp_servers.bayesilisk]
command = "bayesilisk-mcp"
args = []
startup_timeout_sec = 60
tool_timeout_sec = 120
```

If you want a project-local config that points at a checkout directly:

```toml
[mcp_servers.bayesilisk]
command = "python3"
args = ["-m", "bayesilisk.mcp_server"]
cwd = "/absolute/path/to/bayesilisk"
startup_timeout_sec = 60
tool_timeout_sec = 120
```

Restart Codex after changing MCP config.

The launch command is the same across clients:

- installed package: `bayesilisk-mcp`
- checkout/module form: `python3 -m bayesilisk.mcp_server`

The intended Codex loop is:

```text
connector_quickstart
  -> interview_connector_need
  -> establish_provenance
  -> connector_prompt_packet
  -> Codex writes connector code in the target app repo
  -> scenario_plan
  -> connector executes local fixtures
  -> verify_connector_outputs
  -> fix_packet
```

Use this prompt in a target repository:

```text
Use Bayesilisk to build a connector for this repo. Start by interviewing me
about the connector need, then establish provenance, generate a connector prompt
packet, plan scenarios, and verify connector outputs.
```

Bayesilisk remains the verifier. Codex may draft connector code and plans, but
it must not invent observed evidence, pass/fail results, or issue readiness.

### 3. Run The Local Verifier

```sh
python3 -m bayesilisk --seed 150 --format json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --issue-payloads
```

Installed console entry points:

```sh
bayesilisk --seed 150 --format json
bayesilisk-mcp
```

## Local Route: Connector CLI

If you are using Bayesilisk directly rather than through an agent, use the
connector subcommands.

### Guided Connector Loop

```sh
bayesilisk connector init --kind source --with-action-graph --output source-context.json
bayesilisk connector validate source-context.json
bayesilisk connector propose source-context.json --output proposals.json
# execute your connector against local fixtures and write observed-context.json
bayesilisk connector verify --source source-context.json --observed observed-context.json --issue-payloads
```

`validate` rejects verifier-owned fields, production URLs, and malformed
connector inputs. `verify` accepts only local observed evidence and runs
deterministic verification over it.

See [docs/connector-quickstart.md](docs/connector-quickstart.md) and
[docs/connectors.md](docs/connectors.md).

### Scan, Bind Motifs, And Loop

To generate probes from an app surface instead of hand-writing all
`proposalRules`, scan and bind the motif library:

```sh
bayesilisk connector scan openapi.json --bind-motifs --output source-context.json
bayesilisk connector motifs
```

To run the full stateless controller:

```sh
bayesilisk connector loop --state loop.json --spec openapi.json
# after connector execution writes observed-context.json
bayesilisk connector loop --state loop.json --observed observed-context.json
```

The closed loop performs deterministic steps only:

```text
scan -> bind -> validate -> verify -> fix
```

It tracks convergence and returns the exact next action for the connector or
agent to perform.

See [docs/motifs.md](docs/motifs.md) and
[docs/connector-loop.md](docs/connector-loop.md).

## MCP Server

Bayesilisk includes a small local stdio MCP server:

```sh
bayesilisk-mcp
```

<!-- Official MCP Registry ownership verification (do not remove). -->
mcp-name: io.github.sashakolpakov/bayesilisk-mcp

By default the server writes only MCP JSON-RPC frames on `stdout` and stays
quiet on `stderr`. Set `BAYESILISK_MCP_BANNER=1` when running it manually if
you want the ASCII startup banner.

### MCP Tools

Verifier tools:

- `run`
- `rank_context`
- `issue_payloads`
- `propose_probes`

Motif and loop tools:

- `list_motifs`
- `bind_motifs`
- `connector_loop`

Codex orchestration tools:

- `connector_quickstart`
- `interview_connector_need`
- `establish_provenance`
- `connector_prompt_packet`
- `scenario_plan`
- `verify_connector_outputs`
- `fix_packet`

The MCP tools use the same runtime controls as the CLI where relevant,
including `enableEmbeddings`, `embeddingModel`, `enableScenarioProposer`,
`scenarioProvider`, `scenarioModel`, `scenarioProposalLimit`,
`attentionThreshold`, `attentionSelectionLimit`, and `ollamaBaseUrl`.

### Other MCP Clients

**Claude Code**

```sh
claude mcp add --scope project bayesilisk -- bayesilisk-mcp
```

**Cursor**, **Windsurf**, and **JetBrains AI Assistant**

```json
{
  "mcpServers": {
    "bayesilisk": { "command": "bayesilisk-mcp", "args": [] }
  }
}
```

**VS Code**

```json
{
  "servers": {
    "bayesilisk": { "type": "stdio", "command": "bayesilisk-mcp", "args": [] }
  }
}
```

**Zed**

```json
{
  "context_servers": {
    "bayesilisk": { "command": { "path": "bayesilisk-mcp", "args": [] } }
  }
}
```

**Continue**

```yaml
name: Bayesilisk
version: 0.0.1
schema: v1
mcpServers:
  - name: bayesilisk
    type: stdio
    command: bayesilisk-mcp
    args: []
```

## Reports And Findings

Reports can include:

- seed and tool version;
- deterministic boundary metadata;
- connector-declared scenarios and generated sub-scenarios;
- access patterns;
- expected invariant and observed result;
- stable fingerprint and dedupe key;
- classification and issue readiness;
- attention score and reasons when context is supplied;
- posterior probability and risk score;
- suggested issue title and body.

Only findings with:

```text
observedResult = fail
issueReadiness = ready-for-issue
```

should be opened automatically.

Example artifacts:

- [example JSON report](docs/examples/example-report.json)
- [example GitHub issue payloads](docs/examples/example-issue-payloads.json)
- [Cal.com connector evidence](examples/calcom/)
- [connector agent contract](examples/connector-agent-contract.json)
- [typed ABAG example](examples/abag-action-graph-context.json)

The manuscript documents a Cal.com case study at a fixed May 2026 revision. In
that artifact, Bayesilisk generated seven probes from connector-declared route
facts and a typed ABAG workflow surface; all seven produced deterministic
expected-versus-observed violations, and one upstream finding has a targeted fix
pull request with human approval review.

## Playwright And Demo Flows

Playwright is an evidence sensor, not an oracle. It can supply browser evidence
to Bayesilisk, but Bayesilisk still performs deterministic verification.

### Bundled Demo

```sh
bayesilisk-demo
bayesilisk-demo --recording
bayesilisk-demo --no-playwright
```

Module form:

```sh
python3 -m bayesilisk.demo --recording
python3 -m bayesilisk.demo --no-playwright
```

The demo accepts a deterministic seed:

```sh
python3 -m bayesilisk.demo --seed 150 --recording
python3 -m bayesilisk.demo --seed 151 --no-playwright
```

To run the lower-level Playwright adapter and then verify the captured context:

```sh
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format markdown
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --issue-payloads
```

The bundled demo is synthetic local fixture data from
`bayesilisk/demo.py::DEMO_PROBES`. It is not a claim about a customer system.

### Realistic Local App Demo

```sh
python3 -m bayesilisk.realistic_demo --no-playwright
python3 -m bayesilisk.realistic_demo --recording
python3 -m bayesilisk.realistic_demo \
  --context-output /tmp/bayesilisk-realistic-context.json \
  --no-playwright
python3 -m bayesilisk \
  --seed 150 \
  --context /tmp/bayesilisk-realistic-context.json \
  --format markdown
```

Installed console entry point:

```sh
bayesilisk-realistic-demo --recording
```

To use the realistic app like a normal local integration:

```sh
python3 -m bayesilisk.realistic_demo --serve-only
```

Then point the Playwright bridge at the printed
`/internal/bayesilisk-probes` URL.

## Optional Attention And Scenario-Proposer Layers

Bayesilisk works without any model provider. Optional layers can help rank or
propose candidate scenarios, but they remain untrusted inputs.

### Grassmann Attention

By default Bayesilisk uses a dependency-free anchor-plane proxy. To add Ollama
embeddings:

```sh
BAYESILISK_USE_OLLAMA_EMBEDDINGS=1 \
BAYESILISK_OLLAMA_MODEL=nomic-embed-text \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --format json
```

Equivalent CLI flags:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json \
  --enable-embeddings \
  --embedding-model nomic-embed-text \
  --attention-threshold 0.4 \
  --attention-selection-limit 3
```

Attention answers:

```text
Where should Bayesilisk look next?
```

### Scenario Proposer Model

To let a local or API-backed model suggest extra candidates:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --format json
```

Equivalent CLI flags:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json \
  --enable-scenario-proposer \
  --scenario-provider ollama \
  --scenario-model gemma4:e2b \
  --scenario-proposal-limit 3 \
  --ollama-base-url http://localhost:11434
```

Model output is accepted only if it uses known fragment and invariant ids,
targets a selected attention plane, and passes schema validation.

Reports include `effectiveConfiguration`, which records the effective settings
used for attention and scenario-proposer layers.

## Test And Docs

Run the full test suite:

```sh
python3 -m pytest
```

CI deliberately runs deterministic tests and the docs build without Ollama,
browser services, or hidden local state:

```sh
python3 -m pytest -m "not live_playwright and not live_ollama"
sphinx-build -b html docs docs/_build/html
```

Opt-in local live checks:

```sh
python3 -m pytest tests/test_live_integrations.py -m live_playwright -rs
BAYESILISK_LIVE_OLLAMA=1 python3 -m pytest tests/test_live_integrations.py -m live_ollama -rs
```

Build docs locally:

```sh
python3 -m pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Key docs:

- [docs/quickstart.md](docs/quickstart.md)
- [docs/connector-quickstart.md](docs/connector-quickstart.md)
- [docs/connectors.md](docs/connectors.md)
- [docs/motifs.md](docs/motifs.md)
- [docs/connector-loop.md](docs/connector-loop.md)
- [docs/codex-mcp.md](docs/codex-mcp.md)

## Boundaries

Bayesilisk is a verifier and prioritizer. It is not:

- an authorization engine;
- a production scanner;
- a live customer data inspection tool;
- an issue tracker mutator;
- an LLM oracle.

Coding agents may help collect requirements, draft connectors, run local
fixtures, and prepare repairs from verified findings. They must not author
observed evidence, `passed`, or `issueReadiness`.

## Acknowledgments

Thanks to OpenAI for providing model access, including early ChatGPT-5.5
preview access, which helped accelerate the initial Bayesilisk buildout.
