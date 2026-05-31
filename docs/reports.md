# Reports

Bayesilisk emits JSON and Markdown. JSON is the stable integration format. Markdown is intended for humans reviewing findings.

## Main Fields

A full report includes:

- seed and tool version;
- effective configuration for attention, embeddings, model proposals, and safe base URL class;
- production-access boundary;
- scenario id and title;
- fragments and generated sub-scenarios;
- access pattern and domains;
- invariant id, layer, and expectation;
- observed result and observation detail;
- fingerprint and dedupe key;
- issue readiness;
- attention score and reasons;
- posterior probability and risk score;
- suggested issue title and body.
- safe model proposal provenance for accepted model-proposed scenarios.

Contextual reports also expose four first-class ledgers:

- `observedByPlaywright`: concrete browser evidence supplied by Playwright;
- `selectedByGrassmannAttention`: invariant planes selected for exploration;
- `proposedByModel`: untrusted scenario proposal activity;
- `verifiedByBayesilisk`: deterministic invariant results that issue payloads may use.

## Finding Status

`observedResult` is deterministic:

- `fail`: the invariant did not hold for the scenario facts;
- `pass`: the invariant held;
- `probe`: the scenario is not confirmed enough to treat as a failure.

`issueReadiness` controls automation:

- `ready-for-issue`: safe to create an issue if it is not a duplicate;
- `probe-only`: needs a local verifier or human confirmation first;
- `regression-watch`: previously fixed or watched finding;
- `do-not-open-muted`: intentionally muted;
- `no-issue-control`: passing or control scenario.

Issue automation should require both:

```text
observedResult = fail
issueReadiness = ready-for-issue
```

## Scores

`riskScore` is a Bayesian-style priority after deterministic verification. It answers how important a verified result appears.

`attentionScore` is an exploration score. It answers where Bayesilisk should look next.

Keeping these separate prevents embeddings or model output from becoming a hidden bug oracle.

Muted, fixed, or regression-watch invariant planes can apply
`decayForFixedOrMuted` to attention. That lowers future exploration priority but
does not hide deterministic failures or alter `riskScore`.

## Fingerprints

Bayesilisk fingerprints are stable identifiers derived from verified scenario and invariant data. Use them to dedupe issues, mute noisy probes, and mark fixed regressions in observation history.

## Issue Payloads

The `--issue-payloads` mode emits deduped issue payloads for ready failed findings:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/context.json --issue-payloads
```

The CLI does not mutate issue trackers. It returns payloads that another trusted workflow can review and submit.

When a finding came from a model-proposed scenario, issue payloads include the
same safe `modelProvenance` object as the report. This provenance is intended for
auditability only; it does not make the model output trusted.

## Proof Artifacts

Downloadable examples:

- {download}`Example JSON report <examples/example-report.json>`
- {download}`Example GitHub issue payloads <examples/example-issue-payloads.json>`

The README includes a proof-loop diagram, and the same boundary is represented
as a text flow here:

```text
Playwright evidence
  -> Grassmann attention
  -> candidate scenario from catalog, rules, or model
  -> Bayesilisk deterministic verification
  -> ready issue payload or reject/watchlist
```

### Why This Is Not a Black Box

Bayesilisk reports keep evidence, routing, proposal, and verification separate:

- `observedByPlaywright` is browser evidence;
- `selectedByGrassmannAttention` is routing telemetry;
- `proposedByModel` is untrusted candidate scenario activity;
- `verifiedByBayesilisk` is the deterministic verifier ledger.

The issue-worthy result must come from `verifiedByBayesilisk`.

### Model Unavailable? Still Works

The default report path does not require Ollama, hosted model APIs, API keys, or
browser services. A fixed seed with the same local inputs still produces the
same report, schema validation, fingerprints, risk scores, and issue payloads.
