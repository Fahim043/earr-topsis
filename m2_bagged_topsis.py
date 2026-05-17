import random
import m1_normal_topsis as m1

# ═══════════════════════════════════════════════════════════════════════════
# M2: Bagged Fuzzy TOPSIS (Layer 1) — Random Forest Analogy
#
# This is identical to Random Forest's ensemble approach, but with
# Fuzzy TOPSIS as the base learner instead of Decision Trees:
#
#   Random Forest              →  Bagged Fuzzy TOPSIS
#   ─────────────────────────────────────────────────
#   Bootstrap sample of rows   →  Bootstrap sample of DMs (size=K, w/ replacement)
#   Build Decision Tree        →  Run Fuzzy TOPSIS
#   Repeat B times             →  Repeat B times
#   Majority Vote / Average    →  Majority Rank Vote + Average CC
#
# KEY PROPERTIES:
#   - Full bootstrap: bag_size = K (same as RF, not K/2)
#   - With replacement: ~63.2% unique DMs per bag (1 - 1/e)
#   - Mean aggregation inside bags: prevents min/max poisoning
#   - DUAL ensemble: majority vote on RANKS + averaged CC scores
#   - Some bags will be "clean" (no biased DMs) → they produce
#     correct rankings → these correct rankings contribute to votes
# ═══════════════════════════════════════════════════════════════════════════


def run_m2(filepath, num_bags=100, bag_size=None, seed=None):
    """Run true bootstrap bagged fuzzy TOPSIS.

    Each bag samples K decision makers uniformly *with replacement*, matching
    the Random-Forest-style method described in the paper notes. Rankings are
    aggregated with Borda scores, and average closeness coefficients are used
    as the secondary tie-breaker.
    """
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    K = len(dms)

    alts = data["alternatives"]
    num_alts = len(alts)

    if bag_size is None:
        bag_size = K

    rng = random.Random(seed)
    borda_scores = {a: 0.0 for a in alts}
    cc_sums = {a: 0.0 for a in alts}

    for _ in range(num_bags):
        sampled_dms = [rng.choice(dms) for _ in range(bag_size)]

        temp_data = data.copy()
        temp_data["decision_makers"] = sampled_dms

        agg = m1.aggregate_ratings_mean(temp_data)
        norm = m1.normalize_matrix(agg, data["criteria"], alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], data["criteria"], alts)
        d_star, d_min = m1.calculate_distances(weighted, data["criteria"], alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        bag_ranking = sorted(cc.items(), key=lambda x: x[1], reverse=True)
        for rank_pos, (alt, _) in enumerate(bag_ranking, 1):
            borda_scores[alt] += num_alts - rank_pos
            cc_sums[alt] += cc[alt]

    avg_cc = {a: cc_sums[a] / num_bags for a in alts}
    ranked = sorted(
        avg_cc.items(),
        key=lambda x: (borda_scores[x[0]], x[1]),
        reverse=True,
    )
    return ranked


if __name__ == "__main__":
    print("-" * 60)
    print("M2: Bagged Fuzzy TOPSIS (Layer 1 — RF Analogy)")
    print("-" * 60)

    for label, path in [("NORMAL", "topsis_normal_data.json"), ("BIASED", "topsis_biased_data.json")]:
        res = run_m2(path)
        print(f"\n[{label}]")
        for rank, (alt, score) in enumerate(res, 1):
            print(f"  {rank}. {alt}: {score:.4f}")
