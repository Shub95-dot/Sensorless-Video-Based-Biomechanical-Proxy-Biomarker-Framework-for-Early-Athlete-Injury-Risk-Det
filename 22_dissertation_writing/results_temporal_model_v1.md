# Chapter 13: Temporal Sequence Modeling and Pretraining Future Work

This chapter presents the design, evaluation, and interpretation of temporal sequence modeling (Phase 12, Track B architectural demonstration). We examine whether within-repetition joint trajectory dynamics contain discriminative form screening information that is independent of, or superior to, the static endpoint biomarkers established in earlier chapters. First, we define the research question and frame this evaluation as an empirical inquiry where null outcomes are pre-registered as scientifically informative. Second, we detail the Leave-One-Subject-Out (LOSO) cross-validation protocol and the normalization schemes designed to prevent subject-identity leakage. Third, we present the compiled results of the sequence models against naive and static endpoint baselines. Fourth, we interpret these findings under a pre-registered framework, concluding that static endpoints dominate at this cohort scale and diagnosing the failure modes of the deep network. Finally, we present a principled, evidence-grounded future work roadmap for self-supervised representation learning and outline the limitations of this trajectory shape analysis.

---

## 13.1. Purpose and Research Question

The core research question evaluated in this chapter is: **Does modeling the within-repetition frame-by-frame joint-angle trajectory shape distinguish correct from incorrect repetitions beyond what is captured by static endpoint biomarkers?** [source: 23_temporal_model_outputs/temporal_model_design.md].

To maintain clarity, we distinguish this analysis along two structural axes:
*   **Within-Repetition Trajectory Shape**: The frame-by-frame geometric path of a single repetition resampled to a normalized time grid [source: 23_temporal_model_outputs/temporal_model_design.md].
*   **Across-Session Longitudinal Modeling**: The tracking of discrete parameters across multiple testing sessions spaced over days or weeks (which is addressed via the static baseline and digital twin architectures in Chapters 9 and 11) [source: 22_dissertation_writing/results_baseline_v1.md / results_digital_twin_v1.md]. This chapter is strictly restricted to within-repetition trajectory shape classification [source: 23_temporal_model_outputs/temporal_model_design.md].

This evaluation is structured as a **Track B architectural demonstration** [source: 23_temporal_model_outputs/temporal_model_design.md]. Rather than optimizing a model to force a positive result, we treat this experiment as an empirical test of sequence modeling utility. Under this paradigm, a null or negative result (e.g. sequence shape adding no value) is pre-registered as a valuable, successful scientific finding [source: 23_temporal_model_outputs/temporal_model_design.md]. It provides empirical evidence to justify whether clinical screening layers can safely rely on transparent, simple endpoint rules rather than complex deep sequence models [source: 23_temporal_model_outputs/temporal_model_design.md].

---

## 13.2. Experimental Design and Evaluation Rigour

To ensure the credibility of the empirical outcomes, we implemented a rigorous evaluation framework designed to isolate the trajectory shape signal from potential confounding leakage pathways [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.1. Leave-One-Subject-Out (LOSO) Validation
Subject-identity leakage represents a major failure mode in small-cohort biomechanical modeling, where a neural network memorizes subject-specific kinematic offsets and baseline characteristics rather than learning generalizable movement boundaries. To eliminate this confound, we utilized a strict **Leave-One-Subject-Out (LOSO) cross-validation** scheme [source: 23_temporal_model_outputs/temporal_model_design.md]:
*   **Squat Evaluation**: Conducted across $9$ folds corresponding to the $9$ subjects in the `REHAB24-6` cohort ($N=98$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
*   **Lunge Evaluation**: Conducted across $7$ folds corresponding to the $7$ subjects in the `REHAB24-6` lunge cohort ($N=61$ total repetitions) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
In each fold, all repetitions of a single subject were held out entirely as the test set, while the models were trained on the remaining subjects' data. This guarantees that no repetition from the test subject appears in the training split.

### 13.2.2. Temporal Standardization
Because the duration of repetitions varies widely across trials (ranging from $65$ to $155$ frames for squats, and $41$ to $166$ frames for lunges), repetition duration is a potential confounding pathway [source: 23_temporal_model_outputs/temporal_model_design.md]. To isolate shape from duration, each smoothed sagittal knee-flexion trajectory was linearly resampled to a fixed grid of exactly **$T = 100$ points**, mapping the horizontal axis to normalized time (0% to 100% of repetition duration) [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.3. Anti-Leakage Normalization Schemes
We evaluated the models under two distinct normalization schemes to isolate the source of the classification signal [source: 23_temporal_model_outputs/temporal_model_design.md]:
1.  **Scheme A (Offset Subtraction / Zero-Anchor)**:
    $$\theta_{\text{offset}}(t) = \theta(t) - \theta(0)$$
    This subtracts the initial standing angle, neutralizing camera elevation and perspective offsets while preserving the absolute angular Range of Motion (ROM) and maximum flexion depth [source: 23_temporal_model_outputs/temporal_model_design.md].
2.  **Scheme B (Min-Max Scaling / Pure Shape)**:
    $$\theta_{\text{shape}}(t) = \frac{\theta(t) - \min(\theta)}{\max(\theta) - \min(\theta)}$$
    This scales the trajectory values strictly between $0.0$ and $1.0$ [source: 23_temporal_model_outputs/temporal_model_design.md]. This strips away both starting angle offset and maximum range, forcing the model to classify form based **solely** on time-dependent shape geometry (such as ascent/descent velocity asymmetry, deceleration profiles, and timing) [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.4. Models Compared
Four models were trained on identical folds to establish baseline performance bars:
*   **Naive Baseline (Zero-Rule Guess-Majority)**: Predicts the majority training class for all samples, establishing the baseline accuracy floor [source: 23_temporal_model_outputs/temporal_model_design.md].
*   **Endpoint Biomarker Baseline (Peak Flexion alone)**: A Logistic Regression classifier trained only on the single endpoint biomarker `peak_flexion_deg` [source: 23_temporal_model_outputs/temporal_model_design.md].
*   **Interpretable Shape-Feature Baseline (Amplitude-Invariant)**: A Logistic Regression classifier trained on $6$ handcrafted shape features computed directly on the normalized 100-point trajectory $\theta_{\text{norm}}(t)$ (ensuring it is denied absolute amplitude information whenever the LSTM is) [source: 23_temporal_model_outputs/temporal_model_design.md]:
    1.  *Descent-to-Ascent Duration Ratio* ($T_{\text{descent}} / T_{\text{ascent}}$)
    2.  *Trajectory Asymmetry Index* (mean absolute difference between normalized descent and time-reversed ascent curves)
    3.  *Normalized Time-to-Peak Flexion*
    4.  *Descent Velocity Skewness*
    5.  *Ascent Velocity Skewness*
    6.  *Descent Curve Concavity* (trapezoidal area under the normalized descent curve)
*   **Model A (Heavily Regularized LSTM)**: A miniature sequence network designed with high regularization to prevent memorization on our small dataset [source: 23_temporal_model_outputs/temporal_model_design.md]. The architecture consists of an input layer ($100 \times 1$), an LSTM layer with $8$ hidden units (dropout = 0.3, recurrent dropout = 0.3), a dense layer with $4$ hidden units (ReLU, L2 regularization $\lambda = 0.01$), a 0.5 dropout layer, and a single sigmoid output [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.2.5. Pre-Registered Outcome Interpretations
To prevent post-hoc reinterpretation of the results, the interpretations of three potential outcome scenarios were pre-registered in the design document before training [source: 23_temporal_model_outputs/temporal_model_design.md]:
1.  **Outcome 1 (Shape Dynamics)**: LSTM $>$ Shape Baseline $>$ Naive & Endpoint. Concludes that within-rep sequence shape contains key discriminative signals that static endpoints cannot capture, justifying a deep learning approach [source: 23_temporal_model_outputs/temporal_model_design.md].
2.  **Outcome 2 (Simple Geometry)**: Shape Baseline $\approx$ LSTM $>$ Naive & Endpoint. Concludes that shape adds value, but the signal is low-order and captured by simple features, rendering the LSTM unnecessary [source: 23_temporal_model_outputs/temporal_model_design.md].
3.  **Outcome 3 (Endpoint Dominance)**: Endpoint Baseline $\ge$ Shape Baseline $\approx$ LSTM. Concludes that within-repetition shape details carry no discriminative value beyond simple static endpoints [source: 23_temporal_model_outputs/temporal_model_design.md].

---

## 13.3. Results

The compiled global classification performance metrics across all models under both normalization schemes are presented in Table 13.1 [source: 23_temporal_model_outputs/temporal_model_comparison.csv].

### Table 13.1: Global Sequence Model Performance Metrics (LOSO CV)

| Exercise | Normalization | Model | Accuracy | Balanced Accuracy | F1-Score | AUC-ROC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Squat** | Scheme_A (Offset Sub) | **naive** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.5000$ |
| ($N=98$) | | **peak** | **$81.63\%$** | **$81.36\%$** | **$0.8676$** | **$0.9038$** |
| | | **shape** | $38.78\%$ | $33.76\%$ | $0.5161$ | $0.3531$ |
| | | **lstm** | $59.18\%$ | $53.79\%$ | $0.7015$ | $0.4931$ |
| | Scheme_B (Min-Max) | **naive** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.5000$ |
| | | **peak** | **$81.63\%$** | **$81.36\%$** | **$0.8676$** | **$0.9038$** |
| | | **shape** | $38.78\%$ | $33.76\%$ | $0.5161$ | $0.3531$ |
| | | **lstm** | $73.47\%$ | $50.00\%$ | $0.8471$ | $0.6050$ |
| **Lunge** | Scheme_A (Offset Sub) | **naive** | $59.02\%$ | $50.00\%$ | $0.0000$ | $0.5000$ |
| ($N=61$) | | **peak** | **$80.33\%$** | **$81.50\%$** | **$0.7857$** | **$0.8289$** |
| | | **shape** | $57.38\%$ | $58.39\%$ | $0.5517$ | $0.5889$ |
| | | **lstm** | $54.10\%$ | $53.78\%$ | $0.4815$ | $0.5378$ |
| | Scheme_B (Min-Max) | **naive** | $59.02\%$ | $50.00\%$ | $0.0000$ | $0.5000$ |
| | | **peak** | **$80.33\%$** | **$81.50\%$** | **$0.7857$** | **$0.8289$** |
| | | **shape** | $57.38\%$ | $58.39\%$ | $0.5517$ | $0.5889$ |
| | | **lstm** | $42.62\%$ | $39.17\%$ | $0.2222$ | $0.4144$ |

### 13.3.1. Naive and Endpoint Baselines
*   **Naive Majority Floor**: The squat majority class was correct (73.47% accuracy), while the lunge majority class was incorrect (59.02% accuracy), yielding a balanced accuracy of $50.00\%$ by definition [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
*   **Peak Flexion Baseline**: The single static peak flexion baseline outperformed all other models, achieving a balanced accuracy of **$81.36\%$** on squats (AUC-ROC = $0.9038$) and **$81.50\%$** on lunges (AUC-ROC = $0.8289$) [source: 23_temporal_model_outputs/temporal_model_comparison.csv].

### 13.3.2. Sanity-Check of the Sub-Chance Shape Baseline
For squats, the handcrafted shape baseline model returned a sub-chance balanced accuracy of **$33.76\%$** under balanced cross-validation [source: 23_temporal_model_outputs/temporal_model_comparison.csv]. Rather than a bug, diagnostic evaluation verified that this is a **genuine statistical artifact** of training a class-weighted regularized model on zero-signal noise [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]:
*   *Without Class Weights*: Re-running without class weights caused the shape baseline to predict the majority class for almost all repetitions ($71/72$ correct, $26/26$ incorrect), yielding a balanced accuracy of **$49.31\%$** (the $50\%$ random guess floor) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md].
*   *With Class Weights*: When balanced class weights are applied, the optimization loss multiplier on the minority class ($w_0 \approx 3 \times w_1$) shifts the decision boundary heavily to minimize minority errors. Because the 6 shape features contain no actual signal, this shift causes the model to over-predict the minority class on validation splits, generating $40$ false negatives out of $72$ correct reps and driving balanced accuracy below chance ($33.76\%$) [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]. This mathematically confirms that trajectory shape details contain zero useful signal.

### 13.3.3. LSTM Sequence Model Performance
The deep sequence network failed to outperform the simple peak flexion classifier under both normalization schemes:
*   **Scheme B (Min-Max Scaled / Pure Shape)**: With amplitude information completely stripped, the LSTM collapsed to the naive majority baseline on squats, predicting the majority class for all samples and returning exactly **$50.00\%$ Balanced Accuracy** [source: 23_temporal_model_outputs/temporal_model_comparison.csv]. For lunges, the model fell below chance, returning a balanced accuracy of **$39.17\%$** [source: 23_temporal_model_outputs/temporal_model_comparison.csv].
*   **Scheme A (Offset Subtracted / Amplitude Preserved)**: Retaining amplitude offsets resulted in a balanced accuracy of only **$53.79\%$** on squats and **$53.78\%$** on lunges, performing marginally above random guessing [source: 23_temporal_model_outputs/temporal_model_comparison.csv].

---

## 13.4. Interpretation and Overfitting Diagnostics

These results confirm **Outcome 3 (Endpoint Dominance)** [source: 23_temporal_model_outputs/temporal_model_design.md]. Within-repetition sequence shape, timing, and velocity profiles contain no independent discriminative utility beyond static endpoint biomarkers on this dataset [source: 23_temporal_model_outputs/temporal_model_design.md].

### 13.4.1. LSTM Failure Mode Diagnosis
The failure of the LSTM under Scheme A (achieving only $\approx 54\%$ balanced accuracy) is particularly diagnostic. Even though amplitude information (flexion depth) was preserved in the Scheme A input data, the LSTM was unable to extract and generalize it, performing far below the single-feature peak flexion classifier ($81.36\%$). This represents a classic manifestation of **small-data overfitting (subject memorization)** [source: 23_temporal_model_outputs/temporal_model_evaluation_report.md]:
*   With only 7 to 9 subjects, the network's high parameter capacity leads it to memorize subject-specific calibration offsets and tracking noise rather than extracting the generalizable depth boundary.
*   Because the training set is small, the network fails to generalize the flexion threshold across folds, leading to a collapse in validation balanced accuracy.

### 13.4.2. Retroactive Validation of Chapter 10 Screening Layer
This result provides an independent, empirical validation of the Step 10 screening layer design presented in Chapter 10 [source: 22_dissertation_writing/results_screening_layer_v1.md]. Two independently developed components—the cohort-level distributions grounding Step 10's rules and this temporal sequence modeling experiment—converge on the same conclusion: **peak knee flexion depth is the dominant discriminative kinematic biomarker** [source: 22_dissertation_writing/results_screening_layer_v1.md / 23_temporal_model_outputs/temporal_model_design.md]. Relying on transparent, rule-based screening thresholds is not only computationally simpler but statistically superior to sequence-based deep learning approaches at this cohort scale.

---

## 13.5. Self-Supervised Pretraining Future Work

Based on the empirical findings of this chapter, we outline a reasoned, evidence-grounded future work roadmap for self-supervised representation learning:
*   **Current Status**: Self-supervised pretraining was **not implemented** as an active pipeline component [source: dissertation_writeup_index.md]. 
*   **Principled Scoping Rationale**: Self-supervised pretraining (such as masked trajectory autoencoding or contrastive sequence learning) is designed to learn robust feature representations from unlabeled data to improve downstream supervised model performance. However, this chapter's results establish that:
    1.  The supervised sequence model (LSTM) overfits at this subject scale ($N=9$ squats, $N=7$ lunges), failing to generalize.
    2.  The downstream screening task is successfully solved by a single static endpoint biomarker (peak flexion, achieving $81\%$ balanced accuracy).
*   **Conclusion**: Under these constraints, applying self-supervised pretraining to the sequence model is highly unlikely to yield downstream performance gains on this cohort, representing a pre-accepted time-boxed null scoping outcome [source: dissertation_writeup_index.md].
*   **Future Requirements**: Pretraining represents a viable research path only when scaled to significantly larger cohorts (e.g. hundreds of subjects and thousands of repetitions), where representation learning can extract complex, high-dimensional joint-coordination patterns before endpoint saturation occurs.

---

## 13.6. Does Not Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of this temporal evaluation:
*   **Not a Rejection of Sequence Modeling**: We do not claim that temporal sequence modeling or LSTMs are generally without value for biomechanics; we demonstrate specifically that they are not warranted or generalizable at this cohort scale ($9$ squat / $7$ lunge subjects) [source: dissertation_writeup_index.md].
*   **Not a Rejection of Pretraining**: We do not claim that self-supervised pretraining is universally ineffective; we show that it is unlikely to yield downstream gains under the overfitting ceilings of small-cohort datasets.
*   **Screening-not-Prediction Framing**: These sequence models categorize movement deviations matching the manual labeling scheme; they do not predict injury risk or estimate clinical probabilities.

---

## 13.7. Limitations

Several limitations of this temporal sequence analysis must be noted:
1.  **Small Cohort Scale**: The central limitation is the small subject count (9 subjects for squats, 7 subjects for lunges), which prevents deep recurrent neural networks from generalizing.
2.  **Knee Flexion Single-Axis Restriction**: The sequence analysis was restricted to the knee flexion angle trajectory. Out-of-plane movements and coordination patterns involving other joints (such as hip-ankle coupling) were not evaluated.
3.  **Within-Repetition Restraint**: The evaluation was restricted to within-repetition shape classification. Across-session longitudinal trajectory changes (representing physical adaptation or baseline drift) remain unaddressed and represent a distinct future-work axis from the pseudo-session baselines tracked in Chapters 9 and 11.
