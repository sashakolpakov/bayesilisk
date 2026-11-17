#!/usr/bin/env python3
"""Build the canonical PDF and validate a self-contained arXiv source archive."""
from __future__ import annotations

import gzip
import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile

MANUSCRIPT = Path(__file__).resolve().parents[1]
ARCHIVE = MANUSCRIPT / "arxiv-source.tar.gz"


def run(command: list[str], directory: Path) -> None:
    result = subprocess.run(command, cwd=directory, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise SystemExit(f"{' '.join(command)} failed:\n{result.stdout}")


def latex(directory: Path) -> None:
    run(["pdflatex", "-no-shell-escape", "-interaction=nonstopmode", "-halt-on-error",
         "main.tex"], directory)


def check_log(directory: Path) -> None:
    log = (directory / "main.log").read_text()
    errors = [line for line in log.splitlines() if any(marker in line for marker in (
        "undefined", "Rerun to get", "Label(s) may have changed", "Overfull", "! "))]
    if errors:
        raise SystemExit("Unresolved LaTeX diagnostics:\n" + "\n".join(errors))


def main() -> None:
    # Only manuscript inputs belong in the submission; journal cover letters,
    # canonical PDFs and compiler logs are intentionally excluded.
    inputs = [MANUSCRIPT / "main.tex", MANUSCRIPT / "references.bib"]
    inputs += sorted(path for path in (MANUSCRIPT / "assets").rglob("*") if path.is_file())
    with tempfile.TemporaryDirectory(prefix="bayesilisk-arxiv-") as temporary:
        stage = Path(temporary) / "build"
        stage.mkdir()
        for source in inputs:
            target = stage / source.relative_to(MANUSCRIPT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        latex(stage)
        run(["bibtex", "main"], stage)
        latex(stage)
        latex(stage)
        check_log(stage)
        members = [path.relative_to(MANUSCRIPT) for path in inputs] + [Path("main.bbl")]
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for relative in sorted(members):
                data = (stage / relative).read_bytes()
                info = tarfile.TarInfo(relative.as_posix())
                info.size = len(data)
                info.mode = 0o644
                info.mtime = 0
                archive.addfile(info, io.BytesIO(data))
        archive_data = gzip.compress(payload.getvalue(), mtime=0)
        # Compile the exact exported source in a second empty directory. Do not
        # run BibTeX here: this confirms the required generated .bbl is bundled.
        exported = Path(temporary) / "exported"
        exported.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive_data), mode="r:gz") as archive:
            archive.extractall(exported, filter="data")
        latex(exported)
        latex(exported)
        check_log(exported)
        shutil.copyfile(exported / "main.pdf", MANUSCRIPT / "main.pdf")
        ARCHIVE.write_bytes(archive_data)
        print(f"Built {MANUSCRIPT / 'main.pdf'}")
        print(f"Validated {ARCHIVE} ({len(archive_data)} bytes)")
        print("Archive contents: " + ", ".join(str(path) for path in sorted(members)))


if __name__ == "__main__":
    main()
