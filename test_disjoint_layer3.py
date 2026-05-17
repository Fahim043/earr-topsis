"""
test_disjoint_layer3.py — Benchmarking Disjoint Positional vs Bootstrap Layer 3
===============================================================================
Compare the disjoint partition+positional voting variants of M4, M5, M6 
against their original full-bootstrap mean-aggregation counterparts.
We want to see if disjoint subsetting is better or worse for clustering (M5).
"""

import json
import os
import warnings
warnings.filterwarnings('ignore')

from run_all_tests import generate_dataset
import m4_weighted_bagging as m4_orig
import m5_cluster_stratified as m5_orig
import m6_reliability_weighted as m6_orig
import m4_disjoint
import m5_disjoint
import m6_disjoint

if __name__ == "__main__":
    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"

    datasets_config = [
        {"name": "DS1 (10DM, 30%)",   "alts": 5,  "crit": 4,  "dms": 10,  "biased": 3,  "seed": 42},
        {"name": "DS4 (15DM, 40%)",   "alts": 6,  "crit": 5,  "dms": 15,  "biased": 6,  "seed": 200},
        {"name": "DS6 (30DM, 20%)",   "alts": 10, "crit": 6,  "dms": 30,  "biased": 6,  "seed": 500},
        {"name": "DS7 (50DM, 30%)",   "alts": 10, "crit": 8,  "dms": 50,  "biased": 15, "seed": 700},
        {"name": "DS8 (100DM, 20%)",  "alts": 10, "crit": 8,  "dms": 100, "biased": 20, "seed": 1000},
        {"name": "DS10 (500DM, 10%)", "alts": 20, "crit": 12, "dms": 500, "biased": 50, "seed": 5000},
    ]

    print("=" * 140)
    print("LAYER 3 BENCHMARK: ORIGINAL BOOTSTRAP vs DISJOINT POSITIONAL VOTING")
    print("Evaluating Ground Truth A1 Position Recovery on Biased Datasets")
    print("=" * 140)
    print(f"  {'Dataset':<25} | {'M4(Orig)':<10} {'M4(Disj)':<10} | {'M5(Orig)':<10} {'M5(Disj)':<10} | {'M6(Orig)':<10} {'M6(Disj)':<10}")
    print("-" * 140)

    for ds in datasets_config:
        n_data, b_data, _ = generate_dataset(ds["alts"], ds["crit"], ds["dms"], ds["biased"], ds["seed"])
        
        n_path = os.path.join(out_dir, "_temp_n.json")
        b_path = os.path.join(out_dir, "_temp_b.json")
        with open(n_path, 'w') as f: json.dump(n_data, f)
        with open(b_path, 'w') as f: json.dump(b_data, f)

        # Get GT (A1 position) using M1 on normal data
        import m1_normal_topsis as m1
        gt_res = m1.run_m1(n_path)
        gt_a1 = [alt for alt, _ in gt_res].index("A1") + 1
        
        # M4
        m4o, _ = m4_orig.run_m4(b_path)
        m4d, _ = m4_disjoint.run_m4_disjoint(b_path, num_subsets=5)
        
        m4o_a1 = [a for a, _ in m4o].index("A1") + 1
        m4d_a1 = [a for a, _ in m4d].index("A1") + 1
        
        # M5
        m5o, _, _ = m5_orig.run_m5(b_path)
        m5d, _, _ = m5_disjoint.run_m5_disjoint(b_path, num_subsets=5)
        
        m5o_a1 = [a for a, _ in m5o].index("A1") + 1
        m5d_a1 = [a for a, _ in m5d].index("A1") + 1
        
        # M6
        m6o, _ = m6_orig.run_m6(b_path)
        m6d, _ = m6_disjoint.run_m6_disjoint(b_path, num_subsets=5)
        
        m6o_a1 = [a for a, _ in m6o].index("A1") + 1
        m6d_a1 = [a for a, _ in m6d].index("A1") + 1

        def mark(rank):
            return f"✅ #{rank}" if rank > 1 else f"❌ #{rank}"

        label = f"{ds['name']} (GT:#{gt_a1})"
        print(f"  {label:<25} | {mark(m4o_a1):<10} {mark(m4d_a1):<10} | {mark(m5o_a1):<10} {mark(m5d_a1):<10} | {mark(m6o_a1):<10} {mark(m6d_a1):<10}")

    for f in ["_temp_n.json", "_temp_b.json"]:
        try: os.remove(os.path.join(out_dir, f))
        except: pass

    print("=" * 140)
