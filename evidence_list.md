# Bayesilisk Evidence List

This file tracks the evidence needed for a concise Bayesilisk paper and the
current Cal.com artifact status.

## Research Claim

LLMs are useful for proposing scenario spaces, but unsafe as test oracles.
Bayesilisk separates proposal from verification using connector-provided app
context, deterministic rules, and evidence-bearing probes.

## Evidence Goals

- [x] A clear baseline comparison against existing E2E tests and
  Playwright-only probing for Cal.com.
- [x] Quantitative evidence that a weaker local proposal model can produce
  invalid proposals that need finite-state verifier gates.
- [x] A full LLM-agent-only browser-driving baseline.
- [x] A longer sequence not caught by the nearby existing E2E run.
- [ ] Generic Bayesilisk synthesis of longer multi-action runs while keeping the
  connector as a pure action executor.

## Baselines

Compare against:

- [x] Existing E2E tests alone:
  `examples/calcom/baselines/existing-e2e-nearby.json`
- [x] Playwright-only probing:
  `examples/calcom/baselines/playwright-only-probe.json`,
  `examples/calcom/baselines/playwright-only-context.json`, and
  `examples/calcom/baselines/playwright-only-report.md`
- [x] LLM proposals without deterministic verifier, captured as raw weak-model
  proposal output:
  `examples/calcom/weak-model/qwen2.5-coder-3b-source-report.json`
- [x] Bayesilisk with weaker local model proposals plus verifier:
  `examples/calcom/weak-model/qwen2.5-coder-3b-source-report.json`
- [x] Full LLM agent driving Playwright directly:
  `examples/calcom/baselines/llm-agent-oracle.e2e.ts`,
  `examples/calcom/baselines/llm-agent-oracle-run.json`, and
  `examples/calcom/baselines/llm-agent-oracle-result.json`

## Key Result To Chase

Show that Bayesilisk recovers failures that:

- [x] Existing tests do not cover.
- [ ] A plain LLM agent misses or misjudges. The current browser-driving
  10-run baseline misjudged the observed failure in `3` of `10` trials.
- [x] A weaker model may propose noisily, but the verifier prevents false oracle
  claims.

## Artifact Story

Every app needs:

- [x] Repo URL and commit hash.
- [x] Connector code.
- [x] Context JSON.
- [x] Generated proposals.
- [x] Execution evidence.
- [x] Bayesilisk report.
- [x] Baseline run logs.

## Cal.com Artifact Status

App under test:

- Repository: `https://github.com/calcom/cal.com`
- Local checkout: `/private/tmp/bayesilisk-eval-calcom`
- Tested commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Commit date: `2026-05-14 19:30:21 +0000`
- Commit subject: `fix: add system-ui fallback to font stack for non-Latin script support (#29346)`
- Bayesilisk seed: `150`

Checked-in artifacts:

- Connector code: `examples/calcom/bayesilisk-probes.e2e.ts`
- Source context: `examples/calcom/source-context.json`
- Generated proposals: `examples/calcom/generated-proposals.json`
- Execution evidence: `examples/calcom/execution-context.json`
- Bayesilisk JSON report: `examples/calcom/reports/report.json`
- Bayesilisk Markdown report: `examples/calcom/reports/report.md`
- Issue payloads: `examples/calcom/reports/issue-payloads.json`
- Baseline summary: `examples/calcom/baselines/README.md`
- Existing nearby E2E baseline:
  `examples/calcom/baselines/existing-e2e-nearby.json`
- Playwright-only connector baseline:
  `examples/calcom/baselines/playwright-only-probe.json`
- Playwright-only connector context:
  `examples/calcom/baselines/playwright-only-context.json`
- Playwright-only Bayesilisk report:
  `examples/calcom/baselines/playwright-only-report.md`
- Weak local model report:
  `examples/calcom/weak-model/qwen2.5-coder-3b-source-report.json`
- LLM-agent browser baseline:
  `examples/calcom/baselines/llm-agent-oracle.e2e.ts`
- LLM-agent browser run log:
  `examples/calcom/baselines/llm-agent-oracle-run.json`
- LLM-agent oracle result:
  `examples/calcom/baselines/llm-agent-oracle-result.json`
- LLM-agent 10-run browser baseline:
  `examples/calcom/baselines/llm-agent-oracle-10.jsonl`
- LLM-agent 10-run browser run log:
  `examples/calcom/baselines/llm-agent-oracle-10-run.json`
- LLM-agent 10-run summary:
  `examples/calcom/baselines/llm-agent-oracle-10-summary.json`

Observed Cal.com result:

- Source facts supplied by the connector: `3`
- Generated probe proposals: `6`
- Executed connector observations: `6`
- Verified `breakage.context-observed` findings: `6`
- Failure pattern: expected semantic status `404`, observed semantic status
  `200` for unknown or stale `rescheduleUid` variants.

Baseline comparison:

- Nearby upstream E2E files:
  `apps/web/playwright/booking-seats.e2e.ts` and
  `apps/web/playwright/dynamic-booking-pages.e2e.ts`
- Nearby upstream E2E result: `13` expected passed tests, `1` skipped test,
  `0` unexpected failures.
- Playwright-only connector result: `11` observations, `7` passing controls,
  `4` failing observations.
- Bayesilisk generated-proposal result: `6` generated proposals and `6`
  verified unknown/stale `rescheduleUid` findings across public, private, and
  dynamic booking routes.
- Weak local model result using `qwen2.5-coder:3b`: `3` raw proposals, `0`
  accepted, `3` rejected by verifier gates.
- LLM-agent browser baseline using `qwen2.5-coder:3b`: in `10` stochastic runs,
  the agent selected the malformed unknown-`rescheduleUid` URL `6` times,
  selected the plain control URL `1` time, produced invalid selections `3`
  times, matched the deterministic oracle `7` times, and mismatched it `3`
  times.

Observed variants:

- Public booking page with unknown `rescheduleUid`.
- Public booking page with stale `rescheduleUid`.
- Private booking link with unknown `rescheduleUid`.
- Private booking link with stale `rescheduleUid`.
- Dynamic booking page with unknown `rescheduleUid`.
- Dynamic booking page with stale `rescheduleUid`.
- Cancelled booking UID replay through public booking route after creating and
  cancelling a real booking.

Known limitations for the current Cal.com artifact:

- The longer cancelled-booking replay was executed by the Cal.com connector
  baseline. It is evidence that the failure exists, but not yet evidence that
  Bayesilisk generically synthesizes longer multi-action runs.
- The browser-driving LLM-agent baseline is a small sample (`10` trials) using
  one local model. It shows stochastic oracle and action-selection fragility,
  but should not be overgeneralized to all models or prompting strategies.

Architecture note for longer runs:

- Desired connector role: expose action vocabulary, actor/session fixtures,
  state-producing actions, route/action parameter bindings, and observed
  evidence.
- Desired Bayesilisk role: generate bounded action sequences from those
  connector-declared capabilities, rank them with attention, and verify returned
  evidence against deterministic rules.
- Desired connector execution contract: execute a proposed sequence exactly and
  report observations; do not decide pass/fail and do not filter app-specific
  scenarios beyond declaring unsupported actions.

Completed Cal.com evidence runs:

- Run and preserve the nearby upstream E2E tests that motivated the source
  facts: complete.
- Run a Playwright-only probe baseline with the same connector actions but no
  Bayesilisk proposal expansion: complete.
- Run a weaker local model proposal pass and record proposal count, invalid
  proposal count, executed proposal count, and verifier-confirmed findings:
  complete.
- Run a full LLM-agent-only browser-driving baseline and record proposed
  actions, pass/fail claims, and oracle mistakes: complete. The 10-run sample
  produced `3` oracle mismatches.
- Add at least one longer workflow probe around booking/reschedule state if the
  Cal.com fixtures support it reliably: complete.

Remaining Cal.com evidence to collect:

- Add generic Bayesilisk sequence proposal so longer runs can be generated from
  connector-declared capabilities instead of handwritten connector probe logic.
- Repeat the LLM-agent-only baseline with additional local and hosted models if
  the paper needs broader model coverage.
