# BRAC University Thesis LaTeX Draft

This folder follows the BracU thesis template structure from the example `main.tex`:

- `core/`: title page, declaration, approval, ethics statement, abstract, dedication, acknowledgement
- `chapters/`: chapter files
- `appendix/`: appendix files
- `bibliography/`: references
- `images/`: method architecture images
- `tables/`: frozen result tables

## Main File

Compile `main.tex`.

On Overleaf:

1. Upload the whole `bracu_thesis_latex` folder.
2. Set `main.tex` as the main document.
3. Use Biber for bibliography if Overleaf asks.

Local compile:

```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
```

## Replace Before Submission

In `main.tex`, replace:

- `\supervisorname`
- department/school wording if your department requires exact BRAC wording
- date if needed

The student name and ID are currently filled from the available context:

- Md. Fahim Afridi Ani
- 24366010

## Frozen Research Framing

The three proposed methods are:

- M4: Reliability-Weighted Bagged Fuzzy TOPSIS
- M6: Reliability-Weighted Aggregation TOPSIS
- M7/EARR-TOPSIS: Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS

M2 is the corrected bootstrap baseline. M5 is a cluster-stratified ablation/branch.
