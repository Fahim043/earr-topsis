# Hand-Computed Fuzzy TOPSIS Validation Example

This file gives a small manual check for the fuzzy TOPSIS equations used in `m1_normal_topsis.py`. It is intentionally tiny so the arithmetic can be verified by hand and used in the thesis or paper methodology appendix.

## Dataset

Two alternatives, two benefit criteria, two decision makers, and unit fuzzy weights:

| Alternative | Criterion | DM1 TFN | DM2 TFN |
|---|---|---:|---:|
| A1 | C1 | (4, 5, 6) | (5, 6, 7) |
| A1 | C2 | (6, 7, 8) | (5, 6, 7) |
| A2 | C1 | (7, 8, 9) | (6, 7, 8) |
| A2 | C2 | (3, 4, 5) | (4, 5, 6) |

Weights:

```text
w_C1 = (1, 1, 1)
w_C2 = (1, 1, 1)
```

## Step 1: Aggregate DM Ratings

M1 uses the classical fuzzy TOPSIS group aggregation:

\[
\tilde{x}_{ij} =
\left(
\min_k l_{ijk},
\frac{1}{K}\sum_k m_{ijk},
\max_k u_{ijk}
\right)
\]

Therefore:

| Alternative | C1 aggregate | C2 aggregate |
|---|---:|---:|
| A1 | (4, 5.5, 7) | (5, 6.5, 8) |
| A2 | (6, 7.5, 9) | (3, 4.5, 6) |

## Step 2: Normalize Benefit Criteria

For benefit criteria:

\[
\tilde{r}_{ij} =
\left(
\frac{l_{ij}}{u_j^+},
\frac{m_{ij}}{u_j^+},
\frac{u_{ij}}{u_j^+}
\right)
\]

where \(u_j^+ = \max_i u_{ij}\).

For C1, \(u_1^+ = 9\). For C2, \(u_2^+ = 8\).

| Alternative | C1 normalized | C2 normalized |
|---|---:|---:|
| A1 | (0.4444, 0.6111, 0.7778) | (0.6250, 0.8125, 1.0000) |
| A2 | (0.6667, 0.8333, 1.0000) | (0.3750, 0.5625, 0.7500) |

Because the weights are all \((1,1,1)\), the weighted normalized matrix is identical to the normalized matrix.

## Step 3: FPIS and FNIS

\[
A^+_j =
(\max_i v_{ij}^{l}, \max_i v_{ij}^{m}, \max_i v_{ij}^{u})
\]

\[
A^-_j =
(\min_i v_{ij}^{l}, \min_i v_{ij}^{m}, \min_i v_{ij}^{u})
\]

Thus:

| Criterion | FPIS | FNIS |
|---|---:|---:|
| C1 | (0.6667, 0.8333, 1.0000) | (0.4444, 0.6111, 0.7778) |
| C2 | (0.6250, 0.8125, 1.0000) | (0.3750, 0.5625, 0.7500) |

## Step 4: Vertex Distances

The vertex distance between two TFNs is:

\[
d(\tilde{a}, \tilde{b}) =
\sqrt{
\frac{1}{3}
\left[
(a_l-b_l)^2 + (a_m-b_m)^2 + (a_u-b_u)^2
\right]
}
\]

For A1:

```text
d(A1, FPIS) = 0.2222 + 0.0000 = 0.2222
d(A1, FNIS) = 0.0000 + 0.2500 = 0.2500
```

For A2:

```text
d(A2, FPIS) = 0.0000 + 0.2500 = 0.2500
d(A2, FNIS) = 0.2222 + 0.0000 = 0.2222
```

## Step 5: Closeness Coefficient

\[
CC_i =
\frac{D_i^-}{D_i^+ + D_i^-}
\]

So:

| Alternative | \(D^+\) | \(D^-\) | CC |
|---|---:|---:|---:|
| A1 | 0.2222 | 0.2500 | 0.5294 |
| A2 | 0.2500 | 0.2222 | 0.4706 |

Final ranking:

```text
A1 > A2
```

This agrees with the implementation: A1 is closer to the positive ideal because it dominates C2 enough to offset A2's advantage on C1.
