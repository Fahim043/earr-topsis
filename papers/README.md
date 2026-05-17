# Papers Directory Notes

Date: 2026-05-16

This directory contains the local prior-art papers used in the current evidence package.

| File | Citation role in this project |
|---|---|
| `huang2010.pdf` | Direct TOPSIS group aggregation anchor. Its preferential-difference, alternative-priority, and group-ideal aggregation logic is adapted as `EB5_HuangLiGroupIdealTOPSIS` in `external_baselines.py`. |
| `s11257-023-09380-z.pdf` | Review paper for consensus models in group decision-making and group recommender systems. Use in related work to position consensus, agreement, and group satisfaction concepts. |
| `s40747-022-00675-z.pdf` | Consensus-building model with non-reciprocal fuzzy preference relations. Use as a consensus-process and non-consensus-DM literature anchor, not as a direct JSON-dataset comparator. |
| `2311.15933v1.pdf` | Recent fuzzy MAGDM method using TOPSIS and optimization models for expert/attribute weighting in interval-valued intuitionistic fuzzy settings. Use for related-work positioning around expert weighting. |

Only `huang2010.pdf` is directly compatible enough with the current triangular fuzzy TOPSIS pipeline to implement as an external comparator without changing the experiment's data representation.
