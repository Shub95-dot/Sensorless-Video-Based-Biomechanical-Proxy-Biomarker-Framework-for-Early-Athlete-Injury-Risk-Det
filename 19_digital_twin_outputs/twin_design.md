# Continuous-Update Personalised Digital Twin
## Stage 1 — Design on Paper (Architectural Demonstration)

This document describes the design of an architectural demonstration for a continuously-updating personalised "Digital Twin" framework. The digital twin extends the static personalised baseline from Phase 8 by continuously updating the subject's reference state as new repetitions are ingested, while gating subsequent repetitions against the updated state using the Phase 7 validated noise floor.

> [!IMPORTANT]
> **Hard Framing Constraints:**
> *   This framework is an architectural demonstration of a continuous-update baseline methodology. It does **not** track real longitudinal progression, predict future movement patterns, forecast performance, or estimate injury risk.
> *   No predictive, prognostic, or clinical language is used. The framework's scope is strictly limited to baseline-updating mechanics and kinematic deviation detection.

---

## 1. Digital Twin State

The digital twin maintains a lightweight, per-subject statistical representation of the "current normal" movement profile. The twin state for biomarker $i$ at time step $t$ consists of:
1.  **Running Reference Mean ($\mu_{t, i}$):** The rolling average of the subject's repetitions that represent their normal baseline state.
2.  **Running Sample Size ($N_{t, i}$):** The number of repetitions incorporated into the running mean so far.
3.  **Descriptive Baseline Spread ($SD_{t, i}$) [DESCRIPTIVE ONLY]:** The descriptive standard deviation of the baseline reps seen so far (not used for gating).
4.  **Validated Noise Floor ($NF_i$):** The fixed, projection-transferred measurement uncertainty from Phase 7 (constant bounds).

---

## 2. Update Rule

To ensure that the twin's reference adapts to stable variations in normal form while remaining robust to anomalous, short-term kinematic fluctuations, the twin applies a **conditional update rule**:

*   **When a new repetition $x_{t+1, i}$ arrives:**
    1.  Compute the absolute deviation from the current reference:
        $$\Delta_i = |x_{t+1, i} - \mu_{t, i}|$$
    2.  Gate the repetition against the validated noise floor:
        *   **If $\Delta_i \le NF_i$ (WITHIN-NOISE):** The repetition falls within normal measurement variation. It is treated as representative of the subject's baseline. The twin updates its state incrementally:
            $$\mu_{t+1, i} = \frac{N_{t, i} \cdot \mu_{t, i} + x_{t+1, i}}{N_{t, i} + 1}$$
            $$N_{t+1, i} = N_{t, i} + 1$$
        *   **If $\Delta_i > NF_i$ (DEVIATION DETECTED):** The repetition represents a significant kinematic shift. To prevent the baseline from being contaminated by short-term deviations or incorrect movement strategies, the repetition is **excluded** from the update:
            $$\mu_{t+1, i} = \mu_{t, i}$$
            $$N_{t+1, i} = N_{t, i}$$

This conditional logic ensures the digital twin is self-stabilizing: it updates its reference on normal repetitions but isolates and flags deviations without allowing them to drift the baseline.

---

## 3. Measurement-Based Exclusion Explanation

When the digital twin gates a repetition and decides to exclude it from the reference update (due to `DEVIATION DETECTED` status), the framework generates a transparent explanation based on measurement logic:

*   **Exclusion Message:**
    *"Rep N deviated from your baseline beyond validated measurement uncertainty (on biomarker X). The twin does not update the reference from this rep, because from a single observation it cannot distinguish a transient fluctuation from a genuine sustained change — that distinction would require the deviation to persist across multiple sessions."*
*   **Measurement and Epistemic Humility Framing:**
    *   **No Quality Verdicts:** The logic explains *why* the update is withheld (single-observation ambiguity and measurement uncertainty) without declaring the repetition to be "bad" or "incorrect".
    *   **Epistemic Humility:** Expresses that the framework "cannot yet distinguish" rather than issuing a final judgment about movement quality.
    *   **Coherent Future Work Path:** Directly motivates the transient-vs-sustained research line: a deployed longitudinal twin would absorb deviations that persist across real sessions (adaptation/change) and filter out isolated ones (transient fluctuations).

---

## 4. Deviation Re-Gating

Every newly ingested repetition is gated using the current reference state prior to any update:
*   A repetition $x_{t+1, i}$ is flagged as **DEVIATION DETECTED** if:
    $$|x_{t+1, i} - \mu_{t, i}| > NF_i$$
    *Meaning:* A real kinematic deviation from the subject's active baseline, exceeding camera measurement uncertainty.
*   Otherwise, it is flagged as **WITHIN-NOISE** (meaning the variation is within normal measurement limits).

---

## 5. Pseudo-Session Structure

The single-session `REHAB24-6` dataset repetitions are partitioned into sequential **pseudo-sessions** to demonstrate the twin ingesting data, updating, and re-gating:

*   **Pseudo-Session 1 (Initialization):** Ingests Reps 1–2 (both correct).
    *   Initializes the twin state: reference mean $\mu_0$ is computed from Reps 1–2.
*   **Pseudo-Session 2 (Normal Practice):** Ingests Reps 3–5 (all correct).
    *   Each rep is gated against the active twin state.
    *   Because they fall within the noise floor, each rep incrementally updates the twin state. After Rep 5, the updated reference $\mu_1$ reflects all 5 correct reps.
*   **Pseudo-Session 3 (Deviated Practice):** Ingests Reps 6–10 (all incorrect).
    *   Each rep is gated against the updated twin state ($\mu_1$).
    *   Because they exceed the noise floor, they trigger a `DEVIATION DETECTED` flag and are **excluded** from updating the reference. The twin state remains at $\mu_1$ to prevent baseline drift.

---

## 6. "What This Demonstration Does NOT Claim"

*   **No Predictive Forecasting:** The twin does not predict or forecast future movement patterns, load, fatigue, or clinical outcomes.
*   **No Learned Parameters:** It does not use training weights, learning rates, state decay, or neural networks. The update is a transparent arithmetic running mean.
*   **No Real Longitudinal Tracking:** It uses within-session blocks as pseudo-sessions. Inter-day tracking is deferred.
*   **No Injury Prediction:** Deviation triggers are strictly kinematic checks against camera uncertainty, not clinical risk indicators.
*   **Not a Deployed System:** It is a software design prototype demonstrating baseline updating logic.

---

## 7. Worked-Demo Plan (Stage 2)

The implementation script will run the Digital Twin on the Phase 8 clean subjects:
1.  **Squat Subject 8 (`PM_113`)**
2.  **Lunge Subject 6 (`PM_104`)**

### Expected Output Visualizations:
*   **Reference Evolution:** The figure will show the baseline reference mean dynamically adjusting between Reps 1 and 5 as correct reps are ingested, and then flattening/locking during Reps 6–10 to isolate the deviations.
*   **Gating status:** Points will be colored by their individual gating status (gray = baseline, green = within-noise, red = deviation detected) to show the gating tracking the updated state.
*   **Exclusion Explanation display:** The script will output/print the exact measurement-based exclusion messages for reps that are withheld from updates.
*   **Artifacts:** The script will output `worked_example_twin.csv` containing the step-by-step twin states and generate `twin_tracking.png` showing the reference evolution and noise bands across the 10 pseudo-time steps.
