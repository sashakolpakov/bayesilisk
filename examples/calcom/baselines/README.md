# Cal.com Clean Rerun Artifacts

These are the current run logs for the Cal.com Bayesilisk example. They are not
historical baseline archives.

Tested app revision:

- Repository: `https://github.com/calcom/cal.com`
- Commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Local checkout used for the runs: `/private/tmp/bayesilisk-eval-calcom`

## Current Runs

The current package was rebuilt from scratch on May 19, 2026:

1. Bayesilisk generated 6 route-mutation proposals from `source-context.json`.
2. Bayesilisk generated 1 typed-ABAG workflow sequence from
   `sequence-source-context.json`.
3. The Cal.com Playwright connector executed those proposals against the local
   checkout.
4. `../execution-context.json` was consolidated only from the fresh connector
   observations.

Artifacts:

- `generated-proposals-run.json`: Playwright run for the 6 generated
  unknown/stale `rescheduleUid` proposals.
- `generated-sequence-run.json`: Playwright run for the generated bounded
  workflow sequence.

Summary:

- Generated unknown/stale proposals: `6`
- Generated workflow-sequence proposals: `1`
- Connector observations: `7`
- Verified app findings: `7`
- Unexpected Playwright test failures: `0`

Findings:

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
- Cancelled booking UID replay through public booking route: expected `409`,
  observed `200`.

The consolidated evidence is in `../execution-context.json`. The app-only
Bayesilisk report and issue payloads are in `../reports/`.
