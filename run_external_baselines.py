"""
run_external_baselines.py
=========================
Evaluate external/prior-art-inspired comparator baselines on the saved
attack-fraction datasets.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import m1_normal_topsis as m1
from external_baselines import BASELINES
from run_real_dataset_benchmarks import kendall_tau, rank_map, ranking_order, spearman_rho, write_csv


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "outputs" / "attack_fraction_curves"
DEFAULT_OUTPUT = ROOT / "outputs" / "external_baselines"
DATASETS = [
    "healthcare_countries_2021",
    "car_evaluation",
    "healthcare_resource_allocation",
]


def metric_row(
    dataset: str,
    fraction_label: str,
    method: str,
    reference_order: list[str],
    target_alt: str,
    result: list[tuple[str, float]],
) -> dict:
    order = ranking_order(result)
    target_ref_rank = rank_map(reference_order)[target_alt]
    target_rank = rank_map(order)[target_alt]
    target_error = abs(target_rank - target_ref_rank)
    return {
        "dataset": dataset,
        "attacker_fraction_requested": f"{int(fraction_label) / 100:.2f}",
        "target_alt": target_alt,
        "clean_target_rank": target_ref_rank,
        "method": method,
        "spearman": f"{spearman_rho(reference_order, order):.3f}",
        "kendall": f"{kendall_tau(reference_order, order):.3f}",
        "top1_acc": f"{1.0 if order[0] == reference_order[0] else 0.0:.3f}",
        "target_rank": target_rank,
        "target_rank_error": f"{target_error:.3f}",
        "target_blocked": target_error == 0,
    }


def write_wide_summary(path: Path, rows: list[dict]) -> None:
    grouped: dict[tuple[str, str], dict[str, dict]] = {}
    for row in rows:
        key = (row["dataset"], row["attacker_fraction_requested"])
        grouped.setdefault(key, {})[row["method"]] = row

    wide_rows = []
    for dataset, fraction in sorted(grouped):
        methods = grouped[(dataset, fraction)]
        first = next(iter(methods.values()))
        wide = {
            "dataset": dataset,
            "attacker_fraction_requested": fraction,
            "target_alt": first["target_alt"],
            "clean_target_rank": first["clean_target_rank"],
        }
        for method, _ in BASELINES:
            row = methods.get(method, {})
            wide[f"{method}_target_rank"] = row.get("target_rank", "")
            wide[f"{method}_target_error"] = row.get("target_rank_error", "")
            wide[f"{method}_blocked"] = row.get("target_blocked", "")
        wide_rows.append(wide)

    write_csv(path, wide_rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--datasets", nargs="*", default=DATASETS)
    parser.add_argument("--fractions", nargs="+", default=["10", "20", "30", "40", "50", "60"])
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for dataset in args.datasets:
        clean_path = args.input_dir / f"{dataset}_clean.json"
        if not clean_path.exists():
            raise SystemExit(f"Missing clean dataset: {clean_path}")
        reference_order = ranking_order(m1.run_m1(str(clean_path)))
        target_alt = reference_order[-1]

        for fraction in args.fractions:
            contaminated_path = args.input_dir / f"{dataset}_{fraction}pct_contaminated.json"
            if not contaminated_path.exists():
                raise SystemExit(f"Missing contaminated dataset: {contaminated_path}")
            print(f"{dataset} {fraction}%")
            for method, runner in BASELINES:
                result = runner(str(contaminated_path))
                rows.append(metric_row(dataset, fraction, method, reference_order, target_alt, result))

    write_csv(args.output_dir / "external_baseline_metrics.csv", rows)
    write_wide_summary(args.output_dir / "external_baseline_target_rank_wide.csv", rows)
    print(f"Saved external baseline outputs to: {args.output_dir}")


if __name__ == "__main__":
    main()
