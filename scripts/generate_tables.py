#!/usr/bin/env python3
"""Regenerate the manuscript's Table 6 fragment (EEI sensitivity).

Delegates to eei_sensitivity.py --write-latex with paths resolved inside this
package, so the generated fragment is always the canonical script's output.

Note: the manuscript's other tables (EEI score matrix, benchmarks, taxonomy,
etc.) are hand-authored in the manuscript source under paper/, not
script-generated; this generator
covers only the reproducibility-sensitive Table 6.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results" / "tables" / "tab_eei_sensitivity.tex",
    )
    args = parser.parse_args()

    cmd = [
        args.python,
        str(ROOT / "scripts" / "eei_sensitivity.py"),
        "--scores", str(ROOT / "data" / "eei_scores.csv"),
        "--inclusion-ledger", str(ROOT / "data" / "method_metadata.csv"),
        "--write-latex", str(args.out),
    ]
    print("running:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()