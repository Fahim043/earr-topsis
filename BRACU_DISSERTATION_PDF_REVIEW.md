# Review of `BRACU_EARR_TOPSIS_Dissertation.pdf`

PDF reviewed: `/Users/fahimafridi/Downloads/BRACU_EARR_TOPSIS_Dissertation.pdf`

Review date: 2026-05-17

## Verdict

The PDF is strong as a thesis draft, but I would not submit this exact version without revision. It does not contain wild or dishonest claims, and the main experimental story is correctly bounded to structured, statistically distinguishable contamination. However, there are two important method-description mismatches with the current code and several formatting/completeness issues that should be fixed before BRAC submission.

## Must Fix Before Submission

### 1. M6 equation does not exactly match the code

PDF/source location:

`/Users/fahimafridi/Downloads/BRACU_EARR_TOPSIS_Dissertation/chapters/chapter_3.tex`, lines 151-157.

Current text says M6 aggregates as:

```tex
\tilde{x}_{ij}^{rw}=\left(\min_k l_{ijk},
\frac{\sum_{k=1}^{K}\rho_k m_{ijk}}{\sum_{k=1}^{K}\rho_k},
\max_k u_{ijk}\right).
```

But the current implementation in `m6_reliability_weighted.py` weights all three TFN components:

```python
wl += w * l
wm += w * m
wu += w * u
agg[a][c] = [wl, wm, wu]
```

Recommended replacement:

```tex
\tilde{x}_{ij}^{rw} =
\left(
\frac{\sum_{k=1}^{K}\rho_k l_{ijk}}{\sum_{k=1}^{K}\rho_k},
\frac{\sum_{k=1}^{K}\rho_k m_{ijk}}{\sum_{k=1}^{K}\rho_k},
\frac{\sum_{k=1}^{K}\rho_k u_{ijk}}{\sum_{k=1}^{K}\rho_k}
\right).
```

Then remove or rewrite the sentence saying lower and upper components "can also" be weighted, because in the current code they already are weighted.

### 2. M7 equation/algorithm mentions a distance signal that the code does not use as an M7 composite signal

PDF/source location:

`/Users/fahimafridi/Downloads/BRACU_EARR_TOPSIS_Dissertation/chapters/chapter_3.tex`, lines 170-183.

Current text includes:

```tex
\rho_k = \sigma(\alpha s_k^{dist}+\beta s_k^{entropy}
+\gamma s_k^{variance}+\delta s_k^{clone})
```

and the algorithm says:

```tex
Combine entropy, variance, distance, and clone-pattern signals
```

But the implemented M7 reliability uses:

- entropy reliability,
- variance-consistency reliability,
- clone/agreement-pattern reliability,
- gap-based binary filtering.

It deliberately avoids consensus-centroid distance because centroid methods can be hijacked under majority contamination.

Recommended replacement:

```tex
\rho_k =
0.35R_k^{(H)} + 0.35R_k^{(V)} + 0.30R_k^{(C)},
```

where \(R_k^{(H)}\) is entropy reliability, \(R_k^{(V)}\) is variance-consistency reliability, and \(R_k^{(C)}\) is clone/agreement reliability. Then state that a gap-based filter may set low-composite decision makers to near-zero reliability.

In the algorithm, replace:

```tex
Combine entropy, variance, distance, and clone-pattern signals into reliability scores
```

with:

```tex
Combine entropy, variance-consistency, and clone/agreement-pattern signals into reliability scores
```

### 3. Appendix numbering is visually wrong

In the PDF, Appendix sections appear as:

```text
.1 Purpose
.2 Recommended Architecture
.6 Dataset
.7 Aggregation
```

This looks incomplete and unprofessional. It should be:

```text
A.1 Purpose
A.2 Recommended Architecture
B.1 Dataset
B.2 Aggregation
```

Likely cause:

`main.tex` uses `\chapter*{Appendix A ...}` and then normal `\section{...}`, so LaTeX has no appendix chapter number for section numbering.

Source location:

`/Users/fahimafridi/Downloads/BRACU_EARR_TOPSIS_Dissertation/main.tex`, lines 136-147.

Recommended fix:

Use numbered appendix chapters instead of starred chapters:

```tex
\appendix
\chapter{Public Web and API Platform}
\input{appendix/appendix_1}

\chapter{Hand-Computed Validation Example}
\input{appendix/appendix_2}
```

Then remove the manual `\addcontentsline` entries for those appendix chapters.

### 4. Table of contents front-matter page numbers appear stale/inconsistent

In the extracted PDF text, the table of contents says:

```text
Declaration i
Approval i
Ethics Statement ii
Abstract iii
```

But the actual extracted pages show Declaration on i, Approval on ii, Ethics Statement on iii, and Abstract on iv-v.

This may be a compile-pass issue. Recompile the LaTeX cleanly at least twice, or rebuild in Overleaf from scratch.

## Should Fix / Clarify

### 5. API appendix lists future endpoints that are not all currently implemented

PDF/source location:

`/Users/fahimafridi/Downloads/BRACU_EARR_TOPSIS_Dissertation/appendix/appendix_1.tex`, lines 15-23.

The current code has:

- `GET /`
- `GET /health`
- `POST /api/run`
- `GET /api/example`

The appendix also lists:

- `POST /api/validate`
- `POST /api/convert`
- `POST /api/attack-simulate`

This is okay only if clearly presented as "planned/recommended endpoints". If you want to claim the API is already functional, change the appendix to separate:

1. Currently implemented endpoints.
2. Planned future endpoints.

### 6. Approval page still needs institution-specific completion

The approval page contains:

```text
Department/Program Coordinator:
Chairperson:
```

This may be acceptable if BRAC expects blank signature lines, but confirm with the official template/supervisor. It is not a technical error, but it is administratively incomplete until signatures/names are handled correctly.

### 7. Some PDF text extraction shows cramped words

Examples from extracted text:

- `Asmallhand-computedfuzzyTOPSISexample`
- `M3estimatesreliability`
- `explorescluster-stratifiedbagging`
- `Selectedpairwisetarget-error`

This may be only PDF text extraction, not visual layout. Still, visually inspect those pages in the PDF. If the words are actually touching, add normal spaces or rewrite those sentences.

## Claims That Look Correctly Bounded

The following claims are acceptable because the PDF repeatedly limits them to the tested structured threat model:

- M4 and M6 preserve the clean target rank through 40% effective structured contamination.
- M7 preserves the clean target rank across all 18 tested structured attack-fraction scenarios up to 60%.
- M7 is not claimed to be universally robust.
- Adaptive human-mimic attacks remain a limitation.
- Converted pseudo-real datasets are identified as a limitation.
- The API is described as a research prototype requiring production hardening.

## Overall Recommendation

Do not submit this exact PDF yet. Fix the M6 equation, fix the M7 signal description, fix appendix numbering, recompile cleanly, and clarify the API appendix. After those changes, the dissertation will be much safer to send to your supervisor/department.

