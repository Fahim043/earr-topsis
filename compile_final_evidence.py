"""
compile_final_evidence.py
=========================
Collect benchmark CSV outputs into thesis/journal-ready evidence tables.

This script does not rerun experiments. It reads the saved outputs under
outputs/real_dataset_benchmarks, outputs/real_dataset_benchmarks_light, and
outputs/synthetic_repeated_evaluation, then writes compact CSV/Markdown/LaTeX
tables to outputs/final_evidence.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import m1_normal_topsis as m1


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "final_evidence"
METHODS = [f"M{i}" for i in range(1, 8)]


def parse_pm(value: str) -> tuple[float | None, float | None]:
    value = str(value).strip()
    if not value or value.upper() == "NA":
        return None, None
    if "±" in value:
        mean, std = value.split("±", 1)
        return float(mean), float(std)
    return float(value), None


def fmt_num(value: str | float | int | None) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.replace("±", " +/- ")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt_num(v) for v in row) + " |")
    return "\n".join(lines)


def latex_table(headers: list[str], rows: list[list[object]], caption: str, label: str) -> str:
    colspec = "l" * len(headers)
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\small",
        f"\\caption{{{caption}}}",
        f"\\label{{{label}}}",
        f"\\begin{{tabular}}{{{colspec}}}",
        "\\hline",
        " & ".join(headers) + " \\\\",
        "\\hline",
    ]
    for row in rows:
        escaped = [fmt_num(v).replace("_", "\\_").replace("%", "\\%") for v in row]
        lines.append(" & ".join(escaped) + " \\\\")
    lines.extend(["\\hline", "\\end{tabular}", "\\end{table}"])
    return "\n".join(lines)


def dataset_metadata(clean_json: Path) -> dict:
    data = json.loads(clean_json.read_text(encoding="utf-8"))
    clean_order = [alt for alt, _ in m1.run_m1(str(clean_json))]
    target_alt = clean_order[-1]
    return {
        "alternatives": len(data["alternatives"]),
        "criteria": len(data["criteria"]),
        "decision_makers": len(data["decision_makers"]),
        "target_alt": target_alt,
        "clean_target_rank": len(clean_order),
    }


def collect_real_set(source_dir: Path, evidence_set: str) -> tuple[list[dict], list[dict]]:
    long_rows: list[dict] = []
    wide_rows: list[dict] = []

    for contaminated_csv in sorted(source_dir.glob("*_contaminated_metrics.csv")):
        dataset = contaminated_csv.name.removesuffix("_contaminated_metrics.csv")
        clean_csv = source_dir / f"{dataset}_clean_metrics.csv"
        clean_json = source_dir / f"{dataset}_clean.json"
        if not clean_csv.exists() or not clean_json.exists():
            continue
        meta = dataset_metadata(clean_json)

        for mode, csv_path in [("clean", clean_csv), ("contaminated", contaminated_csv)]:
            for row in read_csv(csv_path):
                spearman_mean, spearman_std = parse_pm(row["spearman"])
                kendall_mean, kendall_std = parse_pm(row["kendall"])
                top1_mean, top1_std = parse_pm(row["top1_acc"])
                err_mean, err_std = parse_pm(row["target_rank_error"])
                long_rows.append({
                    "evidence_set": evidence_set,
                    "dataset": dataset,
                    "mode": mode,
                    **meta,
                    "method": row["method"],
                    "spearman": row["spearman"],
                    "spearman_mean": spearman_mean,
                    "spearman_std": spearman_std,
                    "kendall": row["kendall"],
                    "kendall_mean": kendall_mean,
                    "kendall_std": kendall_std,
                    "top1_acc": row["top1_acc"],
                    "top1_mean": top1_mean,
                    "top1_std": top1_std,
                    "target_rank": row["target_rank"],
                    "target_rank_error": row["target_rank_error"],
                    "target_rank_error_mean": err_mean,
                    "target_rank_error_std": err_std,
                    "target_blocked": bool(err_mean == 0.0),
                })

        contaminated_rows = {row["method"]: row for row in read_csv(contaminated_csv)}
        wide = {
            "evidence_set": evidence_set,
            "dataset": dataset,
            **meta,
        }
        for method in METHODS:
            row = contaminated_rows.get(method)
            if row:
                err_mean, err_std = parse_pm(row["target_rank_error"])
                wide[f"{method}_target_rank"] = row["target_rank"]
                wide[f"{method}_target_error"] = row["target_rank_error"]
                wide[f"{method}_blocked"] = bool(err_mean == 0.0)
        wide_rows.append(wide)

    return long_rows, wide_rows


def collect_synthetic(source_dir: Path) -> tuple[list[dict], list[dict]]:
    long_rows: list[dict] = []
    wide_rows: list[dict] = []
    all_csv = source_dir / "all_synthetic_repeated_metrics.csv"
    if not all_csv.exists():
        return long_rows, wide_rows

    rows = read_csv(all_csv)
    by_dataset: dict[str, list[dict]] = {}
    for row in rows:
        by_dataset.setdefault(row["dataset"], []).append(row)

    for dataset, ds_rows in sorted(by_dataset.items()):
        normal_json = source_dir / f"{dataset}_normal.json"
        meta = {}
        if normal_json.exists():
            data = json.loads(normal_json.read_text(encoding="utf-8"))
            clean_order = [alt for alt, _ in m1.run_m1(str(normal_json))]
            meta = {
                "alternatives": len(data["alternatives"]),
                "criteria": len(data["criteria"]),
                "decision_makers": len(data["decision_makers"]),
                "target_alt": "A1",
                "clean_a1_rank": clean_order.index("A1") + 1,
            }
        match = re.search(r"_(\d+)pct", dataset)
        attack_fraction_pct = match.group(1) if match else ""

        wide = {"dataset": dataset, "attack_fraction_pct": attack_fraction_pct, **meta}
        for row in ds_rows:
            rank_mean, rank_std = parse_pm(row["a1_rank_mean"])
            err_mean, err_std = parse_pm(row["a1_rank_error"])
            spearman_mean, spearman_std = parse_pm(row["spearman"])
            kendall_mean, kendall_std = parse_pm(row["kendall"])
            top1_mean, top1_std = parse_pm(row["top1_acc"])
            long_rows.append({
                "dataset": dataset,
                "attack_fraction_pct": attack_fraction_pct,
                **meta,
                "method": row["method"],
                "spearman": row["spearman"],
                "spearman_mean": spearman_mean,
                "spearman_std": spearman_std,
                "kendall": row["kendall"],
                "kendall_mean": kendall_mean,
                "kendall_std": kendall_std,
                "top1_acc": row["top1_acc"],
                "top1_mean": top1_mean,
                "top1_std": top1_std,
                "a1_rank": row["a1_rank_mean"],
                "a1_rank_mean": rank_mean,
                "a1_rank_std": rank_std,
                "a1_rank_error": row["a1_rank_error"],
                "a1_rank_error_mean": err_mean,
                "a1_rank_error_std": err_std,
                "target_blocked": bool(err_mean == 0.0),
            })
            wide[f"{row['method']}_a1_rank"] = row["a1_rank_mean"]
            wide[f"{row['method']}_a1_error"] = row["a1_rank_error"]
            wide[f"{row['method']}_blocked"] = bool(err_mean == 0.0)
        wide_rows.append(wide)

    return long_rows, wide_rows


def collect_attack_curves(source_dir: Path) -> list[dict]:
    summary_csv = source_dir / "attack_fraction_summary.csv"
    if not summary_csv.exists():
        return []
    return read_csv(summary_csv)


def collect_optional_csv(path: Path) -> list[dict]:
    return read_csv(path) if path.exists() else []


def attack_curve_wide(attack_rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str], dict[str, dict]] = {}
    for row in attack_rows:
        key = (row["dataset"], row["attacker_fraction_requested"])
        grouped.setdefault(key, {})[row["method"]] = row

    wide_rows = []
    for dataset, fraction in sorted(grouped):
        methods = grouped[(dataset, fraction)]
        first = next(iter(methods.values()))
        wide = {
            "dataset": dataset,
            "attacker_fraction_requested": fraction,
            "attacker_fraction_effective": first["attacker_fraction_effective"],
            "num_attackers": first["num_attackers"],
            "target_alt": first["target_alt"],
            "clean_target_rank": first["clean_target_rank"],
        }
        for method in METHODS:
            row = methods.get(method, {})
            wide[f"{method}_target_rank"] = row.get("target_rank", "")
            wide[f"{method}_target_error"] = row.get("target_rank_error", "")
            wide[f"{method}_blocked"] = row.get("target_blocked", "")
        wide_rows.append(wide)
    return wide_rows


def build_report(
    real_wide: list[dict],
    synthetic_wide: list[dict],
    attack_rows: list[dict],
    external_wide: list[dict],
    method_summary: list[dict],
    pairwise_tests: list[dict],
    runtime_rows: list[dict],
) -> str:
    publication_datasets = {
        "healthcare_countries_2021",
        "car_evaluation",
        "healthcare_resource_allocation",
    }
    current_real = [
        r for r in real_wide
        if r["evidence_set"] == "post_fix_focused_30x200"
        and r["dataset"] in publication_datasets
    ]
    light_real = [r for r in real_wide if r["evidence_set"] == "light_all_datasets_5x50"]

    def real_rows(rows: list[dict]) -> list[list[object]]:
        return [
            [
                r["dataset"],
                r["alternatives"],
                r["target_alt"],
                r.get("M1_target_rank", ""),
                r.get("M2_target_rank", ""),
                r.get("M3_target_rank", ""),
                r.get("M4_target_rank", ""),
                r.get("M5_target_rank", ""),
                r.get("M6_target_rank", ""),
                r.get("M7_target_rank", ""),
            ]
            for r in rows
        ]

    synthetic_rows = [
        [
            r["dataset"],
            r.get("clean_a1_rank", ""),
            r.get("M1_a1_rank", ""),
            r.get("M2_a1_rank", ""),
            r.get("M3_a1_rank", ""),
            r.get("M4_a1_rank", ""),
            r.get("M5_a1_rank", ""),
            r.get("M6_a1_rank", ""),
            r.get("M7_a1_rank", ""),
        ]
        for r in synthetic_wide
    ]

    attack_curve_rows = []
    if attack_rows:
        for wide in attack_curve_wide(attack_rows):
            attack_curve_rows.append([
                wide["dataset"],
                f"{float(wide['attacker_fraction_requested']):.0%}",
                wide["attacker_fraction_effective"],
                wide["M1_target_rank"],
                wide["M2_target_rank"],
                wide["M3_target_rank"],
                wide["M4_target_rank"],
                wide["M5_target_rank"],
                wide["M6_target_rank"],
                wide["M7_target_rank"],
            ])

    lines = [
        "# Final Evidence Tables for Thesis and Journal Draft",
        "",
        "Generated from saved CSV outputs. These tables summarize target-rank behavior; use the long-form CSV files for full Spearman, Kendall, Top1, and standard deviation values.",
        "",
        "## Key Interpretation",
        "",
        "- M1 is the vulnerable standard fuzzy TOPSIS baseline.",
        "- M2 is true bootstrap bagged fuzzy TOPSIS and should be reported as the corrected ensemble baseline; it often helps but is not sufficient.",
        "- M5 is inconsistent and should be treated as an intermediate/ablation method.",
        "- M4, M6, and M7 are the recommended proposed methods; M3 is a strong internal comparator/intermediate reliability method.",
        "- Target-rank error is more important than Spearman/Kendall for targeted manipulation, because global rank correlations can stay high while the attacked target moves sharply upward.",
        "",
        "## Post-Fix Focused Real/Pseudo-Real Benchmarks",
        "",
        "These are the three larger datasets rerun after the latest code fixes with 30 repeats and 200 bags. Supplier cases are intentionally excluded from this table because they have only two DMs and are diagnostic only.",
        "",
        markdown_table(
            ["Dataset", "Alts", "Target", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
            real_rows(current_real),
        ),
        "",
        "## Earlier Light Real/Pseudo-Real Benchmarks",
        "",
        markdown_table(
            ["Dataset", "Alts", "Target", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
            real_rows(light_real),
        ),
        "",
        "## Repeated Synthetic Benchmarks",
        "",
        markdown_table(
            ["Dataset", "Clean A1 Rank", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
            synthetic_rows,
        ),
        "",
        "## Attack-Fraction Curves",
        "",
    ]
    if attack_curve_rows:
        lines.extend([
            markdown_table(
                ["Dataset", "Req. Attack", "Eff. Attack", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
                attack_curve_rows,
            ),
            "",
        ])
    else:
        lines.extend([
            "No full attack-fraction curve output has been recorded yet. Generate it with:",
            "",
            "```bash",
            "python run_attack_fraction_curves.py --datasets healthcare_countries_2021 car_evaluation healthcare_resource_allocation --max-alternatives 300 --repeats 30 --num-bags 200 --fractions 0.1 0.2 0.3 0.4 0.5 0.6",
            "```",
            "",
        ])
    if external_wide:
        external_rows = [
            [
                r["dataset"],
                f"{float(r['attacker_fraction_requested']):.0%}",
                r["clean_target_rank"],
                r.get("EB1_MedianTOPSIS_target_rank", ""),
                r.get("EB2_TrimmedMeanTOPSIS_target_rank", ""),
                r.get("EB3_MADConsensusTOPSIS_target_rank", ""),
                r.get("EB4_IndividualBordaTOPSIS_target_rank", ""),
                r.get("EB5_HuangLiGroupIdealTOPSIS_target_rank", ""),
            ]
            for r in external_wide
        ]
        lines.extend([
            "## External Comparator Baselines",
            "",
            "These prior-art-inspired comparators are not part of M1-M7. They test robust aggregation, consensus filtering, and individual-rank aggregation alternatives.",
            "",
            markdown_table(
                ["Dataset", "Attack", "Clean Target", "Median", "Trimmed", "MAD Consensus", "Individual Borda", "Huang-Li Group Ideal"],
                external_rows,
            ),
            "",
        ])
    if method_summary:
        summary_rows = [
            [
                r["method"],
                r["cases"],
                r["blocked_cases"],
                r["blocked_rate"],
                r["mean_target_rank_error"],
                r["max_target_rank_error"],
            ]
            for r in method_summary
        ]
        lines.extend([
            "## Statistical Summary",
            "",
            markdown_table(
                ["Method", "Cases", "Blocked", "Blocked Rate", "Mean Target Error", "Max Target Error"],
                summary_rows,
            ),
            "",
        ])
    if pairwise_tests:
        pairwise_rows = [
            [
                r["comparison"],
                r["cases"],
                r["m7_better"],
                r["m7_worse"],
                r["ties"],
                r["sign_test_p_two_sided"],
                r["wilcoxon_p_two_sided_approx"],
            ]
            for r in pairwise_tests
        ]
        lines.extend([
            "## M7 Pairwise Target-Error Tests",
            "",
            "Positive cases mean M7 had lower target-rank error than the comparator over the same dataset/fraction scenario.",
            "",
            markdown_table(
                ["Comparison", "Cases", "M7 Better", "M7 Worse", "Ties", "Sign p", "Wilcoxon p"],
                pairwise_rows,
            ),
            "",
        ])
    if runtime_rows:
        runtime_table = [
            [
                r["dataset"],
                r["method"],
                r["alternatives"],
                r["criteria"],
                r["single_run_seconds"],
                r["projected_30_repeat_seconds"],
            ]
            for r in runtime_rows
        ]
        lines.extend([
            "## Runtime/Scalability Snapshot",
            "",
            "Runtimes are representative single executions at the 30% contaminated setting with 200 bags. Stochastic methods include a projected 30-repeat runtime.",
            "",
            markdown_table(
                ["Dataset", "Method", "Alts", "Criteria", "One Run Sec", "Projected 30x Sec"],
                runtime_table,
            ),
            "",
        ])
    lines.extend([
        "## Remaining Work for A1/Q1-Grade Submission",
        "",
        "1. If the supervisor requires exact prior-art reproductions, select 1-2 specific published algorithms and implement them in addition to the current robust comparators.",
        "2. Freeze M7 and rerun all final tables after any future code changes.",
        "3. Preserve human-mimic/adaptive attacks as a limitation and threat-model boundary.",
        "4. Convert these tables into polished manuscript tables with citations and narrative explanation.",
    ])
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    real_long: list[dict] = []
    real_wide: list[dict] = []
    for path, evidence_set in [
        (ROOT / "outputs" / "real_dataset_benchmarks", "post_fix_focused_30x200"),
        (ROOT / "outputs" / "real_dataset_benchmarks_light", "light_all_datasets_5x50"),
    ]:
        if path.exists():
            long_rows, wide_rows = collect_real_set(path, evidence_set)
            real_long.extend(long_rows)
            real_wide.extend(wide_rows)

    synthetic_long, synthetic_wide = collect_synthetic(ROOT / "outputs" / "synthetic_repeated_evaluation")
    attack_rows = collect_attack_curves(ROOT / "outputs" / "attack_fraction_curves")
    external_wide = collect_optional_csv(ROOT / "outputs" / "external_baselines" / "external_baseline_target_rank_wide.csv")
    external_long = collect_optional_csv(ROOT / "outputs" / "external_baselines" / "external_baseline_metrics.csv")
    ci_rows = collect_optional_csv(ROOT / "outputs" / "statistical_analysis" / "attack_fraction_ci95.csv")
    method_summary = collect_optional_csv(ROOT / "outputs" / "statistical_analysis" / "method_target_error_summary.csv")
    pairwise_tests = collect_optional_csv(ROOT / "outputs" / "statistical_analysis" / "m7_pairwise_target_error_tests.csv")
    runtime_rows = collect_optional_csv(ROOT / "outputs" / "runtime_scalability" / "runtime_scalability.csv")

    write_csv(OUT / "real_metrics_long.csv", real_long)
    write_csv(OUT / "real_contaminated_target_summary_wide.csv", real_wide)
    write_csv(OUT / "synthetic_metrics_long.csv", synthetic_long)
    write_csv(OUT / "synthetic_target_summary_wide.csv", synthetic_wide)
    write_csv(OUT / "attack_fraction_summary.csv", attack_rows)
    write_csv(OUT / "attack_fraction_target_rank_wide.csv", attack_curve_wide(attack_rows))
    write_csv(OUT / "external_baseline_metrics.csv", external_long)
    write_csv(OUT / "external_baseline_target_rank_wide.csv", external_wide)
    write_csv(OUT / "attack_fraction_ci95.csv", ci_rows)
    write_csv(OUT / "method_target_error_summary.csv", method_summary)
    write_csv(OUT / "m7_pairwise_target_error_tests.csv", pairwise_tests)
    write_csv(OUT / "runtime_scalability.csv", runtime_rows)

    report = build_report(
        real_wide,
        synthetic_wide,
        attack_rows,
        external_wide,
        method_summary,
        pairwise_tests,
        runtime_rows,
    )
    (OUT / "final_evidence_report.md").write_text(report, encoding="utf-8")

    publication_datasets = {
        "healthcare_countries_2021",
        "car_evaluation",
        "healthcare_resource_allocation",
    }
    current_real = [
        r for r in real_wide
        if r["evidence_set"] == "post_fix_focused_30x200"
        and r["dataset"] in publication_datasets
    ]
    current_rows = [
        [
            r["dataset"],
            r["alternatives"],
            r["target_alt"],
            r.get("M1_target_rank", ""),
            r.get("M2_target_rank", ""),
            r.get("M3_target_rank", ""),
            r.get("M4_target_rank", ""),
            r.get("M5_target_rank", ""),
            r.get("M6_target_rank", ""),
            r.get("M7_target_rank", ""),
        ]
        for r in current_real
    ]
    latex = latex_table(
        ["Dataset", "Alts", "Target", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
        current_rows,
        "Target rank under structured contamination in post-fix focused benchmarks.",
        "tab:post_fix_target_rank",
    )
    (OUT / "real_target_summary_table.tex").write_text(latex + "\n", encoding="utf-8")

    attack_wide = attack_curve_wide(attack_rows)
    if attack_wide:
        attack_table_rows = [
            [
                r["dataset"],
                f"{float(r['attacker_fraction_requested']):.0%}",
                r["attacker_fraction_effective"],
                r["clean_target_rank"],
                r.get("M1_target_rank", ""),
                r.get("M2_target_rank", ""),
                r.get("M3_target_rank", ""),
                r.get("M4_target_rank", ""),
                r.get("M5_target_rank", ""),
                r.get("M6_target_rank", ""),
                r.get("M7_target_rank", ""),
            ]
            for r in attack_wide
        ]
        (OUT / "attack_fraction_target_rank_table.tex").write_text(
            latex_table(
                ["Dataset", "Req.", "Eff.", "Clean", "M1", "M2", "M3", "M4", "M5", "M6", "M7"],
                attack_table_rows,
                "Target-rank behavior over increasing structured contamination.",
                "tab:attack_fraction_target_rank",
            )
            + "\n",
            encoding="utf-8",
        )

    if external_wide:
        external_table_rows = [
            [
                r["dataset"],
                f"{float(r['attacker_fraction_requested']):.0%}",
                r["clean_target_rank"],
                r.get("EB1_MedianTOPSIS_target_rank", ""),
                r.get("EB2_TrimmedMeanTOPSIS_target_rank", ""),
                r.get("EB3_MADConsensusTOPSIS_target_rank", ""),
                r.get("EB4_IndividualBordaTOPSIS_target_rank", ""),
                r.get("EB5_HuangLiGroupIdealTOPSIS_target_rank", ""),
            ]
            for r in external_wide
        ]
        (OUT / "external_baseline_target_rank_table.tex").write_text(
            latex_table(
                ["Dataset", "Attack", "Clean", "Median", "Trimmed", "MAD", "Borda", "Huang-Li"],
                external_table_rows,
                "Target-rank comparison against external TOPSIS and robust-aggregation comparators.",
                "tab:external_baseline_target_rank",
            )
            + "\n",
            encoding="utf-8",
        )

    if method_summary:
        method_table_rows = [
            [
                r["method"],
                r["cases"],
                r["blocked_cases"],
                r["blocked_rate"],
                r["mean_target_rank_error"],
                r["max_target_rank_error"],
            ]
            for r in method_summary
        ]
        (OUT / "method_target_error_summary_table.tex").write_text(
            latex_table(
                ["Method", "Cases", "Blocked", "Rate", "Mean Error", "Max Error"],
                method_table_rows,
                "Target-rank-error summary across attack-fraction scenarios.",
                "tab:method_target_error_summary",
            )
            + "\n",
            encoding="utf-8",
        )

    if runtime_rows:
        runtime_table_rows = [
            [
                r["dataset"],
                r["method"],
                r["alternatives"],
                r["criteria"],
                r["single_run_seconds"],
                r["projected_30_repeat_seconds"],
            ]
            for r in runtime_rows
        ]
        (OUT / "runtime_scalability_table.tex").write_text(
            latex_table(
                ["Dataset", "Method", "Alts", "Crit.", "One Run Sec", "Projected 30x Sec"],
                runtime_table_rows,
                "Representative runtime and scalability snapshot.",
                "tab:runtime_scalability",
            )
            + "\n",
            encoding="utf-8",
        )

    print(f"Wrote final evidence package to {OUT}")


if __name__ == "__main__":
    main()
