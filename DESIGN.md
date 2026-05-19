# Bayesilisk Design

This document is the governing design for Bayesilisk. Implementation details can evolve, but the trust boundaries in this file are non-negotiable.

## Core Principle

Bayesilisk is a deterministic finite-state verifier with optional attention and proposal layers around it.

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

## Architecture Summary

The architecture is:

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

## Important Task: Generic Sequence Proposals

Bayesilisk can now generate bounded workflow-sequence proposals from a
connector-declared action graph. This is still not free-form browser wandering:
the connector exposes declared actions, state facts, and parameter bindings;
Bayesilisk composes valid sequences; the connector executes concrete app
behavior.

The right architecture is:

```text
connector exposes action vocabulary + state facts
  -> Bayesilisk generates bounded action sequences
  -> connector executes declared actions exactly
  -> connector reports observations
  -> Bayesilisk verifies deterministic invariants
```

Example target sequence:

```text
create booking -> cancel booking -> replay uid via public route
```

The connector must not become the scenario generator. It should expose a small
set of actions, actor/session fixtures, state-producing outputs, and route/action
parameter bindings. Bayesilisk should own the generic sequence proposal layer
that composes those actions into bounded runs.

Current Cal.com status: Bayesilisk generates the cancelled-booking replay as a
bounded workflow sequence from a connector-declared action graph, and the
Cal.com connector executes that generated proposal directly. This is evidence
for the declared-action sequence architecture, not proof that Bayesilisk can
synthesize arbitrary free-form browser runs.

## Design Sprint: Abstract Action Graphs

The current `connectorActionGraph` is useful but too literal. It composes string
tokens such as:

```text
create-booking produces booking.uid
cancel-booking requires booking.uid, produces booking.status.cancelled
open-public-booking-route binds rescheduleUid <- booking.uid
```

This finds the Cal.com sequence, but Bayesilisk does not yet know that the same
flow shape appears in other apps:

```text
create-invoice -> void-invoice -> replay invoice public link
create-reset-token -> expire-token -> replay token
create-invite -> revoke-invite -> accept invite
```

Today the core sees only string dependency flow. The design target is an
Abstract Bayesilisk Action Graph (ABAG): a connector-declared graph whose nodes
and edges carry universal typed tokens plus optional app-specific refinements.
The connector still owns execution. Bayesilisk operates on the abstract graph.

### ABAG Token Vocabulary

Start with a small universal vocabulary, not app nouns:

```text
principal.actor
session.authenticated
session.impersonated
scope.tenant
scope.owner
scope.foreign

resource.type
resource.id
resource.public_id
resource.private_id
resource.foreign_id
resource.stale_id

identifier.replay_token
identifier.single_use_token
identifier.invitation_token
identifier.reset_token

state.active
state.cancelled
state.deleted
state.expired
state.revoked
state.approved
state.rejected

boundary.public_route
boundary.private_route
boundary.api_route
boundary.ui_route
boundary.admin_route

capability.read
capability.write
capability.approve
capability.cancel
capability.export
capability.invite
capability.replay

evidence.status
evidence.redirect
evidence.rendered_state
evidence.network_response
```

App-specific tokens become refinements:

```text
booking.uid -> resource.public_id + resource.type.booking
booking.status.cancelled -> state.cancelled + resource.type.booking
rescheduleUid -> identifier.replay_token + boundary.public_route
```

The reusable object is the motif, not the product noun:

```text
create resource -> transition lifecycle state -> replay old identifier across boundary
create privileged context -> downgrade/revoke privilege -> reuse stale session
create scoped object -> swap tenant/user id -> access through valid route
```

### Codebase Connectors

A codebase connector may aggregate multiple app/module connectors and expose one
ABAG for the whole codebase. Each module connector maps concrete fixtures and
routes to abstract action nodes. Bayesilisk can then store or learn ranking
metadata over graph motifs rather than over app-specific action labels.

Possible matching methods include graph edit distance, Weisfeiler-Lehman graph
kernels, learned graph embeddings, or quasi-isometry-inspired clustering for
graphs that preserve large-scale token flow despite local naming differences.
Those methods remain prioritizers. They do not become oracles.

### Sprint Deliverables

- define a JSON schema for ABAG tokens instead of arbitrary string-only
  `requires` and `produces` entries;
- document token naming rules and the distinction between universal tokens and
  app refinements;
- add connector examples that map concrete app actions into ABAG nodes;
- add motif examples for stale id replay, revoked token replay, tenant swap,
  role downgrade, and duplicate submission;
- update `docs/connectors.md` and `examples/connector-agent-contract.json` so
  test teams can write ABAG-capable connectors without touching Bayesilisk core;
- keep the current string-token graph accepted during the design sprint, but
  treat it as a transitional input form, not the long-term abstraction.

## Important Task: True Grassmann Attention

The current `attentionScore` is an interpretable bounded proxy for Grassmann
attention. It uses failure density, untestedness, invariant sensitivity,
Playwright evidence, novelty, and fixed/muted decay. That proxy is useful for
small artifacts, but it is not the full Grassmann operation.

The target architecture is:

```text
connector context + invariant definitions + nearby tests + observed evidence
  -> feature vectors or local subspace bases
  -> invariant planes
  -> projection or Grassmann-distance score
  -> bounded probe prioritization
  -> deterministic verifier remains authoritative
```

For invariant plane `P_i` with orthonormal basis `U_i` and context vector `q`,
the direct projection score is:

```text
gamma_i(q) = || U_i^T q ||_2^2
```

Equivalent future implementations may use principal angles or another explicit
Grassmann distance between a context subspace and an invariant subspace. The
important requirement is that the Grassmann layer remains only a router. It can
choose where Bayesilisk spends verifier budget; it cannot decide pass/fail.

## Important Task: Calibrated Likelihoods

The current Bayesian ranking path uses invariant-level constants:

```text
prior
fail_likelihood
pass_likelihood
```

Those constants are supplied by the invariant author and selected after the
deterministic evaluator returns pass or fail. This is an initial ranking proxy,
not an empirical calibration.

The target architecture is to estimate likelihood terms from validation data.
For invariant `i`, let `Z_i` mean that the app genuinely violates the invariant,
and let `r_i` be the deterministic verifier result. For a failing result, the
ranking model should estimate:

```text
P(r_i = fail | Z_i)      # true-positive behavior
P(r_i = fail | not Z_i)  # false-positive behavior
```

For a passing result, it should estimate:

```text
P(r_i = pass | Z_i)
P(r_i = pass | not Z_i)
```

Useful calibration sources include:

- historical Bayesilisk findings and their outcomes;
- seeded faults in fixture or demo apps;
- negative controls against known-good states;
- connector evidence quality, such as direct status mismatch versus weaker UI text;
- invariant/probe family, such as stale id, permission boundary, workflow order, or feature flag;
- human validation signals, including accepted upstream issues, fix PRs, and added regression tests.

The calibrated likelihood model still must not decide pass/fail. It only ranks
findings after deterministic verification and helps prioritize future probe
budget.

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

- Deterministic verifier and report assembly: `bayesilisk/invariants.py`, `bayesilisk/facts.py`, and `bayesilisk/reporting.py`
- Playwright context adapter: `bayesilisk/playwright_adapter.py`
- Playwright demo runner: `tools/playwright_probe.py`
- Static demo target: `demo/playwright_target.html`
- Report contract and workflow docs: `docs/bayesilisk.md`
