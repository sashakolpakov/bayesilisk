# Manuscript

“Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the
Oracle”

- [main.tex](main.tex): manuscript source.
- [main.pdf](main.pdf): compiled manuscript.
- [references.bib](references.bib): bibliography.
- [cover_letter.tex](cover_letter.tex): submission cover letter.

The corresponding-author email is `akolpakov@uaustin.org`.
Case-study artifacts are in [examples/calcom](../examples/calcom/), with
comparison summaries in [evidence_list.md](../evidence_list.md).

From this directory, build locally with:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
