# Personalised Kinematic Progression Tracking
## Stage 2 — Design on Paper (Architectural Demonstration)

This document describes the design of an architectural demonstration for personalised kinematic progression tracking. It builds a per-subject movement baseline from a subset of correct repetitions, then detects when subsequent repetitions deviate from that baseline beyond the validated measurement-noise floor.

> [!IMPORTANT]
> **Hard Framing Constraints:**
> *   This framework is an architectural demonstration of a progression-tracking methodology. It does **not** track real longitudinal progression, calculate a risk index, classify reps, predict injury, or assert clinical outcomes.
> *   No predictive language (e.g., "risk", "likelihood", "load", "fatigue") is used. The framework's scope is strictly limited to measurement-uncertainty and kinematic deviation detection.

---

## 1. Subject Selection & Dataset Inventory

To demonstrate both quiet (no-false-alarm) and firing states on real data, we select subjects from the `REHAB24-6` cohort who have a balanced mix of correct (normal form) and incorrect (deviated form) repetitions.

### Subject Cleanliness Confirmation:
*   **Squat Subject 8 (`PM_113`):** Confirmed fully clean. Contains 10 repetitions, all with `phase_identification_status == "ok"` and `spike_rate_pct == 0.0`. No tracking anomalies or pose-extraction failures were recorded for this subject in previous squats validation phases.
*   **Lunge Subject 6 (`PM_104`):** Confirmed fully clean. Contains 10 repetitions, all with `phase_identification_status == "ok"` and `spike_rate_pct == 0.0` (or minimal). No tracking anomalies or occlusion failures were recorded for this subject (earlier lunge exclusions due to occlusion were limited to Subject 5/`PM_042` and Subject 8/`PM_112`).
*   *Note on Subject Mapping:* Subject IDs do not cross-map directly between squat and lunge datasets due to cohort-specific indexing. We verify that `PM_113` (Subject 8 in squats) and `PM_104` (Subject 6 in lunges) represent the correct, clean files.

### Selected Repetitions:
*   **Squat Subject 8 (`PM_113`):** 10 reps (Reps 1–5 correct, Reps 6–10 incorrect). Correct reps show a mean peak flexion of $69.21^\circ$, whereas incorrect reps show a mean peak flexion of $42.06^\circ$ (a $27.15^\circ$ restricted-depth deviation).
*   **Lunge Subject 6 (`PM_104`):** 10 reps (Reps 1–5 correct, Reps 6–10 incorrect). Correct reps show a mean peak flexion of $85.48^\circ$, whereas incorrect reps show a mean peak flexion of $58.84^\circ$ (a $26.64^\circ$ restricted-depth deviation).

---

## 2. Baseline Construction

The per-subject baseline represents the individual's "normal" movement pattern under stable conditions:
*   **Baseline Block:** Constructed from the first **2 correct repetitions** of the session (Reps 1 and 2).
*   **Baseline Reference Value ($\mu_{\text{base}, i}$):** The mean value of biomarker $i$ computed across the baseline block:
    $$\mu_{\text{base}, i} = \frac{1}{2} (x_{1, i} + x_{2, i})$$
*   **Baseline Spread ($SD_{\text{base}, i}$) [DESCRIPTIVE ONLY]:** The standard deviation of biomarker $i$ across the baseline block (descriptive context representing early-session consistency, but **not** used in the gating/flagging rule due to small-sample instability).

---

## 3. Deviation Detection Rule

For each subsequent repetition in the **test sequence** (Reps 3–10, consisting of 3 correct reps and 5 incorrect reps), the framework evaluates whether the kinematic value has significantly shifted from the baseline.

A shift is flagged as a **"real deviation"** only if the difference between the test rep and the baseline mean exceeds the validated measurement-noise floor for that biomarker.

### Exact Detection Rule:
Let $x_{\text{test}, i}$ be the measured value of biomarker $i$ for a test repetition.
1.  Compute the absolute deviation from baseline:
    $$\Delta_i = |x_{\text{test}, i} - \mu_{\text{base}, i}|$$
2.  Retrieve the validated **95% Noise Floor ($NF_i$)** derived from Phase 7 (projection-only component):
    $$NF_i = 1.96 \times SD_{\text{proj}, i}$$
3.  Evaluate the deviation threshold:
    *   If $\Delta_i > NF_i$: Flag the repetition as **DEVIATION DETECTED**, indicating *a real kinematic deviation from the subject's own baseline, exceeding camera measurement uncertainty* (it does **not** signify a "bad", "incorrect", or "injurious" rep).
    *   If $\Delta_i \le NF_i$: Flag the repetition as **WITHIN-NOISE**, indicating that *the change cannot be distinguished from normal camera/projection measurement noise* (no real kinematic change occurred).

### Validated Noise Floors (Phase 7 Projection Transfer):
1.  **#1 start_flexion (Contact equivalent):** $NF_{\#1} = \mathbf{\pm 19.0522^\circ}$ (SD: $9.7205^\circ$)
2.  **#2 peak_flexion (Depth equivalent):** $NF_{\#2} = \mathbf{\pm 11.9885^\circ}$ (SD: $6.1166^\circ$)
3.  **#3 rom (ROM equivalent):** $NF_{\#3} = \mathbf{\pm 23.1666^\circ}$ (SD: $11.8197^\circ$)
4.  **#6 descent_velocity (Loading rate equivalent):** $NF_{\#6} = \mathbf{\pm 40.8615^\circ/\text{s}}$ (SD: $20.8477^\circ/\text{s}$)

---

## 4. Pseudo-Timepoint Framing

Because the REHAB24-6 dataset consists of single-session laboratory collections, **repetition order** is utilized as a **pseudo-time axis** to illustrate longitudinal tracking:
*   Within-session repetition index represents subsequent observation points (Reps 3 to 10).
*   This pseudo-time framing serves to demonstrate the baseline-building and noise-gating software architecture.
*   True longitudinal tracking across days or weeks is future work.

---

## 5. "What This Demonstration Does NOT Claim"

*   **No Real Longitudinal Progression:** It does not track real physiological progression over days/weeks; it uses within-session reps as pseudo-timepoints.
*   **No Injury Prediction or Risk Scoring:** It does not predict injury, score risk, or determine clinical outcomes.
*   **No Cohort Re-Analysis:** It does not re-analyze correct vs. incorrect reps at a group level. The unit of analysis is the individual subject's own reference and their own noise-gated deviation.
*   **Not a Deployed Clinical System:** It is a software architectural demonstration of baseline-building and uncertainty-gating logic.

---

## 6. Worked-Demo Plan (Stage 3)

The script will execute the design on:
1.  **Squat Subject 8 (`PM_113`):** Baseline built from Reps 1–2 (correct). Test sequence evaluates Reps 3–5 (correct, quiet-test) and Reps 6–10 (incorrect, firing-test).
2.  **Lunge Subject 6 (`PM_104`):** Baseline built from Reps 1–2 (correct). Test sequence evaluates Reps 3–5 (correct, quiet-test) and Reps 6–10 (incorrect, firing-test).

### Expected Output & Illustration:
*   **Quiet-Test Sequence (Reps 3–5):** The deviation $\Delta_i$ should remain within the $NF_i$ band. The framework will report "within measurement noise floor" (demonstrating no false alarms across 3 test points).
*   **Firing-Test Sequence (Reps 6–10):** The deviation $\Delta_i$ for peak flexion should exceed the $NF_{\#2}$ threshold of $11.99^\circ$, triggering the deviation flag due to the restricted-depth landing strategy.
*   **Artifacts:** The script will output `worked_example_baseline.csv` containing the baseline means, spreads, and test rep deviation evaluations. It will plot `baseline_tracking.png` illustrating the pseudo-time sequences with baseline means and the shaded noise floor bands.

---

## 7. Empirical Findings (Stage 3 Verification)

Upon executing the Stage 3 tracking script, we obtained the following key empirical findings:

### 1. Separation of Gating Statuses
*   **Quiet-Test Sequence (Reps 3–5):** For both squats and lunges, the correct repetitions stayed strictly within the 95% Noise Floor band (all flagged as `WITHIN-NOISE` for peak flexion: max squat delta was $9.26^\circ$, max lunge delta was $6.77^\circ$). This demonstrates that the framework successfully prevents false alarms on normal repetition-to-repetition variation.
*   **Firing-Test Sequence (Reps 6–10):** For both squats and lunges, the incorrect repetitions dropped dramatically below the baseline mean (all flagged as `DEVIATION DETECTED` for peak flexion: squat deltas range from $23.23^\circ$ to $35.66^\circ$, lunge deltas range from $20.91^\circ$ to $31.98^\circ$). This confirms that real kinematic deviations (such as restricted depth) are reliably flagged.

### 2. High-Confidence Biomarker Dominance (Uncertainty Gating in Action)
A critical finding is that **the deviation detection is carried by the high-confidence peak flexion biomarker**, while the high-noise velocity biomarker contributes little:
*   **Peak Flexion:** Gated by a tight validated noise floor ($\pm 11.99^\circ$, corresponding to its $57.15\%$ weight). It successfully flags all incorrect reps while staying quiet on all correct reps.
*   **Descent Velocity:** Gated by an extremely wide validated noise floor ($\pm 40.86^\circ/\text{s}$, corresponding to its low $4.92\%$ weight). Because of this wide noise floor, the incorrect repetitions generally do **not** independently trigger a deviation flag (with the exception of squat Rep 6, which involved a huge, anomalous velocity surge). For lunges, all 10 repetitions stayed safely within the velocity noise floor.
*   This visualizes the direct clinical utility of the Phase 7 uncertainty weighting: descent velocity contributes little to detection because its measurement uncertainty is large (±40.86°/s), meaning it is correctly down-weighted. The absence of velocity false alarms is a consequence of it being a low-confidence biomarker with a wide noise floor, rather than any active noise suppression mechanism, ensuring that screening decisions are appropriately driven by the high-reliability kinematic metrics.

