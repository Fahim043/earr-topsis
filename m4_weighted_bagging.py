import numpy as np
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M4: Weighted Bagging (Layer 1 + Layer 2 + Layer 3 Option 1)
#
# CONCEPT: Like M2 (RF-style bagging), but sampling is NOT uniform.
# Probability of selecting DM k into a bag:
#   P(k) = R_k / Σ(R_i)
# This is the user's exact formula from the framework specification.
#
# High-reliability DMs appear much more frequently.
# Low-reliability (biased) DMs appear rarely or never.
#
# Uses: reliability.compute_reliability() for R_k
# ═══════════════════════════════════════════════════════════════════════════


def run_m4(filepath, num_bags=100, bag_size=None, seed=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    K = len(dms)

    # Full bootstrap like RF
    if bag_size is None:
        bag_size = K
    rng = np.random.default_rng(seed)

    # Layer 2: Compute reliability via consensus-distance
    R = reliability.compute_reliability(data)

    # Layer 3 Option 1: Direct proportional sampling
    # P(k) = R_k / Σ(R_i) — exactly as specified in the framework
    sum_r = sum(R[dm] for dm in dms)
    if sum_r < 1e-10:
        probs = [1.0 / K] * K  # Fallback to uniform
    else:
        probs = [R[dm] / sum_r for dm in dms]

    bag_results = {a: [] for a in alts}

    for b in range(num_bags):
        # Weighted sampling: reliable DMs picked proportionally more
        sampled_dms = list(rng.choice(dms, size=bag_size, replace=True, p=probs))

        temp_data = data.copy()
        temp_data["decision_makers"] = sampled_dms

        agg = m1.aggregate_ratings_mean(temp_data)
        norm = m1.normalize_matrix(agg, data["criteria"], alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], data["criteria"], alts)
        d_star, d_min = m1.calculate_distances(weighted, data["criteria"], alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        for a in alts:
            bag_results[a].append(cc[a])

    final_cc = {a: sum(bag_results[a]) / num_bags for a in alts}
    ranked = sorted(final_cc.items(), key=lambda x: x[1], reverse=True)
    return ranked, R


if __name__ == "__main__":
    print("-" * 60)
    print("M4: Weighted Bagging (Layer 3 - Option 1)")
    print("-" * 60)

    for label, path in [("NORMAL", "topsis_normal_data.json"), ("BIASED", "topsis_biased_data.json")]:
        res, R = run_m4(path)
        print(f"\n[{label}]")
        print(f"  Reliability: {{{', '.join(f'{k}:{v:.3f}' for k,v in R.items())}}}")
        for rank, (alt, score) in enumerate(res, 1):
            print(f"  {rank}. {alt}: {score:.4f}")
