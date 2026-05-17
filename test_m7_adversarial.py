"""
test_m7_adversarial.py — Adversarial Robustness Experiments for M7
====================================================================
Tests M7 against progressively smarter attackers to find the exact
degradation boundary. This is CRITICAL for Q1 publication.

Attack Strategies:
  Level 0: Perfect clones      → [7,9,9] / [1,1,3] (current baseline)
  Level 1: Noisy clones (±1)   → Add uniform noise ±1 to attack ratings
  Level 2: Noisy clones (±2)   → Add uniform noise ±2 (larger spread)
  Level 3: Diverse extremists   → Attackers pick random extreme ranges
  Level 4: Human mimics         → Attackers add human-like noise (±1.5)
                                  but still bias directionally

Each level tests at 30%, 50%, and 60% attacker ratios.
All methods run with ZERO parameter changes.
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


# ─────────────────────────────────────────────────────────────────────────
# DATASET GENERATOR WITH SMART ATTACKERS
# ─────────────────────────────────────────────────────────────────────────

def generate_fuzzy_rating(base_val, noise_level=1.5):
    m = max(1, min(9, round(base_val + random.uniform(-noise_level, noise_level))))
    l = max(1, m - random.randint(1, 2))
    u = min(9, m + random.randint(1, 2))
    return [l, m, u]


def clamp_tfn(l, m, u):
    """Clamp TFN values to valid [1, 9] range and ensure l <= m <= u."""
    l = max(1, min(9, round(l)))
    m = max(1, min(9, round(m)))
    u = max(1, min(9, round(u)))
    l, m, u = min(l, m), sorted([l, m, u])[1], max(m, u)
    return [l, m, u]


def inject_smart_bias(normal_data, biased_dms, attack_level=0, seed=42):
    """
    Inject bias with varying levels of attacker sophistication.

    Level 0: Perfect clones (identical extreme ratings)
    Level 1: Noisy clones ±1 (small perturbation to avoid clone detection)
    Level 2: Noisy clones ±2 (larger perturbation)
    Level 3: Diverse extremists (each attacker picks slightly different extremes)
    Level 4: Human mimics (human-like noise but directionally biased)
    """
    rng = random.Random(seed)
    biased_data = copy.deepcopy(normal_data)
    target_alt = "A1"

    for dm_idx, dm in enumerate(biased_dms):
        for a in biased_data["alternatives"]:
            for c in biased_data["criteria"]:
                if attack_level == 0:
                    # Perfect clone: identical extreme ratings
                    if a == target_alt:
                        biased_data["ratings"][dm][a][c] = [7, 9, 9]
                    else:
                        biased_data["ratings"][dm][a][c] = [1, 1, 3]

                elif attack_level == 1:
                    # Noisy clone ±1: slight noise to break perfect cloning
                    if a == target_alt:
                        noise = rng.randint(-1, 1)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            7 + noise, 9 + noise, 9 + noise)
                    else:
                        noise = rng.randint(-1, 1)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            1 + noise, 1 + noise, 3 + noise)

                elif attack_level == 2:
                    # Noisy clone ±2: larger spread
                    if a == target_alt:
                        noise = rng.randint(-2, 2)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            7 + noise, 9 + noise, 9 + noise)
                    else:
                        noise = rng.randint(-2, 2)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            1 + noise, 1 + noise, 3 + noise)

                elif attack_level == 3:
                    # Diverse extremist: each attacker picks a random extreme
                    if a == target_alt:
                        base_high = rng.randint(6, 9)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            base_high - 1, base_high, min(9, base_high + 1))
                    else:
                        base_low = rng.randint(1, 3)
                        biased_data["ratings"][dm][a][c] = clamp_tfn(
                            max(1, base_low - 1), base_low, base_low + 1)

                elif attack_level == 4:
                    # Human mimic: uses generate_fuzzy_rating style noise
                    # but with biased base values
                    if a == target_alt:
                        base = 7.5 + rng.uniform(-0.5, 0.5)
                        m_val = max(1, min(9, round(base + rng.uniform(-1.5, 1.5))))
                        l_val = max(1, m_val - rng.randint(1, 2))
                        u_val = min(9, m_val + rng.randint(1, 2))
                        biased_data["ratings"][dm][a][c] = [l_val, m_val, u_val]
                    else:
                        base = 2.5 + rng.uniform(-0.5, 0.5)
                        m_val = max(1, min(9, round(base + rng.uniform(-1.5, 1.5))))
                        l_val = max(1, m_val - rng.randint(1, 2))
                        u_val = min(9, m_val + rng.randint(1, 2))
                        biased_data["ratings"][dm][a][c] = [l_val, m_val, u_val]

    return biased_data


def generate_normal_dataset(num_alts, num_crit, num_dms, seed):
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

    return {
        "alternatives": alts, "criteria": crits,
        "decision_makers": dms, "criteria_weights": weights,
        "ratings": ratings
    }


# ─────────────────────────────────────────────────────────────────────────
# TEST RUNNER
# ─────────────────────────────────────────────────────────────────────────

def get_a1_rank(result):
    order = [alt for alt, _ in result]
    return order.index("A1") + 1 if "A1" in order else -1


def run_experiment(normal_data, biased_dms, attack_level, bias_seed,
                   out_dir, num_bags=100):
    """Run all 7 methods on a smart-attacker dataset and return A1 ranks."""
    biased_data = inject_smart_bias(normal_data, biased_dms, attack_level, bias_seed)

    b_path = os.path.join(out_dir, "_test_adv_biased.json")
    with open(b_path, 'w') as f:
        json.dump(biased_data, f)

    results = {}
    methods = {
        "M1": lambda: m1.run_m1(b_path),
        "M2": lambda: m2.run_m2(b_path, num_bags=num_bags, seed=bias_seed + 2),
        "M3": lambda: m3.run_m3(b_path)[0],
        "M4": lambda: m4.run_m4(b_path, num_bags=num_bags, seed=bias_seed + 4)[0],
        "M5": lambda: m5.run_m5(b_path, num_bags=num_bags, seed=bias_seed + 5)[0],
        "M6": lambda: m6.run_m6(b_path, num_bags=num_bags, seed=bias_seed + 6)[0],
        "M7": lambda: m7.run_m7(b_path, num_bags=num_bags, seed=bias_seed + 7)[0],
    }
    for name, fn in methods.items():
        res = fn()
        results[name] = get_a1_rank(res)

    try:
        os.remove(b_path)
    except:
        pass

    return results


# ─────────────────────────────────────────────────────────────────────────
# MAIN: ADVERSARIAL EXPERIMENT MATRIX
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"

    attack_descriptions = {
        0: "Perfect Clones (identical [7,9,9]/[1,1,3])",
        1: "Noisy Clones ±1 (small perturbation)",
        2: "Noisy Clones ±2 (medium perturbation)",
        3: "Diverse Extremists (random extreme ranges)",
        4: "Human Mimics (human-like noise, biased direction)",
    }

    # Test configurations: (num_dms, num_biased, bias_percent)
    bias_configs = [
        (20, 6, "30%"),
        (20, 10, "50%"),
        (20, 12, "60%"),
    ]

    base_seed = 9999
    num_alts = 8
    num_crit = 6

    method_names = ["M1", "M2", "M3", "M4", "M5", "M6", "M7"]

    print("=" * 130)
    print("M7 ADVERSARIAL ROBUSTNESS EXPERIMENTS")
    print("Testing against progressively smarter attackers")
    print("=" * 130)

    # Generate ground truth
    normal_data = generate_normal_dataset(num_alts, num_crit, 20, base_seed)
    n_path = os.path.join(out_dir, "_test_adv_normal.json")
    with open(n_path, 'w') as f:
        json.dump(normal_data, f)
    gt = m1.run_m1(n_path)
    gt_a1_rank = get_a1_rank(gt)
    os.remove(n_path)

    print(f"\nGround Truth: A1 is at rank #{gt_a1_rank}\n")

    # === RUN ALL EXPERIMENTS ===
    all_results = {}

    for level in range(5):
        print(f"\n{'━' * 130}")
        print(f"  ATTACK LEVEL {level}: {attack_descriptions[level]}")
        print(f"{'━' * 130}")

        header = f"  {'Bias %':<12}"
        for mn in method_names:
            header += f"| {mn:<12}"
        header += "| Result"
        print(header)
        print(f"  {'─' * 115}")

        for num_dms, num_biased, bias_label in bias_configs:
            biased_dms = [f"DM{num_dms - i}" for i in range(num_biased)]

            results = run_experiment(
                normal_data, biased_dms, level, base_seed + level * 100,
                out_dir, num_bags=100
            )

            line = f"  {bias_label:<12}"
            m7_status = "?"
            for mn in method_names:
                rank = results[mn]
                if rank == 1 and gt_a1_rank > 1:
                    marker = f"❌ #{rank}"
                elif rank > 1 or rank == gt_a1_rank:
                    marker = f"✅ #{rank}"
                else:
                    marker = f"⚠️ #{rank}"
                line += f"| {marker:<12}"

            # M7 specific status
            m7_rank = results["M7"]
            if m7_rank == 1 and gt_a1_rank > 1:
                m7_status = "❌ M7 DEFEATED"
            elif m7_rank > 1:
                m7_status = "✅ M7 DEFENDED"
            else:
                m7_status = "✅ A1 truly #1"

            line += f"| {m7_status}"
            print(line)

            all_results[(level, bias_label)] = results

    # === SUMMARY: M7 DEGRADATION MAP ===
    print(f"\n\n{'=' * 130}")
    print("M7 DEGRADATION MAP — Where Does M7 Start Failing?")
    print(f"{'=' * 130}")

    header = f"  {'Attack Level':<45}"
    for _, _, bl in bias_configs:
        header += f"| {bl:<14}"
    print(header)
    print(f"  {'─' * 95}")

    for level in range(5):
        line = f"  L{level}: {attack_descriptions[level]:<41}"
        for _, _, bl in bias_configs:
            rank = all_results[(level, bl)]["M7"]
            if rank == 1 and gt_a1_rank > 1:
                line += f"| ❌ #{rank:<11}"
            else:
                line += f"| ✅ #{rank:<11}"
        print(line)

    print(f"\n  Ground Truth: A1 at #{gt_a1_rank}")
    print(f"{'=' * 130}")

    # === COMPARISON: M6 vs M7 ===
    print(f"\n{'=' * 130}")
    print("M6 vs M7 HEAD-TO-HEAD COMPARISON")
    print(f"{'=' * 130}")

    header = f"  {'Attack Level':<45}"
    for _, _, bl in bias_configs:
        header += f"| {bl:<14}"
    print(header)
    print(f"  {'─' * 95}")

    for level in range(5):
        line = f"  L{level}: {attack_descriptions[level]:<41}"
        for _, _, bl in bias_configs:
            m6r = all_results[(level, bl)]["M6"]
            m7r = all_results[(level, bl)]["M7"]
            cell = f"M6:#{m6r} M7:#{m7r}"
            line += f"| {cell:<14}"
        print(line)

    print(f"{'=' * 130}")
