# Manuscript Draft

This directory contains the current concise LaTeX manuscript for Bayesilisk.

Current target: a compact practice/research case-study article centered on the
Cal.com artifact and the verifier architecture. The draft now includes:

- a claim audit separating scenario generation, connector execution, and
  deterministic oracle ownership;
- a mathematical model of connector contracts, route mutations, bounded action
  sequences, Grassmann-style attention, Bayesian ranking, and evidence
  verification;
- the current Cal.com artifact summary: 7 generated probes, 7 connector
  observations, 7 verified app findings, and issue-ready payloads;
- upstream validation: Cal.com issue `#29399` has targeted fix PR `#29400`,
  and cancelled-booking replay issue `#29407` remains open at capture time;
- explicit limitations: one real app artifact, bounded sequence generation, and
  small local comparison runs rather than a full multi-app benchmark.

Build locally with:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Supporting notes:

- `socratic_passes.md` records the claim-audit passes used to rewrite the text.
- `venue_notes.md` records likely publication venues and current positioning.
