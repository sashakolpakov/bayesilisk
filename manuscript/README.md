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
contains a real connector run and verified findings, but not yet a complete
baseline comparison or a longer multi-step workflow result.
