# Manuscript Draft

This directory contains a concise LaTeX manuscript draft for Bayesilisk.

Current target: short case-study style paper, not ACM TOSEM.

Build locally with:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

The draft intentionally states the current evidence limits: the Cal.com artifact
contains a real connector run, 7 verified app findings, and one generated
bounded workflow sequence. It does not yet include fresh baseline comparisons
against existing E2E tests, Playwright-only probing, weak model proposals, or
browser-driving LLM agents.

The Cal.com artifact also records upstream human response: issue `#29399` has
an open fix PR, `#29400`. That is treated as stronger validation than a closed
issue without fix context.
