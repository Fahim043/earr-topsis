import random
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M4 Disjoint: Weighted Bagging (Disjoint Partitions + Positional Voting)
#
# CONCEPT: Partition DMs into disjoint subsets.
# Probability of placing DM k into a subset is NOT uniform. We distribute
# DMs into subsets based on R_k. Then run positional voting.
# ═══════════════════════════════════════════════════════════════════════════


def run_m4_disjoint(filepath, num_subsets=5, bag_size=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    num_alts = len(alts)

    # Layer 2: Compute reliability via consensus-distance
    R = reliability.compute_reliability(data)

    # We want to build num_subsets. We'll sample WITHOUT replacement
    # until DMs are exhausted, using probabilities.
    remaining_dms = dms.copy()
    
    subsets = [[] for _ in range(num_subsets)]
    subset_idx = 0
    
    while remaining_dms:
        # Recalculate probs for remaining
        sum_r = sum(R[dm] for dm in remaining_dms)
        if sum_r < 1e-10:
            probs = [1.0 / len(remaining_dms)] * len(remaining_dms)
        else:
            probs = [R[dm] / sum_r for dm in remaining_dms]
            
        import numpy as np
        # Pick one DM mapped to the current subset
        chosen_dm = np.random.choice(remaining_dms, p=probs)
        subsets[subset_idx].append(chosen_dm)
        remaining_dms.remove(chosen_dm)
        
        subset_idx = (subset_idx + 1) % num_subsets

    # Dictionary to record rank votes
    rank_votes = {r: {a: 0 for a in alts} for r in range(1, num_alts + 1)}

    for subset_dms in subsets:
        if not subset_dms: continue
        
        temp_data = data.copy()
        temp_data["decision_makers"] = subset_dms

        agg = m1.aggregate_ratings_mean(temp_data)
        norm = m1.normalize_matrix(agg, data["criteria"], alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], data["criteria"], alts)
        d_star, d_min = m1.calculate_distances(weighted, data["criteria"], alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        subset_ranking = sorted(cc.items(), key=lambda x: x[1], reverse=True)
        for rank_pos, (alt, _) in enumerate(subset_ranking, 1):
            rank_votes[rank_pos][alt] += 1

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
