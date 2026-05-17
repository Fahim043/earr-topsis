import math

def distance(x, y):
    return math.sqrt((1/3) * ((x[0]-y[0])**2 + (x[1]-y[1])**2 + (x[2]-y[2])**2))

print("Scenario: A disjoint subset of 4 DMs (3 Normal, 1 Attacker)")
print("Alternatives: A1 (Target), A4 (True Best)")

norm1_A4, norm2_A4, norm3_A4 = (7, 8, 9), (6, 8, 9), (7, 9, 9)
atk_A4   = (1, 1, 3) 

norm1_A1, norm2_A1, norm3_A1 = (3, 5, 7), (2, 4, 6), (3, 5, 7)
atk_A1   = (7, 9, 9)

def standard_agg(t1, t2, t3, t4):
    """Standard Fuzzy TOPSIS Aggregation (Min, Mean, Max)"""
    return (
        min(t1[0], t2[0], t3[0], t4[0]),
        (t1[1]+t2[1]+t3[1]+t4[1])/4,
        max(t1[2], t2[2], t3[2], t4[2])
    )

agg_A4 = standard_agg(norm1_A4, norm2_A4, norm3_A4, atk_A4)
agg_A1 = standard_agg(norm1_A1, norm2_A1, norm3_A1, atk_A1)

print(f"[{'A4 (True Best)':<16}]")
print(f"  Normal DMs: {norm1_A4}, {norm2_A4}, {norm3_A4}")
print(f"  Attacker:   {atk_A4}")
print(f"  => STANDARD SUBSET AGGREGATION: {agg_A4}\n")

print(f"[{'A1 (Target)':<16}]")
print(f"  Normal DMs: {norm1_A1}, {norm2_A1}, {norm3_A1}")
print(f"  Attacker:   {atk_A1}")
print(f"  => STANDARD SUBSET AGGREGATION: {agg_A1}\n")

max_val = max(agg_A4[2], agg_A1[2]) # 9.0
norm_A4 = (agg_A4[0]/max_val, agg_A4[1]/max_val, agg_A4[2]/max_val)
norm_A1 = (agg_A1[0]/max_val, agg_A1[1]/max_val, agg_A1[2]/max_val)

fpis, fnis = (1.0, 1.0, 1.0), (0.0, 0.0, 0.0)

d_star_A4 = distance(norm_A4, fpis)
d_min_A4  = distance(norm_A4, fnis)
cc_A4 = d_min_A4 / (d_star_A4 + d_min_A4)

d_star_A1 = distance(norm_A1, fpis)
d_min_A1  = distance(norm_A1, fnis)
cc_A1 = d_min_A1 / (d_star_A1 + d_min_A1)

print("="*60)
print("FUZZY TOPSIS CLOSENESS COEFFICIENTS (CC)")
print("="*60)
print(f"CC for A4 (True Best): {cc_A4:.4f}")
print(f"CC for A1 (Target):    {cc_A1:.4f}")
print(f"\nWINNER OF THIS SUBSET: {'A1' if cc_A1 > cc_A4 else 'A4'}!")
