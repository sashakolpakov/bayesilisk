# Connector Quickstart

This is the shortest guided path to a working connector. It uses the
`bayesilisk connector` subcommands so you get clear diagnostics at every step
instead of hand-editing JSON and guessing. Coding agents can drive the exact
same loop over MCP — see the parity table at the bottom.

The loop is always:

```text
init -> validate -> propose -> (write a connector, execute it) -> verify
```

Bayesilisk stays app-agnostic. Your connector owns app-specific execution; the
deterministic verifier owns pass/fail. See {doc}`connectors` for the full
contract and {doc}`codex-mcp` for agent setup.

## 1. Scaffold a starter context

```sh
bayesilisk connector init --kind source --with-action-graph --output source-context.json
```

`--kind` is `source` (default), `observed`, or `both`. `--with-action-graph`
adds a `connectorActionGraph` example for multi-step workflow motifs. Omit
`--output` to print to stdout.

Edit the placeholders so every `repositoryFact` references real routes,
invariants, expected statuses, and `proposalRules` drawn from your app's tests,
TODOs, route handlers, and product rules.

## 2. Validate the context

```sh
bayesilisk connector validate source-context.json
```

`validate` exits non-zero and prints readable errors when a context contains
verifier-only fields, points at a production URL, or otherwise cannot produce
probes. It warns loudly when a fact has no `proposalRules`/`proposalGates` so you
never get a silent empty result. To lint observed evidence instead:

```sh
bayesilisk connector validate observed-context.json --observed
```

## 3. Expand probe proposals

```sh
bayesilisk connector propose source-context.json --output proposals.json
```

Unlike a raw export, `propose` reports the proposal count and, when zero are
generated, tells you exactly what is missing. Each proposal carries a
`connectorAction` your connector maps to real fixture/browser/API behavior.

## 4. Execute the connector

Run your app-specific connector against **local, dev, or staging fixtures only**.
For each proposal, perform the real action and record `observedStatus`,
`passed` (`observedStatus == expectedStatus`), `failureDetail`, and any
`artifactPaths`. Never let a model write `observedStatus` or `passed`. Write the
results into an observed-context JSON (`bayesilisk connector init --kind observed`
gives the shape).

## 5. Verify

```sh
bayesilisk connector verify \
  --source source-context.json \
  --observed observed-context.json \
  --issue-payloads --output issues.json
```

`verify` runs the deterministic Bayesilisk verifier over your observed evidence
and emits issue payloads only for confirmed failures. It rejects observed facts
whose `passed` disagrees with `observedStatus == expectedStatus`. A minimal
local-only provenance is built automatically; pass `--provenance prov.json` to
supply your own. Drop `--issue-payloads` for the full report (`--format markdown`
for a readable report).

## CLI / MCP parity

The same loop is available to coding agents over the MCP server. Call
`connector_quickstart` first for the ordered tool list and templates.

| Terminal (`bayesilisk connector ...`) | MCP tool |
| --- | --- |
| `init` | `connector_quickstart`, `connector_prompt_packet` |
| `validate` | `scenario_plan` (validation), `verify_connector_outputs` (observed) |
| `propose` | `propose_probes`, `scenario_plan` |
| `verify` | `verify_connector_outputs`, then `fix_packet` |

The full agent sequence is `interview_connector_need -> establish_provenance ->
connector_prompt_packet -> scenario_plan -> verify_connector_outputs ->
fix_packet`. Bayesilisk verifies; the agent owns app-specific connector
execution, issue creation, and code changes, and acts only on verified output.
