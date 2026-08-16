# Results

Generated outputs (committed where they are manuscript inputs, otherwise
produced by `scripts/reproduce_all.py`):

| Path | Status | Produced by |
|------|--------|-------------|
| `tables/tab_eei_sensitivity.tex` | committed (manuscript Table 6 input) | `generate_tables.py` / `reproduce_all.py` |
| `sensitivity/eei_composites.json` | generated | `compute_eei.py` |
| `sensitivity/null_expectation.json` | generated | `null_model.py` |
| `figures/` | intentionally empty | no automated figure generator exists; figures live as TikZ sources in `paper/figures/` |

The `tables/` fragment is the exact `\input` used by
`paper/Not All Attention Is Equal.tex` (`\input{../results/tables/tab_eei_sensitivity.tex}`);
`--check-latex` verifies regenerated output matches it byte-for-byte.
