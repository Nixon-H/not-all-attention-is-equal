# Data

| File | Contents | Source |
|------|----------|--------|
| `eei_scores.csv` | 21 methods × (E, Ex, I) plus per-axis evidence strings and per-axis source ids (`E_source`/`Ex_source`/`I_source`) | `verification-spreadsheet.csv` (manuscript supplementary) + `sources.csv` mapping |
| `eei_scores.json` | same panel, JSON encoding | generated from `eei_scores.csv` |
| `method_metadata.csv` | v1.0 inclusion ledger: analysis status, decision basis, next action | `method-inclusion-ledger.csv` |
| `sources.csv` | 23 source records (author-year, title, venue, arXiv/DOI/URL) for every scored method | manuscript References section (verbatim) |

## Semantics

- Axes: **E** = Efficiency, **Ex** = Expressiveness, **I** = Interpretability,
  each scored on 1--10 (single-rater estimates, assumed perturbation range ±1).
- The 21-method panel is a purposive design-space selection spanning six of the
  seven taxonomy families; it is not a statistically representative sample of
  the 63-paper synthesis (see paper Section 2).
- `method_metadata.csv` `analysis_status` values: `included_current_matrix`
  for all 21 rows in v1.0. The sensitivity script fails unless the ledger rows
  exactly match the score CSV rows (order + names).
- Row order in the score CSV and ledger matches the manuscript's Table 4.
- Every score cell links to a source id resolved by `sources.csv`; the chain is
  score -> evidence string (`*_evidence`) -> source (`*_source`) -> reference.

## Integrity checks

```bash
python ../scripts/reproduce_all.py
```
runs the ledger-vs-CSV agreement check and aborts on mismatch.