# Codex MCP

Bayesilisk includes a local stdio MCP server for Codex-style connector
workflows. It is designed to help Codex interview the user, establish connector
provenance, generate a connector prompt packet, plan scenarios, verify connector
outputs, and create fix briefs from verified findings only.

The MCP server is local-first:

- it does not connect to production systems;
- it does not mutate issue trackers;
- it does not execute arbitrary app commands;
- it does not let an LLM write observed statuses, pass/fail results, or issue
  readiness.

On startup, the MCP process prints an ASCII Bayesilisk logo and version to
`stderr`. `stdout` is reserved for framed MCP JSON-RPC messages.

## Install From GitHub

Until Bayesilisk is published to PyPI, install it from GitHub.

For normal use, install directly from the repository:

```sh
python3 -m pip install 'git+https://github.com/sashakolpakov/bayesilisk.git'
bayesilisk-mcp
```

For development, clone and install editable:

```sh
git clone https://github.com/sashakolpakov/bayesilisk.git
cd bayesilisk
python3 -m pip install -e .
bayesilisk-mcp
```

From an existing Bayesilisk checkout, run:

```sh
python3 -m pip install -e .
bayesilisk-mcp
```

For development extras:

```sh
python3 -m pip install -e '.[dev]'
```

For browser probing:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
```

After a package release is published to PyPI, the normal package install should
be equivalent:

```sh
python3 -m pip install bayesilisk
```

## Configure Codex

Codex MCP servers are configured under `[mcp_servers.<id>]` in Codex config.
The OpenAI Codex configuration reference documents `command`, `args`, `cwd`,
`startup_timeout_ms`, and `tool_timeout_sec` for MCP servers:
<https://developers.openai.com/codex/config-reference>.

Preferred configuration after installing Bayesilisk:

```toml
[mcp_servers.bayesilisk]
command = "bayesilisk-mcp"
args = []
startup_timeout_ms = 20000
tool_timeout_sec = 120
```

For a project-local config while working inside the Bayesilisk checkout, the
module form also works:

```toml
[mcp_servers.bayesilisk]
command = "python3"
args = ["-m", "bayesilisk.mcp_server"]
cwd = "."
startup_timeout_ms = 20000
tool_timeout_sec = 120
```

If this config is not in the Bayesilisk checkout, prefer installing the package
and using `command = "bayesilisk-mcp"` so no checkout path is needed.

Restart Codex after changing MCP configuration. In Codex, check the MCP tool
list with the normal MCP status UI or command for your Codex client.

## Start A Connector Session

In a target application repo, ask Codex:

```text
Use Bayesilisk to build a connector for this repo. Start by interviewing me
about the connector need, then establish provenance, generate a connector prompt
packet, plan scenarios, and verify connector outputs.
```

The intended MCP tool flow is:

```text
bayesilisk.interview_connector_need
  -> bayesilisk.establish_provenance
  -> bayesilisk.connector_prompt_packet
  -> Codex writes connector code in the target app/test repo
  -> bayesilisk.scenario_plan
  -> connector executes local fixtures
  -> bayesilisk.verify_connector_outputs
  -> bayesilisk.fix_packet
```

Bayesilisk provides the contract, scenario proposal layer, validation, and
deterministic verification. Codex writes app-specific connector code and runs
the target app's local fixtures through ordinary repo tools.

## MCP Tools

Verifier tools:

- `bayesilisk.run`: run a contextual report.
- `bayesilisk.rank_context`: return ranked failed probes from supplied context.
- `bayesilisk.issue_payloads`: return deduped issue payloads for ready failed
  findings.
- `bayesilisk.propose_probes`: expand connector-supplied proposal rules and
  action graphs into app-agnostic probe proposals.

Codex orchestration tools:

- `bayesilisk.interview_connector_need`: normalize the user request and return
  short follow-up questions.
- `bayesilisk.establish_provenance`: record caller-supplied repository, source,
  test, and execution-boundary facts.
- `bayesilisk.connector_prompt_packet`: emit the prompt/spec packet Codex should
  use to create an app-specific connector.
- `bayesilisk.scenario_plan`: build a bounded scenario plan from source context,
  proposal rules, and ABAG action graphs.
- `bayesilisk.verify_connector_outputs`: validate observed connector evidence
  and run deterministic Bayesilisk verification.
- `bayesilisk.fix_packet`: emit a repair brief from verified findings or issue
  payloads only.

The MCP tools accept the same runtime-control names as the CLI where relevant:
`enableEmbeddings`, `embeddingModel`, `enableScenarioProposer`,
`scenarioProvider`, `scenarioModel`, `scenarioProposalLimit`,
`scenarioBaseUrl`, `scenarioApiKeyEnv`, `attentionThreshold`,
`attentionSelectionLimit`, and `ollamaBaseUrl`.

## Trust Rules

Codex may draft:

- connector source context;
- connector action mappings;
- scenario plans;
- connector code in the target app or test repo;
- fix prose and app patches after verified output.

Codex must not:

- edit Bayesilisk core for an app connector;
- invent source evidence;
- invent `observedStatus`;
- set `passed` without executing the app;
- set `issueReadiness`;
- open issues or patch code from raw connector output alone.

Only connector execution against local fixtures may create observed facts. Only
Bayesilisk deterministic verification may produce issue-ready findings.

## Minimal Connector Loop

1. Codex reads local app tests, route handlers, schemas, and fixture helpers.
2. Codex writes source context with explicit `expectedStatus`, `proposalRules`,
   `proposalGates`, or `connectorActionGraph.sequenceRules`.
3. Codex calls `bayesilisk.scenario_plan` or `bayesilisk.propose_probes`.
4. The connector executes returned actions against local fixtures.
5. The connector writes observed context with `expectedStatus`,
   `observedStatus`, `passed`, `targetUrl`, artifacts, network responses, and
   timestamps.
6. Codex calls `bayesilisk.verify_connector_outputs`.
7. Codex creates issues or app patches only from Bayesilisk verified issue
   payloads or fix packets.
