# Canonical Chapter Mapping (Locked)

Numbering has deliberate gaps at Chapters 3 and 7 (reserved).

| Chapter | Source Markdown | LaTeX File | Chapter Title |
|---------|----------------|------------|---------------|
| 1 | `results_introduction_v2.md` | `ch01.tex` | Introduction |
| 2 | `methods_v3.md` | `ch02.tex` | Methodology |
| 3 | RESERVED (gap) | — | `\addtocounter{chapter}{1}` |
| 4 | `results_squat_v2.md` | `ch04.tex` | Squat Screening Results |
| 5 | `results_lunge_v2.md` | `ch05.tex` | Lunge Screening Results |
| 6 | `results_dropjump_validation_v2.md` | `ch06.tex` | Drop-Jump Validation |
| 7 | RESERVED (gap) | — | `\addtocounter{chapter}{1}` |
| 8 | `results_uncertainty_framework_v2.md` | `ch08.tex` | Uncertainty-Weighted Screening Transfer |
| 9 | `results_baseline_v2.md` | `ch09.tex` | Personalised Baseline |
| 10 | `results_screening_layer_v2.md` | `ch10.tex` | Rule-Based Screening Layer |
| 11 | `results_digital_twin_v2.md` | `ch11.tex` | Digital Twin |
| 12 | `results_xai_v2.md` | `ch12.tex` | Counterfactual Explainability |
| 13 | `results_temporal_model_v2.md` | `ch13.tex` | Temporal Model |
| 14 | `results_discussion_v2.md` | `ch14.tex` | General Discussion |
| 15 | `results_conclusion_v2.md` | `ch15.tex` | Conclusion |

## Source Markdown Directory
`22_dissertation_writing/`

## LaTeX Output Directory
`latex_harness/dissertation/chapters/`

## Gap Treatment
Chapters 3 and 7 use `\addtocounter{chapter}{1}` in `main.tex` — no .tex file needed.

## Convention Notes
- `[source:]` tags stripped during conversion → harvested into `appendices/appF_data_provenance.tex`
- `[CITE: key]` → `\citep{key}` (natbib Harvard)
- Sections numbered by LaTeX (`\section`, `\subsection`, `\subsubsection`)
- Labels: `\label{ch:shortname}`, `\label{sec:X.Y}`, `\label{fig:name}`, `\label{tab:name}`
- Figures: `\includegraphics` with `\graphicspath{{figures/}}`
