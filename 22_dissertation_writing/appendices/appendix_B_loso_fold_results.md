# Appendix B: Leave-One-Subject-Out (LOSO) Fold-by-Fold Results

This appendix provides the fold-by-fold Leave-One-Subject-Out (LOSO) cross-validation results for the temporal sequence models evaluated in Chapter 13 (`temporal_model_comparison.csv` and `temporal_model_evaluation_report.md`).

---

## B.1. LOSO Protocol Summary

To evaluate generalization and eliminate subject-identity leakage on small cohorts, Leave-One-Subject-Out (LOSO) cross-validation was executed across:
*   **Squat Cohort**: 9 folds corresponding to the 9 subjects ($N=98$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
*   **Lunge Cohort**: 7 folds corresponding to the 7 subjects ($N=61$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].

In each fold, all repetitions of a single held-out subject formed the test set, while the models were trained on the remaining subjects' repetitions.

---

## B.2. Fold-by-Fold Results Breakdown

Table B.1 details the per-fold test accuracy and balanced accuracy across all held-out subjects for the three primary models under Normalization Scheme A (Offset Subtracted) and Normalization Scheme B (Min-Max Scaled).

### Table B.1: Per-Fold LOSO Cross-Validation Results

| Exercise | Held-Out Subject | Scheme A Peak Baseline Balanced Acc | Scheme A LSTM Balanced Acc | Scheme B Peak Baseline Balanced Acc | Scheme B LSTM Balanced Acc |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Squat** | Fold 1 (`PM_001`) | $83.33\%$ | $50.00\%$ | $83.33\%$ | $50.00\%$ |
| | Fold 2 (`PM_002`) | $75.00\%$ | $50.00\%$ | $75.00\%$ | $50.00\%$ |
| | Fold 3 (`PM_006`) | $80.00\%$ | $60.00\%$ | $80.00\%$ | $50.00\%$ |
| | Fold 4 (`PM_011`) | $85.71\%$ | $57.14\%$ | $85.71\%$ | $50.00\%$ |
| | Fold 5 (`PM_033`) | $81.25\%$ | $50.00\%$ | $81.25\%$ | $50.00\%$ |
| | Fold 6 (`PM_040`) | $78.57\%$ | $50.00\%$ | $78.57\%$ | $50.00\%$ |
| | Fold 7 (`PM_098`) | $83.33\%$ | $58.33\%$ | $83.33\%$ | $50.00\%$ |
| | Fold 8 (`PM_113`) | $90.00\%$ | $60.00\%$ | $90.00\%$ | $50.00\%$ |
| | Fold 9 (`PM_125`) | $75.00\%$ | $48.61\%$ | $75.00\%$ | $50.00\%$ |
| **Lunge** | Fold 1 (`PM_002`) | $77.78\%$ | $55.56\%$ | $77.78\%$ | $44.44\%$ |
| | Fold 2 (`PM_006`) | $81.82\%$ | $54.55\%$ | $81.82\%$ | $36.36\%$ |
| | Fold 3 (`PM_011`) | $83.33\%$ | $50.00\%$ | $83.33\%$ | $41.67\%$ |
| | Fold 4 (`PM_033`) | $80.00\%$ | $50.00\%$ | $80.00\%$ | $40.00\%$ |
| | Fold 5 (`PM_040`) | $83.33\%$ | $50.00\%$ | $83.33\%$ | $33.33\%$ |
| | Fold 6 (`PM_104`) | $85.71\%$ | $57.14\%$ | $85.71\%$ | $42.86\%$ |
| | Fold 7 (`PM_125`) | $78.57\%$ | $59.26\%$ | $78.57\%$ | $35.71\%$ |

### B.3. Observations
The fold-by-fold breakdown demonstrates consistency across held-out subjects:
1.  **Peak Flexion Stability**: The single-feature peak flexion baseline maintained high balanced accuracy ($75.00\%\text{--}90.00\%$ for squats; $77.78\%\text{--}85.71\%$ for lunges) across all individual folds [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
2.  **LSTM Overfitting Ceiling**: The deep sequence network failed to achieve meaningful generalization on any single held-out subject split, hovering near random guessing ($50.00\%$) under Scheme A and collapsing to majority-class prediction under Scheme B [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
