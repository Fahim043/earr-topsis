# Final Evidence Tables for Thesis and Journal Draft

Generated from saved CSV outputs. These tables summarize target-rank behavior; use the long-form CSV files for full Spearman, Kendall, Top1, and standard deviation values.

## Key Interpretation

- M1 is the vulnerable standard fuzzy TOPSIS baseline.
- M2 is true bootstrap bagged fuzzy TOPSIS and should be reported as the corrected ensemble baseline; it often helps but is not sufficient.
- M5 is inconsistent and should be treated as an intermediate/ablation method.
- M4, M6, and M7 are the recommended proposed methods; M3 is a strong internal comparator/intermediate reliability method.
- Target-rank error is more important than Spearman/Kendall for targeted manipulation, because global rank correlations can stay high while the attacked target moves sharply upward.

## Post-Fix Focused Real/Pseudo-Real Benchmarks

These are the three larger datasets rerun after the latest code fixes with 30 repeats and 200 bags. Supplier cases are intentionally excluded from this table because they have only two DMs and are diagnostic only.

| Dataset | Alts | Target | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_evaluation | 300 | Car_1_unacc | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| healthcare_countries_2021 | 26 | Romania | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| healthcare_resource_allocation | 300 | 衡水市_2008 | 1 | 52 | 300 | 300 | 16 | 300 | 300 |

## Earlier Light Real/Pseudo-Real Benchmarks

| Dataset | Alts | Target | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_evaluation | 80 | Car_1_unacc | 1 | 31 | 80 | 80 | 31 | 80 | 80 |
| healthcare_countries_2021 | 26 | Romania | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| healthcare_resource_allocation | 80 | 邯郸市_2008 | 1 | 26 | 80 | 80 | 26 | 80 | 80 |
| supplier_beg_rashid | 4 | A1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| supplier_wu | 4 | A1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 |

## Repeated Synthetic Benchmarks

| Dataset | Clean A1 Rank | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DS10_500DM_10pct | 11 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 11.000 +/- 0.000 | 14.500 +/- 0.500 | 2.000 +/- 0.000 | 13.500 +/- 0.500 | 14.500 +/- 0.500 |
| DS1_10DM_30pct | 4 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 3.000 +/- 0.000 | 5.000 +/- 0.000 | 5.000 +/- 0.000 | 5.000 +/- 0.000 | 5.000 +/- 0.000 |
| DS2_10DM_50pct | 3 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| DS3_20DM_25pct | 1 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 |
| DS4_15DM_40pct | 4 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 4.000 +/- 0.000 | 3.000 +/- 0.000 | 4.000 +/- 0.000 | 3.500 +/- 0.500 | 4.000 +/- 0.000 |
| DS5_6DM_33pct | 1 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 |
| DS6_30DM_20pct | 2 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 |
| DS7_50DM_30pct | 8 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 8.000 +/- 0.000 | 8.000 +/- 0.000 | 1.000 +/- 0.000 | 8.000 +/- 0.000 | 8.000 +/- 0.000 |
| DS8_100DM_20pct | 6 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 5.000 +/- 0.000 | 6.000 +/- 0.000 | 1.000 +/- 0.000 | 6.000 +/- 0.000 | 6.000 +/- 0.000 |
| DS9_200DM_25pct | 2 | 1.000 +/- 0.000 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 | 1.000 +/- 0.000 | 2.000 +/- 0.000 | 2.000 +/- 0.000 |

## Attack-Fraction Curves

| Dataset | Req. Attack | Eff. Attack | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| car_evaluation | 10% | 0.133 | 78 | 272 | 300 | 300 | 289 | 300 | 300 |
| car_evaluation | 20% | 0.200 | 48 | 230 | 300 | 300 | 258 | 300 | 300 |
| car_evaluation | 30% | 0.267 | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| car_evaluation | 40% | 0.400 | 1 | 77 | 300 | 300 | 300 | 300 | 300 |
| car_evaluation | 50% | 0.533 | 1 | 18 | 1 | 1 | 1 | 1 | 300 |
| car_evaluation | 60% | 0.600 | 1 | 8 | 1 | 1 | 1 | 1 | 300 |
| healthcare_countries_2021 | 10% | 0.133 | 1 | 18 | 26 | 26 | 19 | 26 | 26 |
| healthcare_countries_2021 | 20% | 0.200 | 1 | 11 | 26 | 26 | 11 | 26 | 26 |
| healthcare_countries_2021 | 30% | 0.267 | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| healthcare_countries_2021 | 40% | 0.400 | 1 | 2 | 26 | 26 | 26 | 26 | 26 |
| healthcare_countries_2021 | 50% | 0.533 | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| healthcare_countries_2021 | 60% | 0.600 | 1 | 1 | 1 | 1 | 1 | 1 | 26 |
| healthcare_resource_allocation | 10% | 0.133 | 3 | 168 | 300 | 300 | 166 | 300 | 300 |
| healthcare_resource_allocation | 20% | 0.200 | 1 | 101 | 300 | 300 | 62 | 300 | 300 |
| healthcare_resource_allocation | 30% | 0.267 | 1 | 52 | 300 | 300 | 16 | 300 | 300 |
| healthcare_resource_allocation | 40% | 0.400 | 1 | 11 | 300 | 300 | 300 | 300 | 300 |
| healthcare_resource_allocation | 50% | 0.533 | 1 | 1 | 1 | 1 | 1 | 1 | 300 |
| healthcare_resource_allocation | 60% | 0.600 | 1 | 1 | 1 | 1 | 1 | 1 | 300 |

## External Comparator Baselines

These prior-art-inspired comparators are not part of M1-M7. They test robust aggregation, consensus filtering, and individual-rank aggregation alternatives.

| Dataset | Attack | Clean Target | Median | Trimmed | MAD Consensus | Individual Borda | Huang-Li Group Ideal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| car_evaluation | 10% | 300 | 300 | 300 | 300 | 290 | 118 |
| car_evaluation | 20% | 300 | 300 | 300 | 300 | 282 | 73 |
| car_evaluation | 30% | 300 | 300 | 293 | 300 | 267 | 53 |
| car_evaluation | 40% | 300 | 300 | 98 | 300 | 229 | 27 |
| car_evaluation | 50% | 300 | 1 | 1 | 1 | 121 | 15 |
| car_evaluation | 60% | 300 | 1 | 1 | 1 | 85 | 11 |
| healthcare_countries_2021 | 10% | 26 | 26 | 26 | 26 | 25 | 8 |
| healthcare_countries_2021 | 20% | 26 | 26 | 26 | 26 | 22 | 6 |
| healthcare_countries_2021 | 30% | 26 | 26 | 19 | 26 | 22 | 4 |
| healthcare_countries_2021 | 40% | 26 | 23 | 1 | 26 | 16 | 2 |
| healthcare_countries_2021 | 50% | 26 | 1 | 1 | 1 | 12 | 1 |
| healthcare_countries_2021 | 60% | 26 | 1 | 1 | 1 | 9 | 1 |
| healthcare_resource_allocation | 10% | 300 | 300 | 300 | 300 | 275 | 17 |
| healthcare_resource_allocation | 20% | 300 | 299 | 300 | 300 | 257 | 12 |
| healthcare_resource_allocation | 30% | 300 | 292 | 170 | 300 | 238 | 8 |
| healthcare_resource_allocation | 40% | 300 | 278 | 1 | 300 | 179 | 5 |
| healthcare_resource_allocation | 50% | 300 | 1 | 1 | 1 | 127 | 4 |
| healthcare_resource_allocation | 60% | 300 | 1 | 1 | 1 | 95 | 3 |

## Statistical Summary

| Method | Cases | Blocked | Blocked Rate | Mean Target Error | Max Target Error |
| --- | --- | --- | --- | --- | --- |
| EB1_MedianTOPSIS | 18 | 8 | 0.444 | 71.111111 | 299.000000 |
| EB2_TrimmedMeanTOPSIS | 18 | 6 | 0.333 | 106.444444 | 299.000000 |
| EB3_MADConsensusTOPSIS | 18 | 12 | 0.667 | 69.222222 | 299.000000 |
| EB4_IndividualBordaTOPSIS | 18 | 0 | 0.000 | 66.944444 | 215.000000 |
| EB5_HuangLiGroupIdealTOPSIS | 18 | 0 | 0.000 | 188.222222 | 297.000000 |
| M1 | 18 | 0 | 0.000 | 199.388889 | 299.000000 |
| M2 | 18 | 0 | 0.000 | 144.946278 | 299.000000 |
| M3 | 18 | 12 | 0.667 | 69.222222 | 299.000000 |
| M4 | 18 | 12 | 0.667 | 69.222222 | 299.000000 |
| M5 | 18 | 3 | 0.167 | 117.031500 | 299.000000 |
| M6 | 18 | 12 | 0.667 | 69.222222 | 299.000000 |
| M7 | 18 | 18 | 1.000 | 0.000000 | 0.000000 |

## M7 Pairwise Target-Error Tests

Positive cases mean M7 had lower target-rank error than the comparator over the same dataset/fraction scenario.

| Comparison | Cases | M7 Better | M7 Worse | Ties | Sign p | Wilcoxon p |
| --- | --- | --- | --- | --- | --- | --- |
| M7_vs_EB1_MedianTOPSIS | 18 | 10 | 0 | 8 | 0.001953 | 0.005922 |
| M7_vs_EB2_TrimmedMeanTOPSIS | 18 | 12 | 0 | 6 | 0.000488 | 0.002526 |
| M7_vs_EB3_MADConsensusTOPSIS | 18 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7_vs_EB4_IndividualBordaTOPSIS | 18 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7_vs_EB5_HuangLiGroupIdealTOPSIS | 18 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7_vs_M1 | 18 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7_vs_M2 | 18 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7_vs_M3 | 18 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7_vs_M4 | 18 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7_vs_M5 | 18 | 15 | 0 | 3 | 0.000061 | 0.000727 |
| M7_vs_M6 | 18 | 6 | 0 | 12 | 0.031250 | 0.036032 |

## Runtime/Scalability Snapshot

Runtimes are representative single executions at the 30% contaminated setting with 200 bags. Stochastic methods include a projected 30-repeat runtime.

| Dataset | Method | Alts | Criteria | One Run Sec | Projected 30x Sec |
| --- | --- | --- | --- | --- | --- |
| healthcare_countries_2021 | M1 | 26 | 13 | 0.003879 | 0.003879 |
| healthcare_countries_2021 | M2 | 26 | 13 | 0.379782 | 11.393456 |
| healthcare_countries_2021 | M3 | 26 | 13 | 0.011674 | 0.011674 |
| healthcare_countries_2021 | M4 | 26 | 13 | 0.387423 | 11.622676 |
| healthcare_countries_2021 | M5 | 26 | 13 | 0.405515 | 12.165454 |
| healthcare_countries_2021 | M6 | 26 | 13 | 0.290956 | 8.728688 |
| healthcare_countries_2021 | M7 | 26 | 13 | 0.314665 | 9.439956 |
| car_evaluation | M1 | 300 | 6 | 0.027566 | 0.027566 |
| car_evaluation | M2 | 300 | 6 | 2.195600 | 65.868006 |
| car_evaluation | M3 | 300 | 6 | 0.030751 | 0.030751 |
| car_evaluation | M4 | 300 | 6 | 2.225590 | 66.767711 |
| car_evaluation | M5 | 300 | 6 | 2.265995 | 67.979857 |
| car_evaluation | M6 | 300 | 6 | 1.728492 | 51.854771 |
| car_evaluation | M7 | 300 | 6 | 1.818380 | 54.551413 |
| healthcare_resource_allocation | M1 | 300 | 18 | 0.077116 | 0.077116 |
| healthcare_resource_allocation | M2 | 300 | 18 | 6.809488 | 204.284635 |
| healthcare_resource_allocation | M3 | 300 | 18 | 0.103576 | 0.103576 |
| healthcare_resource_allocation | M4 | 300 | 18 | 6.862630 | 205.878902 |
| healthcare_resource_allocation | M5 | 300 | 18 | 7.013459 | 210.403774 |
| healthcare_resource_allocation | M6 | 300 | 18 | 5.468489 | 164.054656 |
| healthcare_resource_allocation | M7 | 300 | 18 | 5.730772 | 171.923161 |

## Remaining Work for A1/Q1-Grade Submission

1. If the supervisor requires exact prior-art reproductions, select 1-2 specific published algorithms and implement them in addition to the current robust comparators.
2. Freeze M7 and rerun all final tables after any future code changes.
3. Preserve human-mimic/adaptive attacks as a limitation and threat-model boundary.
4. Convert these tables into polished manuscript tables with citations and narrative explanation.
