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

The Grassmann layer is an attention router. It builds local context planes from Playwright observations, route names, actors, modules, tenant facts, issue text, scenario fragments, and invariant descriptions.

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

The accepted scenario still goes through the deterministic invariant checker.

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
contract, and a stateless loop controller drives
`scan → bind motifs → validate → verify → fix` to convergence, returning the one
step it cannot perform — connector execution — for the agent to run. Bayesilisk
never executes the application and never decides pass/fail. See
{doc}`connector-loop`.
