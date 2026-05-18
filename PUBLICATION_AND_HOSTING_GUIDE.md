# Publication and Hosting Guide

This project has two public surfaces:

1. **GitHub repository**: source code, README, method diagrams, and frozen benchmark evidence.
2. **Hugging Face Space**: live web application with the Python FastAPI backend.

Final setup:

```text
GitHub
  -> public research/code repository
  -> README with benchmark tables and diagrams
  -> final evidence CSV/TEX tables

Hugging Face Spaces
  -> live deployed system
  -> animated upload UI
  -> FastAPI backend
  -> M4, M6, and M7 execution
```

## GitHub Repository Contents

The public GitHub repository should stay focused. It should contain:

```text
README.md
LICENSE
Dockerfile
.dockerignore
HUGGINGFACE_SPACES_DEPLOYMENT.md
PUBLICATION_AND_HOSTING_GUIDE.md
web_api/
m1_normal_topsis.py
m2_bagged_topsis.py
m3_ml_filtered.py
m4_weighted_bagging.py
m5_cluster_stratified.py
m6_reliability_weighted.py
m7_entropy_reliability.py
reliability.py
external_baselines.py
run_real_dataset_benchmarks.py
run_attack_fraction_curves.py
run_external_baselines.py
run_runtime_scalability.py
compile_final_evidence.py
diagrams/
outputs/final_evidence/
method_architecture_and_proposed_methods.md
METHOD_EVOLUTION_AND_LIMITATIONS.md
external_baselines_and_related_work.md
hand_computed_fuzzy_topsis_example.md
m7_theorems.md
```

The public repository should not include:

```text
raw real datasets
downloaded paper PDFs
personal thesis draft PDFs
LaTeX dissertation folders
old preview images
temporary benchmark JSON dumps
private notes
```

Those files can remain on the local computer, but they should not be tracked in the public repository.

## Push The Clean Repository To GitHub

From the project root:

```bash
git status
git add .
git commit -m "Clean public repository and README"
git push
```

Repository URL:

```text
https://github.com/Fahim043/earr-topsis
```

## Deploy The Live System To Hugging Face

1. Create a Hugging Face account.
2. Create a new Space.
3. Choose:
   - SDK: `Docker`
   - Hardware: `CPU Basic`
4. Name the Space, for example:

```text
earr-topsis
```

The final app URL will look like:

```text
https://YOUR_USERNAME-earr-topsis.hf.space
```

Clone the Space repository:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/earr-topsis
cd earr-topsis
```

Copy the deployable files from this repository:

```text
Dockerfile
.dockerignore
web_api/
m1_normal_topsis.py
m2_bagged_topsis.py
m3_ml_filtered.py
m4_weighted_bagging.py
m5_cluster_stratified.py
m6_reliability_weighted.py
m7_entropy_reliability.py
reliability.py
```

Create or edit the Hugging Face Space `README.md` so the first lines are:

```yaml
---
title: EARR-TOPSIS
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
---
```

Then push:

```bash
git add .
git commit -m "Deploy EARR-TOPSIS live demo"
git push
```

Hugging Face will build the Docker image and start the app.

## Test The Hosted App

Open:

```text
https://YOUR_USERNAME-earr-topsis.hf.space
```

Health check:

```text
https://YOUR_USERNAME-earr-topsis.hf.space/health
```

Expected:

```json
{"status":"ok","service":"EARR-TOPSIS API","version":"0.2.0"}
```

Then test:

- Run Native Example
- Run Crisp Example
- Run M7 Stress Example

For the stress example, the expected demonstration is:

```text
M4 -> Romania
M6 -> Romania
M7 -> Austria
```

## Links To Put In Thesis Or Paper

```text
Code and reproducibility repository:
https://github.com/Fahim043/earr-topsis

Live demonstration system:
https://YOUR_USERNAME-earr-topsis.hf.space
```

Suggested wording:

```text
The complete implementation, method diagrams, final evidence tables, and reproducibility scripts are available in the GitHub repository. A live CPU-hosted demonstration system is deployed through Hugging Face Spaces, where users can upload JSON, CSV, TSV, XLS, XLSX, or XLSM decision datasets and compare the three proposed reliability-aware fuzzy TOPSIS methods.
```

## Limitations To State Honestly

- The hosted system is a research prototype.
- Free CPU hosting can sleep after inactivity.
- Large datasets may take time depending on alternatives, criteria, decision makers, and number of bags.
- The system does not permanently store uploaded data or results.
- Confidential datasets should not be uploaded to a public demo.
- The live tool is for reproducibility and decision-support experimentation, not automatic real-world decision authority.
