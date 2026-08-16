#!/usr/bin/env python3
"""Verify the integrity of the shipped manuscript.

Checks that the manuscript at paper/Not All Attention Is Equal.tex is
well-formed and self-contained inside this package:

  1. first line is the expected two-column 10pt document class;
  2. \\begin{document} and \\end{document} are balanced and ordered;
  3. every \\input{...} target referenced by the manuscript exists
     (resolved relative to the manuscript's directory, e.g. figures/*.tikz
     and the committed Table 6 fragment under ../results/tables/);
  4. the rendered PDF exists and is newer than the .tex source.

When run from the original working repository (which keeps the two-column
master as 1.tex and the one-column variant as 2.tex), the historical identity
check is also performed: the two files must differ only in their
document-class line. This package ships only the two-column master, so that
check is skipped here unless those files are present.
"""

from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "paper" / "Not All Attention Is Equal.tex"
EXPECTED_CLASS = r"\documentclass[10pt,twocolumn]{article}"

ONE_COLUMN = ROOT / "2.tex"
TWO_COLUMN = ROOT / "1.tex"
EXPECTED_ONE = r"\documentclass[10pt]{article}"


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def main() -> None:
    errors: list[str] = []

    if not MANUSCRIPT.exists():
        raise SystemExit(f"{MANUSCRIPT} is missing")
    lines = read_lines(MANUSCRIPT)

    if lines[0].rstrip("\n") != EXPECTED_CLASS:
        errors.append(f"{MANUSCRIPT}: unexpected document-class line")

    text = "".join(lines)
    if text.count(r"\begin{document}") != 1 or text.count(r"\end{document}") != 1:
        errors.append(f"{MANUSCRIPT}: expected exactly one document environment")
    elif text.index(r"\begin{document}") > text.index(r"\end{document}"):
        errors.append(f"{MANUSCRIPT}: document environment is not ordered")

    inputs = re.findall(r"\\input\{([^}]+)\}", text)
    for target in inputs:
        candidate = (MANUSCRIPT.parent / target).resolve()
        if not candidate.exists():
            errors.append(f"{MANUSCRIPT}: \\input target missing: {target}")

    pdf = MANUSCRIPT.with_suffix(".pdf")
    if not pdf.exists():
        errors.append(f"{pdf} is missing (run `make paper`)")
    elif pdf.stat().st_mtime < MANUSCRIPT.stat().st_mtime:
        errors.append(f"{pdf} is older than {MANUSCRIPT.name} (run `make paper`)")

    # Working-repository check: 1.tex (two-column master) vs 2.tex (one-column).
    if ONE_COLUMN.exists() and TWO_COLUMN.exists():
        one = read_lines(ONE_COLUMN)
        two = read_lines(TWO_COLUMN)
        if not one or one[0].rstrip("\n") != EXPECTED_ONE:
            errors.append(f"{ONE_COLUMN}: unexpected document-class line")
        if not two or two[0].rstrip("\n") != EXPECTED_CLASS:
            errors.append(f"{TWO_COLUMN}: unexpected document-class line")
        if one[1:] != two[1:]:
            diff = "".join(
                difflib.unified_diff(
                    one[1:],
                    two[1:],
                    fromfile=str(ONE_COLUMN),
                    tofile=str(TWO_COLUMN),
                    n=2,
                )
            )
            errors.append("manuscript bodies differ:\n" + diff[:8000])

    if errors:
        raise SystemExit(errors[0] + "\n" + "\n".join(errors[1:]))
    print(
        f"OK: {MANUSCRIPT.name} is well-formed; all inputs resolve; "
        f"PDF is up to date"
    )


if __name__ == "__main__":
    main()