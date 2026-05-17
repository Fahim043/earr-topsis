"""
test_m7_supermajority.py — Super-Majority Attack Benchmark for M7
==================================================================
This script proves that M7 (Entropy-Aware Reliability) breaks the 50%
attack horizon that defeated all previous methods (M1–M6).

Datasets:
  DS_SM1: 10 DMs, 5 Alts, 4 Crit, 60% bias (6 attackers)  — Super-Majority
  DS_SM2: 20 DMs, 8 Alts, 6 Crit, 70% bias (14 attackers) — Extreme Majority
  DS_SM3: 10 DMs, 5 Alts, 4 Crit, 50% bias (5 attackers)  — Horizon Limit (revisit)
  DS_SM4: 20 DMs, 8 Alts, 6 Crit, 60% bias (12 attackers) — Large-Scale Super-Majority

All methods run with IDENTICAL code and ZERO parameter changes.
Expected: M1–M6 FAIL. M7 should SUCCEED (or partially succeed).
"""

import json
import random
import copy
import os
import warnings
warnings.filterwarnings('ignore')

import m1_normal_topsis as m1
import m2_bagged_topsis as m2
import m3_ml_filtered as m3
import m4_weighted_bagging as m4
import m5_cluster_stratified as m5
import m6_reliability_weighted as m6
import m7_entropy_reliability as m7
import reliability


# ─────────────────────────────────────────────────────────────────────────
# DATASET GENERATOR (same logic as run_all_tests.py)
# ─────────────────────────────────────────────────────────────────────────

def generate_fuzzy_rating(base_val, noise_level=1.5):
    m = max(1, min(9, round(base_val + random.uniform(-noise_level, noise_level))))
    l = max(1, m - random.randint(1, 2))
    u = min(9, m + random.randint(1, 2))
    return [l, m, u]


def generate_dataset(num_alts, num_crit, num_dms, num_biased, seed, target_alt="A1"):
    """Generate a normal+biased dataset pair."""
    random.seed(seed)

    alts = [f"A{i}" for i in range(1, num_alts + 1)]
    crits = [f"C{j}" for j in range(1, num_crit + 1)]
    dms = [f"DM{k}" for k in range(1, num_dms + 1)]

    true_values = {a: {c: random.uniform(3, 8) for c in crits} for a in alts}
    weights = {c: [random.randint(4, 6), random.randint(6, 8), random.randint(8, 9)] for c in crits}

    ratings = {}
    for dm in dms:
        dm_ratings = {}
        for a in alts:
            alt_ratings = {}
            for c in crits:
                alt_ratings[c] = generate_fuzzy_rating(true_values[a][c])
            dm_ratings[a] = alt_ratings
        ratings[dm] = dm_ratings

    normal_data = {
        "alternatives": alts,
        "criteria": crits,
        "decision_makers": dms,
        "criteria_weights": weights,
        "ratings": ratings
    }

    # Biased version: deep copy + inject bias on last N DMs
    biased_data = copy.deepcopy(normal_data)
    biased_dm_ids = [f"DM{num_dms - i}" for i in range(num_biased)]

    for dm in biased_dm_ids:
        for a in alts:
            for c in crits:
                if a == target_alt:
                    biased_data["ratings"][dm][a][c] = [7, 9, 9]
                else:
                    biased_data["ratings"][dm][a][c] = [1, 1, 3]

    return normal_data, biased_data, biased_dm_ids


# ─────────────────────────────────────────────────────────────────────────
# TEST RUNNER (M1–M7)
# ─────────────────────────────────────────────────────────────────────────

def run_all_methods_with_m7(filepath, num_bags=100, seed=12345):
    res1 = m1.run_m1(filepath)
    res2 = m2.run_m2(filepath, num_bags=num_bags, seed=seed + 2)
    res3, _, _ = m3.run_m3(filepath)
    res4, _ = m4.run_m4(filepath, num_bags=num_bags, seed=seed + 4)
    res5, _, _ = m5.run_m5(filepath, num_bags=num_bags, seed=seed + 5)
    res6, _ = m6.run_m6(filepath, num_bags=num_bags, seed=seed + 6)
    res7, _ = m7.run_m7(filepath, num_bags=num_bags, seed=seed + 7)
    return [res1, res2, res3, res4, res5, res6, res7]


# ─────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"
    method_names = [
        "M1:Baseline", "M2:Bag-RF", "M3:ML-Filt",
        "M4:Wgt-Bag", "M5:Clust-Bag", "M6:Rel-Agg",
        "M7:Entropy"
    ]

    datasets_config = [
        {"name": "DS_SM1 (10DM, 60% bias)",  "alts": 5,  "crit": 4, "dms": 10, "biased": 6,  "seed": 4242},
        {"name": "DS_SM2 (20DM, 70% bias)",  "alts": 8,  "crit": 6, "dms": 20, "biased": 14, "seed": 7777},
        {"name": "DS_SM3 (10DM, 50% bias)",  "alts": 5,  "crit": 4, "dms": 10, "biased": 5,  "seed": 77},
        {"name": "DS_SM4 (20DM, 60% bias)",  "alts": 8,  "crit": 6, "dms": 20, "biased": 12, "seed": 9999},
    ]

    print("=" * 130)
    print("M7 SUPER-MAJORITY ATTACK BENCHMARK")
    print("Testing M1-M7 against >50% coordinated bias attacks")
    print("=" * 130)

    summary_rows = []

    for ds_idx, ds in enumerate(datasets_config):
        normal_data, biased_data, biased_dms = generate_dataset(
            ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"]
        )

        n_path = os.path.join(out_dir, "_test_sm_normal.json")
        b_path = os.path.join(out_dir, "_test_sm_biased.json")
        with open(n_path, 'w') as f: json.dump(normal_data, f)
        with open(b_path, 'w') as f: json.dump(biased_data, f)

        # Ground truth: M1 on clean data
        gt = m1.run_m1(n_path)
        gt_order = [alt for alt, _ in gt]
        gt_a1_rank = gt_order.index("A1") + 1

        # M7 Reliability scores on biased data
        R_m7 = m7.compute_m7_reliability(biased_data)
        biased_R = {dm: f"{R_m7[dm]:.3f}" for dm in biased_dms[:5]}  # Show first 5

        num_bags = 150

        bias_pct = round(ds["biased"] / ds["dms"] * 100)
        print(f"\n{'─'*130}")
        print(f"  {ds['name']}  |  {ds['dms']} DMs, {ds['alts']} Alts, {ds['crit']} Crit  |  {bias_pct}% ATTACK")
        print(f"  Biased DMs: {biased_dms}")
        print(f"  Biased DM M7-Reliability (sample): {biased_R}")
        print(f"  Ground Truth (M1 on Normal): {' > '.join(gt_order)}  (A1 at #{gt_a1_rank})")
        print(f"{'─'*130}")

        biased_results = run_all_methods_with_m7(b_path, num_bags=num_bags, seed=ds["seed"])
        total_alts = ds["alts"]

        header = f"  {'Method':<15}{'Ranking':<55}{'A1 Rank':<10}{'Match':<8}{'Status'}"
        print(header)
        print(f"  {'─'*115}")

        ds_summary = {"name": ds["name"]}
        for mn, res in zip(method_names, biased_results):
            order = [alt for alt, _ in res]
            matches = sum(1 for a, b in zip(gt_order, order) if a == b)
            a1_rank = order.index("A1") + 1 if "A1" in order else -1

            # Determine status
            if a1_rank == 1 and gt_a1_rank > 1:
                status = "❌ FAILED"
            elif a1_rank == gt_a1_rank and matches == total_alts:
                status = "✅ PERFECT"
            elif a1_rank == gt_a1_rank:
                status = "✅ NEAR-PERFECT"
            elif a1_rank >= gt_a1_rank and a1_rank > 1:
                status = "✅ NEUTRALIZED"
            elif a1_rank == gt_a1_rank == 1:
                status = "✅ CORRECT (A1 truly #1)"
            else:
                status = "⚠️  PARTIAL"

            ranking_str = ' > '.join(order)
            if len(ranking_str) > 53:
                ranking_str = ranking_str[:50] + "..."
            print(f"  {mn:<15}{ranking_str:<55}#{a1_rank:<9}{matches}/{total_alts:<6}{status}")
            ds_summary[mn] = {"a1": a1_rank, "match": matches, "status": status}

        summary_rows.append(ds_summary)

    # Cleanup
    for f in ["_test_sm_normal.json", "_test_sm_biased.json"]:
        try: os.remove(os.path.join(out_dir, f))
        except: pass

    # ── SUMMARY TABLE ──
    print(f"\n\n{'='*130}")
    print("SUMMARY: A1 RANK ON SUPER-MAJORITY ATTACK DATASETS")
    print(f"{'='*130}")
    header = f"  {'Dataset':<28}"
    for mn in method_names:
        header += f"| {mn:<14}"
    print(header)
    print(f"  {'─'*125}")

    for row in summary_rows:
        line = f"  {row['name']:<28}"
        for mn in method_names:
            info = row[mn]
            marker = "✅" if "✅" in info["status"] else "❌"
            line += f"| {marker} #{info['a1']:<11}"
        print(line)

    print(f"{'='*130}")
    print("BENCHMARK COMPLETE — M7 uses multi-signal entropy detection (ZERO parameter tuning)")
    print(f"{'='*130}")
