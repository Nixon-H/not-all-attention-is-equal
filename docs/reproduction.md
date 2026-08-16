# Reproduction

## What this reproduces (and what it does not)

> **Reproducibility scope.** This repository reproduces the computational
> analysis performed in this survey, including the 21-method EEI scoring
> matrix, composite scores, rankings, perturbation sensitivity analysis,
> rank-matched null model, and derived tables and figures. Results reported
> by the underlying literature, including hardware benchmarks and LRA
> evaluations, are treated as published evidence and are not re-run here.
> The repository also does not claim to reproduce the historical
> literature-search process beyond the search methodology and records
> explicitly provided.

```
21-method evidence (data/eei_scores.csv + data/sources.csv)
        ↓
E / Ex / I assignments (scoring rubric in docs/scoring_rubric.md)
        ↓
EEI weighting (3 canonical configurations)
        ↓
rankings (compute_eei.py)
        ↓
±1 perturbation sensitivity (200,000 samples, seed 42)
        ↓
rank-matched null model (50,000 x 100, seed 43)
        ↓
results/tables + results/sensitivity + manuscript (paper/)
```

It does **not** rerun the experiments reported by the 21 underlying papers:
benchmark numbers (LRA, perplexity, speedups, ImageNet) are taken from the
sources recorded in `data/sources.csv` as reported in the manuscript. The
reproducible artifact is the analysis, not the underlying measurements.

In particular, the repository does **not** claim to reproduce:

- FlashAttention's original H100 experiments; Mamba's original training runs,
  or the hardware/software environments used by any of the underlying papers;
- Focus's or DashAttention's original benchmarks (e.g., the 2.0x end-to-end
  speedup or the up-to-3.3x kernel speedup appear as recorded evidence only);
- the original LRA evaluations (e.g., RWKV's self-reported 72.07) or any
  other benchmark numbers as measured by the source authors;
- the historical literature-search process: the raw database exports, exact
  query strings, deduplication decisions, and screening log were not retained
  (see `literature/search_strategy.md` for the boundary).

Running `python scripts/reproduce_all.py` reproduces the survey's use of these
published values, not the values themselves as measured by the original
authors.

## Environment

Pins (see `requirements-eei.txt` at package root):

| Package | Tested version |
|---------|----------------|
| Python  | 3.13.5 |
| NumPy   | 2.4.1   |
| SciPy   | 1.17.0  |

Two validation modes:

- **Tolerant** (default): requires Python 3.13.x; patch-level version
  differences produce a warning and the run continues.
- **Strict** (`--strict-env` / `--strict-environment`): hard-fails on any
  difference from the tested versions; use it when you have installed the
  exact pinned stack.

**Verified cross-environment determinism (2026-08-16):** the Table 6
fragment regenerated under Python 3.13.5 / NumPy 2.3.4 / SciPy 1.17.1 is
byte-identical to the fragment generated under Python 3.13.5 / NumPy 2.4.1 /
SciPy 1.17.0, differing only in the environment-comment line. The pipeline is
deterministic across these patch versions.

## Steps

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-eei.txt
```

### Full reproduction

```bash
python scripts/reproduce_all.py            # env check + tables + composites + null model
```

Writes:

- `results/tables/tab_eei_sensitivity.tex` — manuscript Table 6 fragment
- `results/sensitivity/eei_composites.json` — weighted EEI rankings
- `results/sensitivity/null_expectation.json` — rank-matched null expectation

Quick sanity run: `python scripts/reproduce_all.py --smoke` (reduced samples
and null reps).

### Individual steps

```bash
python scripts/eei_sensitivity.py --check-environment          # tolerant env check
python scripts/eei_sensitivity.py --strict-environment         # exact-pin env check
python scripts/eei_sensitivity.py --check-latex results/tables/tab_eei_sensitivity.tex \
       --scores data/eei_scores.csv --inclusion-ledger data/method_metadata.csv
python scripts/compute_eei.py
python scripts/null_model.py                 # full: 50,000 samples, 100 reps, seed 43
python scripts/generate_tables.py
```

## Protocol (from paper Section 2, score-consistency paragraph)

Perturbation sensitivity: each axis score of each method is perturbed by
sampling uniformly from `{score-1, score, score+1}` (clipped to [1,10]); the
composite rankings are recomputed under the three weight configurations with a
single fixed tie convention (descending average ranks); the reported value is
the fraction of 200,000 samples in which a method's rank changes by more than
one position. RNG: NumPy PCG64, seed 42. The null model draws random score
triplets from the observed axis-value distributions (seed 43) and averages the
same pipeline over 100 replicates, interpolating a rank-level instability curve
at each real method's baseline rank.

## Paper compilation

`paper/Not All Attention Is Equal.pdf` is rendered from
`paper/Not All Attention Is Equal.tex` (pdflatex, 2 passes, two-column 10pt).
Figures are TikZ sources in `paper/figures/*.tikz`, `\input` from the
manuscript — no figure-generation script exists. Run with the Makefile target
`make paper` (paths with spaces are quoted there) or directly:

```bash
cd paper
pdflatex -interaction=nonstopmode -halt-on-error "Not All Attention Is Equal.tex"
pdflatex -interaction=nonstopmode -halt-on-error "Not All Attention Is Equal.tex"
```

The package's manuscript copy differs from the original working copy only in
the `\input` path of the Table 6 fragment (`../results/tables/...` instead of
`artifacts/eei/...`).

## Integrity gates

- `eei_sensitivity.py` aborts if the 21 ledger rows do not exactly match the
  score CSV (names and order) — `scripts/reproduce_all.py` runs this check.
- `--check-latex` fails if regenerated Table 6 differs from the committed
  fragment (expected to differ only when the environment metadata comment or
  method names legitimately change, as in the v1.0 standardization of
  "Mamba-2 (SSD)").
- `scripts/check_manuscript_sync.py` verifies the shipped manuscript:
  document-class line, balanced document environment, every `\input` target
  resolves, and the PDF is newer than the .tex. When run from the original
  working repository (which keeps `1.tex`/`2.tex`), it additionally asserts
  those two differ only in the document-class line.