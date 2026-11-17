# Architecture

Bayesilisk separates scenario proposal from verification. A connector declares a
bounded application surface, the core expands and validates candidate probes, and
only deterministic verification over connector-returned evidence can mark a
scenario as pass or fail.

```text
scenario proposal -> contract validation -> connector execution -> deterministic verification
```

Bayesilisk runs in two operating routes over the same deterministic core:

- `local`: you drive the verifier and connector loop directly from the CLI
  against local fixtures, API descriptions, browser evidence, or caller-provided
  context;
- `mcp/agent-bound`: a coding agent such as Codex drives the loop through the
  local MCP server, while Bayesilisk stays the deterministic oracle.

The surrounding layers — connector or Playwright sensor, Grassmann attention, and
the scenario proposer model — improve where Bayesilisk looks next, but they do
not decide whether something is a bug.

## Core Verifier

The finite-state verifier owns:

- scenario fragments;
- fact merging;
- invariant evaluation;
- deterministic pass/fail observations;
- stable fingerprints and dedupe keys;
- Bayesian-style `riskScore`;
- issue readiness.

Each scenario has facts, one or more invariants, and a generation basis. Catalog scenarios are explicit. Generated scenarios are deterministic for a fixed seed and input context.

## Playwright Sensor

Playwright is an evidence collector. It can observe concrete browser or route behavior, including actor role, route, expected status, observed status, invariant id, and target URL.

That evidence becomes context. It does not become proof by itself.

## Grassmann Attention

The Grassmann layer is an attention router. Connector exploration constructs an
orthonormal basis from each goal's descriptions, state requirements and typed
bindings, then computes squared projection of a normalized context vector.
Coverage and failure density supply separate bounded terms. The catalog report
path retains an anchor-plane proxy. See {doc}`connector-exploration` for the
implemented connector score and its evaluation limits.

The catalog path builds local context planes from Playwright observations, route names, actors, modules, tenant facts, issue text, scenario fragments, and invariant descriptions.

Attention answers:

```text
Where should Bayesilisk look next?
```

It does not answer:

```text
Is this definitely a bug?
```

Bayesilisk reports both `attentionScore` and `riskScore` so those meanings stay separate.

## Scenario Proposer Model

The optional model layer proposes candidate scenario JSON. It is untrusted input.

Bayesilisk accepts a proposal only when:

- every fragment id exists;
- every invariant id exists;
- the target plane was selected by attention;
- the target invariant is included in the scenario;
- the facts remain schema-valid;
- provenance is recorded.

The accepted catalog scenario still goes through the deterministic invariant checker.

Connectors have a separate model-guided path over their declared ABAG and goals.
The prompt includes connector instructions, typed action signatures, exploration
attention, retained executable sequences and execution/rejection feedback. A
deterministic gate admits model-selected paths before execution. See
{doc}`connector-exploration`. This path can choose alternative producers and
compositions beyond the catalog and the first-producer planner.

## Feedback Loop

The loop is bounded:

```text
Playwright evidence / issue context / repo facts
  -> Grassmann plane telemetry
  -> high-attention scenario generation
  -> deterministic Bayesilisk verification
  -> stable fingerprints and issue-ready findings
```

Untested planes raise attention. They do not automatically raise risk. Bad planes can affect both only after concrete evidence or deterministic failures.

## Ledgers

Contextual reports should keep these ledgers separate:

- `observedByPlaywright`: concrete browser evidence;
- `selectedByGrassmannAttention`: attention-plane telemetry;
- `proposedByModel`: untrusted candidate scenarios;
- `verifiedByBayesilisk`: deterministic invariant results.

The issue-worthy result must come from `verifiedByBayesilisk`.

## Motif Library

The motif library is the app-agnostic encoding of *what* to probe. It is a small
category over the universal ABAG vocabulary: tokens are objects, connector actions
are morphisms (`requires` → `produces`), workflow sequences are composite
morphisms, and a connector is a functor that executes abstract tokens through
their concrete refinements. A motif is a typed diagram obligation that expands
into the same `proposalRules` / `sequenceRules` the verifier already checks — so
motifs steer search, never the verdict. Motifs ship in versioned packs (an open
core pack plus optionally gated packs). See {doc}`motifs`.

## Automated Loop

A deterministic surface scanner turns an API description into a draft connector
contract. A controller coordinates motif binding, optional model exploration,
admission, execution hand-offs, verification and repair. Caller-owned state
retains execution-checked procedures and feedback for subsequent exploration.
Bayesilisk verifies observations; the connector executes the application. See
{doc}`connector-loop`.
