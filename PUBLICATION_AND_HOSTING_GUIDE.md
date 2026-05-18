# Publication and Hosting Guide

This project has two public surfaces:

1. **GitHub repository**: the complete research/code archive.
2. **Hugging Face Space**: the live web application with Python backend.

GitHub Pages is optional and no longer required if the Hugging Face Space hosts the UI and backend together.

## Final Recommended Setup

```text
GitHub
  -> full repository
  -> README with diagrams, tables, thesis evidence, code map
  -> source code, LaTeX thesis, final evidence CSV/TEX tables

Hugging Face Spaces
  -> live deployed system
  -> animated upload UI
  -> FastAPI backend
  -> M4, M6, M7 execution
```

## Why GitHub Alone Is Not Enough

GitHub can host:

- repository files
- README pages
- images and diagrams
- evidence tables
- static websites through GitHub Pages

GitHub cannot run a persistent Python FastAPI backend on normal repository hosting or GitHub Pages.

For this project, the backend is required because uploaded files must be parsed and processed by Python. That is why the live system should run on Hugging Face Spaces.

## GitHub Repository Checklist

Keep these files and folders public:

```text
README.md
PUBLICATION_AND_HOSTING_GUIDE.md
HUGGINGFACE_SPACES_DEPLOYMENT.md
GITHUB_DEPLOYMENT.md
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
run_*.py
external_baselines.py
compile_final_evidence.py
diagrams/
docs/assets/
outputs/final_evidence/
bracu_thesis_latex/
method_architecture_and_proposed_methods.md
METHOD_EVOLUTION_AND_LIMITATIONS.md
EARR_TOPSIS_STUDY_GUIDE.md
THESIS_DEFENSE_STUDY_GUIDE.md
CODE_FILE_GUIDE.md
```

Be careful before making these public:

```text
papers/
real_datasets/
*.pdf
outputs/pdf_pages_preview*/
```

Only publish them if copyright, privacy, and university rules allow it.

## Step 1: Push Full Repository To GitHub

From the project root:

```bash
git status
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/earr-topsis.git
git push -u origin main
```

If the remote already exists:

```bash
git remote -v
git push
```

Your GitHub URL will look like:

```text
https://github.com/YOUR_USERNAME/earr-topsis
```

This is the URL to place in the thesis/report as the reproducibility repository.

## Step 2: Confirm README Displays Properly

On GitHub, check:

- diagrams render in the README
- method descriptions are visible
- evidence table links work
- final evidence files are present under `outputs/final_evidence/`
- API instructions mention Hugging Face Spaces
- no private or copyrighted file is accidentally exposed

## Step 3: Create Hugging Face Space

1. Create a free Hugging Face account.
2. Go to **Spaces**.
3. Click **Create new Space**.
4. Choose:
   - SDK: `Docker`
   - Hardware: `CPU Basic`
   - Visibility: public for demonstration, private while testing
5. Name it something clear, for example:

```text
earr-topsis
```

The final app URL will be:

```text
https://YOUR_USERNAME-earr-topsis.hf.space
```

## Step 4: Push App To Hugging Face

Clone the empty Space repository:

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/earr-topsis
cd earr-topsis
```

Copy the deployable files from this project into the Space repository:

```text
Dockerfile
.dockerignore
web_api/
m1_normal_topsis.py
m4_weighted_bagging.py
m6_reliability_weighted.py
m7_entropy_reliability.py
reliability.py
```

Also copy these if imports require them later:

```text
m2_bagged_topsis.py
m3_ml_filtered.py
m5_cluster_stratified.py
external_baselines.py
```

Create or edit the Space `README.md` so the first lines are:

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

## Step 5: Test The Hosted App

Open:

```text
https://YOUR_USERNAME-earr-topsis.hf.space
```

Test:

```text
https://YOUR_USERNAME-earr-topsis.hf.space/health
```

Expected:

```json
{"status":"ok","service":"EARR-TOPSIS API","version":"0.2.0"}
```

Then test the UI buttons:

- Run Native Example
- Run Crisp Example
- Run M7 Stress Example

For the stress example, the expected demonstration is:

```text
M4 -> Romania
M6 -> Romania
M7 -> Austria
```

This shows the intended case where M7 handles the structured attack better than M4 and M6.

## Step 6: What To Put In Thesis Or Paper

Use both links:

```text
Code and reproducibility repository:
https://github.com/YOUR_USERNAME/earr-topsis

Live demonstration system:
https://YOUR_USERNAME-earr-topsis.hf.space
```

Suggested wording:

```text
The complete implementation, final evidence tables, method diagrams, and reproducibility scripts are available in the GitHub repository. A live CPU-hosted demonstration system is deployed through Hugging Face Spaces, where users can upload JSON, CSV, TSV, XLS, XLSX, or XLSM decision datasets and compare the three proposed methods.
```

## Do We Need GitHub Pages?

No.

Use GitHub Pages only if you want a static mirror of the frontend. Since the Hugging Face Space can serve both the UI and backend, GitHub Pages is optional.

Recommended:

```text
GitHub Pages: off or optional
GitHub repository: public research archive
Hugging Face Space: live system
```

## Limitations To State Honestly

- The hosted system is a research prototype.
- Free CPU hosting can sleep after inactivity.
- Large datasets may take time depending on number of alternatives, decision makers, criteria, and bags.
- The system does not permanently store uploaded data or results.
- Confidential datasets should not be uploaded to a public demo.
- The live tool is for reproducibility and decision-support experimentation, not automatic real-world decision authority.
