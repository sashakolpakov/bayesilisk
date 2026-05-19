# Bayesilisk Evidence List

This file tracks the current clean Cal.com artifact set and the manuscript
evidence still needed. Historical baseline run logs are intentionally not kept
in `examples/calcom`.

## Research Claim

LLMs are useful for proposing scenario spaces, but unsafe as test oracles.
Bayesilisk separates proposal from verification using connector-provided app
context, deterministic rules, and evidence-bearing probes.

## Current Cal.com Artifact

App under test:

- Repository: `https://github.com/calcom/cal.com`
- Local checkout: `/private/tmp/bayesilisk-eval-calcom`
- Tested commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Commit date: `2026-05-14 19:30:21 +0000`
- Commit subject: `fix: add system-ui fallback to font stack for non-Latin script support (#29346)`
- Bayesilisk seed: `150`

Checked-in current artifacts:

- Connector code: `examples/calcom/bayesilisk-probes.e2e.ts`
- Rule context: `examples/calcom/source-context.json`
- Generated route proposals: `examples/calcom/generated-proposals.json`
- Sequence context: `examples/calcom/sequence-source-context.json`
- Generated sequence proposal: `examples/calcom/generated-sequence-proposals.json`
- Consolidated execution evidence: `examples/calcom/execution-context.json`
- Route-proposal Playwright run log:
  `examples/calcom/baselines/generated-proposals-run.json`
- Sequence Playwright run log:
  `examples/calcom/baselines/generated-sequence-run.json`
- App-only JSON report: `examples/calcom/reports/report.json`
- App-only Markdown report: `examples/calcom/reports/report.md`
- App-only issue payloads: `examples/calcom/reports/issue-payloads.json`
- Upstream human-response references:
  `examples/calcom/upstream-outcomes.md`

Clean rerun result:

- Generated route proposals: `6`
- Generated workflow-sequence proposals: `1`
- Connector observations: `7`
- Verified `breakage.context-observed` app findings: `7`
- Unexpected Playwright test failures: `0`

Upstream response:

- Public unknown/stale `rescheduleUid` was reported as
  `calcom/cal.diy#29399`.
- Private booking-link `rescheduleUid` was added as a related Bayesilisk
  comment on `calcom/cal.diy#29399`.
- A contributor opened fix PR `calcom/cal.diy#29400`, identifying the root
  cause as a missing null guard in `processReschedule`.
- Cancelled booking UID replay was reported as `calcom/cal.diy#29407` and is
  still awaiting upstream response at capture time.

Observed variants:

- Public booking page with unknown `rescheduleUid`: expected `404`, observed
  `200`.
- Public booking page with stale `rescheduleUid`: expected `404`, observed
  `200`.
- Private booking link with unknown `rescheduleUid`: expected `404`, observed
  `200`.
- Private booking link with stale `rescheduleUid`: expected `404`, observed
  `200`.
- Dynamic booking page with unknown `rescheduleUid`: expected `404`, observed
  `200`.
- Dynamic booking page with stale `rescheduleUid`: expected `404`, observed
  `200`.
- Cancelled booking UID replay through public booking route after creating and
  cancelling a real booking: expected `409`, observed `200`.

## Manuscript Evidence Still Needed

- Recreate baseline comparisons as fresh, separately named runs when needed:
  existing E2E, Playwright-only probing, LLM-agent-only browser driving, and
  weak-model proposals without deterministic verification.
- Add at least one second real-app artifact with the same clean artifact
  discipline: repo URL, commit hash, connector, context, generated proposals,
  execution evidence, app-only report, and issue payloads.
- Broaden the LLM-agent baseline across additional local or hosted models if
  the paper needs a model-robust oracle-safety claim.

## Architecture Boundary

- Bayesilisk now generates bounded action-sequence proposals from
  connector-declared capabilities.
- The connector remains the app-specific executor for concrete fixture
  operations.
- This is not arbitrary free-form browser-run synthesis; ranking with attention
  and richer sequence search remain future extensions.
