# Architecture

Bayesilisk is built around one hard rule: the deterministic verifier is the only component that can mark a scenario as pass or fail.

```text
scenario facts -> invariant checks -> pass/fail -> Bayesian ranking
```

The surrounding layers improve where Bayesilisk looks next, but they do not decide whether something is a bug.

## Core Verifier

The verifier owns:

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
