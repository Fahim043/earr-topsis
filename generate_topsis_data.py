import json
import random
import os

random.seed(42)  # Fixed seed for reproducibility

def generate_fuzzy_rating(base_val, noise_level=1.0):
    """Generate a Triangular Fuzzy Number (l, m, u) around a base value."""
    m = max(1, min(9, round(base_val + random.uniform(-noise_level, noise_level))))
    l = max(1, m - random.randint(1, 2))
    u = min(9, m + random.randint(1, 2))
    return [l, m, u]


def generate_topsis_data(num_alternatives=5, num_criteria=4, num_dms=10):
    """
    STEP 1: Generate the NORMAL (clean) dataset.
    All 10 DMs rate honestly based on true underlying values.
    """
    # Fixed true hypothetical quality of each alternative per criterion
    true_values = {}
    for i in range(1, num_alternatives + 1):
        true_values[f"A{i}"] = {
            f"C{j}": random.uniform(3, 8) for j in range(1, num_criteria + 1)
        }

    alts = [f"A{i}" for i in range(1, num_alternatives + 1)]
    crits = [f"C{j}" for j in range(1, num_criteria + 1)]
    dms = [f"DM{k}" for k in range(1, num_dms + 1)]

    # Fixed criteria weights (same for both datasets)
    criteria_weights = {
        c: [random.randint(4, 6), random.randint(6, 8), random.randint(8, 9)]
        for c in crits
    }

    # Generate honest ratings for ALL 10 DMs
    ratings = {}
    for dm in dms:
        dm_ratings = {}
        for alt in alts:
            alt_ratings = {}
            for crit in crits:
                base_val = true_values[alt][crit]
                alt_ratings[crit] = generate_fuzzy_rating(base_val, noise_level=1.5)
            dm_ratings[alt] = alt_ratings
        ratings[dm] = dm_ratings

    data = {
        "alternatives": alts,
        "criteria": crits,
        "decision_makers": dms,
        "criteria_weights": criteria_weights,
        "ratings": ratings
    }

    return data, true_values


def inject_bias(normal_data, biased_dms=None):
    """
    STEP 2: Create BIASED dataset by deep-copying the normal dataset,
    then REPLACING the ratings of the specified DMs with colluding values.
    
    Biased DMs will:
      - Give A1 the maximum possible rating [7, 9, 9]
      - Give all other alternatives the minimum [1, 1, 3]
    
    This simulates a coordinated poisoning attack.
    """
    import copy
    biased_data = copy.deepcopy(normal_data)

    if biased_dms is None:
        biased_dms = ["DM8", "DM9", "DM10"]  # 3 out of 10 = 30% collusion

    for dm in biased_dms:
        for alt in biased_data["alternatives"]:
            for crit in biased_data["criteria"]:
                if alt == "A1":
                    biased_data["ratings"][dm][alt][crit] = [7, 9, 9]  # Max
                else:
                    biased_data["ratings"][dm][alt][crit] = [1, 1, 3]  # Min

    return biased_data


def main():
    # Generate the ONE true normal dataset
    normal_data, true_values = generate_topsis_data()

    # Create biased version by injecting bias INTO a copy of the normal data
    biased_data = inject_bias(normal_data)

    out_dir = "/Users/fahimafridi/Downloads/Folders10000/Research/thesis-topsis"
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "topsis_normal_data.json"), "w") as f:
        json.dump(normal_data, f, indent=4)

    with open(os.path.join(out_dir, "topsis_biased_data.json"), "w") as f:
        json.dump(biased_data, f, indent=4)

    # Verify: DM1-DM7 ratings should be IDENTICAL in both files
    for dm in ["DM1", "DM2", "DM3", "DM4", "DM5", "DM6", "DM7"]:
        assert normal_data["ratings"][dm] == biased_data["ratings"][dm], \
            f"ERROR: {dm} ratings differ between normal and biased!"

    # Verify: DM8-DM10 ratings should DIFFER
    for dm in ["DM8", "DM9", "DM10"]:
        assert normal_data["ratings"][dm] != biased_data["ratings"][dm], \
            f"ERROR: {dm} ratings should differ but don't!"

    print("✅ Datasets generated and verified successfully.")
    print("   - topsis_normal_data.json (all 10 DMs honest)")
    print("   - topsis_biased_data.json (DM8-10 colluding for A1)")
    print(f"   - DM1-DM7 ratings: IDENTICAL in both files")
    print(f"   - DM8-DM10 ratings: BIASED in second file")
    print(f"   - Criteria weights: IDENTICAL in both files")


if __name__ == "__main__":
    main()
