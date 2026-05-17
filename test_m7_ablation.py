"""
test_m7_ablation.py — Component Ablation Study for M7
=======================================================
Proves that EACH component of M7's multi-signal reliability engine
is necessary. Removes one signal at a time and measures degradation.

Ablation Variants:
  M7-Full:       All 3 signals (entropy + variance + clone detection)
  M7-NoEntropy:  Remove entropy signal
  M7-NoClone:    Remove clone detection signal
  M7-NoVariance: Remove variance signal
  M7-OnlyEntropy:   Only entropy (single signal baseline)
  M7-OnlyClone:     Only clone detection
  M7-OnlyVariance:  Only variance

Tests on: 30%, 50%, 60% bias at 20 DMs.
"""

import json
import random
import copy
import os
import math
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import m1_normal_topsis as m1
import m7_entropy_reliability as m7


# ─────────────────────────────────────────────────────────────────────────
# ABLATION RELIABILITY ENGINES
# ─────────────────────────────────────────────────────────────────────────

def compute_reliability_ablation(data, signals="all"):
    """
    M7 reliability with configurable signal ablation.

    signals: 'all', 'no_entropy', 'no_clone', 'no_variance',
             'only_entropy', 'only_clone', 'only_variance'
    """
    dms = data["decision_makers"]
    K = len(dms)

    dm_vectors = {dm: m7.flatten_dm_vector(data, dm) for dm in dms}
    all_vectors = np.array([dm_vectors[dm] for dm in dms])

    # ── Entropy ──
    R_entropy = {}
    if signals not in ("no_entropy",):
        entropy_raw = {dm: m7.compute_entropy(dm_vectors[dm]) for dm in dms}
        max_entropy = max(entropy_raw.values()) if entropy_raw else 1.0
        if max_entropy < 1e-10:
            max_entropy = 1.0
        R_entropy = {dm: entropy_raw[dm] / max_entropy for dm in dms}
    else:
        R_entropy = {dm: 1.0 for dm in dms}  # Disabled = always 1.0

    # ── Variance ──
    R_var = {}
    if signals not in ("no_variance",):
        individual_vars = {dm: float(np.var(dm_vectors[dm])) for dm in dms}
        median_var = float(np.median(list(individual_vars.values())))
        if median_var < 1e-10:
            median_var = 1.0
        for dm in dms:
            ratio = individual_vars[dm] / median_var
            R_var[dm] = math.exp(-abs(ratio - 1.0))
    else:
        R_var = {dm: 1.0 for dm in dms}

    # ── Clone Detection ──
    R_clone = {}
    if signals not in ("no_clone",):
        pairwise_dists = np.zeros((K, K))
        for i in range(K):
            for j in range(i + 1, K):
                d = np.linalg.norm(all_vectors[i] - all_vectors[j])
                pairwise_dists[i][j] = d
                pairwise_dists[j][i] = d

        max_pairwise = np.max(pairwise_dists) if np.max(pairwise_dists) > 0 else 1.0
        clone_threshold = 0.01 * max_pairwise

        for idx, dm in enumerate(dms):
            num_clones = sum(1 for j in range(K)
                             if j != idx and pairwise_dists[idx][j] < clone_threshold)
            clone_frac = num_clones / (K - 1) if K > 1 else 0.0
            R_clone[dm] = math.exp(-3.0 * clone_frac)
    else:
        R_clone = {dm: 1.0 for dm in dms}

    # ── Compute weights based on active signals ──
    if signals == "only_entropy":
        R_composite = {dm: R_entropy[dm] for dm in dms}
    elif signals == "only_clone":
        R_composite = {dm: R_clone[dm] for dm in dms}
    elif signals == "only_variance":
        R_composite = {dm: R_var[dm] for dm in dms}
    elif signals == "no_entropy":
        R_composite = {dm: 0.50 * R_clone[dm] + 0.50 * R_var[dm] for dm in dms}
    elif signals == "no_clone":
        R_composite = {dm: 0.50 * R_entropy[dm] + 0.50 * R_var[dm] for dm in dms}
    elif signals == "no_variance":
        R_composite = {dm: 0.50 * R_entropy[dm] + 0.50 * R_clone[dm] for dm in dms}
    else:  # "all"
        R_composite = {dm: 0.35 * R_entropy[dm] + 0.30 * R_clone[dm] + 0.35 * R_var[dm]
                       for dm in dms}

    # ── Gap-based binary filtering (same as M7) ──
    scores_sorted = sorted(R_composite.values())
    if len(scores_sorted) >= 3:
        gaps = [scores_sorted[i+1] - scores_sorted[i]
                for i in range(len(scores_sorted) - 1)]
        gap_mean = np.mean(gaps)
        gap_std = np.std(gaps)
        gap_threshold = gap_mean + 1.5 * gap_std

        max_gap_idx = np.argmax(gaps)
        max_gap_val = gaps[max_gap_idx]

        if max_gap_val > gap_threshold:
            cutoff_value = scores_sorted[max_gap_idx]
            n_below = max_gap_idx + 1
            if n_below <= int(0.75 * K):
                for dm in dms:
                    if R_composite[dm] <= cutoff_value:
                        R_composite[dm] = 1e-6

    return R_composite


def run_m7_ablation(filepath, signals="all", num_bags=100, bag_size=None, seed=12345):
    """Run M7 with ablated reliability engine."""
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    crits = data["criteria"]

    K = len(dms)
    if bag_size is None:
        bag_size = K
    rng = np.random.default_rng(seed)

    R = compute_reliability_ablation(data, signals=signals)

    # Probability-weighted sampling
    sum_r = sum(R[dm] for dm in dms)
    if sum_r < 1e-10:
        probs = [1.0 / K] * K
    else:
        probs = [R[dm] / sum_r for dm in dms]

    bag_rankings = []
    bag_reliabilities = []

    for _ in range(num_bags):
        sampled_dms = list(rng.choice(dms, size=bag_size, replace=True, p=probs))

        temp_data = data.copy()
        temp_data["decision_makers"] = sampled_dms

        agg = m7.aggregate_ratings_weighted(temp_data, R)
        norm = m1.normalize_matrix(agg, crits, alts)
        weighted = m1.apply_weights(norm, data["criteria_weights"], crits, alts)
        d_star, d_min = m1.calculate_distances(weighted, crits, alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        bag_rankings.append(cc)
        bag_reliabilities.append(float(np.mean([R[dm] for dm in sampled_dms])))

    W = m7.softmax(bag_reliabilities)

    final_cc = {a: 0.0 for a in alts}
    for i in range(num_bags):
        for a in alts:
            final_cc[a] += W[i] * bag_rankings[i][a]

    ranked = sorted(final_cc.items(), key=lambda x: x[1], reverse=True)
    return ranked


# ─────────────────────────────────────────────────────────────────────────
# DATASET GENERATOR
# ─────────────────────────────────────────────────────────────────────────

def generate_fuzzy_rating(base_val, noise_level=1.5):
    m = max(1, min(9, round(base_val + random.uniform(-noise_level, noise_level))))
    l = max(1, m - random.randint(1, 2))
    u = min(9, m + random.randint(1, 2))
    return [l, m, u]


def generate_dataset(num_alts, num_crit, num_dms, num_biased, seed, target_alt="A1"):
    random.seed(seed)
    alts = [f"A{i}" for i in range(1, num_alts + 1)]
    crits = [f"C{j}" for j in range(1, num_crit + 1)]
    dms = [f"DM{k}" for k in range(1, num_dms + 1)]

    true_values = {a: {c: random.uniform(3, 8) for c in crits} for a in alts}
    weights = {c: [random.randint(4, 6), random.randint(6, 8), random.randint(8, 9)]
               for c in crits}

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
        "alternatives": alts, "criteria": crits,
        "decision_makers": dms, "criteria_weights": weights,
        "ratings": ratings
    }

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
# MAIN: ABLATION STUDY
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"

    ablation_configs = [
        ("M7-Full",          "all"),
        ("M7-NoEntropy",     "no_entropy"),
        ("M7-NoClone",       "no_clone"),
        ("M7-NoVariance",    "no_variance"),
        ("M7-OnlyEntropy",   "only_entropy"),
        ("M7-OnlyClone",     "only_clone"),
        ("M7-OnlyVariance",  "only_variance"),
    ]

    bias_configs = [
        {"name": "30% bias (20 DMs)", "alts": 8, "crit": 6, "dms": 20, "biased": 6,  "seed": 9999},
        {"name": "50% bias (20 DMs)", "alts": 8, "crit": 6, "dms": 20, "biased": 10, "seed": 9999},
        {"name": "60% bias (20 DMs)", "alts": 8, "crit": 6, "dms": 20, "biased": 12, "seed": 9999},
    ]

    print("=" * 130)
    print("M7 COMPONENT ABLATION STUDY")
    print("Evaluating which signal components are necessary for robust bias detection")
    print("=" * 130)

    all_results = {}

    for ds in bias_configs:
        normal_data, biased_data, biased_dms = generate_dataset(
            ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"]
        )

        n_path = os.path.join(out_dir, "_test_abl_normal.json")
        b_path = os.path.join(out_dir, "_test_abl_biased.json")
        with open(n_path, 'w') as f: json.dump(normal_data, f)
        with open(b_path, 'w') as f: json.dump(biased_data, f)

        gt = m1.run_m1(n_path)
        gt_order = [alt for alt, _ in gt]
        gt_a1_rank = gt_order.index("A1") + 1

        print(f"\n{'━' * 130}")
        print(f"  {ds['name']}  |  Ground Truth: A1 at #{gt_a1_rank}")
        print(f"{'━' * 130}")

        header = f"  {'Variant':<20}{'A1 Rank':<12}{'Top-3 Match':<15}{'Status'}"
        print(header)
        print(f"  {'─' * 70}")

        for label, signals in ablation_configs:
            res = run_m7_ablation(b_path, signals=signals, num_bags=100, seed=ds["seed"])
            order = [alt for alt, _ in res]

            a1_rank = order.index("A1") + 1 if "A1" in order else -1
            top3_match = sum(1 for a, b in zip(gt_order[:3], order[:3]) if a == b)

            if a1_rank == 1 and gt_a1_rank > 1:
                status = "❌ FAILED — attack not blocked"
            elif a1_rank >= gt_a1_rank:
                status = "✅ DEFENDED"
            else:
                status = "⚠️  PARTIAL"

            print(f"  {label:<20}#{a1_rank:<11}{top3_match}/3{'':<11}{status}")
            all_results[(ds["name"], label)] = a1_rank

    # Cleanup
    for f in ["_test_abl_normal.json", "_test_abl_biased.json"]:
        try: os.remove(os.path.join(out_dir, f))
        except: pass

    # === SUMMARY TABLE ===
    print(f"\n\n{'=' * 130}")
    print("ABLATION SUMMARY: A1 RANK ACROSS CONFIGURATIONS")
    print(f"{'=' * 130}")

    header = f"  {'Variant':<20}"
    for ds in bias_configs:
        header += f"| {ds['name']:<22}"
    print(header)
    print(f"  {'─' * 95}")

    for label, _ in ablation_configs:
        line = f"  {label:<20}"
        for ds in bias_configs:
            rank = all_results[(ds["name"], label)]
            marker = "✅" if rank > 1 else "❌"
            line += f"| {marker} #{rank:<19}"
        print(line)

    print(f"{'=' * 130}")
    print("\nCONCLUSION: In this scenario, entropy and clone-style signals dominate.")
    print("Single-signal removals do not always degrade performance; variance-only is the weakest variant.")
    print(f"{'=' * 130}")
