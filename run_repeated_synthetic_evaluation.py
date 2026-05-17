"""
run_repeated_synthetic_evaluation.py
====================================
Repeated-seed evaluation for synthetic DS1-DS10 experiments.

This produces publication-style metric CSVs instead of one-off pass/fail logs.
Metrics are computed against the clean M1 ranking for each generated dataset.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean, pstdev

from run_all_tests import generate_dataset

import m1_normal_topsis as m1
import m2_bagged_topsis as m2
import m3_ml_filtered as m3
import m4_weighted_bagging as m4
import m5_cluster_stratified as m5
import m6_reliability_weighted as m6
import m7_entropy_reliability as m7


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "outputs" / "synthetic_repeated_evaluation"

METHODS = [
    ("M1", lambda path, num_bags, seed: m1.run_m1(path)),
    ("M2", lambda path, num_bags, seed: m2.run_m2(path, num_bags=num_bags, seed=seed + 2)),
    ("M3", lambda path, num_bags, seed: m3.run_m3(path)[0]),
    ("M4", lambda path, num_bags, seed: m4.run_m4(path, num_bags=num_bags, seed=seed + 4)[0]),
    ("M5", lambda path, num_bags, seed: m5.run_m5(path, num_bags=num_bags, seed=seed + 5)[0]),
    ("M6", lambda path, num_bags, seed: m6.run_m6(path, num_bags=num_bags, seed=seed + 6)[0]),
    ("M7", lambda path, num_bags, seed: m7.run_m7(path, num_bags=num_bags, seed=seed + 7)[0]),
]


DATASETS = [
    {"name": "DS1_10DM_30pct", "alts": 5, "crit": 4, "dms": 10, "biased": 3, "seed": 42},
    {"name": "DS2_10DM_50pct", "alts": 5, "crit": 4, "dms": 10, "biased": 5, "seed": 77},
    {"name": "DS3_20DM_25pct", "alts": 8, "crit": 6, "dms": 20, "biased": 5, "seed": 101},
    {"name": "DS4_15DM_40pct", "alts": 6, "crit": 5, "dms": 15, "biased": 6, "seed": 200},
    {"name": "DS5_6DM_33pct", "alts": 4, "crit": 3, "dms": 6, "biased": 2, "seed": 333},
    {"name": "DS6_30DM_20pct", "alts": 10, "crit": 6, "dms": 30, "biased": 6, "seed": 500},
    {"name": "DS7_50DM_30pct", "alts": 10, "crit": 8, "dms": 50, "biased": 15, "seed": 700},
    {"name": "DS8_100DM_20pct", "alts": 10, "crit": 8, "dms": 100, "biased": 20, "seed": 1000},
    {"name": "DS9_200DM_25pct", "alts": 15, "crit": 10, "dms": 200, "biased": 50, "seed": 2000},
    {"name": "DS10_500DM_10pct", "alts": 20, "crit": 12, "dms": 500, "biased": 50, "seed": 5000},
]


def order(result) -> list[str]:
    return [alt for alt, _ in result]


def ranks(items: list[str]) -> dict[str, int]:
    return {alt: idx + 1 for idx, alt in enumerate(items)}


def spearman(reference: list[str], candidate: list[str]) -> float:
    n = len(reference)
    if n < 2:
        return 1.0
    ref_r = ranks(reference)
    cand_r = ranks(candidate)
    d2 = sum((ref_r[a] - cand_r[a]) ** 2 for a in reference)
    return 1.0 - (6.0 * d2) / (n * (n * n - 1))


def kendall(reference: list[str], candidate: list[str]) -> float:
    ref_r = ranks(reference)
    cand_r = ranks(candidate)
    con = 0
    dis = 0
    for i, a in enumerate(reference):
        for b in reference[i + 1:]:
            if (ref_r[a] - ref_r[b]) * (cand_r[a] - cand_r[b]) > 0:
                con += 1
            else:
                dis += 1
    return (con - dis) / (con + dis) if con + dis else 1.0


def summarize(vals: list[float]) -> str:
    if len(vals) == 1:
        return f"{vals[0]:.3f}"
    return f"{mean(vals):.3f}±{pstdev(vals):.3f}"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-bags", type=int, default=100)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260425)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_rows = []

    for ds in DATASETS:
        normal, biased, biased_dms = generate_dataset(
            ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"]
        )
        normal_path = OUT_DIR / f"{ds['name']}_normal.json"
        biased_path = OUT_DIR / f"{ds['name']}_biased.json"
        normal_path.write_text(json.dumps(normal, indent=2), encoding="utf-8")
        biased_path.write_text(json.dumps(biased, indent=2), encoding="utf-8")

        ref_order = order(m1.run_m1(str(normal_path)))
        ref_rank = ranks(ref_order)
        target_alt = "A1"

        print("\n" + "=" * 110)
        print(f"{ds['name']} | biased DMs={biased_dms} | clean A1 rank=#{ref_rank[target_alt]}")
        print(f"{'Method':<8}{'Spearman':<16}{'Kendall':<16}{'Top1':<12}{'A1Rank':<16}{'A1Err'}")

        dataset_rows = []
        for method_name, runner in METHODS:
            rho_vals = []
            tau_vals = []
            top1_vals = []
            a1_ranks = []
            a1_errors = []
            for rep in range(args.repeats):
                seed = args.seed + ds["seed"] + rep * 1000
                candidate = order(runner(str(biased_path), args.num_bags, seed))
                cand_rank = ranks(candidate)
                rho_vals.append(spearman(ref_order, candidate))
                tau_vals.append(kendall(ref_order, candidate))
                top1_vals.append(1.0 if candidate[0] == ref_order[0] else 0.0)
                a1_ranks.append(cand_rank[target_alt])
                a1_errors.append(abs(cand_rank[target_alt] - ref_rank[target_alt]))
            row = {
                "dataset": ds["name"],
                "method": method_name,
                "spearman": summarize(rho_vals),
                "kendall": summarize(tau_vals),
                "top1_acc": summarize(top1_vals),
                "a1_rank_mean": summarize([float(x) for x in a1_ranks]),
                "a1_rank_error": summarize([float(x) for x in a1_errors]),
            }
            dataset_rows.append(row)
            all_rows.append(row)
            print(
                f"{method_name:<8}{row['spearman']:<16}{row['kendall']:<16}"
                f"{row['top1_acc']:<12}{row['a1_rank_mean']:<16}{row['a1_rank_error']}"
            )
        write_csv(OUT_DIR / f"{ds['name']}_metrics.csv", dataset_rows)

    write_csv(OUT_DIR / "all_synthetic_repeated_metrics.csv", all_rows)
    print("\n" + "=" * 110)
    print(f"Saved repeated synthetic evaluation outputs to: {OUT_DIR}")


if __name__ == "__main__":
    main()
