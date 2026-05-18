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
`rescheduleUid` context. Bayesilisk generated 6 probe proposals. The local
Cal.com connector executed those 6 proposals against local fixtures.

Observed locally:

| Area | Mutation | Expected | Observed |
| --- | --- | ---: | ---: |
| Public booking page with `rescheduleUid` | unknown id | 404 | 200 |
| Public booking page with `rescheduleUid` | stale id | 404 | 200 |
| Private booking link with `rescheduleUid` | unknown id | 404 | 200 |
| Private booking link with `rescheduleUid` | stale id | 404 | 200 |
| Dynamic booking page with `rescheduleUid` | unknown id | 404 | 200 |
| Dynamic booking page with `rescheduleUid` | stale id | 404 | 200 |

These are local fixture observations. They are not production observations.

Strict connector-contract check for these artifacts:

```json
{
  "sourceFactCount": 3,
  "observedFactCount": 6,
  "violations": []
}
```

## Files

- [bayesilisk-probes.e2e.ts](bayesilisk-probes.e2e.ts): Cal.com Playwright connector example.
- [source-context.json](source-context.json): connector source facts and explicit proposal rules.
- [generated-proposals.json](generated-proposals.json): proposals emitted by Bayesilisk from the supplied rules.
- [execution-context.json](execution-context.json): observed connector evidence after executing proposals.
- [reports/report.json](reports/report.json): full Bayesilisk JSON report.
- [reports/report.md](reports/report.md): full Bayesilisk Markdown report.
- [reports/issue-payloads.json](reports/issue-payloads.json): connector-only issue-ready payloads generated from verified findings.

## Reproduce The Bayesilisk Steps

From the Bayesilisk repository root:

```sh
python3 -m bayesilisk \
  --context examples/calcom/source-context.json \
  --probe-proposals-output /tmp/calcom-bayesilisk-proposals.json
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
```

Finally, run Bayesilisk over the observed execution context:

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

## Boundary

This example intentionally keeps Cal.com-specific knowledge in the connector
files and context. Bayesilisk core only expands supplied proposal rules and
verifies observed evidence.
