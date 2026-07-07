# Rule-Based Kinematic Screening Layer
## Stage 1 — Design on Paper (CORE Deliverable - Revised)

This document describes the design of a transparent, rule-based kinematic screening layer. It applies defined kinematic rules to produce a screening flag (SCREENING_POSITIVE or NOT_FLAGGED) and records the reason (which rule(s) fired). This layer serves as the decision foundation for the subsequent counterfactual Explainable AI (XAI) layer (Step 11).

> [!IMPORTANT]
> **Hard Framing Constraints:**
> *   This is a screening layer, **not** a diagnostic tool or predictive model.
> *   No predictive, prognostic, or clinical risk language (e.g., "injury likelihood", "risk score", "injury forecast") is permitted.
> *   A screening flag indicates that *the movement exhibits a kinematic pattern associated with compensation or restriction* based on defined screening heuristics. It is not a diagnostic verdict.

---

## 1. Distinction: Step 10 (Screening) vs. Phase 8/9 (Tracking)

It is critical to distinguish this screening layer (Step 10) from the personalised tracking layers (Phase 8/9) to ensure they represent separate methodological contributions:
*   **Phase 8/9 (Generic Change Detector):** Operates purely as a tracking mechanism. It evaluates the mathematical question: *"Has this repetition statistically shifted from the subject's active reference by an amount exceeding measurement uncertainty?"* It is agnostic to the direction, name, or biomechanical meaning of the shift.
*   **Step 10 (Rule-Based Screening Layer):** Ingests the raw statistical deviations detected by the Phase 8/9 tracking engine and maps them to **Named Screening Rules** (EXCESS_DEPTH, EXCESS_ROM, EXCESS_VELOCITY) with literature-grounded directions. It turns a generic signal change into a structured screening decision with clinical/kinematic meaning. Phase 8/9 provides the *mechanism*; Step 10 provides the *clinical screening logic*.

---

## 2. Flexion Convention & Naming Reconciliation

### Joint Angle Convention:
*   Knee joint angles are measured as the sagittal angle between the thigh and shank.
*   Standing extension corresponds to $\approx 180^\circ$ (collinear alignment).
*   Flexing the knee decreases the joint angle (approaching $0^\circ$).
*   Therefore:
    *   **Lower joint angle = More knee flexion (physically deeper).**
    *   **Higher joint angle = Less knee flexion (physically shallower).**

### Reconciliation with Squat/Lunge Findings:
*   In the REHAB24-6 squat cohort, correct reps have a mean peak flexion angle of $60.85^\circ$ (shallower), while incorrect reps have a mean of $41.14^\circ$ (deeper). This yields a Cohen's d of $+1.73$ (representing correct reps having a larger joint angle).
*   Because incorrect reps exhibit a *smaller* knee angle, they represent an **increase in flexion depth (physically deeper)**.
*   The rule is defined as `x_peak < base - NF`. Since a decrease in joint angle represents physically deeper movement, this rule is named **EXCESS_DEPTH** (representing excessive knee flexion depth relative to baseline). This matches the actual biomechanics and the findings in the squat and lunge chapters.

---

## 3. Cohort Data Distributions & Threshold Grounding

To establish grounded screening rules, we analyze correct-rep (Label 1) and incorrect-rep (Label 0) distributions in the `REHAB24-6` squat (n=98 reps) and lunge (n=61 reps) cohorts.

### A. Squat Cohort Distributions (n = 72 Correct, 26 Incorrect)
1.  **Peak Knee Flexion (`peak_flexion_deg`):**
    *   *Correct (Label 1):* Mean = $60.85^\circ$, SD = $12.72^\circ$, Range = ($36.32^\circ$, $84.73^\circ$)
    *   *Incorrect (Label 0):* Mean = $41.14^\circ$, SD = $6.08^\circ$, Range = ($31.91^\circ$, $56.47^\circ$)
    *   *Direction:* Smaller joint angle represents more flexion (physically deeper). Incorrect reps exhibit a **flexion increase / deep squat shift** (Mean Shift: $-19.71^\circ$).
2.  **Range of Motion (`rom_deg`):**
    *   *Correct (Label 1):* Mean = $111.19^\circ$, SD = $18.06^\circ$, Range = ($73.90^\circ$, $141.44^\circ$)
    *   *Incorrect (Label 0):* Mean = $134.31^\circ$, SD = $7.23^\circ$, Range = ($118.83^\circ$, $145.16^\circ$)
    *   *Direction:* Because incorrect reps are deeper, they cover a **greater joint range of motion** (Mean Shift: $+23.13^\circ$).
3.  **Descent Velocity (`velocity` in deg/s, converted from deg/frame by multiplying by 30):**
    *   *Correct (Label 1):* Mean = $66.94^\circ/\text{s}$, SD = $22.24^\circ/\text{s}$, Range = ($30.22^\circ/\text{s}$, $121.53^\circ/\text{s}$)
    *   *Incorrect (Label 0):* Mean = $83.14^\circ/\text{s}$, SD = $16.22^\circ/\text{s}$, Range = ($59.82^\circ/\text{s}$, $110.62^\circ/\text{s}$)
    *   *Direction:* Incorrect reps exhibit a **faster eccentric descent** (Mean Shift: $+16.20^\circ/\text{s}$).

### B. Lunge Cohort Distributions (n = 25 Correct, 36 Incorrect)
1.  **Peak Knee Flexion (`peak_flexion_deg`):**
    *   *Correct (Label 1):* Mean = $89.66^\circ$, SD = $8.33^\circ$, Range = ($57.55^\circ$, $113.00^\circ$)
    *   *Incorrect (Label 0):* Mean = $68.03^\circ$, SD = $15.11^\circ$, Range = ($46.79^\circ$, $105.27^\circ$)
    *   *Direction:* Incorrect lunges represent a **deeper knee flexion shift** (Mean Shift: $-21.63^\circ$).
2.  **Range of Motion (`rom_deg`):**
    *   *Correct (Label 1):* Mean = $59.02^\circ$, SD = $20.94^\circ$, Range = ($27.31^\circ$, $119.75^\circ$)
    *   *Incorrect (Label 0):* Mean = $90.30^\circ$, SD = $27.00^\circ$, Range = ($42.27^\circ$, $127.63^\circ$)
    *   *Direction:* Incorrect lunges cover a **greater joint range of motion** (Mean Shift: $+31.28^\circ$).
3.  **Descent Velocity (`velocity` in deg/s, front leg descent):**
    *   *Correct (Label 1):* Mean = $30.39^\circ/\text{s}$, SD = $8.26^\circ/\text{s}$
    *   *Incorrect (Label 0):* Mean = $52.64^\circ/\text{s}$, SD = $24.04^\circ/\text{s}$
    *   *Direction:* Incorrect lunges exhibit a **faster step drop / eccentric descent** (Mean Shift: $+22.25^\circ/\text{s}$).

---

## 4. Personalised Gating Rules & Threshold Verification

We implement **Personalised-Deviation Screening**, where repetitions are gated against the subject's own baseline mean using the validated Phase 7 noise floors (Peak Flexion: $\pm 11.99^\circ$, ROM: $\pm 23.17^\circ$, Descent Velocity: $\pm 40.86^\circ/\text{s}$).

### Validation of Thresholds via Cohort Shifts:
Comparing the Phase 7 validated noise floors against the empirical correct-to-incorrect cohort shifts validates this choice:
*   **Peak Flexion:** Noise floor is $\pm 11.99^\circ$. The cohort shifts ($19.71^\circ$ for squats, $21.63^\circ$ for lunges) exceed this floor, meaning the twin can reliably flag depth deviations.
*   **Range of Motion:** Noise floor is $\pm 23.17^\circ$. The cohort shifts ($23.13^\circ$ for squats, $31.28^\circ$ for lunges) meet or exceed this floor, rendering ROM a viable gating biomarker.
*   **Descent Velocity:** Noise floor is $\pm 40.86^\circ/\text{s}$. The cohort shifts ($16.20^\circ/\text{s}$ for squats, $22.25^\circ/\text{s}$ for lunges) are *smaller* than the noise floor. This mathematically explains why velocity does not independently flag deviations: the monocular measurement uncertainty is too wide to resolve these shifts.

---

## 5. Personalised Gating Rules

Let $\mu_{\text{base}, i}$ be the subject's active baseline mean, $x_i$ be the joint angle/speed of the test repetition, and $NF_i$ be the validated Phase 7 noise floor.

### A. Squat Screening Rules

1.  **Rule S1: Excess Squat Depth / Deep Flexion (EXCESS_DEPTH)**
    *   *Gating Check:* $x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - NF_{\text{peak}}$  (where $NF_{\text{peak}} = 11.99^\circ$)
    *   *Biomechanics:* Joint angle decreases below baseline beyond measurement noise, indicating an uncontrolled deep drop.
2.  **Rule S2: Uncontrolled Squat Speed (EXCESS_VELOCITY)**
    *   *Gating Check:* $x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + NF_{\text{velocity}}$  (where $NF_{\text{velocity}} = 40.86^\circ/\text{s}$)
    *   *Biomechanics:* Joint speed exceeds baseline beyond measurement noise, showing rapid descent.
3.  **Rule S3: Excess Squat Range of Motion (EXCESS_ROM)**
    *   *Gating Check:* $x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + NF_{\text{rom}}$  (where $NF_{\text{rom}} = 23.17^\circ$)
    *   *Biomechanics:* Joint excursion exceeds baseline beyond measurement noise.

### B. Lunge Screening Rules

1.  **Rule L1: Excess Lunge Depth / Deep Flexion (EXCESS_DEPTH)**
    *   *Gating Check:* $x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - NF_{\text{peak}}$  (where $NF_{\text{peak}} = 11.99^\circ$)
    *   *Biomechanics:* Joint angle decreases below baseline beyond measurement noise, representing excessive depth.
2.  **Rule L2: Uncontrolled Lunge Speed (EXCESS_VELOCITY)**
    *   *Gating Check:* $x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + NF_{\text{velocity}}$  (where $NF_{\text{velocity}} = 40.86^\circ/\text{s}$)
    *   *Biomechanics:* Exceeds baseline speed beyond measurement noise.
3.  **Rule L3: Excess Lunge Range of Motion (EXCESS_ROM)**
    *   *Gating Check:* $x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + NF_{\text{rom}}$  (where $NF_{\text{rom}} = 23.17^\circ$)
    *   *Biomechanics:* Exceeds baseline excursion beyond measurement noise.

---

## 6. Screening Decision Logic

For each repetition:
1.  Apply the exercise-specific gating checks.
2.  Compile the list of fired rules:
    $$\text{FiredRules} = \{ \text{Rule } R \text{ that evaluates to True} \}$$
3.  Assign the overall **Screening Flag**:
    *   If $\text{FiredRules} \ne \emptyset$: **SCREENING_POSITIVE**
        *   *Reason recorded:* The specific list of rules that fired (e.g., `["EXCESS_DEPTH"]`).
    *   If $\text{FiredRules} = \emptyset$: **NOT_FLAGGED**
        *   *Reason recorded:* `[]`.

---

## 7. Worked-Demo Plan (Stage 2) & Active ROM Firing Verification

The screening rules will be applied to the 10 repetitions of Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) from the `REHAB24-6` dataset.

### Verification of EXCESS_ROM Rule Firing:
*   **Squat Subject 8:** Baseline ROM $= 105.50^\circ$. Gated Noise Floor $= 23.17^\circ$. Incorrect Reps 6–10 have ROM values of $136.50^\circ$, $129.84^\circ$, $132.53^\circ$, $140.93^\circ$, and $142.20^\circ$. This yields deltas of $+31.0^\circ$, $+24.34^\circ$, $+27.03^\circ$, $+35.43^\circ$, and $+36.70^\circ$. **All 5 reps exceed the $23.17^\circ$ threshold and actively fire the `EXCESS_ROM` rule.**
*   **Lunge Subject 6:** Baseline ROM $= 76.78^\circ$. Gated Noise Floor $= 23.17^\circ$. Incorrect Reps 6–10 have ROM values of $117.28^\circ$, $117.52^\circ$, $107.59^\circ$, $119.66^\circ$, and $121.79^\circ$. This yields deltas of $+40.50^\circ$, $+40.74^\circ$, $+30.81^\circ$, $+42.88^\circ$, and $+45.01^\circ$. **All 5 reps exceed the $23.17^\circ$ threshold and actively fire the `EXCESS_ROM` rule.**

This confirms the `EXCESS_ROM` rule is highly active on this data and will not remain inert.

### Expected Firing Output (Squat Subject 8):
*   **Reps 1–2 (Baseline):** Used to compute baseline references. Flagged as `NOT_FLAGGED` by definition.
*   **Reps 3–5 (Quiet correct test reps):** Should return `NOT_FLAGGED` because they remain within noise floor limits.
*   **Reps 6–10 (Firing incorrect test reps):**
    *   *Rep 6:* Flexion delta $= 29.76^\circ$ ($> 11.99^\circ$), Velocity delta $= 60.68^\circ/\text{s}$ ($> 40.86^\circ/\text{s}$), ROM delta $= 31.00^\circ$ ($> 23.17^\circ$). Fired: `["EXCESS_DEPTH", "EXCESS_VELOCITY", "EXCESS_ROM"]` $\rightarrow$ `SCREENING_POSITIVE`.
    *   *Reps 7–10:* Flexion and ROM deltas exceed their respective noise floors. Fired: `["EXCESS_DEPTH", "EXCESS_ROM"]` $\rightarrow$ `SCREENING_POSITIVE`.

### Output Deliverables:
*   Save the results to `20_screening_outputs/worked_example_screening.csv`.
*   We will save derivatives to `20_screening_outputs/`.
