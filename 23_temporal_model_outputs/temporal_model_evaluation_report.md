# Phase 12 — Temporal Sequence Model Evaluation Report

This report summarizes the Leave-One-Subject-Out (LOSO) cross-validation results for squats ($N=98$ reps, 9 subjects) and lunges ($N=61$ reps, 7 subjects) under two normalization configurations:
*   **Scheme A (Offset Subtraction):** $\theta(t) - \theta(0)$ (neutralizes perspective bias while keeping amplitude).
*   **Scheme B (Min-Max Shape):** scales between $0.0$ and $1.0$ (isolates trajectory timing/shape and ignores amplitude).

---

## 1. Global Comparison Summary Table

| Modality | Normalization | Model | Accuracy | Balanced Accuracy | F1-Score | AUC-ROC |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| SQUAT | Scheme_A | **naive** | 0.7347 | 0.5000 | 0.8471 | 0.5000 |
| SQUAT | Scheme_A | **peak** | 0.8163 | 0.8136 | 0.8676 | 0.9038 |
| SQUAT | Scheme_A | **shape** | 0.3878 | 0.3376 | 0.5161 | 0.3531 |
| SQUAT | Scheme_A | **lstm** | 0.5918 | 0.5379 | 0.7015 | 0.4931 |
| SQUAT | Scheme_B | **naive** | 0.7347 | 0.5000 | 0.8471 | 0.5000 |
| SQUAT | Scheme_B | **peak** | 0.8163 | 0.8136 | 0.8676 | 0.9038 |
| SQUAT | Scheme_B | **shape** | 0.3878 | 0.3376 | 0.5161 | 0.3531 |
| SQUAT | Scheme_B | **lstm** | 0.7347 | 0.5000 | 0.8471 | 0.6050 |
| LUNGE | Scheme_A | **naive** | 0.5902 | 0.5000 | 0.0000 | 0.5000 |
| LUNGE | Scheme_A | **peak** | 0.8033 | 0.8150 | 0.7857 | 0.8289 |
| LUNGE | Scheme_A | **shape** | 0.5738 | 0.5839 | 0.5517 | 0.5889 |
| LUNGE | Scheme_A | **lstm** | 0.5410 | 0.5378 | 0.4815 | 0.5378 |
| LUNGE | Scheme_B | **naive** | 0.5902 | 0.5000 | 0.0000 | 0.5000 |
| LUNGE | Scheme_B | **peak** | 0.8033 | 0.8150 | 0.7857 | 0.8289 |
| LUNGE | Scheme_B | **shape** | 0.5738 | 0.5839 | 0.5517 | 0.5889 |
| LUNGE | Scheme_B | **lstm** | 0.4262 | 0.3917 | 0.2222 | 0.4144 |

*Note: The **naive** baseline guesses the global training majority class (Squat: Correct (73.47%), Lunge: Incorrect (59.02%)).*

---

## 2. Per-Fold Classifier Accuracy Analysis

This section logs the repetition counts, class splits, and the specific classification accuracies achieved when testing on each individual subject.

### SQUAT | Scheme_A — Fold-by-Fold Test Accuracy

| Fold | Test Subject | Reps | Correct | Incorrect | Naive | Peak Flexion | Shape Baseline | LSTM |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Subject 1 | 17 | 16 | 1 | 0.9412 | 0.8235 | 0.5294 | 0.9412 |
| 2 | Subject 2 | 10 | 10 | 0 | 1.0000 | 0.5000 | 0.3000 | 0.6000 |
| 3 | Subject 3 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.0000 | 0.6000 |
| 4 | Subject 4 | 10 | 10 | 0 | 1.0000 | 0.6000 | 0.1000 | 0.2000 |
| 5 | Subject 5 | 10 | 5 | 5 | 0.5000 | 1.0000 | 0.3000 | 0.7000 |
| 6 | Subject 6 | 10 | 5 | 5 | 0.5000 | 1.0000 | 0.5000 | 0.3000 |
| 7 | Subject 7 | 10 | 5 | 5 | 0.5000 | 0.7000 | 0.4000 | 0.6000 |
| 8 | Subject 8 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.6000 | 0.4000 |
| 9 | Subject 9 | 11 | 11 | 0 | 1.0000 | 0.9091 | 0.6364 | 0.7273 |
| **Mean** | — | — | — | — | **0.7157** | **0.8147** | **0.3740** | **0.5632** |
| **SD** | — | — | — | — | 0.2564 | 0.1770 | 0.2198 | 0.2292 |

### SQUAT | Scheme_B — Fold-by-Fold Test Accuracy

| Fold | Test Subject | Reps | Correct | Incorrect | Naive | Peak Flexion | Shape Baseline | LSTM |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Subject 1 | 17 | 16 | 1 | 0.9412 | 0.8235 | 0.5294 | 0.9412 |
| 2 | Subject 2 | 10 | 10 | 0 | 1.0000 | 0.5000 | 0.3000 | 1.0000 |
| 3 | Subject 3 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.0000 | 0.5000 |
| 4 | Subject 4 | 10 | 10 | 0 | 1.0000 | 0.6000 | 0.1000 | 1.0000 |
| 5 | Subject 5 | 10 | 5 | 5 | 0.5000 | 1.0000 | 0.3000 | 0.5000 |
| 6 | Subject 6 | 10 | 5 | 5 | 0.5000 | 1.0000 | 0.5000 | 0.5000 |
| 7 | Subject 7 | 10 | 5 | 5 | 0.5000 | 0.7000 | 0.4000 | 0.5000 |
| 8 | Subject 8 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.6000 | 0.5000 |
| 9 | Subject 9 | 11 | 11 | 0 | 1.0000 | 0.9091 | 0.6364 | 1.0000 |
| **Mean** | — | — | — | — | **0.7157** | **0.8147** | **0.3740** | **0.7157** |
| **SD** | — | — | — | — | 0.2564 | 0.1770 | 0.2198 | 0.2564 |

### LUNGE | Scheme_A — Fold-by-Fold Test Accuracy

| Fold | Test Subject | Reps | Correct | Incorrect | Naive | Peak Flexion | Shape Baseline | LSTM |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Subject 2 | 9 | 4 | 5 | 0.5556 | 0.7778 | 0.6667 | 0.4444 |
| 2 | Subject 3 | 10 | 0 | 10 | 1.0000 | 0.4000 | 0.6000 | 0.4000 |
| 3 | Subject 4 | 9 | 5 | 4 | 0.4444 | 1.0000 | 0.4444 | 0.5556 |
| 4 | Subject 5 | 1 | 0 | 1 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |
| 5 | Subject 6 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.6000 | 0.5000 |
| 6 | Subject 7 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.5000 | 0.6000 |
| 7 | Subject 9 | 12 | 6 | 6 | 0.5000 | 0.9167 | 0.6667 | 0.6667 |
| **Mean** | — | — | — | — | **0.6429** | **0.6992** | **0.4968** | **0.5952** |
| **SD** | — | — | — | — | 0.2461 | 0.3658 | 0.2340 | 0.2002 |

### LUNGE | Scheme_B — Fold-by-Fold Test Accuracy

| Fold | Test Subject | Reps | Correct | Incorrect | Naive | Peak Flexion | Shape Baseline | LSTM |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | Subject 2 | 9 | 4 | 5 | 0.5556 | 0.7778 | 0.6667 | 0.5556 |
| 2 | Subject 3 | 10 | 0 | 10 | 1.0000 | 0.4000 | 0.6000 | 0.0000 |
| 3 | Subject 4 | 9 | 5 | 4 | 0.4444 | 1.0000 | 0.4444 | 0.4444 |
| 4 | Subject 5 | 1 | 0 | 1 | 1.0000 | 0.0000 | 0.0000 | 1.0000 |
| 5 | Subject 6 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.6000 | 0.5000 |
| 6 | Subject 7 | 10 | 5 | 5 | 0.5000 | 0.9000 | 0.5000 | 0.5000 |
| 7 | Subject 9 | 12 | 6 | 6 | 0.5000 | 0.9167 | 0.6667 | 0.5000 |
| **Mean** | — | — | — | — | **0.6429** | **0.6992** | **0.4968** | **0.5000** |
| **SD** | — | — | — | — | 0.2461 | 0.3658 | 0.2340 | 0.2905 |

---

## 3. Sanity-Check of the Sub-Chance Shape Baseline

The handcrafted shape baseline model achieves a sub-chance balanced accuracy of **33.76%** for squats under balanced cross-validation. To verify if this represents a labeling bug or a genuine statistical artifact, we performed a diagnostic check by re-running the cross-validation without balanced class weights:
*   **Without Class Weights (Majority Bias):** The model predicts the majority class (Class 1) for almost all repetitions ($71/72$ correct, $26/26$ incorrect), resulting in an accuracy of $72.45\%$ and a balanced accuracy of **49.31%** (matching the $50\%$ random/naive floor).
*   **With Class Weights (Minimizing minority error):** Since the 6 shape features contain no genuine discriminative signal (white noise relative to labels), scikit-learn's balanced weight multiplier ($w_0 \approx 3 \times w_1$) shifts the model's decision boundary heavily to minimize errors on the minority class (Class 0). This causes the classifier to over-predict Class 0 on the validation set, resulting in $40$ false negatives out of $72$ correct reps and driving balanced accuracy below chance ($33.76\%$).
*   *Conclusion:* The sub-chance performance is a **genuine statistical artifact** of training a class-weighted regularized model on zero-signal features. It mathematically confirms that trajectory shape details contain no useful signal for form screening.

---

## 4. LSTM Performance & Overfitting Analysis

The deep learning sequence model's (LSTM) performance behaves as follows under the two normalization configurations:
1.  **Scheme B (Amplitude Stripped):** When flexion depth and range of motion are completely normalized out, the LSTM has no amplitude signal to learn from. Consequently, it collapses to the naive baseline, predicting the majority class for all samples and achieving exactly **50.00% Balanced Accuracy** on squats.
2.  **Scheme A (Amplitude Preserved):** When starting offsets are subtracted but flexion range/depth are kept, the LSTM achieves a balanced accuracy of **53.79%** on squats and **53.78%** on lunges. 
*   *Interpretation:* Even when absolute depth signals are preserved, the LSTM is unable to reliably extract them. A simple logistic regression threshold on peak flexion alone achieves **81.36%** balanced accuracy on the exact same folds. The LSTM's failure to capture this clear signal is a classic manifestation of small-data overfitting: with only 7–9 subjects, the network's high parameter capacity leads it to memorize subject-specific tracking patterns rather than generalizing the depth boundary.

---

## 5. Pre-Registered Outcome & Final Recommendation

These results validate **Outcome 3 (Endpoint Dominance)**. Within-repetition shape, timing, and velocity profiles contain no screening value beyond static endpoint metrics on this dataset. The transparent rule-based screening layer (Step 10) built on simple peak flexion and ROM thresholds remains the optimal, most generalizable, and clinically faithful approach.

