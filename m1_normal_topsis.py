import json
import math
import pprint

# M1: Normal Fuzzy TOPSIS (Manual Implementation)

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def aggregate_ratings(data):
    """Standard Fuzzy TOPSIS aggregation: min(l), mean(m), max(u)
    This is the textbook formula. Used ONLY by M1 baseline."""
    alts = data["alternatives"]
    crits = data["criteria"]
    dms = data["decision_makers"]
    ratings = data["ratings"]
    
    agg = {a: {c: [0,0,0] for c in crits} for a in alts}
    
    for a in alts:
        for c in crits:
            l_vals = [ratings[dm][a][c][0] for dm in dms]
            m_vals = [ratings[dm][a][c][1] for dm in dms]
            u_vals = [ratings[dm][a][c][2] for dm in dms]
            
            agg[a][c] = [
                min(l_vals),
                sum(m_vals)/len(dms),
                max(u_vals)
            ]
    return agg

def aggregate_ratings_mean(data):
    """Ensemble-robust aggregation: mean(l), mean(m), mean(u)
    
    Used by M2-M6 inside bags. In ensemble MCDM, each bag is a 
    sub-committee. Using mean for ALL three TFN components prevents
    a single extreme DM from poisoning the bag via min/max domination.
    
    Theoretical justification: In standard TOPSIS, min/max captures the
    full uncertainty envelope of the COMPLETE panel. But in a random
    sub-sample (bag), the envelope is artificially widened by outliers.
    Mean aggregation preserves the proportional influence of each DM,
    which is the correct behavior for ensemble sub-sampling."""
    alts = data["alternatives"]
    crits = data["criteria"]
    dms = data["decision_makers"]
    ratings = data["ratings"]
    K = len(dms)
    
    agg = {a: {c: [0,0,0] for c in crits} for a in alts}
    
    for a in alts:
        for c in crits:
            l_vals = [ratings[dm][a][c][0] for dm in dms]
            m_vals = [ratings[dm][a][c][1] for dm in dms]
            u_vals = [ratings[dm][a][c][2] for dm in dms]
            
            agg[a][c] = [
                sum(l_vals) / K,
                sum(m_vals) / K,
                sum(u_vals) / K
            ]
    return agg

def _criterion_is_cost(criterion_types, criterion):
    """Return True if a criterion is explicitly marked as cost-type.

    Supported schemas:
      {"C1": "benefit", "C2": "cost"}
      {"benefit": ["C1"], "cost": ["C2"]}

    If no schema is provided, all criteria are treated as benefit criteria,
    matching the original implementation.
    """
    if not criterion_types:
        return False
    if isinstance(criterion_types, dict):
        if criterion in criterion_types:
            return str(criterion_types[criterion]).lower() == "cost"
        return criterion in set(criterion_types.get("cost", []))
    return False


def normalize_matrix(agg_matrix, crits, alts, criterion_types=None):
    norm = {a: {c: [0,0,0] for c in crits} for a in alts}
    for c in crits:
        if _criterion_is_cost(criterion_types, c):
            l_min = min(agg_matrix[a][c][0] for a in alts)
            if l_min == 0:
                l_min = 1e-10
            for a in alts:
                l, m, u = agg_matrix[a][c]
                l = l if l != 0 else 1e-10
                m = m if m != 0 else 1e-10
                u = u if u != 0 else 1e-10
                norm[a][c] = [
                    l_min / u,
                    l_min / m,
                    l_min / l,
                ]
        else:
            u_max = max(agg_matrix[a][c][2] for a in alts)
            if u_max == 0:
                u_max = 1e-10  # Prevent division by zero
            for a in alts:
                norm[a][c] = [
                    agg_matrix[a][c][0] / u_max,
                    agg_matrix[a][c][1] / u_max,
                    agg_matrix[a][c][2] / u_max
                ]
    return norm

def apply_weights(norm_matrix, weights, crits, alts):
    weighted = {a: {c: [0,0,0] for c in crits} for a in alts}
    for a in alts:
        for c in crits:
            w = weights[c]
            r = norm_matrix[a][c]
            weighted[a][c] = [
                r[0] * w[0],
                r[1] * w[1],
                r[2] * w[2]
            ]
    return weighted

def calculate_distances(weighted_matrix, crits, alts):
    # FPIS (v*) and FNIS (v-)
    v_star = {c: [max(weighted_matrix[a][c][0] for a in alts),
                  max(weighted_matrix[a][c][1] for a in alts),
                  max(weighted_matrix[a][c][2] for a in alts)] for c in crits}
    
    v_min = {c: [min(weighted_matrix[a][c][0] for a in alts),
                 min(weighted_matrix[a][c][1] for a in alts),
                 min(weighted_matrix[a][c][2] for a in alts)] for c in crits}
                 
    d_star = {a: 0.0 for a in alts}
    d_min = {a: 0.0 for a in alts}
    
    for a in alts:
        for c in crits:
            v = weighted_matrix[a][c]
            vs = v_star[c]
            vm = v_min[c]
            
            # Vertex distance
            dist_star = math.sqrt((1/3) * ((v[0]-vs[0])**2 + (v[1]-vs[1])**2 + (v[2]-vs[2])**2))
            dist_min = math.sqrt((1/3) * ((v[0]-vm[0])**2 + (v[1]-vm[1])**2 + (v[2]-vm[2])**2))
            
            d_star[a] += dist_star
            d_min[a] += dist_min
            
    return d_star, d_min

def compute_cc(d_star, d_min, alts):
    cc = {}
    for a in alts:
        denom = d_star[a] + d_min[a]
        cc[a] = d_min[a] / denom if denom > 1e-10 else 0.0
    return cc

def run_m1(filepath):
    data = load_data(filepath)
    alts = data["alternatives"]
    crits = data["criteria"]
    weights = data["criteria_weights"]
    
    agg = aggregate_ratings(data)
    norm = normalize_matrix(agg, crits, alts, data.get("criteria_types"))
    weighted = apply_weights(norm, weights, crits, alts)
    d_star, d_min = calculate_distances(weighted, crits, alts)
    cc = compute_cc(d_star, d_min, alts)
    
    # Sort
    ranked = sorted(cc.items(), key=lambda x: x[1], reverse=True)
    return ranked

if __name__ == "__main__":
    print("-" * 50)
    print("M1: Normal Fuzzy TOPSIS")
    print("-" * 50)
    
    normal_res = run_m1("topsis_normal_data.json")
    print("\nResults on NORMAL dataset:")
    for rank, (alt, score) in enumerate(normal_res, 1):
        print(f"{rank}. {alt}: {score:.4f}")
        
    biased_res = run_m1("topsis_biased_data.json")
    print("\nResults on BIASED dataset:")
    for rank, (alt, score) in enumerate(biased_res, 1):
        print(f"{rank}. {alt}: {score:.4f}")
        
    # Note how A1 shoots to the top in the biased dataset due to the 3 colluding out of 10.
