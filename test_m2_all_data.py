"""
test_m2_all_data.py — Testing M2 Bootstrap Bagging on Normal vs Biased Data
============================================================================
Tests true M2 bootstrap bagging (with replacement + Borda aggregation) on all
10 datasets, showing exactly how it performs on normal data versus biased data.
"""

import json
import os
import copy
import warnings
warnings.filterwarnings('ignore')

import m1_normal_topsis as m1
import m2_bagged_topsis as m2
from run_all_tests import generate_dataset

if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"

    datasets_config = [
        {"name": "DS1 (10DM, 30% bias)",   "alts": 5,  "crit": 4,  "dms": 10,  "biased": 3,  "seed": 42},
        {"name": "DS2 (10DM, 50% bias)",   "alts": 5,  "crit": 4,  "dms": 10,  "biased": 5,  "seed": 77},
        {"name": "DS3 (20DM, 25% bias)",   "alts": 8,  "crit": 6,  "dms": 20,  "biased": 5,  "seed": 101},
        {"name": "DS4 (15DM, 40% bias)",   "alts": 6,  "crit": 5,  "dms": 15,  "biased": 6,  "seed": 200},
        {"name": "DS5 (6DM, 33% bias)",    "alts": 4,  "crit": 3,  "dms": 6,   "biased": 2,  "seed": 333},
        {"name": "DS6 (30DM, 20% bias)",   "alts": 10, "crit": 6,  "dms": 30,  "biased": 6,  "seed": 500},
        {"name": "DS7 (50DM, 30% bias)",   "alts": 10, "crit": 8,  "dms": 50,  "biased": 15, "seed": 700},
        {"name": "DS8 (100DM, 20% bias)",  "alts": 10, "crit": 8,  "dms": 100, "biased": 20, "seed": 1000},
        {"name": "DS9 (200DM, 25% bias)",  "alts": 15, "crit": 10, "dms": 200, "biased": 50, "seed": 2000},
        {"name": "DS10 (500DM, 10% bias)", "alts": 20, "crit": 12, "dms": 500, "biased": 50, "seed": 5000},
    ]

    print("=" * 130)
    print("M2 (BOOTSTRAP BAGGING + BORDA VOTING) — NORMAL VS BIASED EVALUATION")
    print("=" * 130)

    for ds in datasets_config:
        normal_data, biased_data, biased_dms = generate_dataset(
            ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"]
        )

        n_path = os.path.join(out_dir, "_test_m2_normal.json")
        b_path = os.path.join(out_dir, "_test_m2_biased.json")
        with open(n_path, 'w') as f: json.dump(normal_data, f)
        with open(b_path, 'w') as f: json.dump(biased_data, f)

        # Baseline M1 on Normal
        gt_res = m1.run_m1(n_path)
        gt_order = [alt for alt, _ in gt_res]
        
        # M2 on Normal
        m2_norm_res = m2.run_m2(n_path, seed=ds["seed"] + 2)
        m2_norm_order = [alt for alt, _ in m2_norm_res]
        
        # M2 on Biased
        m2_bias_res = m2.run_m2(b_path, seed=ds["seed"] + 20)
        m2_bias_order = [alt for alt, _ in m2_bias_res]
        
        def format_rank(order):
            s = " > ".join(order)
            if len(s) > 60:
                s = s[:57] + "..."
            return s

        print(f"\n{ds['name']} | {ds['dms']} DMs total | {ds['biased']} Biased DMs")
        print("-" * 130)
        print(f"{'Data & Method':<25} {'Ranking Output':<65} {'A1 Position'}")
        print("-" * 130)
        print(f"{'M1 (Normal) [Ground Truth]':<25} {format_rank(gt_order):<65} #{gt_order.index('A1')+1}")
        print(f"{'M2 (Normal)':<25} {format_rank(m2_norm_order):<65} #{m2_norm_order.index('A1')+1}")
        print(f"{'M2 (Biased)':<25} {format_rank(m2_bias_order):<65} #{m2_bias_order.index('A1')+1}")
        print("=" * 130)

    for f in ["_test_m2_normal.json", "_test_m2_biased.json"]:
        try: os.remove(os.path.join(out_dir, f))
        except: pass
