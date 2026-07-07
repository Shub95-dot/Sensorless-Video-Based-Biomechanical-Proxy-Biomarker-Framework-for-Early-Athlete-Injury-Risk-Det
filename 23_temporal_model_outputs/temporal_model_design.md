# Phase 12 — Temporal Sequence Model Design

This document details the experimental design and evaluation protocol for Phase 12 (Temporal Sequence Model - Track B demo). The goal is to compare deep sequence modeling (LSTM) against an interpretable shape-feature baseline under a strict Leave-One-Subject-Out (LOSO) validation scheme to determine if within-repetition trajectory shape adds screening utility beyond static endpoint biomarkers.

---

## 1. Task Definition & Framing

*   **Task:** Binary classification of individual repetitions (Class 1 = Correct Form, Class 0 = Incorrect Form/Kinematic Deviation) using only the frame-by-frame knee-flexion trajectory.
*   **Modality-Specific Models:** Squat and lunge trajectories are evaluated separately due to their distinct biomechanical profiles.
*   **Clinical Guardrail (Screening-not-Prediction):** The model categorizes movement deviations (matching the manual labeling scheme of correct vs. incorrect form). It does not predict injury risk, diagnose clinical pathologies, or estimate injury probability.

---

## 2. Trajectory Input & Subject-Identity Anti-Leakage Protocol

To ensure the models learn **shape geometry** rather than memorizing subject-specific biomechanical baselines or camera perspective offsets, we apply the following pre-processing pipeline to every repetition:

1.  **Resampling to Fixed Grid (Temporal Standardization):**
    *   Since repetitions vary in frame length (range 65–155 for squats, 41–166 for lunges), each raw `knee_angle_smoothed` trajectory is linearly resampled to exactly $T = 100$ points.
    *   This maps the horizontal axis to normalized time (0% to 100% of repetition duration), eliminating duration as a confounding leakage pathway.
2.  **Anti-Leakage Normalization:**
    We evaluate and report results under two distinct normalization schemes to isolate the precise source of discriminative signal:
    *   **Scheme A (Zero-Anchor / Offset Subtraction):**
        $$\theta_{\text{offset}}(t) = \theta(t) - \theta(0)$$
        This subtracts the standing extension angle, neutralizing camera elevation/perspective bias while preserving the absolute Range of Motion (ROM) and maximum flexion depth.
    *   **Scheme B (Min-Max Scaling / Pure Shape):**
        $$\theta_{\text{shape}}(t) = \frac{\theta(t) - \min(\theta)}{\max(\theta) - \min(\theta)}$$
        This scales the trajectory strictly between $0.0$ and $1.0$. It strips away both starting angle offset and maximum range, forcing the model to classify form based **solely** on time-dependent shape details (such as ascent/descent velocity asymmetry, deceleration patterns, and timing).

---

## 3. Model A: Heavily Regularized LSTM

To prevent memorization on our small dataset ($N=98$ squats, $N=61$ lunges), Model A is designed as a miniature, high-dropout network:

*   **Architecture:**
    1.  **Input Layer:** Shapes of batch-size $\times 100$ timesteps $\times 1$ feature.
    2.  **LSTM Layer:** 8 hidden units, with recurrent dropout = 0.3 and dropout = 0.3.
    3.  **Dense Layer:** 4 hidden units, ReLU activation, L2 regularization ($\lambda = 0.01$).
    4.  **Dropout Layer:** Dropout rate = 0.5.
    5.  **Output Layer:** 1 unit, Sigmoid activation.
*   **Optimization & Training:** Adam optimizer (learning rate = $1 \times 10^{-3}$), Binary Cross-Entropy loss. Trained for a maximum of 100 epochs, utilizing Early Stopping on validation fold loss with a patience of 15 epochs to prevent over-tuning.
*   **Imbalance Handling:** Training utilizes class weight balancing (`class_weight` proportional to inverse class frequencies) to prevent the gradient updates from favoring the majority class.

---

## 4. Model B: Interpretable Shape-Feature Baseline (Amplitude-Invariant)

To ensure a fair comparison, **all of Model B's shape features are computed directly on the normalized 100-point trajectory $\theta_{\text{norm}}(t)$ (Scheme A or B)**, ensuring it is denied absolute raw amplitude information whenever Model A is:

1.  **Descent-to-Ascent Duration Ratio ($T_{\text{descent}} / T_{\text{ascent}}$):** Measures temporal asymmetry (inherently scale-invariant).
2.  **Trajectory Asymmetry Index:** The mean absolute difference between $\theta_{\text{norm}}(t_{\text{descent}})$ and time-reversed $\theta_{\text{norm}}(t_{\text{ascent}})$ (strictly amplitude-invariant).
3.  **Normalized Time-to-Peak Flexion:** The index $t \in [0, 100]$ where maximum flexion occurs (scale-invariant).
4.  **Descent Velocity Skewness:** Skewness of the numerical derivative of $\theta_{\text{norm}}(t)$ during descent (inherently scale-invariant).
5.  **Ascent Velocity Skewness:** Skewness of the numerical derivative of $\theta_{\text{norm}}(t)$ during ascent (inherently scale-invariant).
6.  **Descent Curve Concavity:** The trapezoidal area under the normalized descent curve $\theta_{\text{norm}}(t_{\text{descent}})$. Since the curve is bounded between 0.0 and 1.0, the resulting area represents shape geometry independent of absolute amplitude.

These 6 features are fed into a Logistic Regression classifier with L2 regularization and balanced class weights.

---

## 5. Naive & Endpoint Baselines (The Threshold Bars)

We compare the temporal models against two baseline bars, which must be clearly surpassed to prove value:

1.  **Naive Baseline (Zero-Rule Guess-Majority):**
    *   *Squat Floor:* **73.47%** (predicts all reps "Correct", 72/98)
    *   *Lunge Floor:* **59.02%** (predicts all reps "Incorrect", 36/61)
2.  **Endpoint Biomarker Baseline (Peak Flexion alone):** A Logistic Regression classifier fit only on the single endpoint biomarker `peak_flexion_deg` using identical cross-validation folds.

---

## 6. Evaluation & Reporting Protocol (LOSO Folds)

*   **Validation Scheme:** Leave-One-Subject-Out (LOSO) cross-validation (9 folds for Squats, 7 folds for Lunges).
*   **Folds Alignment:** All models are evaluated on the exact same folds with random seed `42`.
*   **Class Imbalance Handling:**
    *   All model training uses balanced class weighting.
    *   **Primary Metric:** **Balanced Accuracy** (unweighted mean of sensitivity and specificity), which is robust to class imbalance.
*   **Per-Fold Reporting & Single-Class Folds:**
    *   We report classification accuracy for every single fold (subject) to capture variance across subjects.
    *   *Single-Class Folds:* For subjects with only one true class present (e.g. Squat S2, S4, S9 have 0 incorrect reps; Lunge S3 has 0 correct reps), fold-level Balanced Accuracy, F1-score, and AUC are undefined. For these folds, we report fold-level classification accuracy, and mark the fold-level balanced metrics as `N/A`.
    *   *Pooled Global Metrics:* To obtain robust global Balanced Accuracy, F1, and AUC metrics, we pool the predicted probability outputs from all folds across the entire cohort and compute a single global score. This avoids averaging undefined fold-level division metrics.

---

## 7. Pre-Registered Outcome Interpretations

To prevent retrospective narrative framing ("spinning" a poor result), we define the interpretation of all possible outcomes beforehand:

| Outcome | Metric Relationship | Scientific Conclusion |
| :--- | :--- | :--- |
| **Outcome 1: Shape Dynamics** | LSTM $>$ Shape Baseline $>$ Naive & Endpoint | Within-repetition joint velocity and non-linear sequence shape contain discriminative signal that endpoints cannot capture. A deep learning approach is warranted. |
| **Outcome 2: Simple Geometry** | Shape Baseline $\approx$ LSTM $>$ Naive & Endpoint | Trajectory details add value, but the signal is low-order (timing, asymmetry) and adequately captured by a few simple features. The complex LSTM is unnecessary. |
| **Outcome 3: Endpoint Dominance** | Endpoint Baseline $\ge$ Shape Baseline $\approx$ LSTM | Frame-by-frame trajectory shape adds no discriminative value beyond the simple static peak depth / ROM endpoints. Simple rule-based thresholds are optimal. |

---

## 8. Does-Not-Claim

*   This model is not validated for, and does not claim, diagnostic capabilities regarding joint pathology or injury risk.
*   A "null" or "tie" result (Outcome 3) is a highly valuable, successful scientific finding, demonstrating that clinical screening layers can safely rely on transparent, simple endpoint rules.
