# Cal.com Connector Example

This is a worked real-app connector example for Bayesilisk.

It demonstrates the intended split with the general Bayesilisk core:

```text
Cal.com connector context -> Bayesilisk proposal expansion -> Cal.com connector execution -> Bayesilisk verification
```

Bayesilisk core does not know Cal.com semantics. The connector context supplies
the Cal.com-specific routes, actions, expected statuses, and proposal rules.
Bayesilisk expands those rules and later verifies observed status facts.

The connector is the only app-specific piece. It follows the connector contract
in [docs/connectors.md](../../docs/connectors.md): source facts declare
`routePattern`, `params`, `expectedBehavior.status`, `proposalRules`, and
`availableActions`; observed facts declare `expectedStatus`, `observedStatus`,
and `passed` from local Playwright/API execution.

Explanatory prose is still useful. The `text`, `sourceText`, and `nearbyTests`
fields can help Grassmann attention route and rank the investigation. They do
not authorize proposal expansion by themselves, and they do not decide pass or
fail.

## Version Tested

- App: Cal.com local checkout
- Repository: `https://github.com/calcom/cal.com`
- Commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Commit date: `2026-05-14 19:30:21 +0000`
- Commit subject: `fix: add system-ui fallback to font stack for non-Latin script support (#29346)`
- Bayesilisk seed: `150`

## Observed Result

The connector supplied source-backed proposal rules around stale or unknown
`rescheduleUid` context, plus an action graph for cancelled-booking replay.
Bayesilisk generated 7 probe proposals. The local Cal.com connector executed
those 7 proposals against local fixtures.

Observed locally:

| Area | Mutation | Expected | Observed |
| --- | --- | ---: | ---: |
| Public booking page with `rescheduleUid` | unknown id | 404 | 200 |
| Public booking page with `rescheduleUid` | stale id | 404 | 200 |
| Private booking link with `rescheduleUid` | unknown id | 404 | 200 |
| Private booking link with `rescheduleUid` | stale id | 404 | 200 |
| Dynamic booking page with `rescheduleUid` | unknown id | 404 | 200 |
| Dynamic booking page with `rescheduleUid` | stale id | 404 | 200 |
| Cancelled booking UID replay through public route | replay cancelled uid | 409 | 200 |

These are local fixture observations. They are not production observations.

Current run logs in [baselines](baselines/) include:

- `generated-proposals-run.json`: the 6 unknown/stale `rescheduleUid` probes.
- `generated-sequence-run.json`: the generated cancelled-booking workflow
  sequence.

Strict connector-contract check for these artifacts:

```json
{
  "sourceFactCount": 4,
  "observedFactCount": 7,
  "violations": []
}
```

## Files

- [bayesilisk-probes.e2e.ts](bayesilisk-probes.e2e.ts): Cal.com Playwright connector example.
- [source-context.json](source-context.json): connector source facts and explicit proposal rules.
- [generated-proposals.json](generated-proposals.json): proposals emitted by Bayesilisk from the supplied rules.
- [sequence-source-context.json](sequence-source-context.json): connector-declared action graph for a longer workflow.
- [generated-sequence-proposals.json](generated-sequence-proposals.json): bounded workflow proposal emitted from the action graph.
- [execution-context.json](execution-context.json): consolidated observed connector evidence after executing all 7 proposals.
- [baselines/generated-proposals-run.json](baselines/generated-proposals-run.json): Playwright run log for the 6 generated route probes.
- [baselines/generated-sequence-run.json](baselines/generated-sequence-run.json): Playwright run log for the generated workflow sequence.
- [reports/report.json](reports/report.json): app-only Bayesilisk JSON report for the 7 findings.
- [reports/report.md](reports/report.md): app-only Bayesilisk Markdown report for the 7 findings.
- [reports/issue-payloads.json](reports/issue-payloads.json): connector-only issue-ready payloads generated from verified findings.
- [upstream-outcomes.md](upstream-outcomes.md): upstream issue/PR references showing human response to reported findings.

## Reproduce The Bayesilisk Steps

From the Bayesilisk repository root:

```sh
python3 -m bayesilisk \
  --context examples/calcom/source-context.json \
  --probe-proposals-output /tmp/calcom-bayesilisk-proposals.json

python3 -m bayesilisk \
  --context examples/calcom/sequence-source-context.json \
  --probe-proposals-output /tmp/calcom-bayesilisk-sequence-proposals.json
```

Then run the Cal.com connector in a local Cal.com checkout with the generated
proposal file. The example connector expects Cal.com's Playwright test
environment and local database fixtures.

```sh
BAYESILISK_PROPOSALS_INPUT=/tmp/calcom-bayesilisk-proposals.json \
BAYESILISK_CONTEXT_OUTPUT=/tmp/calcom-bayesilisk-execution-context.json \
node .yarn/releases/yarn-4.12.0.cjs playwright test \
  apps/web/playwright/bayesilisk-probes.e2e.ts \
  --project=@calcom/web \
  --workers=1

BAYESILISK_PROPOSALS_INPUT=/tmp/calcom-bayesilisk-sequence-proposals.json \
BAYESILISK_CONTEXT_OUTPUT=/tmp/calcom-bayesilisk-sequence-context.json \
node .yarn/releases/yarn-4.12.0.cjs playwright test \
  apps/web/playwright/bayesilisk-probes.e2e.ts \
  --project=@calcom/web \
  --workers=1
```

Finally, combine the observed route and sequence evidence into one execution
context, then run Bayesilisk over that consolidated context. The checked-in
`execution-context.json` and reports are the clean current rerun artifacts.

```sh
python3 -m bayesilisk \
  --seed 150 \
  --context examples/calcom/execution-context.json \
  --format markdown \
  --output /tmp/calcom-bayesilisk-report.md
```

Issue payloads:

```sh
python3 -m bayesilisk \
  --seed 150 \
  --context examples/calcom/execution-context.json \
  --issue-payloads \
  --output /tmp/calcom-bayesilisk-issue-payloads.json
```

Only `breakage.context-observed` payloads from the app connector should be used
for Cal.com issue creation.

## Boundary

This example intentionally keeps Cal.com-specific knowledge in the connector
files and context. Bayesilisk core only expands supplied proposal rules and
verifies observed evidence.

For longer workflows, the connector can expose an action graph rather than a
single action. In this example Bayesilisk composes:

```text
create-booking -> cancel-booking -> open-public-booking-route(rescheduleUid=booking.uid)
```

from `sequence-source-context.json`. The connector still executes the concrete
Cal.com fixture actions and reports observations; Bayesilisk owns the generic
bounded sequence proposal and deterministic verification boundary.
