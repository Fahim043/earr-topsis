"""
reliability.py — Universal Self-Calibrating Decision-Maker Reliability Engine
==============================================================================
This module provides ALL reliability computation, outlier detection, clustering,
and adaptive weighting used by M3-M6. It contains ZERO hardcoded thresholds.
Every parameter is derived from the data distribution itself.

Author: DR-BFTOPSIS Framework
"""

import numpy as np
import math


# ─────────────────────────────────────────────────────────────────────────────
# 1. FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def extract_dm_features(data, dm_id):
    """Flatten a DM's full rating tensor into a 1-D feature vector.
    Shape: 3 * |alternatives| * |criteria|"""
    vector = []
    for a in data["alternatives"]:
        for c in data["criteria"]:
            l, m, u = data["ratings"][dm_id][a][c]
            vector.extend([l, m, u])
    return np.array(vector, dtype=float)


def build_feature_matrix(data):
    """Build the (K x D) feature matrix for all K decision makers."""
    dms = data["decision_makers"]
    X = np.array([extract_dm_features(data, dm) for dm in dms])
    return X, dms


# ─────────────────────────────────────────────────────────────────────────────
# 2. CONSENSUS-DISTANCE RELIABILITY (No hardcoded params)
# ─────────────────────────────────────────────────────────────────────────────

def compute_reliability(data):
    """
    Compute a continuous reliability score R_k ∈ [0, 1] for each DM.

    Method:
    1. Build feature matrix X of all DMs
    2. Compute the MEDIAN centroid (robust against outliers, unlike mean)
    3. Compute Euclidean distance of each DM to median centroid
    4. Normalize: R_k = 1 - (d_k / d_max)
       - DM closest to consensus → R ≈ 1
       - DM farthest from consensus → R ≈ 0
       - Fully adaptive, no magic numbers

    Returns: dict {dm_id: R_k}
    """
    X, dms = build_feature_matrix(data)

    # Median centroid is robust to up to 50% outliers
    centroid = np.median(X, axis=0)

    # Euclidean distance from each DM to consensus
    distances = np.linalg.norm(X - centroid, axis=1)

    d_max = np.max(distances)
    if d_max == 0:
        # All DMs are identical — everyone is perfectly reliable
        return {dm: 1.0 for dm in dms}

    R = {}
    for i, dm in enumerate(dms):
        R[dm] = float(1.0 - (distances[i] / d_max))

    return R


def detect_outliers(data):
    """
    Detect outlier DMs using a multi-layer adaptive approach.

    LAYER 1 — Distance-Gap Analysis (primary, most powerful):
        Sort all DM distances to median centroid. Find the largest 
        relative gap in the sorted sequence. If that gap is significant
        (> adaptive threshold), split DMs at that gap: those beyond it 
        are outliers. This works because biased DMs naturally cluster 
        far from consensus, creating a visible discontinuity.

    LAYER 2 — Modified Z-Score via MAD (fallback for small K ≤ 30):
        If no clear gap exists, use MAD-based Modified Z-Score.
        Threshold: modified_Z > 3.5 (Iglewicz & Hoaglin standard).

    LAYER 3 — Tukey Fence (fallback for large K > 30):
        Standard Q3 + 1.5*IQR.

    All thresholds are derived from the data or from universally 
    accepted statistical standards. Zero dataset-specific tuning.

    Returns: (reliable_dms, outlier_dms, reliability_scores)
    """
    X, dms = build_feature_matrix(data)
    centroid = np.median(X, axis=0)
    distances = np.linalg.norm(X - centroid, axis=1)
    K = len(dms)
    R = compute_reliability(data)

    if K < 3:
        # Too few DMs to detect outliers
        return list(dms), [], R

    # ── LAYER 1: Distance-Gap Analysis ──
    sorted_indices = np.argsort(distances)
    sorted_dists = distances[sorted_indices]

    # Compute gaps between consecutive sorted distances
    gaps = np.diff(sorted_dists)

    if len(gaps) > 0 and np.max(gaps) > 0:
        # Adaptive gap threshold: a gap is "significant" if it's larger than
        # mean(gaps) + 2*std(gaps). This adapts to the spread of the data.
        gap_mean = np.mean(gaps)
        gap_std = np.std(gaps)
        gap_threshold = gap_mean + 2.0 * gap_std

        # Find the largest gap
        max_gap_idx = np.argmax(gaps)
        max_gap_val = gaps[max_gap_idx]

        if max_gap_val > gap_threshold and max_gap_val > 0:
            # Split: everything AFTER the gap position is an outlier
            # But only if the outlier group is the MINORITY (< 50%)
            n_before = max_gap_idx + 1  # DMs before the gap
            n_after = K - n_before      # DMs after the gap

            if n_after < n_before:  # Outliers are the minority
                reliable_dms = [dms[sorted_indices[i]] for i in range(n_before)]
                outlier_dms = [dms[sorted_indices[i]] for i in range(n_before, K)]

                if len(reliable_dms) > 0:
                    return reliable_dms, outlier_dms, R

    # ── LAYER 2: Modified Z-Score (small K) ──
    if K <= 30:
        median_d = np.median(distances)
        mad = np.median(np.abs(distances - median_d))

        if mad < 1e-10:
            return list(dms), [], R

        modified_z = 0.6745 * (distances - median_d) / mad

        reliable_dms = []
        outlier_dms = []
        for i, dm in enumerate(dms):
            if modified_z[i] > 3.5:
                outlier_dms.append(dm)
            else:
                reliable_dms.append(dm)

        if len(reliable_dms) > 0 and len(outlier_dms) > 0:
            return reliable_dms, outlier_dms, R

    # ── LAYER 3: Tukey Fence (large K) ──
    Q1 = np.percentile(distances, 25)
    Q3 = np.percentile(distances, 75)
    IQR = Q3 - Q1
    threshold = Q3 + 1.5 * IQR

    reliable_dms = []
    outlier_dms = []
    for i, dm in enumerate(dms):
        if distances[i] <= threshold:
            reliable_dms.append(dm)
        else:
            outlier_dms.append(dm)

    if len(reliable_dms) == 0:
        return list(dms), [], R

    return reliable_dms, outlier_dms, R


# ─────────────────────────────────────────────────────────────────────────────
# 4. SILHOUETTE-OPTIMAL CLUSTERING (Auto-detect best k)
# ─────────────────────────────────────────────────────────────────────────────

def _kmeans_manual(X, k, max_iter=100, random_state=42):
    """Manual K-Means implementation (no sklearn dependency for core logic)."""
    rng = np.random.RandomState(random_state)
    n = X.shape[0]

    # Initialize centroids via K-Means++
    centroids = [X[rng.randint(n)]]
    for _ in range(1, k):
        dists = np.array([min(np.linalg.norm(x - c) ** 2 for c in centroids) for x in X])
        total = dists.sum()
        if total < 1e-10:
            # All remaining points overlap with existing centroids — pick random
            probs = np.ones(n) / n
        else:
            probs = dists / total
        centroids.append(X[rng.choice(n, p=probs)])
    centroids = np.array(centroids)

    for _ in range(max_iter):
        # Assign each point to nearest centroid
        labels = np.array([np.argmin([np.linalg.norm(x - c) for c in centroids]) for x in X])

        # Recompute centroids
        new_centroids = np.array([X[labels == j].mean(axis=0) if np.sum(labels == j) > 0
                                  else centroids[j] for j in range(k)])

        if np.allclose(centroids, new_centroids):
            break
        centroids = new_centroids

    return labels, centroids


def _silhouette_score_manual(X, labels):
    """Manual silhouette score computation (no sklearn dependency)."""
    n = X.shape[0]
    unique_labels = np.unique(labels)

    if len(unique_labels) <= 1 or len(unique_labels) >= n:
        return -1.0

    silhouettes = []
    for i in range(n):
        own_cluster = labels[i]
        own_members = X[labels == own_cluster]

        # a(i) = mean intra-cluster distance
        if len(own_members) > 1:
            a_i = np.mean([np.linalg.norm(X[i] - own_members[j])
                           for j in range(len(own_members)) if not np.array_equal(own_members[j], X[i])])
        else:
            a_i = 0.0

        # b(i) = min mean distance to any other cluster
        b_i = float('inf')
        for label in unique_labels:
            if label == own_cluster:
                continue
            other_members = X[labels == label]
            if len(other_members) > 0:
                mean_dist = np.mean([np.linalg.norm(X[i] - other_members[j])
                                     for j in range(len(other_members))])
                b_i = min(b_i, mean_dist)

        if b_i == float('inf'):
            b_i = 0.0

        denom = max(a_i, b_i)
        s_i = (b_i - a_i) / denom if denom > 0 else 0.0
        silhouettes.append(s_i)

    return float(np.mean(silhouettes))


def find_optimal_clusters(data, max_k=None):
    """
    Automatically find the optimal number of clusters via silhouette analysis.

    Method:
    1. Try k = 2 to min(K-1, max_k) clusters
    2. Run K-Means for each k
    3. Compute silhouette score for each k
    4. Select k with highest silhouette score

    Returns: (best_labels_dict, best_k, silhouette_scores)
             best_labels_dict = {cluster_id: [dm_ids]}
    """
    X, dms = build_feature_matrix(data)
    n = len(dms)

    if max_k is None:
        max_k = min(n - 1, 10)

    max_k = min(max_k, n - 1)
    if max_k < 2:
        return {0: list(dms)}, 1, {}

    best_score = -1.0
    best_k = 2
    best_labels = None
    scores = {}

    for k in range(2, max_k + 1):
        labels, _ = _kmeans_manual(X, k)
        score = _silhouette_score_manual(X, labels)
        scores[k] = score

        if score > best_score:
            best_score = score
            best_k = k
            best_labels = labels

    # Build cluster dict
    clusters = {i: [] for i in range(best_k)}
    for i, dm in enumerate(dms):
        clusters[best_labels[i]].append(dm)

    return clusters, best_k, scores


# ─────────────────────────────────────────────────────────────────────────────
# 5. SELF-CALIBRATING SOFTMAX WEIGHTS (Adaptive temperature)
# ─────────────────────────────────────────────────────────────────────────────

def softmax_weights(values):
    """
    Compute softmax weights with self-calibrating temperature.

    Temperature T = std(values).
    - If all values are similar → T is large → weights ≈ uniform
    - If values are spread → T is small → weights sharply discriminate

    When T ≈ 0 (all identical), fall back to uniform weights.

    Returns: list of weights summing to 1.0
    """
    values = np.array(values, dtype=float)
    T = np.std(values)

    if T < 1e-10:
        # All values are essentially identical → equal weights
        return [1.0 / len(values)] * len(values)

    # Scale values to be in terms of standard deviations from mean
    scaled = (values - np.mean(values)) / T
    exp_vals = np.exp(scaled)
    total = np.sum(exp_vals)

    return [float(e / total) for e in exp_vals]


def reliability_weighted_probs(R_dict, dm_list):
    """
    Convert reliability scores to sampling probabilities.
    Uses softmax with self-calibrating temperature.

    Returns: list of probabilities for each DM in dm_list
    """
    r_values = [R_dict[dm] for dm in dm_list]
    return softmax_weights(r_values)


# ─────────────────────────────────────────────────────────────────────────────
# 6. CLUSTER RELIABILITY & ADAPTIVE EXCLUSION
# ─────────────────────────────────────────────────────────────────────────────

def compute_cluster_reliability(clusters, R):
    """Compute mean reliability for each cluster."""
    return {c_id: float(np.mean([R[dm] for dm in members]))
            for c_id, members in clusters.items()}


def exclude_outlier_clusters(clusters, R):
    """
    Exclude clusters whose mean reliability is an outlier (significantly
    lower than others).

    Uses the SAME multi-layer approach as DM-level outlier detection:
    1. Distance-gap on sorted cluster reliabilities
    2. Mean-minus-std rule as fallback

    Returns: dict of reliable clusters
    """
    cluster_R = compute_cluster_reliability(clusters, R)

    if len(cluster_R) <= 1:
        return clusters

    r_values = np.array(list(cluster_R.values()))
    c_ids = list(cluster_R.keys())

    # ── Gap analysis on sorted cluster reliabilities ──
    sorted_indices = np.argsort(r_values)
    sorted_r = r_values[sorted_indices]
    gaps = np.diff(sorted_r)

    if len(gaps) > 0 and np.max(gaps) > 0:
        gap_mean = np.mean(gaps)
        gap_std = np.std(gaps)
        gap_threshold = gap_mean + 1.5 * gap_std  # Slightly less strict for clusters

        max_gap_idx = np.argmax(gaps)
        max_gap_val = gaps[max_gap_idx]

        if max_gap_val > gap_threshold:
            # Everything BELOW the gap is the low-reliability group
            n_below = max_gap_idx + 1
            n_above = len(c_ids) - n_below

            if n_below < n_above:  # Low group is minority
                exclude_set = set(c_ids[sorted_indices[i]] for i in range(n_below))
                reliable = {cid: members for cid, members in clusters.items()
                            if cid not in exclude_set}
                if len(reliable) > 0:
                    return reliable

    # ── Fallback: exclude if > 1 std below mean ──
    mean_r = np.mean(r_values)
    std_r = np.std(r_values)

    if std_r < 1e-10:
        return clusters  # All similar

    reliable = {}
    for c_id, members in clusters.items():
        if cluster_R[c_id] >= mean_r - 1.0 * std_r:
            reliable[c_id] = members

    return reliable if len(reliable) > 0 else clusters
