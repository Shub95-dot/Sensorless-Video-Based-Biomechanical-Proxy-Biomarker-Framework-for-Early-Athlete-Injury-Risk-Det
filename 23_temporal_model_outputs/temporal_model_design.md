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
*   **Optimization:** Adam optimizer (learning rate = $1 \times 10^{-3}$), Binary Cross-Entropy loss.
*   **Training Safeguards:** Trained for a maximum of 100 epochs, utilizing Early Stopping on validation fold loss with a patience of 15 epochs to prevent over-tuning.

---

## 4. Model B: Interpretable Shape-Feature Baseline

Model B extracts 6 explicit, geometrically interpretable features from the resampled 100-point trajectory and feeds them to a regularized L2 Logistic Regression classifier:

1.  **Descent-to-Ascent Duration Ratio ($T_{\text{descent}} / T_{\text{ascent}}$):** Measures velocity asymmetry between down and up phases.
2.  **Trajectory Asymmetry Index:** The mean absolute difference between the descent trajectory and the time-reversed ascent trajectory.
3.  **Normalized Time-to-Peak Flexion:** The timestep index $t \in [0, 100]$ where maximum flexion occurs, capturing whether peak depth is held or reached early/late.
4.  **Descent Velocity Skewness:** Measures deceleration/acceleration patterns during descent.
5.  **Ascent Velocity Skewness:** Measures acceleration patterns during ascent.
6.  **Descent Concavity (Area Ratio):** The trapezoidal area under the normalized descent curve compared to a linear transition, characterizing the smoothness/profile of the bend.

---

## 5. Naive & Endpoint Baselines (The Threshold Bars)

To determine if trajectory shape adds any value beyond baseline statistics and standard endpoints, we evaluate two comparison baselines:

1.  **Naive Baseline (Zero Rule):** Always predicts the majority class in the training fold (Squats = Correct Form, Lunges = Incorrect Form).
2.  **Endpoint Biomarker Baseline (Peak Flexion alone):** A simple classifier (Logistic Regression) fit only on the single endpoint biomarker `peak_flexion_deg` using identical cross-validation folds.

---

## 6. Evaluation Protocol (LOSO Folds)

*   **Validation Scheme:** Leave-One-Subject-Out (LOSO) cross-validation.
    *   **Squat:** 9 folds (train on 8 subjects, test on the 1 held-out subject).
    *   **Lunge:** 7 folds (train on 6 usable subjects, test on the 1 held-out subject).
*   **Seed Control:** All splits and initializations use a locked random seed (`42`) to guarantee reproducibility.
*   **Primary Metrics:**
    *   Classification Accuracy
    *   Balanced Accuracy (primary metric to account for class imbalance)
    *   F1-Score
*   **Reporting:** We report both the fold-by-fold scores (demonstrating inter-subject variability) and the summary Mean $\pm$ Standard Deviation across all folds.

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
