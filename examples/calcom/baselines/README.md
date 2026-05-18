# Cal.com Baseline Evidence

These artifacts compare the Bayesilisk Cal.com connector result against nearby
baseline workflows.

Tested app revision:

- Repository: `https://github.com/calcom/cal.com`
- Commit: `180ede28f0bddf2738933a6e60a8e80f6116d7da`
- Local checkout used for the runs: `/private/tmp/bayesilisk-eval-calcom`

## Existing E2E Tests Alone

Artifact: `existing-e2e-nearby.json`

Command:

```sh
NEXTAUTH_SECRET=secret \
CALENDSO_ENCRYPTION_KEY=secret \
NEXT_PUBLIC_WEBAPP_URL=http://localhost:3000 \
NEXT_PUBLIC_WEBSITE_URL=http://localhost:3000 \
NEXTAUTH_URL=http://localhost:3000 \
DATABASE_URL=postgresql://postgres:@localhost:5450/calendso \
NEXT_PUBLIC_IS_E2E=1 \
node .yarn/releases/yarn-4.12.0.cjs playwright test \
  apps/web/playwright/booking-seats.e2e.ts \
  apps/web/playwright/dynamic-booking-pages.e2e.ts \
  --project=@calcom/web \
  --workers=1 \
  --reporter=json
```

Summary:

- Specs collected: `14`
- Expected passed tests: `13`
- Skipped tests: `1`
- Unexpected failures: `0`
- Duration: about `33.0s`

Interpretation: the nearby upstream E2E tests passed while the Bayesilisk
proposal run still found unknown/stale `rescheduleUid` cases with expected
semantic status `404` and observed semantic status `200`.

## Playwright-Only Connector Baseline

Artifacts:

- `playwright-only-probe.json`
- `playwright-only-context.json`
- `playwright-only-report.md`
- `llm-agent-oracle.e2e.ts`
- `llm-agent-oracle-run.json`
- `llm-agent-oracle-result.json`
- `llm-agent-oracle-10.jsonl`
- `llm-agent-oracle-10-run.json`
- `llm-agent-oracle-10-summary.json`

Command:

```sh
NEXTAUTH_SECRET=secret \
CALENDSO_ENCRYPTION_KEY=secret \
NEXT_PUBLIC_WEBAPP_URL=http://localhost:3000 \
NEXT_PUBLIC_WEBSITE_URL=http://localhost:3000 \
NEXTAUTH_URL=http://localhost:3000 \
DATABASE_URL=postgresql://postgres:@localhost:5450/calendso \
NEXT_PUBLIC_IS_E2E=1 \
BAYESILISK_CONTEXT_OUTPUT=/private/tmp/calcom-playwright-only-context.json \
node .yarn/releases/yarn-4.12.0.cjs playwright test \
  apps/web/playwright/bayesilisk-probes.e2e.ts \
  --project=@calcom/web \
  --workers=1 \
  --reporter=json
```

Summary:

- Playwright test status: passed.
- Connector observations: `11`
- Passing control observations: `7`
- Failing observations: `4`

The four failing observations were:

- Cancelled booking UID replay through public booking route: expected `409`,
  observed `200`.
- Unknown public booking `rescheduleUid`: expected `404`, observed `200`.
- Unknown dynamic booking `rescheduleUid`: expected `404`, observed `200`.
- Unknown private booking-link `rescheduleUid`: expected `404`, observed `200`.

Interpretation: hand-written Playwright connector probes can expose some of the
same class of bug, but Bayesilisk's proposal expansion produced the broader
unknown/stale Cartesian expansion across all three connector-supplied routes.
The cancelled-booking replay is a longer multi-step fixture sequence:
create booking, cancel booking, then replay the cancelled UID through the public
booking route.

## LLM-Agent Browser Baseline

Artifacts:

- `llm-agent-oracle.e2e.ts`
- `llm-agent-oracle-run.json`
- `llm-agent-oracle-result.json`
- `llm-agent-oracle-10.jsonl`
- `llm-agent-oracle-10-run.json`
- `llm-agent-oracle-10-summary.json`

Command:

```sh
NEXTAUTH_SECRET=secret \
CALENDSO_ENCRYPTION_KEY=secret \
NEXT_PUBLIC_WEBAPP_URL=http://localhost:3000 \
NEXT_PUBLIC_WEBSITE_URL=http://localhost:3000 \
NEXTAUTH_URL=http://localhost:3000 \
DATABASE_URL=postgresql://postgres:@localhost:5450/calendso \
NEXT_PUBLIC_IS_E2E=1 \
BAYESILISK_LLM_AGENT_OUTPUT=/private/tmp/calcom-llm-agent-oracle.json \
BAYESILISK_OLLAMA_BASE_URL=http://localhost:11434 \
BAYESILISK_LLM_AGENT_MODEL=qwen2.5-coder:3b \
node .yarn/releases/yarn-4.12.0.cjs playwright test \
  apps/web/playwright/llm-agent-oracle.e2e.ts \
  --project=@calcom/web \
  --workers=1 \
  --reporter=json
```

Summary:

- Local model: `qwen2.5-coder:3b`
- Browser-driving test status: passed.
- Single-run artifact: the agent selected the unknown-`rescheduleUid` candidate
  URL and judged the observed `200` as a failure, matching the deterministic
  check.
- Ten-run stochastic sample:
  - Runs: `10`
  - Selected malformed unknown-`rescheduleUid` URL: `6`
  - Selected plain control URL: `1`
  - Invalid/unusable selection: `3`
  - Oracle matched deterministic check: `7`
  - Oracle mismatched deterministic check: `3`

Interpretation: this is now a full browser-driving LLM-agent baseline artifact,
and the 10-run sample shows stochastic fragility. In three runs the model
selected the malformed URL, observed semantic status `200`, and still judged the
invariant as `pass`. It also emitted unstable expected statuses, including
numeric `400`, numeric `404`, string `"400 Bad Request"`, prose instead of a
status code, and `null`. This is direct evidence for keeping the oracle
deterministic.

## LLM-Proposal / Weak-Model Baseline

Artifact: `../weak-model/qwen2.5-coder-3b-source-report.json`

Command:

```sh
python -m bayesilisk \
  --seed 150 \
  --context examples/calcom/source-context.json \
  --enable-scenario-proposer \
  --scenario-provider ollama \
  --scenario-model qwen2.5-coder:3b \
  --ollama-base-url http://localhost:11434 \
  --format json \
  --output examples/calcom/weak-model/qwen2.5-coder-3b-source-report.json
```

Summary:

- Local model: `qwen2.5-coder:3b`
- Raw model proposals: `3`
- Accepted model proposals: `0`
- Rejected model proposals: `3`
- Rejection reasons: `invalid-fragment-count` (`1`),
  `target-plane-not-selected` (`2`)
- Bayesilisk connector-rule proposals from the same context: `6`

Interpretation: the weaker local model produced plausible-looking but invalid
scenario proposals against the selected verifier planes. The finite-state
verifier rejected them before execution. This is evidence for the paper claim
that models may propose, but should not act as the oracle.

## Longer-Sequence Evidence

The Playwright-only connector baseline includes longer controls around:

- Cancelled booking direct reschedule.
- Reschedule UID for another event type.
- Disabled event type cancellation.
- Superseded password reset token.
- Seated booking cancellation with missing or random seat references.

Most longer controls passed in this Cal.com run, but one longer multi-step
sequence failed:

```text
create booking -> cancel booking -> replay cancelled booking UID as public
rescheduleUid -> normal booking page opens
```

Current architectural boundary: this longer sequence was executed by the
Cal.com connector baseline. Bayesilisk does not yet synthesize arbitrary
multi-action sequences from an app action graph while keeping the connector as a
pure executor. The intended next layer is generic sequence proposal over
connector-declared actions and state facts.
