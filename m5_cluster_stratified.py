import random
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M5: Cluster-Stratified Bagging (Layer 3 - Option 2)
#
# CONCEPT: Auto-cluster DMs by behavior (silhouette-optimal k).
# Exclude outlier clusters (IQR on cluster reliabilities).
# Stratified sampling across remaining clusters ensures balanced bags.
#
# Uses: reliability.find_optimal_clusters()
#       reliability.exclude_outlier_clusters()
#       reliability.compute_reliability()
# ═══════════════════════════════════════════════════════════════════════════


def run_m5(filepath, num_bags=100, bag_size=None, seed=None):
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]

    K = len(dms)
    if bag_size is None:
        bag_size = K  # Full bootstrap like RF
    rng = random.Random(seed)

    # Auto-detect optimal cluster count via silhouette
    clusters, best_k, sil_scores = reliability.find_optimal_clusters(data)

    # Compute per-DM reliability
    R = reliability.compute_reliability(data)

    # Exclude outlier clusters via IQR on cluster reliabilities
    reliable_clusters = reliability.exclude_outlier_clusters(clusters, R)

    # Stratified allocation proportional to cluster SIZE within reliable pool.
    # If a caller asks for fewer samples than clusters, sample from the largest
    # reliable clusters only; otherwise keep at least one draw per cluster.
    total_reliable = sum(len(m) for m in reliable_clusters.values())
    cluster_ids = list(reliable_clusters)
    if bag_size < len(cluster_ids):
        selected = sorted(cluster_ids, key=lambda k: len(reliable_clusters[k]), reverse=True)[:bag_size]
        allocation = {c_id: 1 for c_id in selected}
    else:
        allocation = {}
        for c_id, members in reliable_clusters.items():
            ratio = len(members) / total_reliable
            allocation[c_id] = max(1, int(round(bag_size * ratio)))

    # Adjust to exact bag_size
    total_alloc = sum(allocation.values())
    while total_alloc > bag_size:
        reducible = [k for k, v in allocation.items() if v > 1]
        if not reducible:
            break
        largest = max(reducible, key=lambda k: allocation[k])
        allocation[largest] -= 1
        total_alloc -= 1
    while total_alloc < bag_size:
        if not allocation:
            break
        largest = max(allocation, key=lambda k: len(reliable_clusters[k]))
        allocation[largest] += 1
        total_alloc += 1

    bag_results = {a: [] for a in alts}

    for b in range(num_bags):
        sampled_dms = []
        for c_id, num_needed in allocation.items():
            sampled = rng.choices(reliable_clusters[c_id], k=num_needed)
            sampled_dms.extend(sampled)

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
    return ranked, clusters, reliable_clusters


if __name__ == "__main__":
    print("-" * 60)
    print("M5: Cluster-Stratified Bagging (Layer 3 - Option 2)")
    print("-" * 60)

    for label, path in [("NORMAL", "topsis_normal_data.json"), ("BIASED", "topsis_biased_data.json")]:
        res, all_c, rel_c = run_m5(path)
        print(f"\n[{label}]")
        print(f"  All clusters: {all_c}")
        print(f"  Reliable clusters used: {rel_c}")
        for rank, (alt, score) in enumerate(res, 1):
            print(f"  {rank}. {alt}: {score:.4f}")
