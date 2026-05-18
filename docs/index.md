# Bayesilisk

```{image} ../logo/bayesilisk_logo.png
:alt: Bayesilisk logo
:width: 180px
:align: center
```

Bayesilisk is a deterministic local layer for permission, entitlement, route,
and data-boundary sitting over Playwright, with Grassmann attention, and
LLM-generated scenario-proposal workflows gated by a finite-state verifier.

**Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the Oracle.**

It is built for testers and agents that need reproducible findings, stable
fingerprints, and issue-ready output without granting a model authority over the
final verdict.

```text
Playwright is the sensor.
Grassmann attention is the router.
The scenario proposer model is the proposer.
Bayesilisk is the judge.
```

The rule engine remains deterministic:

```text
scenario facts -> invariant checks -> pass/fail -> Bayesian ranking
```

```{toctree}
:maxdepth: 2
:caption: Contents

quickstart
architecture
reports
integrations
connectors
development
bayesilisk
```

## Why It Exists

Complex application suites often have permission and data-boundary bugs that
cross feature lines: HR documents plus support takeover, expenses plus DMS
receipts, travel funding plus approval routes, or billing exports plus customer
module entitlements. Bayesilisk provides a local way to compose those cases,
evaluate explicit invariants, and rank findings for follow-up work.

## What It Does Not Do

Bayesilisk does not:

- connect to production systems;
- inspect live customer data;
- mutate issue trackers, databases, or application state;
- let embeddings or model output declare a bug;
- replace application-level authorization checks.

It is a verifier and prioritizer, not an authorization engine.
