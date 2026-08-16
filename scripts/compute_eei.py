#!/usr/bin/env python3
"""Recompute the weighted EEI composites and rankings from data/eei_scores.csv.

Uses the same WEIGHTS configurations as eei_sensitivity.py (imported, so the
two scripts cannot drift apart). Output: tabular text + JSON per weight
configuration written to results/sensitivity/eei_composites.json.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from eei_sensitivity import WEIGHTS, load_scores  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scores",
        type=Path,
        default=ROOT / "data" / "eei_scores.csv",
    )
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "sensitivity")
    args = parser.parse_args()

    names, scores = load_scores(args.scores)
    out: dict[str, dict] = {}
    for label, weights in WEIGHTS.items():
        composite = scores @ weights
        order = np.argsort(-composite, kind="stable")
        ranked = [(i + 1, names[j], float(composite[j])) for i, j in enumerate(order)]
        out[label] = {
            "weights": [float(w) for w in weights],
            "ranked": ranked,
        }
        print(f"== {label} (weights {weights}) ==")
        for rank, name, value in ranked:
            print(f"  {rank:2d}  {name:<24s} {value:.1f}")

    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / "eei_composites.json"
    target.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {target}")


if __name__ == "__main__":
    main()