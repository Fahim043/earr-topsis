# EARR-TOPSIS Study Guide

Date: 2026-05-16

This is the plain-English guide to what you built, why each method exists, what equations matter, what tests were run, and what results you got. Read this before writing, presenting, or defending the thesis.

## 1. One-Sentence Summary

You built a reliability-aware fuzzy TOPSIS framework that protects group decision-making from structured biased decision makers. The final method is called EARR-TOPSIS: Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS.

## 2. The Core Problem

Classical fuzzy TOPSIS assumes that decision makers are honest. In real group decision-making, some decision makers may be biased or coordinated. If several decision makers intentionally give very high scores to one weak target alternative and very low scores to the other alternatives, normal fuzzy TOPSIS can be manipulated.

Your research asks:

> Can fuzzy TOPSIS be made robust when some decision makers provide coordinated biased ratings?

The answer from your experiments:

> Yes, when the biased decision makers leave statistically distinguishable patterns. M4 and M6 work well up to 40% structured contamination, and M7/EARR-TOPSIS works across all tested structured attack levels up to 60%.

## 3. Important Claim Boundary

You should never claim:

> EARR-TOPSIS detects all human bias.

You should claim:

> EARR-TOPSIS is robust against structured, statistically distinguishable coordinated manipulation in fuzzy TOPSIS group decision-making.

The limitation:

> If malicious decision makers deliberately mimic honest human variation, no unsupervised reliability method can guarantee detection without extra information.

## 4. Basic Fuzzy TOPSIS Concepts

### 4.1 Alternatives, Criteria, and Decision Makers

Let:

- \(A_i\): alternative \(i\)
- \(C_j\): criterion \(j\)
- \(D_k\): decision maker \(k\)
- \(n\): number of alternatives
- \(m\): number of criteria
- \(K\): number of decision makers

Each rating is a triangular fuzzy number:

\[
\tilde{x}_{ijk} = (l_{ijk}, m_{ijk}, u_{ijk})
\]

Meaning:

- \(l\): lower possible value
- \(m\): most likely value
- \(u\): upper possible value

Example:

\[
(5,7,8)
\]

means the score is roughly between 5 and 8, with 7 most representative.

### 4.2 Fuzzy Criterion Weights

Each criterion also has a fuzzy weight:

\[
\tilde{w}_j = (l_j^w, m_j^w, u_j^w)
\]

In many tests, weights are simple, such as \((1,1,1)\), unless the dataset gives a more specific weight.

### 4.3 Vertex Distance Between Fuzzy Numbers

To compare two triangular fuzzy numbers:

\[
d(\tilde{a}, \tilde{b}) =
\sqrt{
\frac{(a_l-b_l)^2+(a_m-b_m)^2+(a_u-b_u)^2}{3}
}
\]

This is just Euclidean distance averaged across the three fuzzy components.

### 4.4 TOPSIS Closeness Coefficient

After normalization and weighting, TOPSIS computes:

- distance to positive ideal: \(D_i^+\)
- distance to negative ideal: \(D_i^-\)

The closeness coefficient is:

\[
CC_i = \frac{D_i^-}{D_i^+ + D_i^-}
\]

Higher \(CC_i\) means better rank.

## 5. Your Seven Methods

You built seven methods, M1 to M7. They are not all equal final contributions. The final proposed methods are M4, M6, and M7.

## 6. M1: Classical Fuzzy TOPSIS

### Purpose

M1 is the baseline. It answers:

> What happens if we use normal fuzzy TOPSIS with all decision makers?

### Aggregation

For each alternative and criterion, M1 aggregates all decision makers:

\[
\tilde{x}_{ij} =
\left(
\min_k l_{ijk},
\frac{1}{K}\sum_{k=1}^{K} m_{ijk},
\max_k u_{ijk}
\right)
\]

This uses:

- minimum lower bound
- average middle value
- maximum upper bound

### Benefit Criteria Normalization

For benefit criteria, larger is better:

\[
\tilde{r}_{ij} =
\left(
\frac{l_{ij}}{u_j^+},
\frac{m_{ij}}{u_j^+},
\frac{u_{ij}}{u_j^+}
\right),
\quad
u_j^+ = \max_i u_{ij}
\]

### Cost Criteria Normalization

For cost criteria, smaller is better:

\[
\tilde{r}_{ij} =
\left(
\frac{l_j^-}{u_{ij}},
\frac{l_j^-}{m_{ij}},
\frac{l_j^-}{l_{ij}}
\right),
\quad
l_j^- = \min_i l_{ij}
\]

### Why M1 Fails

If biased decision makers give:

```text
Target A1: high score, e.g. (7,9,9)
Other alternatives: low score, e.g. (1,1,3)
```

then M1 directly includes those ratings in the final matrix. It has no defense.

### Code File

```text
m1_normal_topsis.py
```

## 7. M2: Bootstrap Bagged Fuzzy TOPSIS

### Purpose

M2 asks:

> Does Random-Forest-style bagging alone make fuzzy TOPSIS robust?

### Bootstrap Sampling

For each bag:

\[
S_b = \{D_{b1}, D_{b2}, ..., D_{bK}\}, \quad D_{bt} \sim Uniform(D_1, ..., D_K)
\]

Sampling is with replacement.

### Bag Aggregation

Inside each bag, ratings are averaged:

\[
\tilde{x}_{ij}^{(b)} =
\left(
\frac{1}{|S_b|}\sum_{D_k \in S_b} l_{ijk},
\frac{1}{|S_b|}\sum_{D_k \in S_b} m_{ijk},
\frac{1}{|S_b|}\sum_{D_k \in S_b} u_{ijk}
\right)
\]

### Final Ranking

Each bag gives a ranking. Rankings are combined using Borda voting:

\[
Borda_i = \sum_{b=1}^{B} (n - rank_i^{(b)})
\]

### What Was Fixed

Originally, M2 claimed bootstrap bagging but actually partitioned decision makers without replacement and hardcoded subset count. That was wrong. It was fixed to:

- sample with replacement
- respect `num_bags`
- respect `bag_size`
- use deterministic seeds

### Result

M2 improves over M1 but does not stop coordinated attacks. It is a corrected baseline, not a final proposed method.

### Code File

```text
m2_bagged_topsis.py
```

## 8. M3: Reliability Filtering

### Purpose

M3 asks:

> Can we detect suspicious decision makers and remove them?

### Flatten Decision Maker Ratings

Each decision maker's full rating tensor is converted into a vector:

\[
\mathbf{x}_k \in \mathbb{R}^{3nm}
\]

Example: all ratings of DM1 are flattened into one long row of numbers.

### Median Consensus Center

\[
\mathbf{c} = median(\mathbf{x}_1, ..., \mathbf{x}_K)
\]

### Distance from Consensus

\[
d_k = ||\mathbf{x}_k - \mathbf{c}||_2
\]

### Reliability

\[
R_k = 1 - \frac{d_k}{\max_s d_s}
\]

If a decision maker is far from the consensus center, reliability is low.

### What It Does

M3 removes suspicious decision makers and then runs fuzzy TOPSIS.

### Strength

Strong when attackers are a distinguishable minority.

### Weakness

If attackers become majority, they can shift the consensus center.

### Code File

```text
m3_ml_filtered.py
```

## 9. M4: Reliability-Weighted Bagging

### Purpose

M4 is Proposed Method 1.

It asks:

> What if reliable decision makers are sampled more often in bagging?

### Sampling Probability

\[
P(D_k) = \frac{R_k}{\sum_{s=1}^{K} R_s}
\]

Reliable decision makers are more likely to be selected into bags.

### Pipeline

1. Compute reliability \(R_k\)
2. Convert reliability into sampling probabilities
3. Bootstrap sample decision makers with replacement
4. Run fuzzy TOPSIS in each bag
5. Average bag closeness coefficients
6. Produce final ranking

### Why It Matters

M4 is the first strong robust method. It keeps the ensemble idea but makes it reliability-aware.

### Result

M4 blocks structured attacks through 40% effective contamination in the three larger datasets.

### Weakness

At majority contamination, reliability scores based on consensus can be hijacked.

### Code File

```text
m4_weighted_bagging.py
```

## 10. M5: Cluster-Stratified Bagging

### Purpose

M5 asks:

> Can clustering decision makers help detect coordinated attacker groups?

### Idea

Each decision maker is flattened:

\[
\mathbf{x}_k \rightarrow cluster(D_k)
\]

Then the method tries to sample from reliable clusters and reduce influence from unreliable clusters.

### Why It Is Interesting

If attackers behave similarly, they may form a separate cluster.

### Result

M5 is inconsistent:

- sometimes helps
- sometimes behaves like M2
- sometimes fails badly

### Final Role

M5 is not a final proposed method. It is an ablation or explored design branch.

### Code File

```text
m5_cluster_stratified.py
```

## 11. M6: Reliability-Weighted Aggregation

### Purpose

M6 is Proposed Method 2.

It asks:

> What if reliability is used directly inside fuzzy aggregation?

### Weighted Fuzzy Aggregation

\[
\tilde{x}_{ij}^{(R)} =
\left(
\frac{\sum_k R_k l_{ijk}}{\sum_k R_k},
\frac{\sum_k R_k m_{ijk}}{\sum_k R_k},
\frac{\sum_k R_k u_{ijk}}{\sum_k R_k}
\right)
\]

### Why It Is Strong

Even if a biased decision maker appears in a bag, their rating contributes little if \(R_k\) is low.

### Pipeline

1. Compute reliability
2. Sample bags uniformly
3. Inside each bag, aggregate ratings using reliability weights
4. Run fuzzy TOPSIS
5. Weight bags by average reliability
6. Produce final ranking

### Result

M6 also blocks structured attacks through 40% effective contamination.

### Weakness

If reliability scores are wrong, aggregation can still be misled.

### Code File

```text
m6_reliability_weighted.py
```

## 12. M7: EARR-TOPSIS

### Full Name

Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS.

### Purpose

M7 is Proposed Method 3 and your final method.

It asks:

> Can multi-signal reliability detect structured attackers better than only distance-to-consensus?

M7 is designed because M3/M4/M6 can fail when attackers become majority and shift the consensus center.

## 13. M7 Reliability Signals

### 13.1 Entropy Signal

For each decision maker, compute a histogram distribution \(p_{kh}\). Shannon entropy:

\[
H_k = -\sum_h p_{kh}\log(p_{kh})
\]

Low entropy means the decision maker repeats the same ratings too often.

Attack example:

```text
A1: (7,9,9)
All others: (1,1,3)
```

This is repetitive and suspicious.

### 13.2 Variance-Consistency Signal

Let:

\[
\sigma_k^2 = Var(\mathbf{x}_k)
\]

and:

\[
\tilde{\sigma}^2 = median(\sigma_1^2, ..., \sigma_K^2)
\]

Then:

\[
R_k^{(V)} =
\exp\left(
-\left|\frac{\sigma_k^2}{\tilde{\sigma}^2}-1\right|
\right)
\]

If a decision maker's rating spread is too unusual, reliability decreases.

### 13.3 Clone/Agreement Signal

If many decision makers are nearly identical, that can indicate coordination.

\[
R_k^{(C)} = \exp(-3 \cdot clone\_fraction_k)
\]

More clone-like behavior means lower reliability.

### 13.4 Composite Reliability

\[
R_k =
0.35R_k^{(H)}
+0.35R_k^{(V)}
+0.30R_k^{(C)}
\]

This combines entropy, variance, and clone/agreement signals.

## 14. M7 Final Ensemble

### Step 1: Reliability-Weighted Sampling

\[
P(D_k) = \frac{R_k}{\sum_s R_s}
\]

### Step 2: Reliability-Weighted Aggregation Inside Bags

\[
\tilde{x}_{ij}^{(b,R)} =
\frac{\sum_{D_k \in S_b} R_k \tilde{x}_{ijk}}
{\sum_{D_k \in S_b} R_k}
\]

### Step 3: Bag Quality Weighting

Each bag has average reliability \(q_b\). Bags are weighted by softmax:

\[
W_b = \frac{\exp(q_b/T)}{\sum_{s=1}^{B}\exp(q_s/T)}
\]

### Step 4: Final Closeness

\[
CC_i^{final} = \sum_{b=1}^{B} W_b CC_i^{(b)}
\]

### Result

M7 blocks all 18 structured attack-fraction scenarios.

### Weakness

Adaptive human-mimic attackers remain a limitation.

### Code File

```text
m7_entropy_reliability.py
```

## 15. Final Proposed Methods

Your final proposed methods are:

| Role | Method | Meaning |
|---|---|---|
| Proposed Method 1 | M4 | Reliability-weighted bagging |
| Proposed Method 2 | M6 | Reliability-weighted aggregation |
| Proposed Method 3 | M7 / EARR-TOPSIS | Entropy-aware reliability-weighted ensemble |

Not proposed as final:

| Method | Role |
|---|---|
| M1 | Classical baseline |
| M2 | Corrected bootstrap baseline |
| M3 | Reliability-filtering intermediate comparator |
| M5 | Cluster-stratified ablation branch |

## 16. Tests We Ran

## 16.1 Code Correctness Fixes

We fixed and checked:

1. M2 true bootstrap with replacement
2. deterministic seeds
3. mixed benefit/cost criteria handling
4. M5 small bag-size guard
5. M7 entropy probability calculation
6. final evidence compiler

## 16.2 Hand-Computed Fuzzy TOPSIS Example

A small fuzzy TOPSIS example was computed manually.

Expected:

\[
CC(A_1)=0.52941176
\]

\[
CC(A_2)=0.47058824
\]

The code matched this.

Purpose:

> Proves the basic fuzzy TOPSIS core is mathematically consistent on a small case.

## 16.3 Synthetic Repeated Evaluation

We tested synthetic datasets with different:

- number of decision makers
- number of alternatives
- attack fractions
- bias structures

Finding:

- M1 and M2 fail often.
- M3/M4/M6 improve when attackers are distinguishable.
- M5 is inconsistent.
- exact 50% or majority cases are difficult for earlier methods.

## 16.4 Real/Pseudo-Real Benchmark

Main datasets:

| Dataset | Alternatives | Criteria | DMs |
|---|---:|---:|---:|
| healthcare_countries_2021 | 26 | 13 | 15 |
| car_evaluation | 300 | 6 | 15 |
| healthcare_resource_allocation | 300 | 18 | 15 |

Target = clean lowest-ranked alternative.

Contamination = structured target-promotion attack.

### Focused Result

| Dataset | Clean Target Rank | M1 | M2 | M3 | M4 | M5 | M6 | M7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| healthcare_countries_2021 | 26 | 1 | 7 | 26 | 26 | 5 | 26 | 26 |
| car_evaluation | 300 | 24 | 180 | 300 | 300 | 192 | 300 | 300 |
| healthcare_resource_allocation | 300 | 1 | 52 | 300 | 300 | 16 | 300 | 300 |

Interpretation:

- M1 collapses.
- M2 improves but does not fully block.
- M4/M6/M7 block.
- M5 is unstable.

## 16.5 Attack-Fraction Curves

We tested:

```text
10%, 20%, 30%, 40%, 50%, 60%
```

Across the three main datasets.

Main finding:

- M4 and M6 work through 40%.
- M7 works through all tested fractions, including 53.3% and 60% effective contamination.

## 16.6 External Baseline Tests

External comparators:

| Baseline | Meaning |
|---|---|
| EB1 | Median TOPSIS |
| EB2 | Trimmed-Mean TOPSIS |
| EB3 | MAD-Consensus TOPSIS |
| EB4 | Individual-Borda TOPSIS |
| EB5 | Huang-Li Group-Ideal TOPSIS adaptation |

### Summary

| Method | Cases | Blocked | Blocked Rate | Mean Target Error |
|---|---:|---:|---:|---:|
| EB1 Median TOPSIS | 18 | 8 | 0.444 | 71.11 |
| EB2 Trimmed-Mean TOPSIS | 18 | 6 | 0.333 | 106.44 |
| EB3 MAD-Consensus TOPSIS | 18 | 12 | 0.667 | 69.22 |
| EB4 Individual-Borda TOPSIS | 18 | 0 | 0.000 | 66.94 |
| EB5 Huang-Li Group-Ideal TOPSIS | 18 | 0 | 0.000 | 188.22 |
| M4 | 18 | 12 | 0.667 | 69.22 |
| M6 | 18 | 12 | 0.667 | 69.22 |
| M7 | 18 | 18 | 1.000 | 0.00 |

Interpretation:

- external baselines help at low/moderate contamination
- they collapse at high contamination
- M7 is strongest under structured attacks

## 16.7 Statistical Tests

Pairwise target-error tests:

| Comparison | M7 Better | M7 Worse | Ties | Sign p | Wilcoxon p |
|---|---:|---:|---:|---:|---:|
| M7 vs M1 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7 vs M2 | 18 | 0 | 0 | 0.000008 | 0.000214 |
| M7 vs M4 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7 vs M6 | 6 | 0 | 12 | 0.031250 | 0.036032 |
| M7 vs EB5 Huang-Li | 18 | 0 | 0 | 0.000008 | 0.000214 |

Meaning:

- M7 is always better than M1/M2/EB5 in tested scenarios.
- M7 ties M4/M6 in low-to-40% cases.
- M7 beats M4/M6 in majority/high-contamination cases.

## 16.8 Runtime Tests

Runtime at 30% contamination and 200 bags:

| Dataset | M1 sec | M2 sec | M4 sec | M6 sec | M7 sec |
|---|---:|---:|---:|---:|---:|
| healthcare_countries_2021 | 0.004 | 0.380 | 0.387 | 0.291 | 0.315 |
| car_evaluation | 0.028 | 2.196 | 2.226 | 1.728 | 1.818 |
| healthcare_resource_allocation | 0.077 | 6.809 | 6.863 | 5.468 | 5.731 |

Meaning:

- M7 is slower than classical TOPSIS.
- But M7 is practical for offline decision support.
- M7 is comparable to other ensemble methods.

## 17. What You Built in Code

| File | Purpose |
|---|---|
| `m1_normal_topsis.py` | classical fuzzy TOPSIS |
| `m2_bagged_topsis.py` | corrected bootstrap bagged TOPSIS |
| `m3_ml_filtered.py` | reliability filtering |
| `m4_weighted_bagging.py` | proposed M4 |
| `m5_cluster_stratified.py` | cluster ablation |
| `m6_reliability_weighted.py` | proposed M6 |
| `m7_entropy_reliability.py` | final EARR-TOPSIS |
| `run_real_dataset_benchmarks.py` | real/pseudo-real benchmark runner |
| `run_attack_fraction_curves.py` | attack-fraction experiments |
| `run_external_baselines.py` | external comparator tests |
| `analyze_statistics.py` | CI and paired tests |
| `compile_final_evidence.py` | final tables |
| `web_api/app.py` | API for uploading datasets and running M4/M6/M7 |

## 18. The Story You Tell in Defense

Say this:

> My work starts with classical fuzzy TOPSIS and shows that it is vulnerable to coordinated biased decision makers. I then tested whether bootstrap bagging alone can help. It helps slightly but does not solve the problem. Therefore, I introduced reliability-aware methods. M4 uses reliability during bag sampling, M6 uses reliability inside fuzzy aggregation, and M7 combines entropy, variance consistency, and clone/agreement signals with reliability-weighted ensemble aggregation. The experiments show that M4 and M6 are strong up to 40% structured contamination, while M7 blocks all tested structured contamination levels up to 60%. The method is not claimed to defeat all human bias; it is robust under structured, statistically distinguishable coordinated attacks.

## 19. Simple Analogy

Imagine a committee voting on suppliers.

- M1 trusts everyone equally.
- M2 makes many random subcommittees but still trusts everyone.
- M3 removes suspicious committee members.
- M4 invites reliable members more often into subcommittees.
- M5 groups similar members and tries to avoid suspicious groups.
- M6 lets everyone speak, but gives reliable members louder voices.
- M7 checks if members sound suspiciously repetitive, clone-like, or statistically unnatural, then builds reliable subcommittees and gives reliable subcommittees more weight.

## 20. Questions You May Be Asked

### Q1: Why not propose M2?

Because M2 is only bagging. It does not detect reliability. It improves over M1 but still fails to block attacks.

### Q2: Why not propose M5?

Because M5 is inconsistent. Clustering is useful but unstable across datasets.

### Q3: Why propose M4?

Because it is the first strong reliability-aware ensemble method and works through 40% contamination.

### Q4: Why propose M6?

Because it directly reduces biased decision-maker influence during fuzzy aggregation.

### Q5: Why is M7 strongest?

Because it uses multiple reliability signals and works even when M3/M4/M6 collapse under majority structured attacks.

### Q6: Does M7 detect all bias?

No. It detects structured, distinguishable biased behavior. Adaptive human-mimic attacks remain a limitation.

### Q7: What is the novelty?

The novelty is combining reliability-aware fuzzy TOPSIS with structured adversarial evaluation, multi-signal reliability, entropy/clone detection, weighted sampling, weighted aggregation, and bag-quality weighting.

### Q8: What metric matters most?

Target-rank error. Spearman and Kendall can stay high even when the target alternative is successfully promoted.

## 21. Final Thesis Claim

Use this:

> EARR-TOPSIS improves fuzzy TOPSIS group decision robustness against structured coordinated decision-maker contamination by combining entropy-aware reliability estimation, reliability-weighted sampling, reliability-weighted aggregation, and bag-quality weighting. Experiments show that it preserves the clean target rank across all tested structured attack-fraction scenarios, outperforming standard fuzzy TOPSIS, corrected bootstrap bagging, robust aggregation baselines, consensus filtering, and group-ideal TOPSIS aggregation under the tested threat model.

## 22. What To Memorize

Memorize these five points:

1. M1 fails because it trusts all DMs equally.
2. M2 is corrected bootstrap bagging, but bagging alone is not enough.
3. M4 samples reliable DMs more often.
4. M6 weights DM ratings directly by reliability.
5. M7 uses entropy, variance, and clone signals and is strongest under structured attacks.

That is the heart of the whole thesis.
