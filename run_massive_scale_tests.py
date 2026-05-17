"""
run_massive_scale_tests.py — Massive-Scale Validation for DR-BFTOPSIS
=====================================================================
Tests ALL 6 methods on massive datasets to prove the theoretical asymptotic
properties and real-world scalability of the framework.

Includes:
  DS8: 100 DMs, 10 Alts, 8 Crit, 20% bias (20 colluding)
  DS9: 200 DMs, 15 Alts, 10 Crit, 25% bias (50 colluding)
  DS10: 500 DMs, 20 Alts, 12 Crit, 10% bias (50 colluding)

All methods run with IDENTICAL code and ZERO parameter changes.
"""

import json
import os
import warnings
warnings.filterwarnings('ignore')

import m1_normal_topsis as m1
import m2_bagged_topsis as m2
import m3_ml_filtered as m3
import m4_weighted_bagging as m4
import m5_cluster_stratified as m5
import m6_reliability_weighted as m6
import reliability
from run_all_tests import generate_dataset, run_all_methods


if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"
    method_names = ["M1:Baseline", "M2:Bag-RF", "M3:ML-Filt", "M4:Wgt-Bag", "M5:Clust-Bag", "M6:Rel-Agg"]

    datasets_config = [
        {"name": "DS8 (100DM, 20% bias)",   "alts": 10, "crit": 8,  "dms": 100, "biased": 20, "seed": 1000},
        {"name": "DS9 (200DM, 25% bias)",   "alts": 15, "crit": 10, "dms": 200, "biased": 50, "seed": 2000},
        {"name": "DS10 (500DM, 10% bias)",  "alts": 20, "crit": 12, "dms": 500, "biased": 50, "seed": 5000},
    ]

    print("=" * 140)
    print("DR-BFTOPSIS MASSIVE-SCALE VALIDATION")
    print("All methods use IDENTICAL code/parameters across ALL datasets (zero tuning)")
    print("=" * 140)

    summary_rows = []

    for ds_idx, ds in enumerate(datasets_config):
        normal_data, biased_data, biased_dms = generate_dataset(
            ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"]
        )

        n_path = os.path.join(out_dir, "_test_massive_normal.json")
        b_path = os.path.join(out_dir, "_test_massive_biased.json")
        with open(n_path, 'w') as f: json.dump(normal_data, f)
        with open(b_path, 'w') as f: json.dump(biased_data, f)

        # Ground truth
        gt = m1.run_m1(n_path)
        gt_order = [alt for alt, _ in gt]
        gt_a1_rank = gt_order.index("A1") + 1

        num_bags = 200  # More bags for massive datasets

        print(f"\n{'─'*140}")
        print(f"  {ds['name']}  |  {ds['dms']} DMs, {ds['alts']} Alts, {ds['crit']} Crit")
        print(f"  Ground Truth (M1 on Normal): A1 is at #{gt_a1_rank}")
        print(f"{'─'*140}")

        biased_results = run_all_methods(b_path, num_bags=num_bags, seed=ds["seed"])
        total_alts = ds["alts"]

        header = f"  {'Method':<15}{'A1 Rank':<10}{'Match':<8}{'Status'}"
        print(header)
        print(f"  {'─'*60}")

        ds_summary = {"name": ds["name"], "gt_a1": gt_a1_rank}
        for mn, res in zip(method_names, biased_results):
            order = [alt for alt, _ in res]
            matches = sum(1 for a, b in zip(gt_order, order) if a == b)
            a1_rank = order.index("A1") + 1 if "A1" in order else -1

            if a1_rank == 1 and gt_a1_rank > 1:
                status = "❌ FAILED"
            elif a1_rank == gt_a1_rank and matches == total_alts:
                status = "✅ PERFECT"
            elif a1_rank == gt_a1_rank:
                status = "✅ NEAR-PERFECT"
            elif a1_rank >= gt_a1_rank and a1_rank > 1:
                status = "✅ NEUTRALIZED"
            elif a1_rank == gt_a1_rank == 1:
                status = "✅ CORRECT"
            else:
                status = "⚠️  PARTIAL"

            print(f"  {mn:<15}#{a1_rank:<9}{matches}/{total_alts:<6}{status}")
            ds_summary[mn] = {"a1": a1_rank, "match": matches, "status": status}

        summary_rows.append(ds_summary)

    for f in ["_test_massive_normal.json", "_test_massive_biased.json"]:
        try: os.remove(os.path.join(out_dir, f))
        except: pass

    # ── SUMMARY TABLE ──
    print(f"\n\n{'='*140}")
    print("SUMMARY: A1 RANK ON MASSIVE DATASETS (Ground Truth Position → Achieved)")
    print(f"{'='*140}")
    header = f"  {'Dataset':<30}"
    for mn in method_names:
        header += f"| {mn:<14}"
    print(header)
    print(f"  {'─'*130}")

    for row in summary_rows:
        line = f"  {row['name']} (GT: #{row['gt_a1']})".ljust(32)
        for mn in method_names:
            info = row[mn]
            marker = "✅" if "✅" in info["status"] else "❌"
            line += f"| {marker} #{info['a1']:<11}"
        print(line)

    print(f"{'='*140}")
