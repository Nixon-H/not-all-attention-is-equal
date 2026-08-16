# Not All Attention Is Equal: A Quantitative Survey of the EEI Trade-off

Reproducibility package for the paper *"Not All Attention Is Equal: A
Quantitative Survey of the EEI Trade-off"* (Efficiency--Expressiveness--
Interpretability framework), by Aditya Singh (Nixon-H).

**Repository:** <https://github.com/Nixon-H/not-all-attention-is-equal>

## Reproducibility scope

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
Underlying papers (published benchmarks, complexity claims)
        │  treated as extracted evidence, not re-run
        ▼
21-method EEI score assignments (data/eei_scores.csv)
        ▼
EEI calculations (Equal / Retrieval / Deployment weights)
        ▼
Rankings and tie handling
        ▼
±1 perturbation sensitivity  ──►  rank-matched null model
        ▼
Tables / figures / reported analysis  ──►  manuscript
```

Running `python scripts/reproduce_all.py` reproduces the survey's use of the
published values — e.g. Focus's 2.0x speedup or RWKV's LRA 72.07 appear as
recorded evidence — not the original papers' experiments. The repository
reproduces the survey's analysis of those papers, nothing less and nothing
more. (See `docs/reproduction.md` for the full boundary.)

## Layout

```
not-all-attention-is-equal/
├── README.md
├── LICENSE                     # CC BY 4.0
├── CITATION.cff
├── requirements-eei.txt        # pinned numpy/scipy (Python 3.13.x, see file)
├── Makefile                    # reproduce / paper / check / clean
├── paper/                      # manuscript sources
│   ├── Not All Attention Is Equal.tex   # two-column 10pt master
│   ├── Not All Attention Is Equal.pdf
│   └── figures/                # TikZ figure sources (\input from .tex);
│                              # 7 external .tikz files + Figure 2 (PRISMA
│                              # flow) inline in the manuscript = 8 figures
├── data/
│   ├── eei_scores.csv          # 21 methods x (E, Ex, I) + evidence + per-axis source ids
│   ├── eei_scores.json         # same panel as JSON
│   ├── method_metadata.csv     # v1.0 method inclusion ledger
│   ├── sources.csv             # source_id -> full reference for every score
│   └── README.md
├── scripts/
│   ├── eei_sensitivity.py      # perturbation-sensitivity protocol (Table 6)
│   ├── compute_eei.py          # weighted EEI composites + rankings
│   ├── null_model.py           # rank-matched null expectation
│   ├── generate_tables.py      # regenerates the Table 6 fragment
│   ├── check_manuscript_sync.py# manuscript integrity check (inputs resolve, PDF fresh)
│   └── reproduce_all.py        # end-to-end runner
├── results/                    # generated outputs land here
│   ├── tables/                 # tab_eei_sensitivity.tex (committed Table 6 fragment)
│   ├── figures/                # (figure outputs; see paper/figures)
│   └── sensitivity/            # committed + regenerated outputs
├── literature/
│   ├── search_strategy.md      # search scope + author-maintained counts
│   ├── included_papers.csv     # the 21-method scored panel with sources
│   └── README.md
└── docs/
    ├── methodology.md          # EEI framework specification
    ├── scoring_rubric.md       # the scoring rubric as applied
    └── reproduction.md         # step-by-step reproduction instructions
```

## Reproduce (analysis pipeline)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-eei.txt
python scripts/reproduce_all.py            # env check + Table 6 + composites + null model
python scripts/eei_sensitivity.py --check-latex results/tables/tab_eei_sensitivity.tex
```

Expected: env check passes (or warns on a compatible 3.13.x environment),
`--check-latex` exits 0 (regenerated Table 6 matches the committed fragment
byte-for-byte), and sensitivity/null outputs land in `results/sensitivity/`.

The perturbation protocol (200,000 samples, PCG64, seed 42; Table 6) and the
null model (50,000 samples x 100 repetitions, seed 43) are described in the
manuscript, Section 2.

### Environment modes

| Mode | Behavior |
|------|----------|
| Tolerant (default) | Requires Python 3.13.x; warns — does not fail — on patch-level differences (e.g. NumPy 2.3.5 vs the tested 2.4.1). The computation is deterministic across these versions. |
| Strict (`--strict-env`) | Hard-fails unless Python 3.13.5 / NumPy 2.4.1 / SciPy 1.17.0 are present. Use this when you have installed the exact pinned stack. |

Tested environment (2026-08-16): Python 3.13.5, NumPy 2.4.1, SciPy 1.17.0.

### Build the paper

```bash
make paper           # pdflatex x2 in paper/
```

or `make reproduce paper check clean` for the full loop. `make check` runs the
manuscript integrity check plus the committed-table fidelity check.

## Data provenance

- `data/eei_scores.csv` mirrors `verification-spreadsheet.csv`; the 21-method
  ledger (`data/method_metadata.csv`) is checked for exact agreement against
  the score CSV by the sensitivity script.
- Every E/Ex/I assignment carries an evidence string (what was judged) and a
  `*_source` id (which work it was judged against). `data/sources.csv`
  resolves every source id — the score -> evidence -> source chain is fully
  traceable. All source metadata is taken verbatim from the manuscript's own
  References section.
- `literature/search_strategy.md` records the search scope and
  author-maintained counts, and states the boundary: raw database exports,
  query strings, deduplication decisions, and the screening log were not
  retained and are not reconstructed.

## Provenance / edits note

- `paper/Not All Attention Is Equal.tex` and all figures are the manuscript
  as of 2026-08-11 (two-column 10pt; timeline figure-08 year conventions:
  cited publication/release years, per the caption). It differs from the
  original working copy only in the `\input` path of the committed Table 6
  fragment (`../results/tables/...` instead of the repository-internal
  `artifacts/eei/...`), keeping the package self-contained.
- No `.bib` exists: the manuscript uses a hand-typeset References section
  with inline author--year citations; `data/sources.csv` covers the scored
  panel.
- Figures are hand-authored TikZ sources; seven are external `.tikz` files in
  `paper/figures/` and Figure 2 (the PRISMA/literature-screening flow) is
  drawn inline in the manuscript, so the compiled document has eight figures
  total. There is no automated figure generator, so `generate_figures.py` is
  intentionally not shipped. `pdflatex main` regenerates the PDF from source.
- Papers' original PDFs are intentionally not bundled (copyright); the
  `literature/` + `data/sources.csv` layer provides identifiers and links
  instead.

## License

CC BY 4.0 (see LICENSE).