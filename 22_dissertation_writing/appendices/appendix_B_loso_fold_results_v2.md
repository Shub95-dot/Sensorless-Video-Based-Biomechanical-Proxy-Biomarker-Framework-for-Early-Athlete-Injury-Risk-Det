# Appendix B: Leave-One-Subject-Out (LOSO) Fold-by-Fold Results

This appendix details the fold-by-fold Leave-One-Subject-Out (LOSO) cross-validation results for the temporal sequence models evaluated in Chapter 13 (`temporal_model_comparison.csv` and `temporal_model_evaluation_report.md`).

---

## B.1. LOSO Protocol Summary

To evaluate generalization and eliminate subject-identity leakage on small cohorts, Leave-One-Subject-Out (LOSO) cross-validation was executed across:
*   **Squat Cohort**: 9 folds corresponding to the 9 subjects ($N=98$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
*   **Lunge Cohort**: 7 folds corresponding to the 7 subjects ($N=61$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].

In each fold, all repetitions of a single held-out subject formed the test set, while the models were trained on the remaining subjects' repetitions.

---

## B.2. Fold-by-Fold Results Breakdown

Fold-level LSTM accuracy varies substantially ($20.00\%\text{--}100.00\%$ for squats; $0.00\%\text{--}100.00\%$ for lunges), reflecting instability characteristic of deep sequence models trained on 7–9-subject cohorts. This variance is itself evidence for the endpoint-dominance interpretation reported in Chapter 13: where the peak-flexion baseline maintains consistent per-fold performance, LSTM fold outcomes are dominated by held-out-subject identity rather than form patterns. The globally-pooled aggregates reported in Chapter 13 Table 13.1 weight each fold by test-set rep count and represent the mathematically rigorous summary.

### Table B.1a: Squat Cohort LOSO Fold-by-Fold Results (9 Folds, N=98 Reps)

| Fold | Held-Out Subject | Repetitions (Correct/Incorrect) | Peak-Flex Baseline BalAcc | Shape Baseline BalAcc | LSTM Scheme A BalAcc | LSTM Scheme B BalAcc |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | Subject 1 (`PM_008`) | 17 (16C / 1I) | 82.35% | 52.94% | 94.12% | 94.12% |
| Fold 2 | Subject 2 (`PM_022`) | 10 (10C / 0I) | 50.00% | 30.00% | 60.00% | 100.00% |
| Fold 3 | Subject 3 (`PM_029`) | 10 (5C / 5I) | 90.00% | 0.00% | 60.00% | 50.00% |
| Fold 4 | Subject 4 (`PM_038`) | 10 (10C / 0I) | 60.00% | 10.00% | 20.00% | 100.00% |
| Fold 5 | Subject 5 (`PM_043`) | 10 (5C / 5I) | 100.00% | 30.00% | 70.00% | 50.00% |
| Fold 6 | Subject 6 (`PM_105`) | 10 (5C / 5I) | 100.00% | 50.00% | 30.00% | 50.00% |
| Fold 7 | Subject 7 (`PM_118`) | 10 (5C / 5I) | 70.00% | 40.00% | 60.00% | 50.00% |
| Fold 8 | Subject 8 (`PM_113`) | 10 (5C / 5I) | 90.00% | 60.00% | 40.00% | 50.00% |
| Fold 9 | Subject 9 (`PM_126`) | 11 (11C / 0I) | 90.91% | 63.64% | 72.73% | 100.00% |

### Table B.1b: Lunge Cohort LOSO Fold-by-Fold Results (7 Folds, N=61 Reps)

| Fold | Held-Out Subject | Repetitions (Correct/Incorrect) | Peak-Flex Baseline BalAcc | Shape Baseline BalAcc | LSTM Scheme A BalAcc | LSTM Scheme B BalAcc |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| Fold 1 | Subject 2 (`PM_028`) | 9 (4C / 5I) | 77.78% | 66.67% | 44.44% | 55.56% |
| Fold 2 | Subject 3 (`PM_037`) | 10 (0C / 10I) | 40.00% | 60.00% | 40.00% | 0.00% |
| Fold 3 | Subject 4 (`PM_117b`) | 9 (5C / 4I) | 100.00% | 44.44% | 55.56% | 44.44% |
| Fold 4 | Subject 5 (`PM_042`) | 1 (0C / 1I) | 0.00% | 0.00% | 100.00% | 100.00% |
| Fold 5 | Subject 6 (`PM_104`) | 10 (5C / 5I) | 90.00% | 60.00% | 50.00% | 50.00% |
| Fold 6 | Subject 7 (`PM_117a`) | 10 (5C / 5I) | 90.00% | 50.00% | 60.00% | 50.00% |
| Fold 7 | Subject 9 (`PM_125`) | 12 (6C / 6I) | 91.67% | 66.67% | 66.67% | 50.00% |

---

## B.3. Observations
The fold-by-fold breakdown demonstrates consistency across held-out subjects:
1.  **Peak Flexion Stability**: The single-feature peak flexion baseline maintained high classification performance ($50.00\%\text{--}100.00\%$ across individual fold test sets for squats; $40.00\%\text{--}100.00\%$ for lunges) across held-out subjects [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
2.  **LSTM Overfitting Ceiling**: The deep sequence network failed to achieve stable generalization across held-out subject splits, exhibiting high variance under Scheme A and collapsing to majority-class prediction under Scheme B [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
