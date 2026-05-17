import random
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M5 Disjoint: Cluster-Stratified Disjoint Bagging + Positional Voting
#
# CONCEPT: DMs are partitioned into K-Means clusters. Bias clusters are 
# dropped. The surviving DMs are evenly dealt out into 5 disjoint subsets
# to guarantee stratified representation avoiding cluster-lumping.
# ═══════════════════════════════════════════════════════════════════════════


def run_m5_disjoint(filepath, num_subsets=5, bag_size=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    num_alts = len(alts)

    clusters, best_k, sil_scores = reliability.find_optimal_clusters(data)
    R = reliability.compute_reliability(data)
    
    # 1. Drop the outlier clusters
    reliable_clusters = reliability.exclude_outlier_clusters(clusters, R)

    # Compile the surviving DMs grouped by cluster
    clustered_dms = list(reliable_clusters.values())
    
    # Shuffle each cluster internally to prevent artifacting
    for cl in clustered_dms:
        random.shuffle(cl)
        
    subsets = [[] for _ in range(num_subsets)]
    
    # 2. Stratified Dealing (Card-dealer method)
    # Deal out DMs from each cluster into the subsets sequentially
    subset_idx = 0
    for cluster in clustered_dms:
        for dm in cluster:
            subsets[subset_idx].append(dm)
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

    return final_ranking, clusters, best_k
