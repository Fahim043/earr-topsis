"""
run_attack_fraction_curves.py
=============================
Run M1-M7 across multiple synthetic contamination fractions on real/pseudo-real
datasets.

This is the main missing experiment for thesis/journal reporting after the
single 30% contamination benchmark. It records how each method degrades as the
attacker fraction increases.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import m1_normal_topsis as m1
from run_real_dataset_benchmarks import (
    evaluate_dataset,
    inject_synthetic_bias,
    load_real_datasets,
    ranking_order,
    rank_map,
    write_csv,
)


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "outputs" / "attack_fraction_curves"
PUBLICATION_DATASETS = [
    "healthcare_countries_2021",
    "car_evaluation",
    "healthcare_resource_allocation",
]


def fraction_label(value: float) -> str:
    return f"{round(value * 100):02d}pct"


def parse_target_error(value: str) -> str:
    return str(value).split("±", 1)[0]


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def summarize_fraction_rows(
    dataset_name: str,
    fraction: float,
    clean_reference: list[str],
    target_alt: str,
    attackers: list[str],
    num_dms: int,
    rows: list[dict],
) -> list[dict]:
    target_ref_rank = rank_map(clean_reference)[target_alt]
    summary = []
    for row in rows:
        summary.append({
            "dataset": dataset_name,
            "attacker_fraction_requested": f"{fraction:.2f}",
            "attacker_fraction_effective": f"{len(attackers) / num_dms:.3f}",
            "num_attackers": len(attackers),
            "target_alt": target_alt,
            "clean_target_rank": target_ref_rank,
            "method": row["method"],
            "spearman": row["spearman"],
            "kendall": row["kendall"],
            "top1_acc": row["top1_acc"],
            "target_rank": row["target_rank"],
            "target_rank_error": row["target_rank_error"],
            "target_blocked": parse_target_error(row["target_rank_error"]) == "0.000",
        })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-bags", type=int, default=200)
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260425)
    parser.add_argument("--max-alternatives", type=int, default=300)
    parser.add_argument(
        "--fractions",
        nargs="+",
        type=float,
        default=[0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
        help="Requested attacker fractions to evaluate.",
    )
    parser.add_argument(
        "--datasets",
        nargs="*",
        default=PUBLICATION_DATASETS,
        help="Dataset names to run. Defaults to the three publication-facing larger datasets.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUT_DIR,
        help="Directory where JSON and CSV outputs will be saved.",
    )
    args = parser.parse_args()

    if any(f <= 0 or f >= 1 for f in args.fractions):
        raise SystemExit("All fractions must be between 0 and 1.")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    selected = set(args.datasets or [])
    all_rows: list[dict] = []

    eval_args = SimpleNamespace(
        repeats=args.repeats,
        num_bags=args.num_bags,
        seed=args.seed,
    )

    for dataset_name, clean_data in load_real_datasets(args.max_alternatives, args.seed, selected):
        clean_data = copy.deepcopy(clean_data)
        clean_path = output_dir / f"{dataset_name}_clean.json"
        save_json(clean_path, clean_data)
        clean_reference = ranking_order(m1.run_m1(str(clean_path)))
        target_alt = clean_reference[-1]

        print("\n" + "=" * 120)
        print(f"DATASET: {dataset_name}")
        print(
            f"Alternatives={len(clean_data['alternatives'])}, "
            f"Criteria={len(clean_data['criteria'])}, "
            f"DMs={len(clean_data['decision_makers'])}"
        )
        print(f"Target: {target_alt} (clean M1 rank #{len(clean_reference)})")

        clean_rows = evaluate_dataset(clean_path, clean_reference, target_alt, eval_args, dataset_name, "clean")
        write_csv(output_dir / f"{dataset_name}_clean_metrics.csv", clean_rows)

        for fraction in args.fractions:
            label = fraction_label(fraction)
            contaminated_data, attackers = inject_synthetic_bias(clean_data, target_alt, fraction)
            contaminated_path = output_dir / f"{dataset_name}_{label}_contaminated.json"
            save_json(contaminated_path, contaminated_data)

            effective_fraction = len(attackers) / len(clean_data["decision_makers"])
            print("\n" + "-" * 120)
            print(
                f"{dataset_name}: requested={fraction:.0%}, "
                f"effective={effective_fraction:.1%}, attackers={attackers}"
            )

            rows = evaluate_dataset(
                contaminated_path,
                clean_reference,
                target_alt,
                eval_args,
                dataset_name,
                f"contaminated_{label}",
            )
            write_csv(output_dir / f"{dataset_name}_{label}_contaminated_metrics.csv", rows)
            all_rows.extend(
                summarize_fraction_rows(
                    dataset_name,
                    fraction,
                    clean_reference,
                    target_alt,
                    attackers,
                    len(clean_data["decision_makers"]),
                    rows,
                )
            )
            write_csv(output_dir / "attack_fraction_summary.csv", all_rows)

    write_csv(output_dir / "attack_fraction_summary.csv", all_rows)
    print("\n" + "=" * 120)
    print(f"Saved attack-fraction curve outputs to: {output_dir}")


if __name__ == "__main__":
    main()
