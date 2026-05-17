# External Baselines and Related-Work Anchors

This document records the external comparator baselines added for reviewer-facing evaluation. These are not part of the proposed M1-M7 progression; they are prior-art-inspired baselines used to show that M7 is not only beating weak internal variants.

## Literature Anchors

The comparator choices are grounded in four common lines of group MCDM literature:

1. Classical fuzzy TOPSIS group decision making.
   - Chen's fuzzy TOPSIS extension is a standard reference for fuzzy group decision settings, and it is cited in the group TOPSIS aggregation literature.
   - Huang and Li (2012) note that arithmetic/geometric aggregation of decision-maker judgments is common in group TOPSIS but can be too intuitive and may ignore preference priorities. See: [A Study on Aggregation of TOPSIS Ideal Solutions for Group Decision-Making](https://link.springer.com/article/10.1007/s10726-010-9218-2).

2. Aggregating individual TOPSIS outputs rather than only aggregating raw decision matrices.
   - Huang and Li propose a group TOPSIS aggregation model involving individual preference/ranking information and group ideal solutions. This motivates the individual-rank aggregation comparator and the EB5 Huang-Li group-ideal comparator.

3. Consensus-reaching models in group decision making.
   - Recent consensus-building models emphasize detecting non-consensus decision makers and adjusting or managing disagreement. See: [A consensus building model in group decision making with non-reciprocal fuzzy preference relations](https://link.springer.com/article/10.1007/s40747-022-00675-z).
   - Broad reviews of consensus models also place fuzzy preference relations and agreement processes as central tools in group decision problems. See: [An overview of consensus models for group decision-making and group recommender systems](https://link.springer.com/article/10.1007/s11257-023-09380-z).

4. Optimization/consensus-based expert weighting in fuzzy MAGDM.
   - A recent TOPSIS-and-optimization approach models expert weighting through minimizing differences between individual and overall evaluations. See: [A new fuzzy multi-attribute group decision-making method based on TOPSIS and optimization models](https://arxiv.org/abs/2311.15933).

## Implemented External Baselines

The baselines are implemented in `external_baselines.py` and evaluated by `run_external_baselines.py`.

| Baseline | Description | Why It Is Relevant |
|---|---|---|
| EB1_MedianTOPSIS | Component-wise median aggregation of DM TFNs, then fuzzy TOPSIS. | Robust aggregation comparator. |
| EB2_TrimmedMeanTOPSIS | Component-wise 20% trimmed mean aggregation, then fuzzy TOPSIS. | Tests whether simple robust averaging is enough. |
| EB3_MADConsensusTOPSIS | Filters DMs far from the median consensus vector using MAD/IQR logic, then applies fuzzy TOPSIS. | Consensus/outlier filtering comparator. |
| EB4_IndividualBordaTOPSIS | Runs TOPSIS per DM and aggregates individual rankings by Borda voting. | Group TOPSIS/ranking aggregation comparator. |
| EB5_HuangLiGroupIdealTOPSIS | Runs fuzzy TOPSIS per DM, then aggregates individual closeness coefficients using Huang-Li preferential differences, alternative priorities, and group ideal distances. | Direct TOPSIS group-ideal prior-art adaptation. |

## External Baseline Results

Output files:

- `outputs/external_baselines/external_baseline_metrics.csv`
- `outputs/external_baselines/external_baseline_target_rank_wide.csv`

Target rank under structured contamination:

| Dataset | Attack | Clean Target Rank | EB1 Median | EB2 Trimmed | EB3 MAD Consensus | EB4 Individual Borda |
|---|---:|---:|---:|---:|---:|---:|
| healthcare countries 2021 | 10% | 26 | 26 | 26 | 26 | 25 |
| healthcare countries 2021 | 20% | 26 | 26 | 26 | 26 | 22 |
| healthcare countries 2021 | 30% | 26 | 26 | 19 | 26 | 22 |
| healthcare countries 2021 | 40% | 26 | 23 | 1 | 26 | 16 |
| healthcare countries 2021 | 50% | 26 | 1 | 1 | 1 | 12 |
| healthcare countries 2021 | 60% | 26 | 1 | 1 | 1 | 9 |
| car evaluation | 10% | 300 | 300 | 300 | 300 | 290 |
| car evaluation | 20% | 300 | 300 | 300 | 300 | 282 |
| car evaluation | 30% | 300 | 300 | 293 | 300 | 267 |
| car evaluation | 40% | 300 | 300 | 98 | 300 | 229 |
| car evaluation | 50% | 300 | 1 | 1 | 1 | 121 |
| car evaluation | 60% | 300 | 1 | 1 | 1 | 85 |
| healthcare resource allocation | 10% | 300 | 300 | 300 | 300 | 275 |
| healthcare resource allocation | 20% | 300 | 299 | 300 | 300 | 257 |
| healthcare resource allocation | 30% | 300 | 292 | 170 | 300 | 238 |
| healthcare resource allocation | 40% | 300 | 278 | 1 | 300 | 179 |
| healthcare resource allocation | 50% | 300 | 1 | 1 | 1 | 127 |
| healthcare resource allocation | 60% | 300 | 1 | 1 | 1 | 95 |

The full EB5 table is available in `outputs/final_evidence/external_baseline_target_rank_wide.csv`. In summary, EB5 blocked 0/18 tested attack-fraction scenarios and had mean target-rank error 188.22. This poor adversarial result is expected because Huang and Li's model explicitly assumes honest decision makers and is designed for preference aggregation/satisfaction, not malicious coordinated manipulation.

## Interpretation

The external comparators make the final claim stronger:

- Median, trimmed-mean, and MAD consensus baselines perform well at low-to-moderate contamination.
- They generally collapse at majority contamination because the robust center itself becomes contaminated.
- Individual Borda aggregation reduces some damage but never fully preserves the target rank in the tested settings.
- Huang-Li group-ideal aggregation is an important prior-art comparator, but by itself it does not detect adversarial DMs.
- M7 is the only tested method that preserved the clean target rank across all 18 structured attack-fraction scenarios.

This should be framed carefully:

> M7 outperforms robust aggregation and consensus-filtering comparators under the tested structured attack model.

Do not claim:

> M7 dominates all possible robust MCDM methods.

The local `papers/` directory currently contains the four related-work PDFs used for this framing. The Huang-Li paper is the closest direct TOPSIS aggregation comparator for the current triangular fuzzy TOPSIS data. The consensus-model and interval intuitionistic fuzzy MAGDM papers are useful literature anchors, but their exact algorithms use different input representations, so they are not clean drop-in baselines for the current JSON datasets without changing the experimental problem definition.
