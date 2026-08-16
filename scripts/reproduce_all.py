#!/usr/bin/env python3
"""End-to-end reproduction for the EEI package.

Steps:
  1. strict environment check (pins in requirements-eei.txt)
  2. regenerate the Table 6 fragment into results/tables/
  3. recompute EEI composites and rankings -> results/sensitivity/
  4. run the rank-matched null model -> results/sensitivity/

Exit code is non-zero on any failure, so this can gate CI.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts"


def run(python: str, script: str, *args: str) -> None:
    cmd = [python, str(SCRIPT / script), *args]
    print(">>>", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--smoke", action="store_true", help="quick run (reduced null reps/samples)"
    )
    parser.add_argument(
        "--strict-env",
        action="store_true",
        help="enforce exact environment pins (tested stack: Python 3.13.5, NumPy 2.4.1, SciPy 1.17.0)",
    )
    args = parser.parse_args()

    # 1. environment
    run(
        args.python, "eei_sensitivity.py",
        "--scores", str(ROOT / "data" / "eei_scores.csv"),
        "--inclusion-ledger", str(ROOT / "data" / "method_metadata.csv"),
        "--check-environment",
        *(["--strict-environment"] if args.strict_env else []),
    )
    # 2. Table 6 fragment
    run(
        args.python, "eei_sensitivity.py",
        "--scores", str(ROOT / "data" / "eei_scores.csv"),
        "--inclusion-ledger", str(ROOT / "data" / "method_metadata.csv"),
        "--write-latex", str(ROOT / "results" / "tables" / "tab_eei_sensitivity.tex"),
    )
    # 3. composites
    run(args.python, "compute_eei.py")
    # 4. null model
    extra = ("--smoke",) if args.smoke else ()
    run(args.python, "null_model.py", *extra)

    print("REPRODUCTION OK")


if __name__ == "__main__":
    main()