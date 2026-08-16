# Literature search strategy (author-maintained reconstruction)

This file records the literature-search scope as stated in the manuscript
(paper/Not All Attention Is Equal.tex, Section 2.1 "Literature search" and
Table "tab:methodology"). It is a **reconstruction, not an independently
reproducible systematic-review record**: the original review did not retain
the raw database exports, the exact database-specific query strings, the
deduplication decisions, or the paper-level screening log (see the boundary
statement below). Nothing in this directory is fabricated; every number and
criterion below appears verbatim (or as a direct paraphrase) in the
manuscript.

## Scope

- **Databases:** arXiv, IEEE Xplore, the ACL Anthology, and the ACM Digital
  Library.
- **Window:** papers published between January 2015 and **31 May 2026**;
  foundational works predating the window are cited for context.
- **Keyword families** (title and abstract): attention, Transformers,
  efficient attention, sparse attention, state-space models, mechanistic
  interpretability.
- **Methodology:** structured narrative review with PRISMA-inspired flow
  reporting (Moher et al., 2009), adapted for a rapidly evolving literature.
  Not preregistered.

## Author-maintained counts

| Source | Retrieved (approx.) | Retained after title/abstract screening (approx.) |
|--------|--------------------:|--------------------------------------------------:|
| arXiv | ~820 | ~48 |
| IEEE Xplore | ~140 | ~15 |
| ACL Anthology | ~210 | ~22 |
| ACM Digital Library | ~95 | ~9 |
| **Total** | **~1,265** | **~94** (unique, after deduplication) |

After duplicate removal approximately 1,123 unique records were screened on
title/abstract; approximately 94 proceeded to full-text review, from which 31
were excluded, yielding **63 papers** in the final narrative synthesis. The
per-source retained counts are not additive across rows (the same paper may be
retained from multiple sources).

## Inclusion criteria

A paper was eligible if it (i) introduces a novel attention mechanism,
positional encoding, or efficiency innovation; (ii) provides theoretical
analysis or mechanistic interpretability results for Transformer
architectures; or (iii) presents a benchmark, survey, or empirical comparison
of attention methods.

## Exclusion criteria

Papers focused exclusively on application domains without architectural
novelty; papers superseded by later extended versions; and non-peer-reviewed
technical reports, except where they introduced widely adopted methods (e.g.,
FlashAttention, Mamba).

## From synthesis to scored panel

Of the 63 retained papers, 21 methods were purposively selected for the EEI
scored panel to span six of the seven taxonomy families. The panel is a
design-space comparison across architectural layers, not a statistically
representative sample of the 63-paper synthesis. The panel membership and its
source mapping are recorded in `included_papers.csv`; full score provenance
(scores -> evidence -> source) is in `data/eei_scores.csv` together with
`data/sources.csv`.

## Boundary statement

Quoted from the manuscript:

> "It was not preregistered, and the raw database exports, exact
> database-specific query strings, deduplication decisions, and paper-level
> screening log were not retained. The counts below are therefore an
> author-maintained reconstruction of the search process, not an
> independently reproducible systematic-review record."