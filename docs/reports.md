# Reports

Bayesilisk emits JSON and Markdown. JSON is the stable integration format. Markdown is intended for humans reviewing findings.

## Main Fields

A full report includes:

- seed and tool version;
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

## Fingerprints

Bayesilisk fingerprints are stable identifiers derived from verified scenario and invariant data. Use them to dedupe issues, mute noisy probes, and mark fixed regressions in observation history.

## Issue Payloads

The `--issue-payloads` mode emits deduped issue payloads for ready failed findings:

```sh
python3 -m bayesilisk --seed 150 --context /tmp/context.json --issue-payloads
```

The CLI does not mutate issue trackers. It returns payloads that another trusted workflow can review and submit.
