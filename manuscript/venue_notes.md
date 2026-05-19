# Venue Notes

Current recommendation: aim first for a practice-oriented journal/magazine
article, then harden toward a stronger empirical software engineering venue
after adding at least one more real-app artifact.

## Best Immediate Fit: IEEE Software

IEEE Software is still the best near-term fit because the current manuscript is
a practice/research case study: a tool architecture, a real application artifact,
issue-ready evidence, and practical guidance for teams writing connectors.

Positioning:

- Lead with "LLMs propose scenarios; deterministic verifiers remain the oracle."
- Emphasize engineering practice: Playwright as sensor, connector contracts,
  issue payloads, and maintainer validation.
- Keep the math compact and explanatory rather than theorem-heavy.

Source: https://www.computer.org/digital-library/magazines/so/cfp-ieee-software

## Artifact Venues

JOSS is a possible software-artifact venue if the goal is a citable open-source
software paper. It is not the best home for the Cal.com case-study argument
because JOSS focuses on software quality and research use rather than a full
empirical testing claim.

Sources:

- https://joss.theoj.org/about
- https://joss.readthedocs.io/en/latest/submitting.html

SoftwareX is another software-artifact option, but it is an open-access Elsevier
journal and should be checked carefully for current article-publishing charges
before investing effort.

Source: https://www.sciencedirect.com/journal/softwarex

## Stronger Research-Journal Targets

Journal of Systems and Software or Automated Software Engineering become more
credible after multi-app evaluation and an ablation study that separates
connector context, generated proposals, attention ranking, Bayesian ordering,
weak-model noise, and deterministic verification. The current Cal.com baselines
already support the architectural distinction; a broader venue will want effect
sizes across projects and models.

Sources:

- https://www.sciencedirect.com/journal/journal-of-systems-and-software
- https://link.springer.com/journal/10515/aims-and-scope

## Not Yet: TOSEM/TSE-Style Claims

ACM TOSEM and IEEE TSE are premature for the current artifact. They would expect
a larger empirical package than the current Cal.com-centered artifact, even
with useful local baselines and upstream PR validation. A credible TOSEM/TSE
submission would need at least:

- multiple real applications;
- reproducible connector branches or patches;
- fixed-seed and varied-seed experiments;
- baseline comparisons against existing E2E, Playwright-only probes, LLM-agent
  browser runs, and LLM-as-oracle variants;
- false-positive and invalid-proposal analysis;
- ablations for attention, Bayesian ranking, model proposals, and sequence
  generation.

Source: https://dl.acm.org/journal/tosem
