"""
run_runtime_scalability.py
==========================
Measure representative per-run runtime for M1-M7 on saved benchmark datasets.

The table reports one execution per method and projects the stochastic methods
to the 30-repeat experimental setting used in the final benchmarks.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_real_dataset_benchmarks import METHODS, ranking_order, write_csv


ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "outputs" / "attack_fraction_curves"
DEFAULT_OUTPUT = ROOT / "outputs" / "runtime_scalability"
DATASETS = [
    "healthcare_countries_2021",
    "car_evaluation",
    "healthcare_resource_allocation",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--datasets", nargs="*", default=DATASETS)
    parser.add_argument("--fraction", default="30", help="Contaminated fraction label to time, e.g. 30 for 30pct.")
    parser.add_argument("--num-bags", type=int, default=200)
    parser.add_argument("--projected-repeats", type=int, default=30)
    parser.add_argument("--seed", type=int, default=20260425)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for dataset in args.datasets:
        path = args.input_dir / f"{dataset}_{args.fraction}pct_contaminated.json"
        if not path.exists():
            raise SystemExit(f"Missing dataset file: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))

        print(f"\n{dataset}: {len(data['alternatives'])} alternatives, {len(data['criteria'])} criteria")
        for method, runner, stochastic in METHODS:
            start = time.perf_counter()
            result = runner(str(path), args.num_bags, args.seed)
            elapsed = time.perf_counter() - start
            projected = elapsed * (args.projected_repeats if stochastic else 1)
            rows.append({
                "dataset": dataset,
                "alternatives": len(data["alternatives"]),
                "criteria": len(data["criteria"]),
                "decision_makers": len(data["decision_makers"]),
                "fraction": f"{args.fraction}pct",
                "method": method,
                "num_bags": args.num_bags if stochastic else 0,
                "single_run_seconds": f"{elapsed:.6f}",
                "projected_30_repeat_seconds": f"{projected:.6f}",
                "top_ranked": ranking_order(result)[0],
            })
            print(f"  {method}: {elapsed:.3f}s")

    write_csv(args.output_dir / "runtime_scalability.csv", rows)
    print(f"\nSaved runtime outputs to: {args.output_dir}")


if __name__ == "__main__":
    main()
