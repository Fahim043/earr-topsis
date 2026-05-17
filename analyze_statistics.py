"""
analyze_statistics.py
=====================
Create confidence-interval and paired-comparison tables from saved benchmark
summaries.

The current benchmark files store mean±std summaries rather than every raw
repeat. Therefore, confidence intervals are computed from summary statistics
where available, and paired tests compare methods across dataset/fraction
scenarios using target-rank-error means.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "outputs" / "final_evidence"
EXTERNAL = ROOT / "outputs" / "external_baselines"
OUT = ROOT / "outputs" / "statistical_analysis"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def parse_pm(value: str) -> tuple[float, float | None]:
    value = str(value).strip()
    if "±" in value:
        mean, std = value.split("±", 1)
        return float(mean), float(std)
    return float(value), None


def ci95(mean: float, std: float | None, n: int) -> tuple[float, float]:
    if std is None or n <= 1:
        return mean, mean
    t_crit = 2.045 if n == 30 else 1.96
    half_width = t_crit * std / math.sqrt(n)
    return mean - half_width, mean + half_width


def average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda x: x[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and abs(indexed[j][1] - indexed[i][1]) < 1e-12:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def sign_test_p_two_sided(positive: int, negative: int) -> float:
    n = positive + negative
    if n == 0:
        return 1.0
    smaller = min(positive, negative)
    prob = sum(math.comb(n, k) for k in range(smaller + 1)) / (2 ** n)
    return min(1.0, 2 * prob)


def wilcoxon_approx(differences: list[float]) -> dict:
    nonzero = [d for d in differences if abs(d) > 1e-12]
    if not nonzero:
        return {"n": 0, "w_plus": 0.0, "w_minus": 0.0, "z": 0.0, "p_two_sided": 1.0}
    abs_values = [abs(d) for d in nonzero]
    ranks = average_ranks(abs_values)
    w_plus = sum(rank for rank, diff in zip(ranks, nonzero) if diff > 0)
    w_minus = sum(rank for rank, diff in zip(ranks, nonzero) if diff < 0)
    n = len(nonzero)
    mean_w = n * (n + 1) / 4
    var_w = n * (n + 1) * (2 * n + 1) / 24
    w_stat = min(w_plus, w_minus)
    if var_w <= 0:
        z = 0.0
        p = 1.0
    else:
        z = (w_stat - mean_w + 0.5) / math.sqrt(var_w)
        p = math.erfc(abs(z) / math.sqrt(2))
    return {"n": n, "w_plus": w_plus, "w_minus": w_minus, "z": z, "p_two_sided": p}


def build_ci_table(attack_rows: list[dict]) -> list[dict]:
    rows = []
    for row in attack_rows:
        n = 30 if "±" in row["target_rank_error"] else 1
        for metric in ["spearman", "kendall", "top1_acc", "target_rank_error"]:
            mean, std = parse_pm(row[metric])
            low, high = ci95(mean, std, n)
            rows.append({
                "dataset": row["dataset"],
                "attacker_fraction_requested": row["attacker_fraction_requested"],
                "attacker_fraction_effective": row["attacker_fraction_effective"],
                "method": row["method"],
                "metric": metric,
                "mean": f"{mean:.6f}",
                "std": "" if std is None else f"{std:.6f}",
                "n": n,
                "ci95_low": f"{low:.6f}",
                "ci95_high": f"{high:.6f}",
            })
    return rows


def collect_target_errors() -> dict[tuple[str, str], dict[str, float]]:
    scenarios: dict[tuple[str, str], dict[str, float]] = {}
    for row in read_csv(FINAL / "attack_fraction_summary.csv"):
        key = (row["dataset"], row["attacker_fraction_requested"])
        mean, _ = parse_pm(row["target_rank_error"])
        scenarios.setdefault(key, {})[row["method"]] = mean

    for row in read_csv(EXTERNAL / "external_baseline_metrics.csv"):
        key = (row["dataset"], row["attacker_fraction_requested"])
        mean, _ = parse_pm(row["target_rank_error"])
        scenarios.setdefault(key, {})[row["method"]] = mean
    return scenarios


def build_pairwise_tests(scenarios: dict[tuple[str, str], dict[str, float]]) -> list[dict]:
    methods = sorted({m for values in scenarios.values() for m in values if m != "M7"})
    rows = []
    for method in methods:
        differences = []
        cases = 0
        for values in scenarios.values():
            if method not in values or "M7" not in values:
                continue
            # Positive means M7 had lower target-rank error than comparator.
            differences.append(values[method] - values["M7"])
            cases += 1
        positive = sum(1 for d in differences if d > 1e-12)
        negative = sum(1 for d in differences if d < -1e-12)
        ties = sum(1 for d in differences if abs(d) <= 1e-12)
        wilcoxon = wilcoxon_approx(differences)
        rows.append({
            "comparison": f"M7_vs_{method}",
            "cases": cases,
            "m7_better": positive,
            "m7_worse": negative,
            "ties": ties,
            "mean_error_reduction": f"{(sum(differences) / cases if cases else 0.0):.6f}",
            "sign_test_p_two_sided": f"{sign_test_p_two_sided(positive, negative):.6f}",
            "wilcoxon_n": wilcoxon["n"],
            "wilcoxon_w_plus": f"{wilcoxon['w_plus']:.6f}",
            "wilcoxon_w_minus": f"{wilcoxon['w_minus']:.6f}",
            "wilcoxon_z_approx": f"{wilcoxon['z']:.6f}",
            "wilcoxon_p_two_sided_approx": f"{wilcoxon['p_two_sided']:.6f}",
        })
    return rows


def build_method_summary(scenarios: dict[tuple[str, str], dict[str, float]]) -> list[dict]:
    methods = sorted({m for values in scenarios.values() for m in values})
    rows = []
    for method in methods:
        vals = [values[method] for values in scenarios.values() if method in values]
        blocked = sum(1 for v in vals if abs(v) <= 1e-12)
        rows.append({
            "method": method,
            "cases": len(vals),
            "blocked_cases": blocked,
            "blocked_rate": f"{blocked / len(vals):.3f}" if vals else "",
            "mean_target_rank_error": f"{sum(vals) / len(vals):.6f}" if vals else "",
            "max_target_rank_error": f"{max(vals):.6f}" if vals else "",
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()

    attack_rows = read_csv(FINAL / "attack_fraction_summary.csv")
    if not attack_rows:
        raise SystemExit("Missing outputs/final_evidence/attack_fraction_summary.csv")

    scenarios = collect_target_errors()
    write_csv(args.output_dir / "attack_fraction_ci95.csv", build_ci_table(attack_rows))
    write_csv(args.output_dir / "m7_pairwise_target_error_tests.csv", build_pairwise_tests(scenarios))
    write_csv(args.output_dir / "method_target_error_summary.csv", build_method_summary(scenarios))
    print(f"Saved statistical analysis outputs to: {args.output_dir}")


if __name__ == "__main__":
    main()
