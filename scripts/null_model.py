#!/usr/bin/env python3
"""Rank-matched null expectation of EEI rank instability.

Runs the same perturbation pipeline on random score triplets drawn from the
observed axis-value distributions (null_expectation in eei_sensitivity.py).
Per-method null expected instability is compared against the real methods'
instability (from eei_sensitivity.py --format text).

Defaults mirror the manuscript's null protocol (50,000 samples, 100 reps,
seed 43) with a --smoke flag for quick sanity runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import rankdata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eei_sensitivity import (  # noqa: E402
    NULL_REPS_DEFAULT,
    NULL_SAMPLES_DEFAULT,
    NULL_SEED_DEFAULT,
    WEIGHTS,
    load_scores,
    null_expectation,
)

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scores", type=Path, default=ROOT / "data" / "eei_scores.csv")
    parser.add_argument("--null-samples", type=int, default=NULL_SAMPLES_DEFAULT)
    parser.add_argument("--null-reps", type=int, default=NULL_REPS_DEFAULT)
    parser.add_argument("--null-seed", type=int, default=NULL_SEED_DEFAULT)
    parser.add_argument("--batch-size", type=int, default=10_000)
    parser.add_argument("--smoke", action="store_true", help="samples=2_000, reps=2")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "sensitivity")
    args = parser.parse_args()

    samples = 2_000 if args.smoke else args.null_samples
    reps = 2 if args.smoke else args.null_reps

    names, scores = load_scores(args.scores)
    query_ranks = {
        label: rankdata(-(scores @ weights), method="average")
        for label, weights in WEIGHTS.items()
    }
    expected = null_expectation(
        scores, samples, reps, args.null_seed, args.batch_size, query_ranks
    )

    rows = []
    print(f"null expectation ({reps} reps x {samples:,} samples, seed {args.null_seed})")
    for label in WEIGHTS:
        print(f"== {label} ==")
        for i, name in enumerate(names):
            value = float(expected[label][i])
            rows.append({"weight": label, "method": name, "null_expected_instability": value})
            print(f"  {name:<24s} {value:.3f}")

    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / "null_expectation.json"
    target.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()