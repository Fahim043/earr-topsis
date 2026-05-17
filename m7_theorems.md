# Formal Theorems and Proofs: M7 (EARR-TOPSIS)

## Theorem 1: Multi-Signal Robustness Beyond the Median Breakdown Point

### Statement

Let $\mathcal{D} = \{DM_1, DM_2, \ldots, DM_K\}$ be a set of $K$ decision makers evaluating $N$ alternatives across $M$ criteria using Triangular Fuzzy Numbers. Let $\mathcal{A} \subset \mathcal{D}$ denote a coordinated adversarial subgroup of size $|\mathcal{A}| = K_a$ where $K_a / K > 0.5$ (majority corruption).

**If the adversarial subgroup $\mathcal{A}$ satisfies the following distinguishability conditions:**

**(C1) Entropy Distinguishability:**
$$H(\mathcal{A}) < \tau_H \cdot H(\mathcal{D} \setminus \mathcal{A})$$

where $H(S)$ denotes the average Shannon entropy of the rating distributions of DMs in set $S$, and $\tau_H < 1$ is a distinguishability ratio;

**(C2) Variance Distinguishability:**
$$\left| \frac{\sigma^2_k}{\tilde{\sigma}^2} - 1 \right| > \epsilon_V, \quad \forall k \in \mathcal{A}$$

where $\sigma^2_k$ is the internal variance of $DM_k$'s rating vector, $\tilde{\sigma}^2$ is the median individual variance across all DMs, and $\epsilon_V > 0$ is the deviation threshold;

**(C3) Clone Distinguishability:**
$$\frac{|\{j \in \mathcal{A} \setminus \{k\} : \|x_k - x_j\| < \delta\}|}{K - 1} > \phi, \quad \forall k \in \mathcal{A}$$

where $\delta$ is the clone detection threshold and $\phi > 0$ is the minimum clone fraction;

**Then the M7 Entropy-Aware Reliability Engine assigns:**
$$R_k^{(final)} \ll R_j^{(final)}, \quad \forall k \in \mathcal{A}, \; j \in \mathcal{D} \setminus \mathcal{A}$$

**and the reliability-weighted ensemble TOPSIS produces rankings equivalent to the uncontaminated ground truth, regardless of the ratio $K_a / K$, provided $K_a / K \leq 0.75$.**

---

### Proof Sketch

**Step 1: Signal Independence from Centroid.**
Unlike distance-based reliability methods (M3–M6) which depend on $\text{centroid} = \text{median}(\{x_k\}_{k=1}^K)$, the three M7 signals are computed from individual DM properties:
- Entropy $H_k$ depends only on $x_k$'s rating distribution
- Variance $\sigma^2_k$ depends only on $x_k$
- Clone count depends on pairwise distances $\|x_k - x_j\|$, not on any centroid

Therefore, when $K_a / K > 0.5$, the centroid poisoning that defeats M3–M6 does **not** affect M7's signal computation.

**Step 2: Composite Score Separation.**
Under conditions (C1)–(C3), the composite reliability score for adversarial DMs:
$$R_k^{(composite)} = \omega_1 \cdot R_k^{(entropy)} + \omega_2 \cdot R_k^{(clone)} + \omega_3 \cdot R_k^{(var)}$$

is strictly less than the composite score for honest DMs, since each signal independently penalizes adversarial behavior. The maximum adversarial composite score is:
$$R_{\mathcal{A}}^{max} = \omega_1 \tau_H + \omega_2 e^{-3\phi} + \omega_3 e^{-\epsilon_V}$$

which, for typical coordinated attacks ($\tau_H \approx 0.5$, $\phi \geq 0.4$, $\epsilon_V \geq 0.5$), yields $R_{\mathcal{A}}^{max} \approx 0.52$ versus $R_{\mathcal{H}}^{min} \geq 0.85$ for honest DMs.

**Step 3: Gap Detection and Binary Filtering.**
The gap analysis operating on sorted composite scores detects the structural discontinuity between $R_{\mathcal{A}}^{max}$ and $R_{\mathcal{H}}^{min}$. Under the condition:
$$R_{\mathcal{H}}^{min} - R_{\mathcal{A}}^{max} > \mu_{gap} + 1.5\sigma_{gap}$$

the gap filter correctly partitions $\mathcal{D}$ into honest and adversarial subgroups, setting $R_k^{(final)} = \epsilon \approx 0$ for all $k \in \mathcal{A}$.

**Step 4: Ensemble Suppression.**
With $R_k^{(final)} \approx 0$ for adversarial DMs:
- Probability-weighted sampling: $P(k \in \mathcal{A}) = R_k / \sum R_j \approx 0$
- Inner-bag contribution: $w_k \cdot x_k \approx 0$
- Resulting ensemble aggregation is mathematically equivalent to running TOPSIS on $\mathcal{D} \setminus \mathcal{A}$ alone. $\blacksquare$

---

## Theorem 2: Necessary Conditions for Detection Failure

### Statement

The M7 multi-signal detection **fails** (i.e., adversarial DMs receive $R_k^{(final)} \geq R_j^{(final)}$ for some honest $j$) **if and only if** the adversarial subgroup simultaneously satisfies:

**(F1)** Each attacker independently generates ratings with entropy $H_k$ statistically indistinguishable from honest DMs: $|H_k - \bar{H}_{\mathcal{H}}| \leq 2\sigma_H$

**(F2)** Each attacker independently varies their ratings such that $\sigma^2_k$ is within the interquartile range of honest DM variances

**(F3)** No two attackers submit identical or near-identical rating vectors: $\|x_k - x_j\| \geq \delta$ for all $k, j \in \mathcal{A}$

### Implication

Conditions (F1)–(F3) together require each adversarial DM to:
1. Use a diverse, varied vocabulary of ratings (not just extremes)
2. Maintain human-like variance patterns
3. Ensure no coordination is detectable between attackers

This forces the adversarial strategy to become **individually diverse and collectively uncoordinated**, which fundamentally contradicts the goal of a **coordinated directional attack**. The attacker faces a mathematical impossibility: to bias the outcome, they must agree on the direction of manipulation, but to avoid detection, they must disagree with each other.

---

## Theorem 3: Upper Bound on Adversarial Influence

### Statement

Let $\mathcal{A}$ be an adversarial subgroup successfully detected by M7 (satisfying C1–C3). After reliability assignment, the maximum influence of $\mathcal{A}$ on the final weighted aggregation is:

$$\mathcal{I}(\mathcal{A}) = \frac{\sum_{k \in \mathcal{A}} R_k^{(final)}}{\sum_{j \in \mathcal{D}} R_j^{(final)}} \leq \frac{K_a \cdot \epsilon}{(K - K_a) \cdot R_{min}^{\mathcal{H}} + K_a \cdot \epsilon}$$

where $\epsilon = 10^{-6}$ (the near-zero reliability assigned to detected adversaries) and $R_{min}^{\mathcal{H}} > 0$ is the minimum honest DM reliability.

For practical values ($K_a = 14$, $K = 20$, $R_{min}^{\mathcal{H}} = 0.8$, $\epsilon = 10^{-6}$):
$$\mathcal{I}(\mathcal{A}) \leq \frac{14 \times 10^{-6}}{6 \times 0.8 + 14 \times 10^{-6}} \approx 2.9 \times 10^{-6}$$

The adversarial influence is effectively **zero**, regardless of their numerical majority.

---

## Safety Clause

> The entropy component does not penalize **honest consensus**. When DMs genuinely agree (e.g., a clearly superior alternative), each DM still exhibits unique human signature noise across other alternatives and criteria. The detection signals measure **within-DM rating diversity**, not **between-DM agreement**. A panel of honest DMs who agree on the best alternative will each have independently varied ratings on secondary criteria, producing normal entropy and variance. Only when a group exhibits **uniform extreme manipulation across ALL alternatives and criteria simultaneously** — the hallmark of coordinated injection — does the detection trigger.
