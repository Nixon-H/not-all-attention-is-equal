# Literature

This directory documents the literature-search component of the survey. It
deliberately contains **only information the authors actually possess**.

| File | Contents | Status |
|------|----------|--------|
| `search_strategy.md` | Databases, date window, keyword families, author-maintained counts, inclusion/exclusion criteria | Author-maintained reconstruction (see boundary statement) |
| `included_papers.csv` | The 21-method EEI scored panel with source mappings and architectural layers | Complete for the scored panel only |

Not included (and not reconstructed): raw database exports, exact
database-specific query strings, deduplication decisions, and the
paper-level screening log. These were not retained by the original review and
are not fabricated here. The 21-method panel is a purposive design-space
selection, not a statistically representative sample of the 63-paper
synthesis; it is not a complete "included studies" table for the narrative
review.

Full score provenance (score -> evidence string -> source) is available in
`data/eei_scores.csv` (columns `E_source`, `Ex_source`, `I_source`) with
`data/sources.csv` resolving every source id.