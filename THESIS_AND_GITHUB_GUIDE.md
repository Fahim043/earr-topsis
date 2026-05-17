# Thesis, API, and GitHub Guide

This guide explains what to do next, how the thesis files are organized, how the API works, and how to put the project on GitHub.

## 1. What "Full Thesis Report" Means

Your professor is asking for a complete dissertation-style document, not only a short paper draft. A full thesis report usually includes:

1. Title page
2. Declaration
3. Approval page
4. Ethics statement
5. Abstract
6. Dedication
7. Acknowledgement
8. Table of contents
9. List of figures
10. List of tables
11. Chapter 1: Introduction
12. Chapter 2: Literature Review
13. Chapter 3: Methodology
14. Chapter 4: Experimental Design
15. Chapter 5: Results
16. Chapter 6: Discussion
17. Chapter 7: Conclusion
18. Bibliography
19. Appendix

I generated this in the BRAC template structure here:

```text
bracu_thesis_latex/main.tex
```

Use this folder for thesis submission.

## 2. What You Must Edit Before Submission

Open:

```text
bracu_thesis_latex/main.tex
```

Replace:

```latex
\newcommand{\supervisorname}{Insert Supervisor Name}
```

Check these too:

```latex
\newcommand{\studentname}{Md. Fahim Afridi Ani}
\newcommand{\studentid}{24366010}
\newcommand{\department}{Department of Computer Science and Engineering}
\newcommand{\school}{School of Data and Sciences}
\newcommand{\submissiondate}{May 2026}
```

If BRAC or your supervisor wants exact wording, change only those command values.

## 3. How To Compile the Thesis in Overleaf

1. Go to Overleaf.
2. Create a new blank project.
3. Upload the entire `bracu_thesis_latex` folder contents.
4. Make sure `main.tex` is at the project root.
5. Set compiler to pdfLaTeX.
6. Set bibliography tool to Biber if Overleaf asks.
7. Compile.

If bibliography does not appear:

1. Click Menu.
2. Check that the bibliography tool is Biber.
3. Recompile twice.

## 4. What the Thesis Says

The thesis name is:

```text
Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS for Bias-Resistant Group Decision-Making
```

Short method name:

```text
EARR-TOPSIS
```

The three proposed methods are:

1. M4: Reliability-Weighted Bagged Fuzzy TOPSIS
2. M6: Reliability-Weighted Aggregation TOPSIS
3. M7/EARR-TOPSIS: Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS

M2 is not a main proposed method. M2 is the corrected bootstrap baseline.

M5 is not a main proposed method. M5 is a cluster-stratified ablation branch because it is inconsistent.

## 5. Is the API Functional?

Yes, the prototype API is functional locally. It has been tested through HTTP using the health endpoint and the `/api/run` endpoint for native JSON, flat fuzzy CSV, and crisp CSV example uploads.

API folder:

```text
web_api/
```

Run locally:

```bash
cd web_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Run with example JSON:

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -F "file=@examples/example_native.json" \
  -F "methods=M4,M6,M7" \
  -F "num_bags=20" \
  -F "seed=42"
```

## 6. API Upload Formats

The API supports three formats.

### Format A: Native JSON

Best for research users who already know fuzzy TOPSIS.

Required keys:

```text
alternatives
criteria
decision_makers
criteria_weights
ratings
```

Example:

```text
web_api/examples/example_native.json
```

### Format B: Flat Fuzzy CSV/XLSX

Best for Excel users.

Required columns:

```text
decision_maker, alternative, criterion, l, m, u
```

Optional columns:

```text
weight_l, weight_m, weight_u, criteria_type
```

Example:

```text
web_api/examples/example_flat_fuzzy.csv
```

### Format C: Crisp CSV/XLSX

Best for simple demo users.

First column: alternative name.

Other columns: numeric criteria.

Example:

```text
web_api/examples/example_crisp.csv
```

Important: crisp files are converted into pseudo-fuzzy decision panels for demo purposes. For serious research, native fuzzy JSON or flat fuzzy CSV is better.

## 7. How To Put This on GitHub

From the project root:

```bash
git init
git add .
git commit -m "Initial EARR-TOPSIS thesis and API release"
```

Create a new GitHub repository named something like:

```text
earr-topsis
```

Then connect and push:

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/earr-topsis.git
git push -u origin main
```

Do not upload private files or huge unnecessary outputs if GitHub rejects the push. If needed, add a `.gitignore`.

## 8. GitHub Pages Site

GitHub Pages can host static pages, but not Python APIs.

Recommended structure:

```text
docs/
  index.html
  methods.html
  thesis.html
  api.html
```

Then in GitHub:

1. Go to repository Settings.
2. Go to Pages.
3. Source: deploy from branch.
4. Branch: main.
5. Folder: `/docs`.

The static site can explain the method and link to the API backend.

## 9. API Deployment Options

Because the API uses Python, deploy it separately.

Good beginner options:

1. Render
2. Railway
3. Hugging Face Spaces
4. University server

For Render:

1. Create a new Web Service.
2. Connect the GitHub repo.
3. Root directory: `web_api`.
4. Build command:

```bash
pip install -r requirements.txt
```

5. Start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

## 10. Code Explanation

### `m1_normal_topsis.py`

This is the classical fuzzy TOPSIS baseline. It:

1. loads the JSON dataset;
2. aggregates all decision-maker ratings;
3. normalizes benefit/cost criteria;
4. applies fuzzy weights;
5. computes positive and negative ideal solutions;
6. computes closeness coefficients;
7. returns a ranking.

### `m2_bagged_topsis.py`

This is the corrected bootstrap baseline. It samples decision makers with replacement, runs fuzzy TOPSIS on each bag, and combines bag rankings. It helps with stability but does not detect biased decision makers.

### `m3_ml_filtered.py`

This computes reliability using distance from a median consensus vector and filters suspicious decision makers. It is strong when attackers are a distinguishable minority.

### `m4_weighted_bagging.py`

This is Proposed Method 1. It computes reliability and uses it as the bootstrap sampling probability. Reliable decision makers enter bags more often. Suspicious decision makers enter less often.

### `m5_cluster_stratified.py`

This clusters decision makers and samples from reliable clusters. It is conceptually useful but inconsistent in results, so it is an ablation branch.

### `m6_reliability_weighted.py`

This is Proposed Method 2. It applies reliability inside the fuzzy aggregation formula. Even if a biased decision maker is sampled, their ratings have low influence.

### `m7_entropy_reliability.py`

This is Proposed Method 3 and the final method, EARR-TOPSIS. It combines:

1. entropy signal;
2. variance-consistency signal;
3. clone/agreement-pattern signal;
4. reliability-weighted sampling;
5. reliability-weighted aggregation;
6. bag-quality weighting.

It is the strongest method in the final structured attack tests.

### `run_real_dataset_benchmarks.py`

Runs M1 to M7 on real/pseudo-real datasets and reports clean and contaminated metrics.

### `run_attack_fraction_curves.py`

Runs the 10 percent to 60 percent attack-fraction experiments.

### `run_external_baselines.py`

Runs external comparator baselines: median, trimmed mean, MAD consensus, individual Borda, and Huang-Li group ideal.

### `analyze_statistics.py`

Creates confidence intervals and paired target-error tests.

### `compile_final_evidence.py`

Collects saved outputs into final CSV, Markdown, and LaTeX tables.

### `web_api/app.py`

FastAPI app that lets users upload datasets and run M4, M6, and M7.

## 11. What To Tell Your Professor

You can say:

```text
The thesis report is now in BRAC template format. The method name is EARR-TOPSIS.
The three proposed methods are M4, M6, and M7. M2 is kept as the corrected bootstrap baseline.
The code package includes benchmark scripts, frozen tables, statistical tests, external baselines,
and a prototype API for dataset upload and method execution.
```

## 12. Immediate Next Steps

1. Open `bracu_thesis_latex/main.tex`.
2. Replace supervisor name.
3. Upload `bracu_thesis_latex` to Overleaf.
4. Compile.
5. Read the PDF once from start to end.
6. Fix university formatting details if BRAC asks.
7. Send the PDF to your professor.
8. After professor approval, prepare the Q1 journal version from the same chapters and frozen tables.
