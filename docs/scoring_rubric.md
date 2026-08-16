# Scoring Rubric

Source: `artifacts/validation/rubric.en.txt` in the original manuscript repository
(the EEI scoring rubric used to assign every E/Ex/I score in the 21-method panel).

================================================================================
EEI SCORING RUBRIC — Verbatim from paper/Not All Attention Is Equal.tex (the manuscript; table tab:eei-scores)
================================================================================
Source: Table~\ref{tab:eei-rubric} and surrounding text in Section 2.
Extracted: 2026-08-09
================================================================================

AXIS DEFINITIONS
================

Efficiency (E):
  Integrates three factors:
  (i)   asymptotic time complexity as a function of sequence length L,
  (ii)  constant-factor overhead including kernel launch costs and memory
        bandwidth utilization,
  (iii) hardware compatibility, measured by whether the method can exploit
        tensor cores, SRAM tiling, or FP8 acceleration.
  Scores assume contemporary accelerator execution unless otherwise stated.

Expressiveness (Ex):
  Judges whether an attention variant can represent complex token interactions.
  Four sub-dimensions:
  (i)   retrieval accuracy on long-range dependency tasks and benchmarks such as
        Needle-in-a-Haystack and RULER (Hsieh et al., 2024); language-modeling
        quality on datasets such as PG-19 is treated as complementary evidence,
  (ii)  ability to implement copying and induction heads,
  (iii) sensitivity to fine-grained positional distinctions,
  (iv)  capacity to represent full pairwise interactions versus constrained
        patterns.

Interpretability (I):
  Captures how amenable a mechanism is to mechanistic analysis.
  Four sub-dimensions:
  (i)   whether attention weights are directly analyzable (softmax distributions)
        or mediated by recurrence/SSM dynamics,
  (ii)  availability of open-source probing tools and SAEs for the architecture,
  (iii) existence of established theoretical frameworks (e.g., induction heads,
        the SSD duality) that explain model behavior,
  (iv)  empirical verification that individual heads or state dimensions
        correspond to interpretable features.

IMPORTANT: Direct observability of attention weights should not be equated with
faithful causal explanation. I scores treat weight observability as one input
among several rather than as evidence of causal understanding.

================================================================================
1–10 SCALE ANCHORS
================================================================================

Score | Efficiency (E)                                                 | Expressiveness (Ex)                                              | Interpretability (I)
------+----------------------------------------------------------------+------------------------------------------------------------------+---------------------------------------------------------------
1–3   | >O(L^2) without accelerator-aware optimization                | Cannot model long-range retrieval                                | Opaque; no probing tools exist
4–5   | O(L^2) with basic GPU kernel                                   | Full-attention-level quality on short-context evaluations         | Internal representations partially analyzable; limited
      |                                                                | reported by the source, with limited evidence of long-range      | component attribution
      |                                                                | retrieval                                                        |
6–7   | Sub-quadratic (O(L√L) or O(L log L)) or O(L^2) with IO-aware   | Near-baseline quality on evaluated long-context tasks, with      | Components partially mappable; probing or SAE/state-
      | tiling                                                         | some degradation on retrieval-sensitive evaluations               | analysis tools available for some models
8–9   | O(L) or near-linear (O(L log L)) with strong hardware          | Quality comparable to the corresponding full-attention baseline  | Established theoretical framework; components align
      | utilization, or O(L^2) at near-peak IO-awareness              | on the source's evaluated long-context benchmarks, with only     | with identifiable functional roles
      |                                                                | limited reported degradation                                     |
10    | O(L) with demonstrated hardware-efficient implementation       | Full-attention representational capacity with exact pairwise      | Every relevant component fully characterized with
      | under the evaluation protocol                                  | computation and no structural restriction                        | causal evidence

================================================================================
KEY RUBRIC NOTES
================================================================================

- Bands are qualitative anchors, not strict ceilings.
- IO-aware exact methods achieving near-peak hardware utilization (e.g.,
  FlashAttention) receive high E despite O(L^2) compute.
- E=10 is an aspirational maximum for linear-time, highly optimized
  implementations; a method's improvement over a prior linear-time method
  cannot exceed it.
- Ex=10 indicates full-attention representational capacity with exact pairwise
  computation and no approximation or structural restriction.
- I=10 is an aspirational anchor representing comprehensive causal
  characterization of head or state functions rather than a currently
  demonstrated empirical standard; no surveyed method currently satisfies
  this level.
- The I axis primarily reflects the availability of interpretability tooling
  and theoretical frameworks for each architecture class, rather than being a
  model-independent property of inherent interpretability.

================================================================================
COMPOSITE SCORE FORMULA
================================================================================

EEI(w_E, w_Ex, w_I) = w_E * E + w_Ex * Ex + w_I * I
where w_E + w_Ex + w_I = 1

Three canonical weight configurations:
  Equal:             w_E = 1/3, w_Ex = 1/3, w_I = 1/3
  Retrieval-focused: w_E = 0.2, w_Ex = 0.6, w_I = 0.2
  Deployment-focused: w_E = 0.6, w_Ex = 0.2, w_I = 0.2

Alternative formulations (not default):
  EEI_min = min(E/τ_E, Ex/τ_Ex, I/τ_I)  — threshold-based
  EEI_×   = ∏ score_i^w_i               — weighted geometric mean

================================================================================
TIE CONVENTION
================================================================================

scipy.stats.rankdata with method='average', descending.
Tied methods receive the mean of the ranks they occupy.

================================================================================
SCORE PROPERTIES
================================================================================

- Single-rater estimates with assumed ±1 perturbation range.
- Ordinal scales: equal numerical values across axes do not imply commensurate
  quantities.
- The weighted composite is an exploratory index, not a statistically validated
  cardinal score.
- The perturbation analysis (200,000 samples, seed 42) is a sensitivity check,
  not a confidence procedure.
- Only coarse tier-level groupings (top, mid, bottom) are robust; fine-grained
  claims within the 7.0–7.7 composite range are not supported.
