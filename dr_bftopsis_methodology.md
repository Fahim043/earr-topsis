# DR-BFTOPSIS: Methodological Architecture and Algorithms

This document formalizes the mathematics and architecture of the **Data-Driven, Reliability-Aware Decision-Maker Bagged Fuzzy TOPSIS (DR-BFTOPSIS)** framework. Here, we outline the exact operational process for all 6 algorithmic methods—from the baseline Fuzzy TOPSIS algorithm to the advanced Reliability-Aware Ensemble variants—proving theoretical capability up to hundreds of Decision Makers (DMs).

---

## 1. Universal Reliability Engine (The Core Innovation)
To eliminate hardcoded thresholds and parameters, the DR-BFTOPSIS model uses a data-driven **Universal Reliability Engine** that adapts to any dataset configuration automatically:

1. **Feature Extraction:** Flatten each DM's rating tensor into a 1-D feature vector.
2. **Median Centroid Consensus:** A median-based coordinate is computed to determine the abstract consensus point, making the engine theoretically robust up to 50% bias contamination.
3. **Continuous Reliability Score ($R_k$):** Based on Euclidean distance $d_k$ to the consensus centroid, normalized as $R_k = 1 - (d_k / d_{max})$.
4. **Distance-Gap Outlier Detection:** A 3-layer anomaly detection framework:
   - *Layer 1:* **Distance-Gap Analysis** (Primary). Sorts distances and isolates the maximum structural gap in the series ($> \text{mean} + 2\cdot\text{std}$).
   - *Layer 2:* **MAD-based Modified Z-Score** (Fallback for $K \le 30$). $|Z_{mod}| > 3.5$.
   - *Layer 3:* **Tukey Fence / IQR** (Fallback for $K > 30$). 

---

## 2. Normal Fuzzy TOPSIS (M1)
**Concept:** The baseline deterministic approach where all decision makers (DMs) are aggregated with equal consideration. No outlier removal or ensembles are used. Identifies the baseline flaw where a few biased DMs drastically alter final rankings using theoretical envelope aggregation `min/mean/max`.

---

## 3. Bagged Fuzzy TOPSIS - Layer 1 (M2)
**Concept:** Introduces ensemble learning to MCDM via a **Random Forest Analogy**. 

### Algorithm & Mathematical Definition
1. **Full Bootstrap Sampling:** Create $B$ bags. Each bag contains exactly $K$ DMs sampled *uniformly with replacement* (identical to Random Forest bootstrap size, theoretically allowing ~63.2% unique representation per bag).
2. **Ensemble-Robust Mean Aggregation:** Within a bag, `min/max/mean` is abandoned for `mean(l), mean(m), mean(u)` to prevent a single extreme DM (a 'poison pill') from dictating the envelope of the sub-committee.
3. **Dual Ensemble Aggregation:** 
   - Uses **Majority Rank Voting (Borda count)** as the primary ensemble metric (mirroring RF classification).
   - Uses **Averaged Closeness Coefficients (CC)** as tie-breakers.

*Limitation:* Without reliability weighting, uniform sampling preserves the raw bias ratio, mathematically proving that unguided bagging alone is insufficient for coordinated malicious injection.

---

## 4. ML-Filtered Fuzzy TOPSIS - Layer 2 (M3)
**Concept:** Applies Machine Learning and Advanced Robust Statistics to actively *reject* unreliable/biased DMs before allowing evaluation to proceed.

### Algorithm & Mathematical Definition
1. Execute the **Universal Reliability Engine's Distance-Gap Outlier Detection**.
2. Isolate DMs who statically drift from consensus groups.
3. Completely filter those outlier DMs from the operational pool.
4. Run standard deterministic Fuzzy TOPSIS strictly on validated (reliable) DMs.
   
---

## 5. Reliability-Aware Bagging: Weighted Sampling - Layer 3 Option 1 (M4)
**Concept:** Instead of filtering (which discards data), we use direct probability theory to suppress bias continuously inside the Random Forest algorithm.

### Algorithm & Mathematical Definition
1. Calculate the Reliability Score $R_k \in [0, 1]$ for each DM.
2. **Proportional Probability Sampling:** During full-bootstrap bagging ($size=K$), the probability of selecting $DM_k$ is weighted exactly by its relative reliability:
   $$ P(k) = \frac{R_k}{\sum_{j=1}^K R_j} $$
3. Execute standard bag aggregation (mean TFN aggregation) inside the bags. The ensemble inherently silences outliers since biased DMs possess $R_k \approx 0$ and rarely appear in constructed bags.

---

## 6. Reliability-Aware Bagging: Cluster-Stratified - Layer 3 Option 2 (M5)
**Concept:** DMs fall into distinct behavioral clusters. **Silhouette-optimal K-Means** identifies natural voting blocs, isolates the anomaly clusters, and performs stratified multi-sample representation to perfectly balance bag sentiment.

### Algorithm & Mathematical Definition
1. **Optimal Clustering:** Automatically determine $k$ (clusters) via maximum Silhouette Score calculation across all Euclidean distance spaces.
2. **Cluster Exclusion:** Execute gap analysis on cluster mean reliabilities to exclude entire rogue voting blocs simultaneously.
3. **Stratified Allocation:** Distribute exactly $K$ uniform sample slots across the surviving validated clusters proportional to their initial geometric size. 

---

## 7. Reliability-Weighted Aggregation - Layer 3 Option 3 (M6)
**Concept:** Resolves bias strictly at the voting weight stage using Deep Learning principles. Sampling remains uniformly random, but influence acts as a neural attention mechanism at two discrete levels.

### Algorithm & Mathematical Definition
1. **Inner-Bag Weighting (Layer A):** Inside every bag, individual DM ratings are aggregated linearly proportional to their $R_k$. DMs sampled randomly who happen to be biased get a weight of $\approx 0$ inside the evaluation sub-committee.
2. **Outer-Bag Softmax Ensemble (Layer B):** Compute a collective reliability score for every individual bag, $\bar{R}_{bag}$. Convert these ensemble reliabilities to final voting weights $W_b$ using a **Self-Calibrating Softmax Function** ($T = \sigma(R)$):
   $$ W_b = Softmax(\bar{R}_{bag}) $$
3. Aggregate the ensemble CC evaluations strictly adhering to $W_b$.

---
**Conclusion:**
By integrating Random Forest mathematics with advanced Distance-Gap Anomaly Detection and Self-Calibrating neural-style thresholds, **DR-BFTOPSIS** successfully neutralizes concerted matrix contamination without the necessity for manual variable tuning or dataset pre-processing, operating flawlessly up to production scales. 
