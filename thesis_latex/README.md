# Thesis LaTeX Draft

This directory contains the thesis/dissertation draft for BRAC University submission.

## Main File

Compile:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

If BRAC provides an official LaTeX template, keep the chapter files and tables, then move them into that template.

## Before Submission

Replace these placeholders in `main.tex`:

- student ID
- supervisor name
- department/program wording if BRAC requires exact phrasing
- submission month/year if needed

## Method Name

The selected thesis/paper method name is:

`EARR-TOPSIS`: Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS.

The three proposed methods are:

- M4: Reliability-Weighted Bagged Fuzzy TOPSIS
- M6: Reliability-Weighted Aggregation TOPSIS
- M7/EARR-TOPSIS: Entropy-Aware Reliability-Weighted Robust Fuzzy TOPSIS

M2 remains the corrected bootstrap baseline. M5 remains a cluster-stratified ablation branch.
