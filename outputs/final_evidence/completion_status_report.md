# Completion Status Report

Date: 2026-05-16

This file records the current project state after the close-out pass. It is intended as a practical bridge between the codebase, the thesis/dissertation write-up, and the journal-paper draft.

## Current Verdict

The project is thesis/dissertation-draft ready as an empirical prototype and is much closer to journal shape than before. The main A1/Q1 technical evidence package is now substantially complete inside this repository: attack-fraction curves, external comparator baselines, one Huang-Li group-ideal TOPSIS adaptation, statistical summaries, runtime/scalability timing, and a hand-checked fuzzy TOPSIS example have all been added. The remaining work is mostly manuscript polishing, exact citation selection, and supervisor-level approval of the final comparator set.

The central hypothesis is supported under the tested threat model:

> Standard fuzzy TOPSIS and plain bagging are vulnerable to coordinated decision-maker contamination, while reliability-aware filtering and weighting can preserve the clean target rank when attackers leave statistically distinguishable structure.

The correct limitation is:

> M7 is robust against structured, distinguishable coordinated manipulation. It is not guaranteed against adaptive attackers that deliberately mimic honest human rating variation.

## Code Fixes Completed

| Area | Status | Notes |
|---|---|---|
| M2 bootstrap | Fixed | Uses true sampling with replacement and respects `num_bags` / `bag_size`. |
| Deterministic seeds | Fixed | Stochastic methods support repeatable runs. |
| M1 mixed criteria | Fixed | M1-M7 now pass optional `criteria_types` into normalization. |
| M5 small bag allocation | Fixed | Guarded custom cases where `bag_size` is smaller than cluster count. |
| Evidence compiler | Added | `compile_final_evidence.py` creates CSV, Markdown, and LaTeX evidence tables. |
| Attack-fraction runner | Added and run | `run_attack_fraction_curves.py` generated 10%-60% degradation curves. |
| External comparators | Added and run | Median, trimmed-mean, MAD-consensus, and individual-Borda TOPSIS baselines. |
| Huang-Li comparator | Added and run | Group-ideal TOPSIS aggregation adapted to individual fuzzy TOPSIS closeness values. |
| Statistical summaries | Added and run | CI table and paired target-error comparisons. |
| Runtime table | Added and run | Representative 30% contamination runtimes at 200 bags. |
| Hand-computed example | Added | Small fuzzy TOPSIS calculation matches code output. |
| Method architecture document | Updated | Explains M1-M7, equations, progression, and recommends M4, M6, and M7 as the three proposed methods. |
| Thesis LaTeX draft | Added | `thesis_latex/main.tex` with chapters, frozen tables, and references. |
| BRAC template LaTeX draft | Added | `bracu_thesis_latex/main.tex` follows the university example structure. |
| Full dissertation guide | Added | `THESIS_AND_GITHUB_GUIDE.md` explains thesis submission, API use, GitHub setup, and code/method roles. |
| Public API scaffold | Added | `web_api/` exposes upload-and-run API for M4, M6, and M7. |

## Main Evidence Artifacts

| File | Purpose |
|---|---|
| `outputs/final_evidence/final_evidence_report.md` | Main human-readable evidence summary. |
| `outputs/final_evidence/real_metrics_long.csv` | Full real/pseudo-real metrics in long form. |
| `outputs/final_evidence/real_contaminated_target_summary_wide.csv` | Target-rank summary across M1-M7. |
| `outputs/final_evidence/synthetic_metrics_long.csv` | Full repeated synthetic metrics. |
| `outputs/final_evidence/synthetic_target_summary_wide.csv` | Synthetic target-rank summary. |
| `outputs/final_evidence/real_target_summary_table.tex` | LaTeX target-rank table for paper draft. |
| `outputs/final_evidence/attack_fraction_target_rank_table.tex` | LaTeX attack-fraction curve table. |
| `outputs/final_evidence/external_baseline_target_rank_table.tex` | LaTeX external comparator table. |
| `outputs/final_evidence/method_target_error_summary_table.tex` | LaTeX statistical target-error summary table. |
| `outputs/final_evidence/runtime_scalability_table.tex` | LaTeX runtime/scalability table. |
| `outputs/final_evidence/attack_fraction_summary.csv` | Full 10%-60% attack-fraction metrics. |
| `outputs/final_evidence/attack_fraction_target_rank_wide.csv` | Paper-ready attack-fraction target-rank table. |
| `outputs/final_evidence/external_baseline_metrics.csv` | Long-form external comparator metrics. |
| `outputs/final_evidence/external_baseline_target_rank_wide.csv` | External comparator target-rank table. |
| `outputs/final_evidence/attack_fraction_ci95.csv` | 95% CI table from repeated-run summaries. |
| `outputs/final_evidence/method_target_error_summary.csv` | Method-level target-error summary across 18 curve scenarios. |
| `outputs/final_evidence/m7_pairwise_target_error_tests.csv` | M7 paired target-error tests vs internal and external comparators. |
| `outputs/final_evidence/runtime_scalability.csv` | Runtime/scalability snapshot. |
| `outputs/attack_fraction_curves/attack_fraction_summary.csv` | Raw full curve output from the benchmark runner. |
| `outputs/attack_fraction_curves_smoke/attack_fraction_summary.csv` | Smoke-test output proving the new curve runner works. |
| `method_architecture_and_proposed_methods.md` | Full method explanation with math and recommended 3-method framing. |
| `external_baselines_and_related_work.md` | External comparator definitions and literature anchors. |
| `hand_computed_fuzzy_topsis_example.md` | Manual fuzzy TOPSIS validation example. |
| `paper_writing_package.md` | Final paper-writing bridge with proposed-method choice, key tables, and evidence file map. |
| `thesis_latex/main.tex` | Main LaTeX thesis/dissertation draft. |
| `bracu_thesis_latex/main.tex` | BRAC University template-compatible thesis/dissertation draft. |
| `THESIS_AND_GITHUB_GUIDE.md` | Step-by-step thesis, API, GitHub, and code explanation guide. |
| `web_api/README.md` | Public demo/API setup notes. |

## Post-Fix Real/Pseudo-Real Target-Rank Summary

Target rank is measured under structured contamination. Higher is better here because the synthetic attack target is chosen as the clean lowest-ranked alternative.

| Dataset | Alternatives | Clean Target Rank | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| healthcare countries 2021 | 26 | 26 | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| car evaluation | 300 | 300 | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| healthcare resource allocation | 300 | 300 | 1 | 52 | 300 | 300 | 16 | 300 | 300 |

Interpretation:

- M1 collapses under targeted contamination.
- M2 improves over M1 but remains insufficient.
- M5 is inconsistent and should be treated as an intermediate or ablation method.
- M4, M6, and M7 are the recommended proposed methods; M3 is a strong internal comparator/intermediate method.
- M7's healthcare-resource Top1 value can be 0 even when the target attack is blocked; this is a benign top-two swap, not target-promotion failure.

## Full Attack-Fraction Curve Summary

The full curve was run for the three publication-facing larger datasets using 30 repeats and 200 bags. Target rank is shown under contamination; the clean target rank is the last rank in each dataset.

| Dataset | Clean Target Rank | Effective Attack | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| healthcare countries 2021 | 26 | 13.3% | 1 | 18 | 26 | 26 | 19 | 26 | 26 |
| healthcare countries 2021 | 26 | 20.0% | 1 | 11 | 26 | 26 | 11 | 26 | 26 |
| healthcare countries 2021 | 26 | 26.7% | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| healthcare countries 2021 | 26 | 40.0% | 1 | 2 | 26 | 26 | 26 | 26 | 26 |
| healthcare countries 2021 | 26 | 53.3% | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| healthcare countries 2021 | 26 | 60.0% | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| car evaluation | 300 | 13.3% | 78 | 272 | 300 | 300 | 289 | 300 | 300 |
| car evaluation | 300 | 20.0% | 48 | 230 | 300 | 300 | 258 | 300 | 300 |
| car evaluation | 300 | 26.7% | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| car evaluation | 300 | 40.0% | 1 | 77 | 300 | 300 | 300 | 300 | 300 |
| car evaluation | 300 | 53.3% | 1 | 18 | 1 | 1 | 1 | 1 | 300 |
| car evaluation | 300 | 60.0% | 1 | 8 | 1 | 1 | 1 | 1 | 300 |
| healthcare resource allocation | 300 | 13.3% | 3 | 168 | 300 | 300 | 166 | 300 | 300 |
| healthcare resource allocation | 300 | 20.0% | 1 | 101 | 300 | 300 | 62 | 300 | 300 |
| healthcare resource allocation | 300 | 26.7% | 1 | 52 | 300 | 300 | 16 | 300 | 300 |
| healthcare resource allocation | 300 | 40.0% | 1 | 11 | 300 | 300 | 300 | 300 | 300 |
| healthcare resource allocation | 300 | 53.3% | 1 | 1 | 1 | 1 | 1 | 1 | 300 |
| healthcare resource allocation | 300 | 60.0% | 1 | 1 | 1 | 1 | 1 | 1 | 300 |

Interpretation:

- M1 collapses early and strongly.
- M2 degrades gradually but does not prevent target promotion.
- M3, M4, and M6 work well through 40% effective contamination, then collapse at majority contamination.
- M7 preserves the target rank at every tested fraction, including 53.3% and 60.0% structured contamination.
- This is strong evidence for M7 under structured distinguishable attacks, but it does not remove the adaptive human-mimic limitation.

## Verification Commands Run

| Command | Result |
|---|---|
| `python -m py_compile ...` | Passed for touched method and evidence scripts. |
| Small cost-criteria smoke test | Passed: lower cost alternative ranked first. |
| Hand-computed TOPSIS smoke test | Passed: code returns A1 = 0.52941176, A2 = 0.47058824. |
| `python compile_final_evidence.py` | Passed and regenerated final evidence package. |
| `python run_all_tests.py` | Passed; confirms M1/M2 vulnerability and M3/M4/M6 improvements on synthetic cases. |
| `python run_attack_fraction_curves.py ... --repeats 2 --num-bags 10` | Passed smoke test for healthcare countries. |
| `python run_attack_fraction_curves.py ... --repeats 30 --num-bags 200` | Passed full 3-dataset 10%-60% curve run. |
| `python run_external_baselines.py` | Passed; generated five comparator baseline tables, including EB5 Huang-Li group-ideal TOPSIS. |
| `python analyze_statistics.py` | Passed; generated CI and paired-test tables. |
| `python run_runtime_scalability.py --fraction 30 --num-bags 200` | Passed; generated runtime table. |
| `python test_m7_supermajority.py` | Passed as a stress test; M7 defended 3 of 4 super-majority scenarios and failed the exact 50% case. |
| `python test_m7_adversarial.py` | Passed as a limitation test; M7 fails adaptive human-mimic scenarios. |
| `python test_m7_ablation.py` | Passed; entropy/clone signals dominate in the current ablation setting. |

## What Is Still Required for A1/Q1 Submission

1. Decide whether the supervisor accepts the current five external comparator baselines, including the Huang-Li group-ideal TOPSIS adaptation, or wants one additional exact published algorithm reproduced.

2. Freeze the method definitions before final manuscript tables. Do not keep changing M7 after the final result section is drafted.

3. Frame claims narrowly:

- avoid "universal robustness";
- avoid "always defeats majority bias";
- use "robust under distinguishable structured coordinated attacks";
- report adaptive human-mimic attacks as a limitation and future-work direction.

4. Convert the generated tables into polished manuscript tables and add journal-style citations.

## Recommended Next Paper Tables

| Table | Source |
|---|---|
| Dataset summary | `real_metrics_long.csv` plus converted JSON metadata. |
| Main contamination target-rank table | `real_target_summary_table.tex`. |
| Full metric table | `real_metrics_long.csv`. |
| Synthetic repeated results | `synthetic_target_summary_wide.csv`. |
| Attack-fraction curves | `attack_fraction_target_rank_wide.csv` and `attack_fraction_summary.csv`. |
| External baseline comparison | `external_baseline_target_rank_wide.csv`. |
| Statistical support | `method_target_error_summary.csv`, `m7_pairwise_target_error_tests.csv`, `attack_fraction_ci95.csv`. |
| M7 limitation map | Output from `test_m7_adversarial.py`. |
| Ablation table | Output from `test_m7_ablation.py`. |
| Runtime table | `runtime_scalability.csv`. |
