# Methodology (EEI Framework Specification)

Source: `artifacts/validation/rubric.spec.md` in the original manuscript repository.
The narrative derivation, score-consistency protocol, and limitations discussion
appear in manuscript Section 2 (``EEI`` framework subsections).

# EEI Scoring Rubric — Operational Specification
# For fresh scorers applying the rubric without having read the manuscript.
# Source: manuscript paper/Not All Attention Is Equal.tex (verbatim EEI framework section)

## Pre-conditions
- You have the candidate method's paper + any public benchmark results.
- You do NOT look at the existing 21-method score table.
- You have this spec and nothing else from the manuscript.

## Step 1: Gather Evidence

For each axis, collect the following:

### Efficiency (E) Evidence
1. Asymptotic complexity claim (O(L), O(L log L), O(L^2), etc.)
2. Hardware utilization: does the paper report tensor-core usage, SRAM tiling,
   FP8 support, or kernel-launch overhead measurements?
3. Speedup numbers: against what baseline, on what hardware, at what sequence
   length? (Note: speedups are descriptive only, not the primary E anchor.)
4. Is there a demonstrated implementation (code, kernel) under an evaluation
   protocol?

### Expressiveness (Ex) Evidence
1. Long-range retrieval: RULER, Needle-in-a-Haystack, or similar benchmark scores.
2. Language modeling: perplexity on PG-19, WikiText, or similar.
3. Induction head / copying task performance.
4. Positional sensitivity: does the method distinguish fine-grained positions?
5. Pairwise interaction capacity: full, approximated, or structurally constrained?

### Interpretability (I) Evidence
1. Weight observability: are attention weights directly visible, or mediated by
   recurrence/SSM dynamics?
2. Tooling: open-source probing tools, SAEs, state-analysis utilities?
3. Theoretical frameworks: induction heads, SSD duality, etc. — are they
   established for this architecture class?
4. Causal verification: empirical evidence linking heads/dimensions to specific
   features?

## Step 2: Assign Axis Scores

Use the scale anchors below. Bands are qualitative, not strict ceilings.

### Efficiency Score
| Range | Anchor |
|-------|--------|
| 1–3   | >O(L^2), no accelerator-aware optimization |
| 4–5   | O(L^2) with basic GPU kernel |
| 6–7   | Sub-quadratic (O(L√L), O(L log L)) OR O(L^2) with IO-aware tiling |
| 8–9   | O(L) or near-linear with strong hardware utilization, OR O(L^2) at near-peak IO-awareness |
| 10    | O(L) with demonstrated hardware-efficient implementation under evaluation protocol |

### Expressiveness Score
| Range | Anchor |
|-------|--------|
| 1–3   | Cannot model long-range retrieval |
| 4–5   | Full-attention-level quality on short-context; limited long-range evidence |
| 6–7   | Near-baseline on long-context; some degradation on retrieval-sensitive evaluations |
| 8–9   | Comparable to full-attention baseline on evaluated long-context; only limited reported degradation |
| 10    | Full-attention representational capacity; exact pairwise computation; no structural restriction |

### Interpretability Score
| Range | Anchor |
|-------|--------|
| 1–3   | Opaque; no probing tools |
| 4–5   | Partially analyzable; limited component attribution |
| 6–7   | Partially mappable; probing/SAE tools available for some models |
| 8–9   | Established theoretical framework; components align with functional roles |
| 10    | Every component fully characterized with causal evidence (aspirational; no method achieves this) |

## Step 3: Compute Composite Scores

For each weight configuration:
- Equal:             (E + Ex + I) / 3
- Retrieval-focused: 0.2*E + 0.6*Ex + 0.2*I
- Deployment-focused: 0.6*E + 0.2*Ex + 0.2*I

## Step 4: Rank

Sort by composite (descending). Ties: assign average rank (scipy.stats.rankdata
with method='average').

## Step 5: Report

For each method, report:
1. (E, Ex, I) triplet
2. Three composite scores (Equal, Retrieval, Deployment)
3. Rank under each weighting
4. One-line justification per axis per method, citing the exact evidence row
5. Caveat flag if evidence is insufficient for any axis

## Constraint Checklist
- [ ] Scores are integers in [1, 10]
- [ ] No score of 10 on I (aspirational; no method satisfies it)
- [ ] E=10 only for O(L) with demonstrated hardware-efficient implementation
- [ ] Ex=10 only for exact pairwise computation with no structural restriction
- [ ] Weight configs exactly: (1/3,1/3,1/3), (0.2,0.6,0.2), (0.6,0.2,0.2)
- [ ] Tie rule: descending average ranks
- [ ] No peeking at the 21-method panel during scoring
