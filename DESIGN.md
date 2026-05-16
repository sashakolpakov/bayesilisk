# Bayesilisk Design

This document is the governing design for Bayesilisk. Implementation details can evolve, but the trust boundaries in this file are non-negotiable.

## Core Principle

Bayesilisk is a deterministic verifier with optional attention and proposal layers around it.

The core rule engine remains the authority:

```text
scenario facts -> invariant checks -> pass/fail -> Bayesian ranking
```

No embedding, Grassmann score, model output, issue text, or Playwright observation may directly decide that something is a violation. Those inputs can influence where Bayesilisk looks next. They cannot override the deterministic invariant result.

## Required Ledgers

Every contextual report must keep these ledgers conceptually separate:

- `observedByPlaywright`: concrete browser or route behavior observed by Playwright, such as actor, route, expected status, observed status, and source target.
- `selectedByGrassmannAttention`: attention-plane telemetry that explains why Bayesilisk should explore a scenario family.
- `proposedByModel`: untrusted scenario candidates produced by a configured scenario proposer model, if that optional layer is enabled.
- `verifiedByBayesilisk`: deterministic invariant results, fingerprints, issue readiness, and risk scores.

The final issue-worthy result must come from `verifiedByBayesilisk`.

## Layer 1: Deterministic Core

The deterministic core owns:

- scenario fragments;
- fact merging;
- invariant evaluation;
- pass/fail observations;
- stable fingerprints and dedupe keys;
- Bayesian-style `riskScore`;
- issue readiness.

The Bayesian score is a prioritization calculation after a rule result:

```text
posterior = prior * likelihood / (prior * likelihood + (1 - prior) * (1 - likelihood))
```

`riskScore` answers:

```text
Given this scenario's deterministic rule result, how likely or important is this finding?
```

It does not answer where to explore next.

## Layer 2: Playwright as Sensor

Playwright is an observation source, not the verifier.

Playwright may provide:

- route names;
- actor roles;
- module or tenant context if the target exposes it;
- expected status;
- observed status;
- probe title;
- source URL or target identity.

Example observation plane:

```text
support + /api/hr/documents + expected 403 + observed 200
```

Bayesilisk can convert this to context, prior adjustments, and attention signals. It still must run deterministic scenario invariants before producing a verified finding.

## Layer 3: Grassmann Context Plane

The Grassmann layer is an attention router.

It takes context from:

- Playwright observations;
- route names;
- actors, modules, tenant facts, and process facts;
- issue and PR text;
- existing Bayesilisk fragments;
- invariant descriptions.

It compares local context planes such as:

```text
Playwright observed plane:
  support + /api/hr/documents + expected 403 + observed 200

Invariant plane:
  HR documents require customer HR/admin role

Scenario fragment plane:
  support takeover expired + HR document route
```

The Grassmann answer is:

```text
Which invariant or scenario plane is this evidence closest to?
```

It must not answer:

```text
Is this definitely a bug?
```

## Attention Score

`attentionScore` answers:

```text
Where should Bayesilisk look next?
```

The bounded scoring model is:

```text
attentionScore =
  0.45 * failureDensity
+ 0.25 * untestedness
+ 0.15 * sensitivity
+ 0.10 * playwrightEvidence
+ 0.05 * novelty
- decayForFixedOrMuted
```

The score is capped to `[0.0, 1.0]`.

Untested planes can raise attention. They must not automatically raise risk. Bad planes can raise attention strongly; they can affect risk only after deterministic failures or concrete Playwright evidence is converted into validated scenario context.

Reports should expose both:

```json
{
  "riskScore": 0.94964,
  "attentionScore": 0.82,
  "attentionReasons": [
    "playwright-observed-failure",
    "under-tested-hr-support-plane",
    "near-sensitive-invariant:hr.documents_customer_role_boundary"
  ]
}
```

## Bounded Feedback Loop

The intended loop is:

```text
Playwright evidence / issue context / repo facts
  -> embed or anchor into Grassmann planes
  -> update plane telemetry

Plane telemetry
  -> coverage count
  -> failure count
  -> recent failure density
  -> untestedness / novelty
  -> distance to sensitive invariants
  -> muted/fixed regression state

Bayesilisk scenario generator
  -> samples more scenarios from high-attention planes

Bayesilisk verifier
  -> still runs deterministic invariants
  -> produces normal fingerprints/issues
```

Feedback is bounded:

- attention scores are capped;
- scenario generation count remains bounded by caller input;
- fixed or muted findings decay attention;
- model proposals are optional and schema-validated;
- deterministic invariants remain authoritative.

## Layer 4: Scenario Proposer Model

A configured model can generate candidate scenario JSON only.

The preferred local Ollama model is `gemma4:e2b`. Other local or test-scoped chat models may be used for experimentation, but scenario proposals must pass the same schema validation.

Example:

```json
{
  "title": "Support actor reaches HR document route after expired takeover",
  "fragments": [
    "role.support_takeover_expired",
    "hr.payroll_file_route"
  ],
  "invariants": [
    "roles.route_matrix_allowed",
    "support.takeover_session_required",
    "hr.documents_customer_role_boundary"
  ]
}
```

Model output is untrusted candidate input.

Bayesilisk must validate:

- fragment ids exist;
- invariant ids exist;
- route is known or explicitly caller-provided through a validated schema;
- facts are schema-valid;
- target plane is selected by Grassmann attention;
- target invariant is included in the scenario;
- no production claims are invented;
- generated scenario provenance is recorded.

Required provenance includes:

- model provider;
- model name;
- prompt or prompt hash;
- embedding model if embeddings were used;
- source Playwright probe or context source;
- accepted/rejected proposal counts.

Only accepted proposals may become generated scenarios, and even then they must be marked as model-proposed.

## Compatibility Pipeline

The full architecture is:

```text
Playwright
  -> observes concrete app behavior

Grassmann/embedding layer
  -> maps observed behavior to nearest invariant/scenario plane

Scenario proposer model
  -> proposes new scenario compositions in that plane

Bayesilisk core
  -> deterministically verifies and ranks those scenarios

Issue payloads
  -> stable fingerprints, dedupe, tracker-ready output
```

Short form:

```text
Playwright is the sensor.
Grassmann is the router.
The scenario proposer model is the proposer.
Bayesilisk is the judge.
```

## Implementation Requirements

Implementations must preserve:

- deterministic baseline reports for the same seed and inputs;
- scenario-matrix tests where every catalog scenario references valid fragments and invariants;
- deterministic catalog coverage with at least one pass and one fail for every invariant;
- no production access;
- local-only optional model and embedding calls unless the caller explicitly supplies another local/test endpoint;
- explicit report fields for attention and model provenance;
- stable fingerprints based on verified scenarios and invariants;
- clear separation between attention, proposal, and verification.

Implementations must not:

- let embeddings declare failures;
- let model output skip validation;
- hide deterministic failures because attention is low;
- open issues from `probe-only`, muted, or regression-watch findings by default;
- treat Playwright observations as production proof unless the caller explicitly supplied a production-safe verifier context.

## Current Implementation Map

- Deterministic verifier: `bayesilisk/bayesilisk.py`
- Playwright context adapter: `bayesilisk/playwright_adapter.py`
- Playwright demo runner: `tools/playwright_probe.py`
- Static demo target: `demo/playwright_target.html`
- Report contract and workflow docs: `docs/bayesilisk.md`
