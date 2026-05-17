"""
external_baselines.py
=====================
Prior-art-inspired comparator baselines for fuzzy group TOPSIS experiments.

These are intentionally kept separate from M1-M7. They are not proposed as
new methods; they provide reviewer-facing comparison points based on common
group aggregation, robust aggregation, and consensus/outlier-filtering ideas.
"""

from __future__ import annotations

import math
from statistics import median

import numpy as np

import m1_normal_topsis as m1


def _rank_from_aggregate(data: dict, agg: dict) -> list[tuple[str, float]]:
    alts = data["alternatives"]
    crits = data["criteria"]
    norm = m1.normalize_matrix(agg, crits, alts, data.get("criteria_types"))
    weighted = m1.apply_weights(norm, data["criteria_weights"], crits, alts)
    d_star, d_min = m1.calculate_distances(weighted, crits, alts)
    cc = m1.compute_cc(d_star, d_min, alts)
    return sorted(cc.items(), key=lambda x: x[1], reverse=True)


def _cc_from_aggregate(data: dict, agg: dict) -> dict[str, float]:
    alts = data["alternatives"]
    crits = data["criteria"]
    norm = m1.normalize_matrix(agg, crits, alts, data.get("criteria_types"))
    weighted = m1.apply_weights(norm, data["criteria_weights"], crits, alts)
    d_star, d_min = m1.calculate_distances(weighted, crits, alts)
    return m1.compute_cc(d_star, d_min, alts)


def _dm_vector(data: dict, dm: str) -> np.ndarray:
    values = []
    for alt in data["alternatives"]:
        for crit in data["criteria"]:
            values.extend(data["ratings"][dm][alt][crit])
    return np.array(values, dtype=float)


def _average_rank_desc(scores: dict[str, float]) -> dict[str, float]:
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    ranks: dict[str, float] = {}
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and abs(ordered[j][1] - ordered[i][1]) < 1e-12:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[ordered[k][0]] = avg_rank
        i = j
    return ranks


def aggregate_component_median(data: dict) -> dict:
    """Component-wise median TFN aggregation across DMs."""
    alts = data["alternatives"]
    crits = data["criteria"]
    dms = data["decision_makers"]
    ratings = data["ratings"]
    agg = {a: {c: [0.0, 0.0, 0.0] for c in crits} for a in alts}

    for alt in alts:
        for crit in crits:
            for idx in range(3):
                agg[alt][crit][idx] = float(median(ratings[dm][alt][crit][idx] for dm in dms))
    return agg


def aggregate_trimmed_mean(data: dict, trim_fraction: float = 0.20) -> dict:
    """Component-wise trimmed mean TFN aggregation across DMs."""
    alts = data["alternatives"]
    crits = data["criteria"]
    dms = data["decision_makers"]
    ratings = data["ratings"]
    agg = {a: {c: [0.0, 0.0, 0.0] for c in crits} for a in alts}

    trim = int(math.floor(len(dms) * trim_fraction))
    for alt in alts:
        for crit in crits:
            for idx in range(3):
                values = sorted(ratings[dm][alt][crit][idx] for dm in dms)
                if trim > 0 and len(values) > 2 * trim:
                    values = values[trim:-trim]
                agg[alt][crit][idx] = float(sum(values) / len(values))
    return agg


def filter_dms_by_mad_consensus(data: dict, z: float = 2.5) -> list[str]:
    """Keep DMs whose rating vector is close to the robust median vector."""
    dms = data["decision_makers"]
    if len(dms) <= 2:
        return list(dms)

    vectors = np.array([_dm_vector(data, dm) for dm in dms])
    center = np.median(vectors, axis=0)
    distances = np.linalg.norm(vectors - center, axis=1)
    dist_med = float(np.median(distances))
    mad = float(np.median(np.abs(distances - dist_med)))

    if mad < 1e-10:
        q1, q3 = np.percentile(distances, [25, 75])
        iqr = q3 - q1
        threshold = q3 + 1.5 * iqr if iqr > 1e-10 else float(np.max(distances))
    else:
        threshold = dist_med + z * 1.4826 * mad

    kept = [dm for dm, distance in zip(dms, distances) if distance <= threshold]
    return kept or list(dms)


def run_median_topsis(filepath: str) -> list[tuple[str, float]]:
    data = m1.load_data(filepath)
    return _rank_from_aggregate(data, aggregate_component_median(data))


def run_trimmed_mean_topsis(filepath: str, trim_fraction: float = 0.20) -> list[tuple[str, float]]:
    data = m1.load_data(filepath)
    return _rank_from_aggregate(data, aggregate_trimmed_mean(data, trim_fraction))


def run_mad_consensus_topsis(filepath: str) -> list[tuple[str, float]]:
    data = m1.load_data(filepath)
    kept = filter_dms_by_mad_consensus(data)
    filtered = data.copy()
    filtered["decision_makers"] = kept
    agg = m1.aggregate_ratings_mean(filtered)
    return _rank_from_aggregate(data, agg)


def run_individual_borda_topsis(filepath: str) -> list[tuple[str, float]]:
    """Run TOPSIS per DM and aggregate individual rankings by Borda score."""
    data = m1.load_data(filepath)
    alts = data["alternatives"]
    num_alts = len(alts)
    borda = {alt: 0.0 for alt in alts}
    cc_sum = {alt: 0.0 for alt in alts}

    for dm in data["decision_makers"]:
        single = data.copy()
        single["decision_makers"] = [dm]
        agg = m1.aggregate_ratings_mean(single)
        ranked = _rank_from_aggregate(data, agg)
        for rank_pos, (alt, cc) in enumerate(ranked, start=1):
            borda[alt] += num_alts - rank_pos
            cc_sum[alt] += cc

    avg_cc = {alt: cc_sum[alt] / len(data["decision_makers"]) for alt in alts}
    return sorted(avg_cc.items(), key=lambda x: (borda[x[0]], x[1]), reverse=True)


def run_huang_li_group_ideal_topsis(filepath: str) -> list[tuple[str, float]]:
    """Huang-Li style group-ideal TOPSIS aggregation adapted to fuzzy TOPSIS.

    Huang and Li aggregate individual TOPSIS closeness values using preferential
    differences, alternative priorities, and a group ideal-solution distance.
    Here, each DM first receives individual fuzzy TOPSIS closeness coefficients;
    those coefficients are then aggregated using their group-ideal equations.
    """
    data = m1.load_data(filepath)
    alts = data["alternatives"]
    dms = data["decision_makers"]
    n_alts = len(alts)

    individual_cc: dict[str, dict[str, float]] = {}
    individual_ranks: dict[str, dict[str, float]] = {}
    for dm in dms:
        single = data.copy()
        single["decision_makers"] = [dm]
        agg = m1.aggregate_ratings_mean(single)
        cc = _cc_from_aggregate(data, agg)
        individual_cc[dm] = cc
        individual_ranks[dm] = _average_rank_desc(cc)

    pair_sums: dict[str, float] = {}
    for dm in dms:
        total = 0.0
        for i, alt_i in enumerate(alts):
            for alt_j in alts[i + 1:]:
                total += abs(individual_cc[dm][alt_i] - individual_cc[dm][alt_j])
        pair_sums[dm] = total

    denom = sum(pair_sums.values())
    if denom <= 1e-12:
        alpha = {dm: 1.0 / len(dms) for dm in dms}
    else:
        alpha = {dm: pair_sums[dm] / denom for dm in dms}

    beta_raw = {
        alt: sum(n_alts / individual_ranks[dm][alt] for dm in dms)
        for alt in alts
    }
    beta_total = sum(beta_raw.values())
    beta_group = {alt: beta_raw[alt] / beta_total for alt in alts}

    weighted_cc = {
        dm: {
            alt: alpha[dm] * individual_cc[dm][alt] * beta_group[alt]
            for alt in alts
        }
        for dm in dms
    }
    positive = {dm: max(weighted_cc[dm][alt] for alt in alts) for dm in dms}
    negative = {dm: min(weighted_cc[dm][alt] for alt in alts) for dm in dms}

    group_cc: dict[str, float] = {}
    for alt in alts:
        d_pos = math.sqrt(sum((weighted_cc[dm][alt] - positive[dm]) ** 2 for dm in dms))
        d_neg = math.sqrt(sum((weighted_cc[dm][alt] - negative[dm]) ** 2 for dm in dms))
        group_cc[alt] = d_neg / (d_pos + d_neg) if d_pos + d_neg > 1e-12 else 0.0

    return sorted(group_cc.items(), key=lambda x: x[1], reverse=True)


BASELINES = [
    ("EB1_MedianTOPSIS", run_median_topsis),
    ("EB2_TrimmedMeanTOPSIS", run_trimmed_mean_topsis),
    ("EB3_MADConsensusTOPSIS", run_mad_consensus_topsis),
    ("EB4_IndividualBordaTOPSIS", run_individual_borda_topsis),
    ("EB5_HuangLiGroupIdealTOPSIS", run_huang_li_group_ideal_topsis),
]
