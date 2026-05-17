import numpy as np
import math
import m1_normal_topsis as m1

# ═══════════════════════════════════════════════════════════════════════════
# M7: Entropy-Aware Reliability-Weighted Ensemble TOPSIS
# Candidate final model — "EARR-TOPSIS"
#
# PHILOSOPHY:
#   We do NOT assume majority = correct.
#   We do NOT assume low variance = bias.
#   We detect STRUCTURED ABNORMAL AGREEMENT PATTERNS using multi-signal
#   anomaly detection.
#
# ARCHITECTURE: Layer 1 (Bagging) + Layer 2 (Distance) + Layer 3 (NEW)
#   Layer 3 = Entropy + Variance Consistency + Clone/Agreement Pattern
#
# KEY INNOVATION — "Consensus Structure vs Agreement Pattern":
#   Honest consensus → slight variation + aligned structure
#   Attack block     → perfect agreement + directional distortion
#
# CLAIM (Multi-Signal Robustness Under Distinguishable Attack Patterns):
#   If adversarial DMs exhibit statistically distinguishable entropy or
#   variance patterns from honest DMs, then the reliability-weighted
#   ensemble can suppress their influence, including some majority-attack
#   settings. Human-mimic attacks remain a limitation.
#
# SAFETY CLAUSE:
#   The entropy component does not penalize consensus itself, but only
#   consensus that is statistically inconsistent with global structural
#   variation.
# ═══════════════════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────────────────
# 1. FEATURE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────

def flatten_dm_vector(data, dm):
    """Flatten all ratings of a DM into a single 1-D vector.
    Shape: 3 * |alternatives| * |criteria|"""
    vec = []
    for a in data["alternatives"]:
        for c in data["criteria"]:
            vec.extend(data["ratings"][dm][a][c])
    return np.array(vec, dtype=float)


# ─────────────────────────────────────────────────────────────────────────
# 2. INDIVIDUAL SIGNAL COMPUTATIONS
# ─────────────────────────────────────────────────────────────────────────

def compute_entropy(vec, bins=10):
    """
    Shannon entropy of a DM's rating distribution.
    High entropy = diverse ratings (honest human behavior).
    Low entropy  = repetitive patterns (coordinated attack signal).

    Scientifically grounded: entropy-based anomaly detection is a
    well-established paradigm in robust statistics literature.
    """
    counts, _ = np.histogram(vec, bins=bins)
    total = np.sum(counts)
    if total <= 0:
        return 0.0
    probs = counts[counts > 0] / total
    return float(-np.sum(probs * np.log(probs + 1e-10)))


def compute_variance_score(vec, global_var):
    """
    Variance consistency score.
    V_k = sigma_k / sigma_global
    R_var = exp(-|V_k - 1|)

    Honest DMs → variance close to global → score ≈ 1.0
    Attackers  → unnaturally consistent   → score penalized
    """
    var_k = np.var(vec)
    if global_var < 1e-10:
        return 1.0
    ratio = var_k / global_var
    return math.exp(-abs(ratio - 1))


def cosine_similarity(a, b):
    """Cosine similarity between two vectors."""
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom < 1e-10:
        return 0.0
    return float(np.dot(a, b) / denom)


# ─────────────────────────────────────────────────────────────────────────
# 3. CORE M7 RELIABILITY ENGINE (Multi-Signal, 100% Centroid-Free)
# ─────────────────────────────────────────────────────────────────────────

def compute_m7_reliability(data):
    """
    Multi-signal reliability score for each DM.

    CRITICAL DESIGN: This engine uses ZERO centroid computation.
    When attackers exceed 50%, ANY centroid (mean, median, trimmed)
    is mathematically hijacked. Instead, all three signals are
    INHERENT properties of each DM's individual behavior:

    Signal 1 — Entropy: How diverse are this DM's rating patterns?
        Honest humans give varied scores → high entropy.
        Attackers repeat [7,9,9] and [1,1,3] → low entropy.

    Signal 2 — Variance Deviation: Is this DM's internal variance
        consistent with normal human behavior?
        Measured against MEDIAN individual variance (robust statistic).

    Signal 3 — Clone Detection: How many other DMs are near-identical?
        Honest humans are NEVER perfect clones.
        Coordinated attackers submit identical ratings → many clones.

    Final score: weighted sum + gap-based binary filtering.
    DMs whose composite score is below a gap-detected threshold
    are marked as attackers and excluded entirely.

    Returns: dict {dm_id: R_k^(final)}
    """
    dms = data["decision_makers"]
    K = len(dms)

    # ── Step 1: Build feature vectors ──
    dm_vectors = {dm: flatten_dm_vector(data, dm) for dm in dms}
    all_vectors = np.array([dm_vectors[dm] for dm in dms])

    # ── Step 2: Signal A — Entropy (individual property) ──
    entropy_raw = {dm: compute_entropy(dm_vectors[dm]) for dm in dms}
    max_entropy = max(entropy_raw.values()) if entropy_raw else 1.0
    if max_entropy < 1e-10:
        max_entropy = 1.0
    R_entropy = {dm: entropy_raw[dm] / max_entropy for dm in dms}

    # ── Step 3: Signal B — Variance deviation ──
    individual_vars = {dm: float(np.var(dm_vectors[dm])) for dm in dms}
    median_var = float(np.median(list(individual_vars.values())))
    if median_var < 1e-10:
        median_var = 1.0
    R_var = {}
    for dm in dms:
        ratio = individual_vars[dm] / median_var
        R_var[dm] = math.exp(-abs(ratio - 1.0))

    # ── Step 4: Signal C — Clone detection ──
    pairwise_dists = np.zeros((K, K))
    for i in range(K):
        for j in range(i + 1, K):
            d = np.linalg.norm(all_vectors[i] - all_vectors[j])
            pairwise_dists[i][j] = d
            pairwise_dists[j][i] = d

    max_pairwise = np.max(pairwise_dists) if np.max(pairwise_dists) > 0 else 1.0
    clone_threshold = 0.01 * max_pairwise

    R_clone = {}
    for idx, dm in enumerate(dms):
        num_clones = sum(1 for j in range(K)
                         if j != idx and pairwise_dists[idx][j] < clone_threshold)
        clone_frac = num_clones / (K - 1) if K > 1 else 0.0
        R_clone[dm] = math.exp(-3.0 * clone_frac)

    # ── Step 5: Composite reliability (weighted sum) ──
    # Additive combination prevents one slightly-off signal from
    # zeroing out an honest DM.
    R_composite = {}
    for dm in dms:
        R_composite[dm] = (
            0.35 * R_entropy[dm]
            + 0.30 * R_clone[dm]
            + 0.35 * R_var[dm]
        )

    # ── Step 6: Gap-based binary filtering ──
    # Sort composite scores and find the largest gap.
    # DMs below the gap are likely attackers → set R to near-zero.
    # This is the SAME gap-analysis principle used in reliability.py
    # but applied to multi-signal composite scores.
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
            n_above = K - n_below

            # Only filter if the lower group is NOT the overwhelming majority
            # (safety: don't accidentally remove all honest DMs)
            if n_below <= int(0.75 * K):
                for dm in dms:
                    if R_composite[dm] <= cutoff_value:
                        R_composite[dm] = 1e-6  # Effectively zero

    return R_composite


# ─────────────────────────────────────────────────────────────────────────
# 4. RELIABILITY-WEIGHTED AGGREGATION (Same as M6 Inner-Bag)
# ─────────────────────────────────────────────────────────────────────────

def aggregate_ratings_weighted(data, R):
    """
    Reliability-weighted fuzzy aggregation.
    Each DM's contribution is proportional to their R_k^(final).
    DMs with R_k ≈ 0 contribute near-nothing to the aggregate TFN.
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


# ─────────────────────────────────────────────────────────────────────────
# 5. SELF-CALIBRATING SOFTMAX (Outer-Bag Weighting)
# ─────────────────────────────────────────────────────────────────────────

def softmax(values):
    """Numerically stable softmax with self-calibrating temperature.
    T = std(values). When reliabilities diverge → sharp discrimination.
    When similar → near-uniform weights."""
    values = np.array(values, dtype=float)
    T = np.std(values)
    if T < 1e-10:
        return np.ones(len(values)) / len(values)
    scaled = (values - np.mean(values)) / T
    exp_vals = np.exp(scaled)
    return exp_vals / np.sum(exp_vals)


# ─────────────────────────────────────────────────────────────────────────
# 6. MAIN M7 PIPELINE
# ─────────────────────────────────────────────────────────────────────────

def run_m7(filepath, num_bags=100, bag_size=None, seed=None):
    """
    M7: Entropy-Aware Reliability-Weighted Ensemble TOPSIS.

    TRIPLE-LAYER DEFENSE PIPELINE:
    1. Compute multi-signal reliability R_k^(final) for all DMs.
    2. For each bag:
       a. LAYER A — Probability-weighted sampling (like M4):
          P(k) = R_k / ΣR_j. Biased DMs with R≈0 are almost never selected.
       b. LAYER B — Inner-bag reliability-weighted aggregation (like M6):
          Even if a biased DM slips through sampling, their ratings
          are multiplied by R_k ≈ 0 inside the bag.
       c. Record CC scores and bag collective reliability.
    3. LAYER C — Outer-bag softmax weighting:
       Bags with higher collective reliability get more voting power.
    4. Produce final weighted-average CC scores and ranking.
    """
    data = m1.load_data(filepath)
    dms = data["decision_makers"]
    alts = data["alternatives"]
    crits = data["criteria"]

    K = len(dms)
    if bag_size is None:
        bag_size = K  # Full bootstrap like RF
    rng = np.random.default_rng(seed)

    # ── Step 1: Compute M7 multi-signal reliability ──
    R = compute_m7_reliability(data)

    # ── Probability-weighted sampling distribution ──
    # P(k) = R_k / Σ(R_j) — biased DMs with R≈0.001 have near-zero
    # probability of being selected into any bag
    sum_r = sum(R[dm] for dm in dms)
    if sum_r < 1e-10:
        probs = [1.0 / K] * K  # Fallback to uniform
    else:
        probs = [R[dm] / sum_r for dm in dms]

    bag_rankings = []
    bag_reliabilities = []

    for _ in range(num_bags):
        # LAYER A: Probability-weighted sampling
        sampled_dms = list(rng.choice(dms, size=bag_size, replace=True, p=probs))

        temp_data = data.copy()
        temp_data["decision_makers"] = sampled_dms

        # LAYER B: Inner-bag reliability-weighted aggregation
        agg = aggregate_ratings_weighted(temp_data, R)
        norm = m1.normalize_matrix(agg, crits, alts, data.get("criteria_types"))
        weighted = m1.apply_weights(norm, data["criteria_weights"], crits, alts)
        d_star, d_min = m1.calculate_distances(weighted, crits, alts)
        cc = m1.compute_cc(d_star, d_min, alts)

        bag_rankings.append(cc)
        bag_reliabilities.append(float(np.mean([R[dm] for dm in sampled_dms])))

    # ── Step 2: LAYER C — Outer-bag softmax weighting ──
    W = softmax(bag_reliabilities)

    final_cc = {a: 0.0 for a in alts}
    for i in range(num_bags):
        for a in alts:
            final_cc[a] += W[i] * bag_rankings[i][a]

    ranked = sorted(final_cc.items(), key=lambda x: x[1], reverse=True)
    return ranked, R


# ─────────────────────────────────────────────────────────────────────────
# 7. STANDALONE TEST
# ─────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("M7: Entropy-Aware Reliability-Weighted Ensemble TOPSIS (EARR)")
    print("=" * 65)

    for label, path in [("NORMAL", "topsis_normal_data.json"),
                        ("BIASED", "topsis_biased_data.json")]:
        result, R = run_m7(path)
        print(f"\n[{label}]")
        print(f"  Reliability: {{{', '.join(f'{k}:{v:.3f}' for k, v in R.items())}}}")
        for i, (alt, score) in enumerate(result, 1):
            print(f"  {i}. {alt}: {score:.4f}")
