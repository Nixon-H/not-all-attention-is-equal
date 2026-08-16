#!/usr/bin/env python3
"""Reproduce the EEI score-perturbation sensitivity analysis.

The implementation deliberately ranks integer-weighted score sums.  This avoids
floating-point artifacts that would otherwise split mathematical ties such as
8/3 + 10/3 + 6/3.  Perturbations are independent discrete draws from {-1,0,1},
applied to every method-axis cell and then clamped to the rubric domain [1,10].
Ranks are descending average ranks for ties.  A rank is counted as unstable when
its absolute change from the unperturbed rank is greater than one position.

The table also reports a rank-matched null expectation: the same perturbation
and ranking pipeline applied to score triplets drawn uniformly (with
replacement) from the distinct values observed on each axis, averaged over
replicates and bucketed by baseline rank.  This isolates the component of rank
instability produced by perturbation magnitude and rank censoring (top ranks
cannot move upward, bottom ranks cannot move downward) from the component that
depends on the specific score configuration.

Usage (from the repository root):
  python scripts/eei_sensitivity.py
  python scripts/eei_sensitivity.py --format latex
  python scripts/eei_sensitivity.py --write-latex results/tables/tab_eei_sensitivity.tex
  python scripts/eei_sensitivity.py --check-environment --check-latex results/tables/tab_eei_sensitivity.tex
  python scripts/eei_sensitivity.py --strict-environment
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import rankdata


WEIGHTS = {
    "Equal": np.array([1, 1, 1], dtype=np.int16),
    "Retrieval": np.array([1, 3, 1], dtype=np.int16),
    "Deployment": np.array([3, 1, 1], dtype=np.int16),
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXPECTED_PYTHON = "3.13.5"
EXPECTED_NUMPY = "2.4.1"
EXPECTED_SCIPY = "1.17.0"

NULL_REPS_DEFAULT = 100
NULL_SAMPLES_DEFAULT = 50_000
NULL_SEED_DEFAULT = 43
TIE_METHODS = ("average", "min", "ordinal", "dense")
ALLOWED_INCLUSION_STATUSES = {
    "included_current_matrix",
    "deferred_prospective_round",
    "excluded_prospective_round",
}


def load_scores(path: Path) -> tuple[list[str], np.ndarray]:
    names: list[str] = []
    scores: list[list[int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            names.append(row["method"])
            scores.append([int(row["E"]), int(row["Ex"]), int(row["I"])])
    return names, np.asarray(scores, dtype=np.int16)


def validate_inclusion_ledger(path: Path, score_names: list[str]) -> None:
    """Ensure the scored population matches the frozen method ledger exactly.

    The ledger separates the existing 21-row analysis from candidates that must
    be adjudicated in a future, prospectively declared scoring round.  This
    prevents silent post-hoc additions or removals from changing the reported
    rankings and sensitivity results.
    """
    required = {
        "analysis_version",
        "method",
        "analysis_status",
        "score_row_present",
        "decision_basis",
        "next_action",
    }
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{path}: inclusion ledger is missing columns: {', '.join(sorted(missing))}"
            )
        rows = list(reader)

    ledger_names = [row["method"].strip() for row in rows]
    duplicates = sorted({name for name in ledger_names if ledger_names.count(name) > 1})
    if duplicates:
        raise ValueError(f"{path}: duplicate method rows: {', '.join(duplicates)}")

    for row in rows:
        method = row["method"].strip()
        status = row["analysis_status"].strip()
        present = row["score_row_present"].strip().lower()
        if not method or not row["analysis_version"].strip():
            raise ValueError(f"{path}: method and analysis_version are required")
        if status not in ALLOWED_INCLUSION_STATUSES:
            raise ValueError(f"{path}: {method}: unsupported analysis_status {status!r}")
        if present not in {"yes", "no"}:
            raise ValueError(f"{path}: {method}: score_row_present must be yes or no")
        if not row["decision_basis"].strip() or not row["next_action"].strip():
            raise ValueError(f"{path}: {method}: decision_basis and next_action are required")
        expected_present = status == "included_current_matrix"
        if (present == "yes") != expected_present:
            raise ValueError(
                f"{path}: {method}: score_row_present is inconsistent with {status}"
            )

    included = [
        row["method"].strip()
        for row in rows
        if row["analysis_status"].strip() == "included_current_matrix"
    ]
    if included != score_names:
        raise ValueError(
            "The ordered included_current_matrix rows in the method ledger do not "
            "exactly match the score CSV. Update the ledger and all derived outputs "
            "as one versioned analysis change."
        )


def validate_environment(strict: bool) -> None:
    actual = {
        "Python": sys.version.split()[0],
        "NumPy": np.__version__,
        "SciPy": scipy.__version__,
    }
    expected = {
        "Python": EXPECTED_PYTHON,
        "NumPy": EXPECTED_NUMPY,
        "SciPy": EXPECTED_SCIPY,
    }
    mismatches = [
        f"{name} expected {expected[name]}, found {actual[name]}"
        for name in expected
        if actual[name] != expected[name]
    ]
    if strict:
        if mismatches:
            raise RuntimeError(
                "Environment mismatch: " + "; ".join(mismatches) + "\n"
                "Exact pins are enforced only where you have installed the tested "
                "stack. On a compatible environment the pipeline is deterministic "
                "across the listed patch versions; see docs/reproduction.md."
            )
        print(
            f"Environment OK (exact pins): Python {actual['Python']}, "
            f"NumPy {actual['NumPy']}, SciPy {actual['SciPy']}"
        )
        return
    if mismatches:
        print(
            "WARNING: " + "; ".join(mismatches)
            + "\nContinuing in tolerant mode (same 3.13.x line is assumed "
              "deterministic for this analysis). Use --strict-environment to "
              "enforce exact pins; see docs/reproduction.md.",
            file=sys.stderr,
        )
    else:
        print(
            f"Environment OK: Python {actual['Python']}, "
            f"NumPy {actual['NumPy']}, SciPy {actual['SciPy']}"
        )


def simulate(
    scores: np.ndarray,
    samples: int,
    seed: int,
    batch_size: int,
    tie_method: str = "average",
) -> dict[str, np.ndarray]:
    rng = np.random.Generator(np.random.PCG64(seed))
    baseline = {
        name: rankdata(-(scores @ weights), method=tie_method)
        for name, weights in WEIGHTS.items()
    }
    changed = {
        name: np.zeros(scores.shape[0], dtype=np.int64) for name in WEIGHTS
    }
    any_changed = {
        name: np.zeros((), dtype=np.int64) for name in WEIGHTS
    }

    for start in range(0, samples, batch_size):
        batch = min(batch_size, samples - start)
        noise = rng.integers(
            -1,
            2,
            size=(batch, scores.shape[0], scores.shape[1]),
            dtype=np.int16,
        )
        perturbed = np.clip(scores[None, :, :] + noise, 1, 10)
        for name, weights in WEIGHTS.items():
            ranks = rankdata(-(perturbed @ weights), method=tie_method, axis=1)
            delta = np.abs(ranks - baseline[name][None, :]) > 1
            changed[name] += np.sum(delta, axis=0)
            any_changed[name] += np.any(delta, axis=1).sum()

    return {name: values / samples for name, values in changed.items()}


def axis_value_sets(scores: np.ndarray) -> list[np.ndarray]:
    """Distinct rubric values observed on each axis, in ascending order."""
    return [np.unique(scores[:, j]) for j in range(scores.shape[1])]


def null_expectation(
    scores: np.ndarray,
    samples: int,
    reps: int,
    seed: int,
    batch_size: int,
    query_ranks: dict[str, np.ndarray],
) -> dict[str, np.ndarray]:
    """Rank-matched null expected instability under random score triplets.

    Each replicate draws 21 score triplets whose axis values are sampled
    uniformly from the distinct values observed on that axis, applies the
    identical perturbation/ranking pipeline, and averages instability within
    groups of methods that share the same baseline (average-tie) rank.  The
    resulting per-replicate rank->instability curve is linearly interpolated at
    the real methods' baseline rank positions and averaged over replicates, so
    a real method is compared against the instability that random scores assign
    to its rank position (including the censoring of boundary ranks).
    """
    rng = np.random.Generator(np.random.PCG64(seed))
    n_methods = scores.shape[0]
    value_sets = axis_value_sets(scores)
    accum = {
        name: np.zeros(len(ranks), dtype=np.float64)
        for name, ranks in query_ranks.items()
    }
    for _ in range(reps):
        draw = np.empty((n_methods, scores.shape[1]), dtype=np.int16)
        for j, values in enumerate(value_sets):
            draw[:, j] = rng.choice(values, size=n_methods)
        fractions = simulate(
            draw,
            samples,
            int(rng.integers(0, 2**31 - 1)),
            batch_size,
        )
        for name, weights in WEIGHTS.items():
            baseline = rankdata(-(draw @ weights), method="average")
            groups: dict[float, list[float]] = {}
            for idx in range(n_methods):
                groups.setdefault(float(baseline[idx]), []).append(
                    float(fractions[name][idx])
                )
            keys = np.asarray(sorted(groups), dtype=np.float64)
            means = np.asarray([np.mean(groups[k]) for k in keys], dtype=np.float64)
            accum[name] += np.interp(query_ranks[name], keys, means)
    return {name: accum[name] / reps for name in WEIGHTS}


def tie_method_means(
    scores: np.ndarray,
    samples: int,
    seed: int,
    batch_size: int,
) -> dict[str, dict[str, float]]:
    """Mean instability fraction per weighting under each rank tie convention."""
    out: dict[str, dict[str, float]] = {}
    for method in TIE_METHODS:
        fractions = simulate(scores, samples, seed, batch_size, tie_method=method)
        out[method] = {
            name: float(fractions[name].mean()) for name in WEIGHTS
        }
    return out


def any_method_moved_fraction(
    scores: np.ndarray,
    samples: int,
    seed: int,
    batch_size: int,
) -> dict[str, float]:
    """Fraction of samples in which at least one method changes rank by >1."""
    rng = np.random.Generator(np.random.PCG64(seed))
    out: dict[str, float] = {}
    moved = {name: 0 for name in WEIGHTS}
    for start in range(0, samples, batch_size):
        batch = min(batch_size, samples - start)
        noise = rng.integers(
            -1,
            2,
            size=(batch, scores.shape[0], scores.shape[1]),
            dtype=np.int16,
        )
        perturbed = np.clip(scores[None, :, :] + noise, 1, 10)
        for name, weights in WEIGHTS.items():
            baseline = rankdata(-(scores @ weights), method="average")
            ranks = rankdata(-(perturbed @ weights), method="average", axis=1)
            moved[name] += int(
                np.any(np.abs(ranks - baseline[None, :]) > 1, axis=1).sum()
            )
    return {name: value / samples for name, value in moved.items()}


def print_summary(summary: dict[str, dict[str, float]]) -> None:
    print("summary,equal,retrieval,deployment")
    for key in ("observed_mean", "null_mean", "excess", "pop_sd"):
        values = [100 * summary[weight][key] for weight in WEIGHTS]
        print(f"{key},{values[0]:.1f},{values[1]:.1f},{values[2]:.1f}")


def print_text(
    names: list[str],
    fractions: dict[str, np.ndarray],
    summary: dict[str, dict[str, float]],
) -> None:
    print("method,equal,retrieval,deployment")
    for idx, name in enumerate(names):
        values = [100 * fractions[key][idx] for key in WEIGHTS]
        print(f'{name},{values[0]:.1f},{values[1]:.1f},{values[2]:.1f}')
    print_summary(summary)


def latex_name(name: str) -> str:
    return name.replace("%", r"\%").replace("&", r"\&")


def print_latex(
    names: list[str],
    fractions: dict[str, np.ndarray],
    summary: dict[str, dict[str, float]],
) -> None:
    for idx, name in enumerate(names):
        values = [100 * fractions[key][idx] for key in WEIGHTS]
        print(
            f'{latex_name(name):23s} & {values[0]:.1f}\\% & '
            f'{values[1]:.1f}\\% & {values[2]:.1f}\\% \\\\'
        )
    print(r"\midrule")
    for key in ("observed_mean", "null_mean", "excess", "pop_sd"):
        values = [100 * summary[weight][key] for weight in WEIGHTS]
        label = {
            "observed_mean": "Mean",
            "null_mean": "Null expectation (rank-matched)",
            "excess": "Excess over null (pp)",
            "pop_sd": "Pop. Std. Dev.",
        }[key]
        print(
            f'{label:32s} & {values[0]:.1f}\\% & {values[1]:.1f}\\% & '
            f'{values[2]:.1f}\\% \\\\'
        )


def _summary(
    fractions: dict[str, np.ndarray],
    null_expected: dict[str, np.ndarray],
) -> dict[str, dict[str, float]]:
    """Observed mean, rank-matched null mean, excess, and population SD.

    Each entry of ``null_expected[name]`` is already the null expectation at
    that method's own baseline rank, so the rank-matched null mean is simply
    the average across methods.
    """
    summary: dict[str, dict[str, float]] = {}
    for name in WEIGHTS:
        observed = float(fractions[name].mean())
        null_mean = float(null_expected[name].mean())
        summary[name] = {
            "observed_mean": observed,
            "null_mean": null_mean,
            "excess": observed - null_mean,
            "pop_sd": float(fractions[name].std(ddof=0)),
        }
    return summary


def render_latex_table(
    names: list[str],
    fractions: dict[str, np.ndarray],
    baseline_ranks: dict[str, np.ndarray],
    null_expected: dict[str, np.ndarray],
    samples: int,
    seed: int,
    batch_size: int,
    null_reps: int,
    null_samples: int,
    null_seed: int,
    value_sets: list[np.ndarray],
) -> str:
    summary = _summary(fractions, null_expected)
    sets = "; ".join(f"{k}: {v.tolist()}" for k, v in zip(("E", "Ex", "I"), value_sets))
    caption = (
        r"\caption{Monte Carlo score-perturbation sensitivity: fraction of "
        r"samples in which a method's average-tie rank changes by more than one "
        r"position, rounded to whole percentage points (Monte Carlo standard "
        r"error per cell $\approx 0.1$~pp). \textit{Null expectation "
        r"(rank-matched):} mean instability under the same perturbation process "
        f"applied to {null_reps} replicates of score triplets drawn from the "
        r"distinct values observed on each axis "
        f"({sets.replace('EEx', 'E/Ex')}), "
        f"({null_reps} reps, {null_samples} samples each, seed {null_seed}), "
        r"averaged at each method's baseline rank. \textit{Excess:} observed "
        r"mean minus null expectation; values near zero indicate that rank "
        r"instability follows from perturbation magnitude and rank censoring "
        r"rather than the specific score configuration.}"
    )
    lines = [
        "% Generated by Scripts/eei_sensitivity.py; do not edit by hand.",
        f"% samples={samples}, seed={seed}, batch_size={batch_size}, noise_dtype=int16",
        (
            f"% null: reps={null_reps}, samples_per_rep={null_samples}, "
            f"seed={null_seed}; tie_method=average"
        ),
        (
            f"% rng=NumPy Generator(PCG64); Python={sys.version.split()[0]}; "
            f"NumPy={np.__version__}; SciPy={scipy.__version__}"
        ),
        r"\begin{table}[t]",
        r"\centering",
        r"\scriptsize",
        r"\renewcommand{\arraystretch}{1.08}",
        caption,
        r"\label{tab:eei_sensitivity}",
        r"\begin{tabular}{lccc}",
        r"\toprule",
        r"Method & Equal & Retrieval & Deployment \\",
        r"\midrule",
    ]
    for idx, name in enumerate(names):
        values = [round(100 * fractions[key][idx]) for key in WEIGHTS]
        lines.append(
            f"{latex_name(name)} & {values[0]}\\% & "
            f"{values[1]}\\% & {values[2]}\\% \\\\"
        )
    rows = [
        ("Mean", "observed_mean"),
        ("Null expectation (rank-matched)", "null_mean"),
        ("Excess over null (pp)", "excess"),
        ("Pop. Std. Dev.", "pop_sd"),
    ]
    lines.append(r"\midrule")
    for label, key in rows:
        scale = 100.0 if key != "excess" else 100.0
        values = [
            f"{round(scale * summary[weight][key]):+d} pp"
            if key == "excess"
            else f"{round(scale * summary[weight][key])}\\%"
            for weight in WEIGHTS
        ]
        lines.append(f"{label} & {values[0]} & {values[1]} & {values[2]} \\\\")
    lines.extend(
        [
            r"\bottomrule",
            r"\end{tabular}",
            r"\end{table}",
            "",
        ]
    )
    return "\n".join(lines)


def write_latex_table(path: Path, rendered: str) -> None:
    path.write_text(rendered, encoding="utf-8")


def check_latex_table(path: Path, rendered: str) -> None:
    committed = path.read_text(encoding="utf-8")
    if committed != rendered:
        raise RuntimeError(
            f"Generated LaTeX differs from {path}. Regenerate the committed table "
            "under the pinned environment and review the diff."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scores",
        type=Path,
        default=PROJECT_ROOT / "data/eei_scores.csv",
    )
    parser.add_argument(
        "--inclusion-ledger",
        type=Path,
        default=PROJECT_ROOT / "data/method_metadata.csv",
        help="Versioned method-population ledger checked against the score CSV.",
    )
    parser.add_argument("--samples", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--batch-size", type=int, default=10_000)
    parser.add_argument("--null-reps", type=int, default=NULL_REPS_DEFAULT)
    parser.add_argument("--null-samples", type=int, default=NULL_SAMPLES_DEFAULT)
    parser.add_argument("--null-seed", type=int, default=NULL_SEED_DEFAULT)
    parser.add_argument(
        "--tie-variants",
        action="store_true",
        help="Also report mean instability under min/ordinal/dense tie handling.",
    )
    parser.add_argument("--format", choices=("text", "latex"), default="text")
    parser.add_argument(
        "--write-latex",
        type=Path,
        help="Write the complete compileable Table 6 fragment to this path.",
    )
    parser.add_argument(
        "--check-latex",
        type=Path,
        help="Fail unless generated Table 6 text exactly matches this committed file.",
    )
    parser.add_argument(
        "--check-environment",
        action="store_true",
        help="Validate Python/NumPy/SciPy against the tested versions "
        "(tolerant: warns on patch-level differences and continues).",
    )
    parser.add_argument(
        "--strict-environment",
        action="store_true",
        help="Like --check-environment but hard-fails on ANY version difference "
        "(tested stack: Python 3.13.5, NumPy 2.4.1, SciPy 1.17.0).",
    )
    args = parser.parse_args()

    if args.check_environment or args.strict_environment:
        validate_environment(strict=args.strict_environment)
    names, scores = load_scores(args.scores)
    validate_inclusion_ledger(args.inclusion_ledger, names)
    fractions = simulate(scores, args.samples, args.seed, args.batch_size)
    baseline_ranks = {
        name: rankdata(-(scores @ weights), method="average")
        for name, weights in WEIGHTS.items()
    }
    null_expected = null_expectation(
        scores,
        args.null_samples,
        args.null_reps,
        args.null_seed,
        args.batch_size,
        baseline_ranks,
    )
    summary = _summary(fractions, null_expected)
    if args.tie_variants:
        variants = tie_method_means(
            scores, args.samples, args.seed, args.batch_size
        )
        print("tie_variant_mean,equal,retrieval,deployment")
        for method, means in variants.items():
            values = [100 * means[weight] for weight in WEIGHTS]
            print(f"{method},{values[0]:.1f},{values[1]:.1f},{values[2]:.1f}")
    rendered = render_latex_table(
        names,
        fractions,
        baseline_ranks,
        null_expected,
        args.samples,
        args.seed,
        args.batch_size,
        args.null_reps,
        args.null_samples,
        args.null_seed,
        axis_value_sets(scores),
    )
    if args.check_latex is not None:
        check_latex_table(args.check_latex, rendered)
    if args.write_latex is not None:
        write_latex_table(args.write_latex, rendered)
    if args.format == "latex":
        print_latex(names, fractions, summary)
    else:
        print_text(names, fractions, summary)


if __name__ == "__main__":
    main()