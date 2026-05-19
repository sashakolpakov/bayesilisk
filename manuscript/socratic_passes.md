# Socratic Passes For The Manuscript

These notes record the claim-audit passes used to rewrite `main.tex`.

## Pass 1: What Is The Paper Claim?

Question: Is the claim that an LLM finds and judges bugs?

Answer: No. The claim is that model/coding-agent proposals can help expand the
scenario space, while deterministic Bayesilisk invariants remain the oracle.

Manuscript consequence: the abstract, introduction, and formal model all say
that candidate generation can be heuristic or model-assisted, but verification
is deterministic and evidence-bound.

## Pass 2: Who Owns Scenario Generation?

Question: Does the connector produce scenarios?

Answer: No. The connector declares the app-specific search surface: routes,
actions, identifiers, state facts, invariants, and valid mutation/action schemas.
Bayesilisk expands that declared surface into concrete candidate scenarios.

Manuscript consequence: the architecture wording now says "scenario generation
belongs to Bayesilisk"; connector execution is separate.

## Pass 3: What Makes A Scenario Executable?

Question: What happens when an LLM proposes a hallucinated or malformed scenario?

Answer: Bayesilisk rejects it by deterministic validation: unknown ids, unknown
target planes, non-string fields, duplicate proposals, impossible counts, and
unsupported actions become proposer telemetry, not product findings.

Manuscript consequence: the formal model defines `V_C(s)` and distinguishes
invalid candidates from executable probes.

## Pass 4: What Is Grassmann Attention Allowed To Do?

Question: Can attention decide pass/fail?

Answer: No. Attention ranks invariant planes and directs exploration. It cannot
override the verifier.

Manuscript consequence: the math section gives the ideal projection score and
the current bounded anchor-plane scoring formula, then states that the score is
a prioritizer only.

## Pass 5: What Is Bayesian Ranking Allowed To Do?

Question: Is posterior risk the bug verdict?

Answer: No. The posterior score orders findings after deterministic evidence
exists. The pass/fail verdict is the invariant result.

Manuscript consequence: the paper separates `rho_i` as a ranking score from
`phi_i(e)` as the deterministic evidence verifier.

## Pass 6: What External Validation Exists?

Question: Are the reports useful to humans?

Answer: The Cal.com report set produced upstream issues. Issue `#29399` has a
targeted fix PR, `#29400`, that diagnoses a missing null guard and adds a
regression Playwright test. Issue `#29407` remains open.

Manuscript consequence: the upstream validation section uses one targeted fix PR
as practical validation and does not overclaim that all findings have been
patched.

## Pass 7: What Is Not Proven Yet?

Question: What would a reviewer still attack?

Answer: The current empirical evidence is one real app, bounded workflow
generation, small local comparison runs, and connector-dependent coverage.

Manuscript consequence: the threats-to-validity section states those limits
directly instead of hiding them.
