# Paper Writing Package

Date: 2026-05-16

This file is the writing bridge for the thesis/dissertation chapter and journal manuscript. It records the final method framing, the key result tables, the prior-art papers currently in the repository, and the exact evidence files to use while drafting.

## Final Verdict

The evidence package is ready for thesis/journal-paper writing under a careful threat model. The claim should be:

> Reliability-aware fuzzy TOPSIS methods reduce targeted rank manipulation when biased decision makers leave statistically distinguishable structure. M7 is strongest under the tested structured coordinated attacks, including majority structured attacks.

Do not claim:

> The method detects all human bias or all strategic adversaries.

The remaining work is manuscript work: narrative, citations, final table polishing, and supervisor approval of the exact comparator set.

## Three Proposed Methods

Use M4, M6, and M7 as the three proposed methods.

| Proposed role | Method | What it adds | Best evidence |
|---|---|---|---|
| Proposed Method 1 | M4 Reliability-weighted bagging | Samples reliable DMs more often inside bootstrap bags. | Blocks the structured attack through 40% effective contamination on all three larger datasets. |
| Proposed Method 2 | M6 Reliability-weighted aggregation | Weights DM ratings directly in fuzzy aggregation. | Also blocks through 40% effective contamination, with simpler interpretation than M7. |
| Proposed Method 3 | M7 Entropy-aware reliability ensemble | Combines entropy, variance consistency, clone/agreement detection, reliability-weighted sampling, reliability-weighted aggregation, and bag-quality weighting. | Blocks all 18 attack-fraction scenarios, including 53.3% and 60.0% effective structured contamination. |

M2 should be presented as the corrected bootstrap ensemble baseline. It is important historically and methodologically, but it is not strong enough to be one of the three proposed final methods. M5 should be presented as a cluster-stratified branch/ablation because it is conceptually useful but experimentally inconsistent.

## Main Result Tables

### Focused real/pseudo-real benchmark

Target rank under structured 26.7% effective contamination. Higher is better because the attack target is chosen as the clean lowest-ranked alternative.

| Dataset | Alternatives | Clean target rank | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| healthcare_countries_2021 | 26 | 26 | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| car_evaluation | 300 | 300 | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| healthcare_resource_allocation | 300 | 300 | 1 | 52 | 300 | 300 | 16 | 300 | 300 |

Interpretation: M1 collapses; M2 helps but does not block; M4/M6/M7 block the attack in the three larger datasets; M5 is unstable.

### Attack-fraction curve

Clean target rank is the last rank in each dataset. Values show the contaminated target rank.

| Dataset | Clean | Effective attack | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| healthcare_countries_2021 | 26 | 13.3% | 1 | 18 | 26 | 26 | 19 | 26 | 26 |
| healthcare_countries_2021 | 26 | 20.0% | 1 | 11 | 26 | 26 | 11 | 26 | 26 |
| healthcare_countries_2021 | 26 | 26.7% | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| healthcare_countries_2021 | 26 | 40.0% | 1 | 2 | 26 | 26 | 26 | 26 | 26 |
| healthcare_countries_2021 | 26 | 53.3% | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| healthcare_countries_2021 | 26 | 60.0% | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| car_evaluation | 300 | 13.3% | 78 | 272 | 300 | 300 | 289 | 300 | 300 |
| car_evaluation | 300 | 20.0% | 48 | 230 | 300 | 300 | 258 | 300 | 300 |
| car_evaluation | 300 | 26.7% | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| car_evaluation | 300 | 40.0% | 1 | 77 | 300 | 300 | 300 | 300 | 300 |
| car_evaluation | 300 | 53.3% | 1 | 18 | 1 | 1 | 1 | 1 | 300 |
| car_evaluation | 300 | 60.0% | 1 | 8 | 1 | 1 | 1 | 1 | 300 |
| healthcare_resource_allocation | 300 | 13.3% | 3 | 168 | 300 | 300 | 166 | 300 | 300 |
| healthcare_resource_allocation | 300 | 20.0% | 1 | 101 | 300 | 300 | 62 | 300 | 300 |
| healthcare_resource_allocation | 300 | 26.7% | 1 | 52 | 300 | 300 | 16 | 300 | 300 |
| healthcare_resource_allocation | 300 | 40.0% | 1 | 11 | 300 | 300 | 300 | 300 | 300 |
| healthcare_resource_allocation | 300 | 53.3% | 1 | 1 | 1 | 1 | 1 | 1 | 300 |
| healthcare_resource_allocation | 300 | 60.0% | 1 | 1 | 1 | 1 | 1 | 1 | 300 |

Interpretation: M4 and M6 are strong through 40% effective contamination; M7 is the only method that blocks all tested structured fractions.

### External comparator summary

| Method | Cases | Blocked cases | Blocked rate | Mean target-rank error | Max target-rank error |
|---|---:|---:|---:|---:|---:|
| EB1 Median TOPSIS | 18 | 8 | 0.444 | 71.11 | 299 |
| EB2 Trimmed-Mean TOPSIS | 18 | 6 | 0.333 | 106.44 | 299 |
| EB3 MAD-Consensus TOPSIS | 18 | 12 | 0.667 | 69.22 | 299 |
| EB4 Individual-Borda TOPSIS | 18 | 0 | 0.000 | 66.94 | 215 |
| EB5 Huang-Li Group-Ideal TOPSIS | 18 | 0 | 0.000 | 188.22 | 297 |
| M4 | 18 | 12 | 0.667 | 69.22 | 299 |
| M6 | 18 | 12 | 0.667 | 69.22 | 299 |
| M7 | 18 | 18 | 1.000 | 0.00 | 0 |

Interpretation: robust aggregation and consensus filtering help at low/moderate contamination but collapse at majority contamination. Huang-Li is important prior art, but assumes honest DMs and is not adversarially robust.

### Pairwise statistical evidence

M7 has lower target-rank error than M1, M2, EB4, and EB5 in all 18 scenarios. Against M3, M4, M6, and EB3, M7 improves the six majority/high-contamination scenarios and ties the other twelve.

| Comparison | M7 better | M7 worse | Ties | Sign-test p | Wilcoxon approx p |
|---|---:|---:|---:|---:|---:|
| M7 vs M1 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7 vs M2 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7 vs M4 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7 vs M6 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7 vs EB5 Huang-Li | 18 | 0 | 0 | 0.000008 | 0.000214 |

### Runtime snapshot

Representative one-run time at 30% contamination and 200 bags.

| Dataset | M1 sec | M2 sec | M4 sec | M6 sec | M7 sec |
|---|---:|---:|---:|---:|---:|
| healthcare_countries_2021 | 0.003879 | 0.379782 | 0.387423 | 0.290956 | 0.314665 |
| car_evaluation, 300 alts | 0.027566 | 2.195600 | 2.225590 | 1.728492 | 1.818380 |
| healthcare_resource_allocation, 300 alts | 0.077116 | 6.809488 | 6.862630 | 5.468489 | 5.730772 |

Interpretation: M7 is much slower than M1, but comparable to the other ensemble methods and practical for offline decision-support analysis.

## Exact Evidence Files

Use these files directly when writing:

| File | Use |
|---|---|
| `bracu_thesis_latex/main.tex` | BRAC University template-compatible thesis/dissertation draft. |
| `bracu_thesis_latex/core/` | BRAC-style front matter files. |
| `bracu_thesis_latex/chapters/` | BRAC-style chapter files. |
| `thesis_latex/main.tex` | Main LaTeX thesis/dissertation draft. |
| `thesis_latex/chapters/` | Chapter-by-chapter thesis content. |
| `thesis_latex/tables/` | Frozen thesis result tables. |
| `web_api/` | Public demo/API scaffold for upload-and-run method trials. |
| `outputs/final_evidence/final_evidence_report.md` | Main readable evidence report. |
| `outputs/final_evidence/completion_status_report.md` | Current status and readiness report. |
| `method_architecture_and_proposed_methods.md` | Full M1-M7 method explanation, math, and diagrams. |
| `external_baselines_and_related_work.md` | Comparator definitions and prior-art anchors. |
| `hand_computed_fuzzy_topsis_example.md` | Hand-computed validation example. |
| `professor_draft_report.md` | Professor-facing research status report. |
| `outputs/final_evidence/real_metrics_long.csv` | Full real/pseudo-real Spearman, Kendall, Top1, target-rank metrics. |
| `outputs/final_evidence/real_contaminated_target_summary_wide.csv` | Wide target-rank table for real/pseudo-real contamination. |
| `outputs/final_evidence/attack_fraction_summary.csv` | Full attack-fraction metrics. |
| `outputs/final_evidence/attack_fraction_target_rank_wide.csv` | Wide attack-fraction target-rank table. |
| `outputs/final_evidence/external_baseline_metrics.csv` | Full external comparator metrics. |
| `outputs/final_evidence/external_baseline_target_rank_wide.csv` | Wide external comparator table. |
| `outputs/final_evidence/attack_fraction_ci95.csv` | 95% confidence-interval summaries. |
| `outputs/final_evidence/method_target_error_summary.csv` | Blocked-rate and target-error summary. |
| `outputs/final_evidence/m7_pairwise_target_error_tests.csv` | Paired statistical comparisons. |
| `outputs/final_evidence/runtime_scalability.csv` | Runtime table. |
| `outputs/final_evidence/real_target_summary_table.tex` | LaTeX real target-rank table. |
| `outputs/final_evidence/attack_fraction_target_rank_table.tex` | LaTeX attack-fraction table. |
| `outputs/final_evidence/external_baseline_target_rank_table.tex` | LaTeX external baseline table. |
| `outputs/final_evidence/method_target_error_summary_table.tex` | LaTeX statistical summary table. |
| `outputs/final_evidence/runtime_scalability_table.tex` | LaTeX runtime table. |

## Local Papers

| Local file | Paper role |
|---|---|
| `papers/huang2010.pdf` | Main direct TOPSIS group aggregation prior-art anchor; used for EB5. |
| `papers/s11257-023-09380-z.pdf` | Consensus-model review for group decision-making and group recommender systems. |
| `papers/s40747-022-00675-z.pdf` | Consensus-building model with fuzzy preference relations; supports discussion of consensus and non-consensus DMs. |
| `papers/2311.15933v1.pdf` | Recent fuzzy MAGDM TOPSIS/optimization paper; supports expert-weight and TOPSIS-related positioning. |

## Recommended Manuscript Claim

Use wording close to:

> The proposed reliability-aware fuzzy TOPSIS framework improves resistance to targeted rank manipulation under structured coordinated decision-maker contamination. In attack-fraction experiments over three larger real/pseudo-real datasets, M4 and M6 preserved the clean target rank through 40% effective contamination, while M7 preserved the clean target rank across all tested structured contamination levels up to 60%. These results outperform standard fuzzy TOPSIS, corrected bootstrap bagging, robust aggregation comparators, consensus-filtering comparators, and a Huang-Li group-ideal TOPSIS aggregation adaptation. The method is not claimed to be universally robust against adaptive adversaries that deliberately mimic honest human rating variation.

## Remaining Writing Decisions

1. Decide the final paper title and method name. Suggested: `Entropy-Aware Reliability-Weighted Ensemble Fuzzy TOPSIS for Robust Group Decision-Making`.
2. Decide whether to call the framework `EARR-TOPSIS`, `DR-BFTOPSIS`, or another single name. Do not use multiple names in the manuscript.
3. Freeze the result tables before writing the final Results section.
4. Ask the professor whether EB5 plus EB1-EB4 is enough external comparison, or whether one more exact published algorithm should be implemented.
