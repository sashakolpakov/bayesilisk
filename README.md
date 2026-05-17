# Bayesilisk

[![CI](https://github.com/sashakolpakov/bayesilisk/actions/workflows/ci.yml/badge.svg)](https://github.com/sashakolpakov/bayesilisk/actions/workflows/ci.yml)

<p align="center">
  <img src="logo/bayesilisk_logo.png" alt="Bayesilisk logo" width="220">
</p>

**Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the Oracle.**

Bayesilisk is a deterministic local layer for permission, entitlement, route,
and data-boundary sitting over Playwright, with Grassmann attention, and
LLM-generated scenario-proposal workflows gated by a finite-state verifier.

Bayesilisk is intentionally local-first. It uses static scenario fragments,
caller-provided context, optional observation history, optional browser evidence,
and optional local model proposals. It does not connect to production systems or
inspect live customer data. It is built for testers and agents that need
reproducible findings without granting a model authority over the final verdict.

## What It Is

Bayesilisk is designed to find "bad spots" in authorization and data-boundary
logic before those gaps become hard-to-debug application bugs.

It checks scenarios involving:

- permission and role-route matrices;
- customer module entitlements;
- expense approval and receipt evidence;
- billing export access;
- HR document access boundaries;
- support takeover sessions;
- DMS tenant and process boundaries;
- travel funding and travel-expense consistency.

The core verifier is deterministic:

```text
scenario facts -> invariant checks -> pass/fail -> Bayesian ranking
```

No embedding, model output, issue text, or Playwright observation can directly
declare a bug. Those layers can only steer where Bayesilisk looks next.

See [DESIGN.md](DESIGN.md) for the governing architecture:

```text
Playwright is the sensor.
Grassmann attention is the router.
The scenario proposer model is the proposer.
Bayesilisk is the judge.
```

## Quick Start

Run the CLI from the repository root:

```sh
python3 -m bayesilisk --seed 150 --format json
python3 -m bayesilisk --seed 150 --format markdown --output /tmp/bayesilisk.md
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-context.json --issue-payloads
```

After installation, the same entry points are available as:

```sh
bayesilisk --seed 150 --format json
bayesilisk-mcp
```

Run the test suite:

```sh
python3 -m pytest
```

GitHub CI runs deterministic tests and the Sphinx docs build without Ollama,
hosted models, browser services, or hidden local state:

```sh
python3 -m pytest -m "not live_playwright and not live_ollama"
sphinx-build -b html docs docs/_build/html
```

Live browser/model checks are local opt-in tests:

```sh
python3 -m pytest tests/test_live_integrations.py -m live_playwright -rs
BAYESILISK_LIVE_OLLAMA=1 python3 -m pytest tests/test_live_integrations.py -m live_ollama -rs
```

## Reports

Reports include:

- seed and tool version;
- deterministic production-access boundary;
- scenario fragments and generated sub-scenarios;
- access patterns;
- expected invariant and observed result;
- stable fingerprint and dedupe key;
- classification and issue readiness;
- attention score and attention reasons when context is supplied;
- posterior probability and risk score;
- suggested issue title and body.

Only findings with:

```text
observedResult = fail
issueReadiness = ready-for-issue
```

should be opened automatically. `probe-only`, `regression-watch`,
`do-not-open-muted`, and `no-issue-control` findings are intentionally not
automatic issue material.

## Proof Artifacts

![Bayesilisk proof loop](docs/assets/bayesilisk-proof-loop.gif)

The proof loop is deliberately split:

```text
Playwright evidence -> Grassmann attention -> model proposal -> Bayesilisk verification -> issue payload
```

Example artifacts:

- [example JSON report](docs/examples/example-report.json)
- [example GitHub issue payloads](docs/examples/example-issue-payloads.json)

### Why This Is Not a Black Box

Bayesilisk exposes separate ledgers for `observedByPlaywright`,
`selectedByGrassmannAttention`, `proposedByModel`, and `verifiedByBayesilisk`.
Only `verifiedByBayesilisk` contains deterministic invariant results that can
feed issue payloads. Model output remains untrusted candidate input.

### Model Unavailable? Still Works

The default verifier path requires no model provider. With no Ollama or hosted
model configured, Bayesilisk still composes deterministic scenarios, evaluates
finite-state invariants, ranks findings, validates report schemas, and emits
issue payloads from verified failures.

## Microsoft Playwright Bridge

Bayesilisk includes a static demo target and an optional Microsoft Playwright
probe. Playwright observes concrete browser behavior and writes Bayesilisk
context; Bayesilisk still performs deterministic verification afterward.

Install the optional browser dependency:

```sh
python3 -m pip install -e '.[playwright]'
python3 -m playwright install chromium
```

Run the bundled demo probe:

```sh
python3 tools/playwright_probe.py --demo --output /tmp/bayesilisk-playwright-context.json
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format markdown
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --issue-payloads
```

The demo page is local and static. It intentionally includes a few wrong observed
statuses so the probe can produce route, role, and invariant context without
touching production systems.

## Grassmann Attention

Contextual reports include a bounded Grassmann-style attention layer. It treats
Playwright observations, repository facts, issue text, and invariant descriptions
as local context planes, then scores which planes look bad or under-tested.

By default this uses a dependency-free anchor-plane proxy. Set
`BAYESILISK_USE_OLLAMA_EMBEDDINGS=1` to add Ollama `/api/embed` similarities with
`BAYESILISK_OLLAMA_MODEL`, defaulting to `nomic-embed-text`.

Attention scores answer:

```text
Where should Bayesilisk look next?
```

Risk scores answer:

```text
Given this deterministic rule result, how important is this finding?
```

Those are deliberately separate.

## Scenario Proposer Model

Set `BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1` to let a local scenario proposer
model suggest extra scenario compositions through Ollama `/api/chat`.

The preferred local proposer is `gemma4:e2b`:

```sh
BAYESILISK_USE_OLLAMA_SCENARIO_MODEL=1 \
BAYESILISK_OLLAMA_SCENARIO_MODEL=gemma4:e2b \
python3 -m bayesilisk --seed 150 --context /tmp/bayesilisk-playwright-context.json --format json
```

Model output is untrusted. Bayesilisk accepts a proposal only if it uses known
fragment ids and invariant ids, targets a selected attention plane, and passes
schema validation. Accepted proposals appear as `generated.model.*` scenarios
with `weak-model-proposal:*` provenance for compatibility with the earlier
report field name.

## MCP Server

Bayesilisk includes a small stdio MCP tool server:

```sh
python3 -m bayesilisk.mcp_server
```

It exposes:

- `bayesilisk.run`;
- `bayesilisk.rank_context`;
- `bayesilisk.issue_payloads`.

Agents should pass current issue lists, open PRs, branch facts, local verifier
notes, Playwright observations, and known Bayesilisk fingerprints as context.
The MCP server still runs locally and does not mutate GitHub or production
systems.

## Documentation

Sphinx documentation lives in [docs/](docs/). The GitHub Pages workflow builds it
with MyST Markdown support and publishes it from GitHub Actions.

Local docs build:

```sh
python3 -m pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

## Development Notes

The test suite includes scenario-matrix coverage:

- every catalog scenario must reference valid fragments and invariants;
- every invariant must have at least one passing control and one failing
  bad-spot case in the deterministic catalog;
- Playwright, Grassmann attention, and model proposals must not override
  finite-state verifier results.

Current public planning issues are tracked in GitHub Issues.

## Boundaries

Bayesilisk is a verifier and prioritizer, not an authorization engine. It must
not connect to production systems, inspect live customer data, create migrations,
or emit internal platform claims as customer package claims.
