import random
import m1_normal_topsis as m1
import reliability
import m6_reliability_weighted as m6_base

# ═══════════════════════════════════════════════════════════════════════════
# M6 Disjoint: Reliability-Weighted Positional Voting
#
# CONCEPT: DMs uniformly partitioned into disjoint subsets.
# However, within each subset, DMs are weighted by their Reliability.
# Then, each subset's Positional Vote is weighted by the aggregate Softmax
# reliability of that subset (instead of standard 1-vote-per-subset).
# ═══════════════════════════════════════════════════════════════════════════


def run_m6_disjoint(filepath, num_subsets=5, bag_size=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    num_alts = len(alts)
    K = len(dms)

    R = reliability.compute_reliability(data)
    
    # 1. Uniform Disjoint Partition
    shuffled_dms = dms.copy()
    random.shuffle(shuffled_dms)

    subsets = []
    chunk_size = max(1, K // num_subsets)
    for i in range(num_subsets):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size if i < num_subsets - 1 else K
        
        subset_dms = shuffled_dms[start_idx:end_idx]
        if subset_dms:
            subsets.append(subset_dms)

    # 2. Evaluate Mean Reliability for each subset
    subset_R_scores = []
    for s_dms in subsets:
        avg_r = sum(R.get(dm, 0) for dm in s_dms) / len(s_dms)
        subset_R_scores.append(avg_r)
        
    # 3. Softmax weighting for final voting power
    softmax_weights = reliability.softmax_weights(subset_R_scores)

    # Dictionary to record FRACTIONAL rank votes (since subsets carry different voting weights)
    rank_votes = {r: {a: 0.0 for a in alts} for r in range(1, num_alts + 1)}

    # 4. Run Weighted TOPSIS on each disjoint subset
    for i, subset_dms in enumerate(subsets):
        temp_data = data.copy()
        temp_data["decision_makers"] = subset_dms

        # Inner-Bag weighting based on R_k
        agg = m6_base.aggregate_ratings_weighted(temp_data, R)
        norm = m1.normalize_matrix(agg, data["criteria"], alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], data["criteria"], alts)
        d_star, d_min = m1.calculate_distances(weighted, data["criteria"], alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        subset_ranking = sorted(cc.items(), key=lambda x: x[1], reverse=True)
        
        # Determine the subset's vote weight
        vote_power = softmax_weights[i]
        
        for rank_pos, (alt, _) in enumerate(subset_ranking, 1):
            rank_votes[rank_pos][alt] += vote_power

    # 5. Positional Voting Resolution
    final_ranking = []
    available_alts = set(alts)

    for position in range(1, num_alts + 1):
        if not available_alts: break
        votes_for_pos = {a: rank_votes[position][a] for a in available_alts}
        best_alt = max(available_alts, key=lambda a: (
            votes_for_pos[a], 
            sum(rank_votes[p][a] for p in range(1, position)),
            sum(rank_votes[p][a] for p in range(1, num_alts + 1))
        ))
        final_ranking.append((best_alt, 0.0))
        available_alts.remove(best_alt)

    return final_ranking, R
