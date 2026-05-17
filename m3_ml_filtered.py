import json
import m1_normal_topsis as m1
import reliability

# ═══════════════════════════════════════════════════════════════════════════
# M3: ML-Filtered Fuzzy TOPSIS (Layer 2)
#
# CONCEPT: Use data-driven outlier detection to REMOVE unreliable DMs
# before running standard Fuzzy TOPSIS. No hardcoded parameters.
#
# Uses: reliability.detect_outliers() → IQR-based Tukey fence
# ═══════════════════════════════════════════════════════════════════════════


def run_m3(filepath):
    data = m1.load_data(filepath)

    # Detect outliers via universal IQR-based Tukey fence
    reliable_dms, outlier_dms, R = reliability.detect_outliers(data)

    if len(reliable_dms) == 0:
        reliable_dms = data["decision_makers"]  # Safety fallback

    # Run Normal TOPSIS on ONLY the reliable DMs
    filtered_data = data.copy()
    filtered_data["decision_makers"] = reliable_dms

    agg = m1.aggregate_ratings(filtered_data)
    norm = m1.normalize_matrix(agg, data["criteria"], data["alternatives"], data.get("criteria_types"))
    weighted = m1.apply_weights(norm, data["criteria_weights"], data["criteria"], data["alternatives"])
    d_star, d_min = m1.calculate_distances(weighted, data["criteria"], data["alternatives"])
    cc = m1.compute_cc(d_star, d_min, data["alternatives"])

    ranked = sorted(cc.items(), key=lambda x: x[1], reverse=True)
    return ranked, R, outlier_dms


if __name__ == "__main__":
    print("-" * 60)
    print("M3: ML-Filtered Fuzzy TOPSIS (Layer 2)")
    print("-" * 60)

    for label, path in [("NORMAL", "topsis_normal_data.json"), ("BIASED", "topsis_biased_data.json")]:
        res, R, outliers = run_m3(path)
        print(f"\n[{label}]")
        print(f"  Outliers detected: {outliers}")
        print(f"  Reliability: {{{', '.join(f'{k}:{v:.3f}' for k,v in R.items())}}}")
        for rank, (alt, score) in enumerate(res, 1):
            print(f"  {rank}. {alt}: {score:.4f}")
