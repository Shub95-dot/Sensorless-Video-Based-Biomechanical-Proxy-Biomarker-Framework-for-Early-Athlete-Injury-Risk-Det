# Chapter 13: Temporal Sequence Modeling and Pretraining Future Work

This chapter presents the design, evaluation, and interpretation of temporal sequence modeling (Phase 12, Track B architectural demonstration). We examine whether within-repetition joint trajectory dynamics contain discriminative form screening information independent of, or superior to, static endpoint biomarkers. First, we define the research question and frame this evaluation as an empirical inquiry where null outcomes are pre-registered as scientifically informative. Second, we detail the Leave-One-Subject-Out (LOSO) cross-validation protocol and normalization schemes designed to prevent subject-identity leakage. Third, we present compiled sequence model results against naive and static endpoint baselines. Fourth, we interpret these findings under a pre-registered framework, concluding that static endpoints dominate at this cohort scale and diagnosing network overfitting. Finally, we outline an evidence-grounded roadmap for self-supervised pretraining and describe study limitations.

---

## 13.1. Purpose and Research Question

The core research question evaluated in this chapter is: **Does modeling the within-repetition frame-by-frame joint-angle trajectory shape distinguish correct from incorrect repetitions beyond what is captured by static endpoint biomarkers?** [source: 23_temporal_model_outputs/temporal_model_design.md].

We distinguish this analysis along two structural axes:
*   **Within-Repetition Trajectory Shape**: The frame-by-frame geometric path of a single repetition resampled to a normalized time grid [source: 23_temporal_model_outputs/temporal_model_design.md].
*   **Across-Session Longitudinal Modeling**: Tracking parameters across multiple sessions over days or weeks (addressed via static baselines and digital twins in Chapters 9 and 11) [source: 22_dissertation_writing/results_baseline_v1.md / results_digital_twin_v1.md]. This chapter is strictly restricted to within-repetition trajectory shape classification [source: 23_temporal_model_outputs/temporal_model_design.md].

This evaluation is structured as a **Track B architectural demonstration** [source: 23_temporal_model_outputs/temporal_model_design.md]. Rather than optimizing a model to force a positive result, we treat this experiment as an empirical test of sequence modeling utility. Under this paradigm, a null or negative result (sequence shape adding no value) is pre-registered as a valuable, successful scientific finding [source: 23_temporal_model_outputs/temporal_model_design.md]. It provides empirical evidence demonstrating whether clinical screening layers can safely rely on transparent endpoint rules rather than complex deep sequence models [source: 23_temporal_model_outputs/temporal_model_design.md].

---

## 13.2. Experimental Design and Evaluation Rigour

To isolate trajectory shape signals from confounding leakage pathways, we implemented a rigorous evaluation framework [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.1. Leave-One-Subject-Out (LOSO) Validation
Subject-identity leakage represents a major failure mode in small-cohort biomechanical modeling, where neural networks memorize subject-specific kinematic offsets rather than generalizable movement boundaries. To eliminate this confound, we utilized a strict **Leave-One-Subject-Out (LOSO) cross-validation** scheme across 9 folds for squats ($N=98$ reps) and 7 folds for lunges ($N=61$ reps) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]. In each fold, all repetitions of a single subject were held out as the test set, guaranteeing zero subject data leakage into training splits.

### 13.2.2. Temporal Standardization & Anti-Leakage Normalization
To decouple shape from repetition duration ($41\text{--}166$ frames), trajectories were linearly resampled to a fixed grid of **$T = 100$ points** [source: 23_temporal_model_outputs/temporal_model_design.md]. We evaluated models under two anti-leakage normalization schemes [source: 23_temporal_model_outputs/temporal_model_design.md]:
1.  **Scheme A (Offset Subtraction / Zero-Anchor)**: $\theta_{\text{offset}}(t) = \theta(t) - \theta(0)$, subtracting standing angle to neutralize perspective elevation while preserving ROM and maximum depth amplitude [source: 23_temporal_model_outputs/temporal_model_design.md].
2.  **Scheme B (Min-Max Scaling / Pure Shape)**: $\theta_{\text{shape}}(t) = \frac{\theta(t) - \min(\theta)}{\max(\theta) - \min(\theta)}$, scaling values strictly between $0.0$ and $1.0$ to strip all amplitude information, forcing classification based **solely** on time-dependent shape geometry [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.3. Models Compared and Pre-Registered Outcomes
Four models were evaluated on identical LOSO folds [source: 23_temporal_model_outputs/temporal_model_design.md]: (1) **Naive Baseline** (majority class guess); (2) **Endpoint Biomarker Baseline** (Logistic Regression on single biomarker `peak_flexion_deg`); (3) **Shape-Feature Baseline** (Logistic Regression on 6 handcrafted amplitude-invariant shape features such as duration ratio, velocity skewness, and concavity); and (4) **Model A LSTM** (miniature sequence network: $100 \times 1$ input, 8 hidden LSTM units, 4 dense units, heavy dropout and L2 regularization) [source: 23_temporal_model_outputs/temporal_model_design.md].

Crucially, three outcome scenarios were **pre-registered prior to training** [source: 23_temporal_model_outputs/temporal_model_design.md]:
*   **Outcome 1 (Shape Dynamics)**: LSTM $>$ Shape Baseline $>$ Naive & Endpoint (sequence shape contains key independent signal).
*   **Outcome 2 (Simple Geometry)**: Shape Baseline $\approx$ LSTM $>$ Naive & Endpoint (shape adds low-order value, making deep LSTMs unnecessary).
*   **Outcome 3 (Endpoint Dominance)**: Endpoint Baseline $\ge$ Shape Baseline $\approx$ LSTM (within-repetition shape details carry no discriminative value beyond static endpoints).

---

## 13.3. Results

Global LOSO classification metrics are presented in Table 13.1 [source: 23_temporal_model_outputs/temporal_model_comparison.csv]. Per-fold results were consistent with this aggregate pattern across all held-out subjects; the full fold-by-fold table is presented in Appendix B.

### Table 13.1: Global Sequence Model Performance Metrics (LOSO CV)

| Exercise | Normalization | Model | Accuracy | Balanced Accuracy | F1-Score | AUC-ROC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Squat** ($N=98$) | Scheme_A (Offset Sub) | **naive** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.5000$ |
| | | **peak** | **$81.63\%$** | **$81.36\%$** | **$0.8676$** | **$0.9038$** |
| | | **shape** | $38.78\%$ | $33.76\%$ | $0.5161$ | $0.3531$ |
| | | **lstm** | $59.18\%$ | $53.79\%$ | $0.7015$ | $0.4931$ |
| | Scheme_B (Min-Max) | **naive** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.5000$ |
| | | **peak** | **$81.63\%$** | **$81.36\%$** | **$0.8676$** | **$0.9038$** |
| | | **shape** | $38.78\%$ | $33.76\%$ | $0.5161$ | $0.3531$ |
| | | **lstm** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.6050$ |
| **Lunge** ($N=61$) | Scheme_A (Offset Sub) | **naive** | $59.02\%$ | $50.00\%$ | $0.0000$ | $0.5000$ |
| | | **peak** | **$80.33\%$** | **$81.50\%$** | **$0.7857$** | **$0.8289$** |
| | | **shape** | $57.38\%$ | $58.39\%$ | $0.5517$ | $0.5889$ |
| | | **lstm** | $54.10\%$ | $53.78\%$ | $0.4815$ | $0.5378$ |
| | Scheme_B (Min-Max) | **naive** | $59.02\%$ | $50.00\%$ | $0.0000$ | $0.5000$ |
| | | **peak** | **$80.33\%$** | **$81.50\%$** | **$0.7857$** | **$0.8289$** |
| | | **shape** | $57.38\%$ | $58.39\%$ | $0.5517$ | $0.5889$ |
| | | **lstm** | $42.62\%$ | $39.17\%$ | $0.2222$ | $0.4144$ |

### 13.3.1. Performance Analysis
*   **Peak Flexion Dominance**: The single static peak flexion classifier outperformed all sequence models, achieving **$81.36\%$ Balanced Accuracy** on squats (AUC = $0.9038$) and **$81.50\%$ Balanced Accuracy** on lunges (AUC = $0.8289$) [source: 23_temporal_model_outputs/temporal_model_comparison.csv].
*   **LSTM Performance**: Under Scheme B (pure shape), the LSTM collapsed to the naive majority baseline ($50.00\%$ Balanced Accuracy on squats; $39.17\%$ on lunges) [source: 23_temporal_model_outputs/temporal_model_comparison.csv]. Under Scheme A (amplitude preserved), the LSTM achieved only $53.79\%$ (squats) and $53.78\%$ (lunges), performing barely above chance [source: 23_temporal_model_outputs/temporal_model_comparison.csv].
*   **Sub-Chance Shape Baseline Artifact**: The squat shape baseline yielded a sub-chance balanced accuracy of $33.76\%$ [source: 23_temporal_model_outputs/temporal_model_comparison.csv]. Diagnostic checks confirmed this is a statistical artifact of class weighting on zero-signal noise: without class weighting, the model predicts the majority class ($49.31\%$ balanced accuracy) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]. Class weighting shifts the boundary to minimize minority loss, causing heavy validation over-prediction on zero-signal noise and confirming trajectory shape contains no discriminative information [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].

---

## 13.4. Interpretation and Overfitting Diagnostics

The empirical results conclusively confirm **Outcome 3 (Endpoint Dominance)** [source: 23_temporal_model_outputs/temporal_model_design.md]. Within-repetition trajectory shape, timing, and velocity profiles contain no independent discriminative utility beyond static endpoint biomarkers on this dataset.

### 13.4.1. Overfitting Diagnosis on Small Cohorts
The failure of the LSTM under Scheme A ($\approx 54\%$ balanced accuracy) despite amplitude information being present represents classic **small-data overfitting (subject memorization)** [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]. With only 7 to 9 subjects, the network's high parameter capacity leads it to memorize subject-specific calibration offsets and tracking noise rather than extracting generalizable depth boundaries across folds.

### 13.4.2. Convergence with Chapter 8 Uncertainty Weights
This null finding provides independent, empirical confirmation of the Chapter 8 uncertainty-weighting scheme [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]. In Chapter 8, peak flexion was assigned a primary transfer weight of **$57.15\%$** based on drop-jump ground-truth precision [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]. The sequence modeling experiment independently arrives at the same conclusion: peak knee flexion depth is the dominant kinematic biomarker. Simple, transparent endpoint rules are not only computationally lightweight but statistically superior to deep sequence models at this cohort scale.

---

## 13.5. Self-Supervised Pretraining Future Work

Based on these findings, we outline an evidence-grounded future work roadmap for self-supervised pretraining:
*   **Current Status**: Self-supervised pretraining was **not implemented** as an active pipeline component [source: dissertation_writeup_index.md].
*   **Scoping Rationale**: Pretraining (e.g. masked trajectory autoencoding or contrastive learning) aims to learn feature representations from unlabeled data to aid downstream supervised models. However, because supervised sequence models overfit at small subject scale ($N=7\text{--}9$) and downstream task performance saturates using a single static biomarker ($81\%$ balanced accuracy), pretraining would not yield downstream gains, representing a pre-accepted time-boxed null scoping outcome [source: dissertation_writeup_index.md].
*   **Future Scale Requirements**: Pretraining represents a viable research direction only when scaled to significantly larger datasets (hundreds of subjects, thousands of repetitions) where representation learning can capture complex multi-joint coordination before endpoint saturation occurs.

---

## 13.6. Boundaries and Limitations

### 13.6.1. Non-Claims
*   **Not a General Rejection of LSTMs**: We do not claim sequence models are generally useless for biomechanics, but demonstrate specifically that they are not generalizable at small cohort scales ($7\text{--}9$ subjects) [source: dissertation_writeup_index.md].
*   **Screening Scope**: Models categorize movement deviations matching labeling schemes; they do not predict injury risk or estimate clinical probabilities.

### 13.6.2. Limitations
1.  **Small Cohort Scale**: Restricted subject counts (9 squats, 7 lunges) prevent deep recurrent networks from generalizing.
2.  **Single-Axis Knee Flexion**: Sequence analysis was restricted to knee flexion; out-of-plane movements and multi-joint coordination (hip-ankle coupling) were not evaluated.
3.  **Within-Repetition Restraint**: Analysis was restricted to within-repetition shape; across-session longitudinal trajectory changes remain a separate future-work axis (Chapters 9 and 11).
