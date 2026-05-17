import random
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M6: Reliability-Weighted Aggregation (Layer 3 - Option 3)
#
# CONCEPT: Sampling is UNIFORM (same as M2), but:
#   Layer A — Inside each bag, DM ratings are aggregated with reliability
#             weights (biased DMs contribute ≈ 0 even when sampled)
#   Layer B — Bags are ensemble-aggregated using self-calibrating softmax
#             weights based on each bag's collective reliability.
#
# Uses: reliability.compute_reliability() + reliability.softmax_weights()
# ═══════════════════════════════════════════════════════════════════════════


def aggregate_ratings_weighted(data, R):
    """
    Reliability-weighted fuzzy aggregation. Instead of min/mean/max,
    each DM's contribution is proportional to their reliability R_k.
    DMs with R_k ≈ 0 contribute near-nothing.
    """
    alts = data["alternatives"]
    crits = data["criteria"]
    dms = data["decision_makers"]
    ratings = data["ratings"]

    agg = {a: {c: [0, 0, 0] for c in crits} for a in alts}

    total_r = sum(R.get(dm, 1e-6) for dm in dms)
    if total_r < 1e-10:
        total_r = 1.0

    for a in alts:
        for c in crits:
            wl, wm, wu = 0.0, 0.0, 0.0
            for dm in dms:
                w = R.get(dm, 1e-6) / total_r
                l, m, u = ratings[dm][a][c]
                wl += w * l
                wm += w * m
                wu += w * u
            agg[a][c] = [wl, wm, wu]

    return agg


def run_m6(filepath, num_bags=100, bag_size=None, seed=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    crits = data["criteria"]

    K = len(dms)
    if bag_size is None:
        bag_size = K  # Full bootstrap like RF
    rng = random.Random(seed)

    # Compute reliability via universal consensus-distance
    R = reliability.compute_reliability(data)

    bag_rankings = []
    bag_reliabilities = []

    for b in range(num_bags):
        # Uniform sampling (same as M2)
        sampled_dms = rng.choices(dms, k=bag_size)

        temp_data = data.copy()
        temp_data["decision_makers"] = sampled_dms

        # LAYER A: Reliability-weighted aggregation INSIDE the bag
        agg = aggregate_ratings_weighted(temp_data, R)
        norm = m1.normalize_matrix(agg, crits, alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], crits, alts)
        d_star, d_min = m1.calculate_distances(weighted, crits, alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        bag_rankings.append(cc)
        bag_reliabilities.append(sum(R[dm] for dm in sampled_dms) / bag_size)

    # LAYER B: Self-calibrating softmax ensemble weighting
    W = reliability.softmax_weights(bag_reliabilities)

    final_cc = {a: 0.0 for a in alts}
    for b in range(num_bags):
        for a in alts:
            final_cc[a] += W[b] * bag_rankings[b][a]

    ranked = sorted(final_cc.items(), key=lambda x: x[1], reverse=True)
    return ranked, R


if __name__ == "__main__":
    print("-" * 60)
    print("M6: Reliability-Weighted Aggregation (Layer 3 - Option 3)")
    print("-" * 60)

    for label, path in [("NORMAL", "topsis_normal_data.json"), ("BIASED", "topsis_biased_data.json")]:
        res, R = run_m6(path)
        print(f"\n[{label}]")
        print(f"  Reliability: {{{', '.join(f'{k}:{v:.3f}' for k,v in R.items())}}}")
        for rank, (alt, score) in enumerate(res, 1):
            print(f"  {rank}. {alt}: {score:.4f}")
