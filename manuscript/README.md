# Manuscript

“Beyond E2E Scripts: Using LLM-Proposed Scenarios Without Letting the LLM Be the
Oracle”

- [main.tex](main.tex): canonical manuscript source.
- [main.pdf](main.pdf): compiled manuscript.
- [references.bib](references.bib): bibliography.
- [arxiv-source.tar.gz](arxiv-source.tar.gz): validated arXiv source upload.
- [cover_letter.tex](cover_letter.tex): journal cover-letter draft, excluded from
  the arXiv bundle; its venue and submission declarations require author review
  before journal use.

The corresponding-author email is `akolpakov@uaustin.org`. The manuscript includes
the acknowledgment: “GPT-6.1-sol assisted with coding and manuscript editing.”
AI assistance is disclosed as assistance, with authorship retained by the named
human author.

The current implementation account covers full-ABAG model proposals,
deterministic admission, connector-goal subspace projection, and receipt-backed
procedure retention/revalidation. The Cal.com results remain the fixed May 2026
artifact: the browser case study was not rerun for this manuscript update, and
it does not establish a measured advantage for these later exploration features.
Case-study artifacts are in [examples/calcom](../examples/calcom/), with
comparison summaries in [evidence_list.md](../evidence_list.md).

## Build and prepare an arXiv upload

Install Python 3.12 or later and a TeX distribution with `pdflatex`, `bibtex`, and
the standard packages used in `main.tex`. From the repository root, run:

```sh
python3 manuscript/tools/build_arxiv.py
```

The script builds in a temporary directory, runs BibTeX and the required LaTeX
passes, creates `arxiv-source.tar.gz`, and compiles the exact exported archive
in a second clean directory without running BibTeX. It rejects compilation
errors, unresolved citations/references, rerun requests, and overfull boxes.
It updates `main.pdf` only after the exported source passes those checks.

The archive contains `main.tex`, `main.bbl`, `references.bib`, and manuscript
assets, with portable relative paths. The generated `main.bbl` is essential:
ordinary repository builds ignore it, so copying tracked TeX inputs alone would
omit the resolved bibliography. The archive excludes PDFs, auxiliary files,
build tools, and the journal cover letter. Its file metadata is normalized so
unchanged source and bibliography output produce the same archive bytes.

Upload `arxiv-source.tar.gz` as the source submission and select `main.tex` with
pdfLaTeX if prompted. The named author should review the PDF and supply arXiv
metadata, subject classification, and submission declarations. A successful
local export build does not establish acceptance by arXiv's compiler or moderation;
no arXiv upload is performed by this script.

For a direct local build from this directory:

```sh
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
