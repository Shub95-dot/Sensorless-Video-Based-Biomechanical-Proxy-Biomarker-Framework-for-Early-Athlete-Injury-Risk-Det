# Chapter 10: Rule-Based Screening Layer

This chapter presents the design, implementation, and verification of the rule-based screening layer (Step 10 of the biomechanical processing pipeline). While lower pipeline layers track raw joint coordinate data and calculate kinematics, clinical application requires interpreting these measurements into structured screening decisions. This chapter details a screening layer that converts joint angle deviations into named screening flags representing known, literature-grounded kinematic compensation patterns.

---

## 10.1. Purpose and Core Deliverable Framing

The rule-based screening layer represents Step 10 of the primary pipeline architecture and serves as a core **Track A deliverable** [source: 20_screening_outputs/screening_rules_design.md]. This distinguishes it from Track B architectural demonstrations (such as the digital twin sequence models), establishing it as the primary functional component of the screening system [source: 20_screening_outputs/screening_rules_design.md].

The primary purpose of this layer is to act as the transparent decision-making foundation of the clinical screening tool. It ingests kinematics (joint angles, ranges of motion, and velocities) and outputs a binary screening status (`SCREENING_POSITIVE` or `NOT_FLAGGED`) along with the specific list of rules triggered [source: 20_screening_outputs/screening_rules_design.md]. Because screening checks are structured as deterministic, explicit logical statements, this layer remains completely transparent. This transparency is essential because it forms the exact decision layer that the subsequent Counterfactual Explainable AI (XAI) component (Step 11) is designed to explain, providing clinical users with clear mathematical justifications for every screening outcome.

---

## 10.2. Critical Distinction: Screening vs. Tracking

It is essential to distinguish this screening layer (Step 10) from the personalised tracking baselines (Chapters 9 and 11) [source: 22_dissertation_writing/results_baseline_v1.md / results_digital_twin_v1.md]:
*   **Generic Tracking (Chapters 9 and 11)**: Evaluates a generic mathematical question: *"Has this repetition shifted from the subject's reference by an amount exceeding measurement uncertainty?"* [source: 22_dissertation_writing/results_baseline_v1.md]. This check is direction-agnostic and biomechanically blind; it simply flags any statistically significant signal change as a generic deviation.
*   **Named-Rule Screening (Chapter 10)**: Ingests raw deviations detected by the tracking engine and maps them to **Named Screening Rules** (`EXCESS_DEPTH`, `EXCESS_ROM`, and `EXCESS_VELOCITY`) with direction-specific thresholds [source: 20_screening_outputs/screening_rules_design.md]. It evaluates: *"Does this deviation match a known kinematic pattern associated with elevated injury risk or technique compensation?"* [source: 20_screening_outputs/screening_rules_design.md].

Tracking asks if something changed; screening asks if that change represents a specific, predefined movement deviation.

---

## 10.3. Screening Modality Choice (Option B)

Two primary modalities can evaluate joint kinematics in markerless pose estimation [source: 20_screening_outputs/screening_rules_design.md]:
1.  **Option A (Fixed Population Thresholds)**: Gating joint values against absolute, cohort-wide normal values (e.g., flagging any squat where knee flexion exceeds $60^\circ$).
2.  **Option B (Personalised-Deviation Screening)**: Gating deviations against the subject's own baseline mean plus the validated measurement noise floor [source: 20_screening_outputs/screening_rules_design.md].

We selected **Option B (Personalised-Deviation Screening)** and rejected Option A [source: 20_screening_outputs/screening_rules_design.md]. Monocular pose estimation is subject to systematic projection bias (overestimation or underestimation) caused by the angle between the subject's sagittal plane and the camera's optical axis [source: 22_dissertation_writing/results_dropjump_validation_v1.md]. Because this perspective angle is constant within a single subject's testing session, the resulting projection bias is also constant. By calculating deviations relative to the subject's session baseline, this systematic projection bias is mathematically cancelled:
$$\Delta_i = |x_{\text{test}} - \mu_{\text{base}}| = |(x_{\text{true}} + \text{bias}) - (\mu_{\text{true}} + \text{bias})| = |x_{\text{true}} - \mu_{\text{true}}|$$

This makes Option B highly robust to camera perspective offsets. In contrast, Option A would false-alarm or fail to detect deviations because perspective offsets vary unpredictably between subjects and camera setups, rendering universal absolute thresholds unviable for monocular video screening [source: 20_screening_outputs/screening_rules_design.md].

---

## 10.4. Rules Definition and Cohort-Level Grounding

Sagittal knee joint angles represent included angles between thigh and shank segments ($\approx 180^\circ$ = full extension; smaller angles = deeper flexion) [source: 20_screening_outputs/screening_rules_design.md]. Comparing correct and incorrect distributions in the `REHAB24-6` squat ($n=98$) and lunge ($n=61$) cohorts grounds the direction of each rule [source: 20_screening_outputs/screening_rules_design.md]:

### 10.4.1. The Three Named Screening Rules
1.  **Peak Knee Flexion (`EXCESS_DEPTH`)**:
    *   *Squat Cohort*: Correct mean = $60.85^\circ \pm 12.72^\circ$; Incorrect mean = $41.14^\circ \pm 6.20^\circ$ ($d = +1.7306$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
    *   *Lunge Cohort*: Correct mean = $89.66^\circ \pm 8.33^\circ$; Incorrect mean = $68.03^\circ \pm 15.11^\circ$ ($d = 1.6904$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Grounding*: Incorrect repetitions exhibit smaller joint angles, representing a shift toward excessive flexion depth (mean shifts: $-19.71^\circ$ for squats, $-21.63^\circ$ for lunges). The **EXCESS_DEPTH** rule fires when knee flexion angle drops below baseline minus noise floor:
        $$x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - NF_{\text{peak}}$$
2.  **Range of Motion (`EXCESS_ROM`)**:
    *   *Squat Cohort*: Correct mean = $111.19^\circ \pm 18.06^\circ$; Incorrect mean = $134.31^\circ \pm 7.23^\circ$ ($d = -1.4484$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Lunge Cohort*: Correct mean = $59.02^\circ \pm 20.94^\circ$; Incorrect mean = $90.30^\circ \pm 27.00^\circ$ ($d = -1.2653$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Grounding*: Excessive depth causes incorrect repetitions to cover greater joint excursion (mean shifts: $+23.13^\circ$ for squats, $+31.28^\circ$ for lunges). The **EXCESS_ROM** rule fires when joint excursion exceeds baseline plus noise floor:
        $$x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + NF_{\text{rom}}$$
3.  **Descent Velocity (`EXCESS_VELOCITY`)**:
    *   *Squat Cohort*: Correct mean = $66.94^\circ/\text{s} \pm 22.24^\circ/\text{s}$; Incorrect mean = $83.14^\circ/\text{s} \pm 16.22^\circ/\text{s}$ (shift: $+16.20^\circ/\text{s}$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Lunge Cohort*: Correct mean = $30.39^\circ/\text{s} \pm 8.26^\circ/\text{s}$; Incorrect mean = $52.64^\circ/\text{s} \pm 24.04^\circ/\text{s}$ (shift: $+22.25^\circ/\text{s}$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Grounding*: Incorrect repetitions exhibit faster eccentric descent. The **EXCESS_VELOCITY** rule fires when descent speed exceeds baseline plus noise floor:
        $$x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + NF_{\text{velocity}}$$

It is critical to emphasize that these thresholds are screening heuristics derived from empirical distributions, not validated clinical diagnostic cut-offs.

### 10.4.2. Applied Noise Floors
Gating noise floors ($NF_i$) transferred from Chapter 8 ground-truth validation are [source: 20_screening_outputs/screening_rules_design.md]:
*   $NF_{\text{peak}} = \mathbf{11.99^\circ}$
*   $NF_{\text{rom}} = \mathbf{23.17^\circ}$
*   $NF_{\text{velocity}} = \mathbf{40.86^\circ/\text{s}}$

---

## 10.5. Applied Results

The screening rules were executed on Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) from `REHAB24-6` [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.1. Squat Screening Results (Subject `PM_113`)
*   **Baseline Means (Reps 1–2)**: Peak flexion = **$72.98^\circ$**, ROM = **$105.50^\circ$**, descent velocity = **$49.94^\circ/\text{s}$** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Gating Thresholds**: `EXCESS_DEPTH` $< \mathbf{60.99^\circ}$ ($72.98^\circ - 11.99^\circ$); `EXCESS_ROM` $> \mathbf{128.67^\circ}$ ($105.50^\circ + 23.17^\circ$); `EXCESS_VELOCITY` $> \mathbf{90.80^\circ/\text{s}}$ ($49.94^\circ/\text{s} + 40.86^\circ/\text{s}$) [source: 20_screening_outputs/worked_example_screening.csv].
*   **Quiet-Test Reps (Reps 3–5)**: Correct repetitions stayed within noise limits, returning **`NOT_FLAGGED`** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Firing-Test Reps (Reps 6–10)**: All five incorrect repetitions returned **`SCREENING_POSITIVE`** [source: 20_screening_outputs/worked_example_screening.csv]:
    *   *Repetition 6*: Peak flexion $43.22^\circ$ (margin: **$17.77^\circ$**), ROM $136.50^\circ$ (margin: **$7.83^\circ$**), velocity $110.62^\circ/\text{s}$ (margin: **$19.82^\circ/\text{s}$**). Fired: `["EXCESS_DEPTH", "EXCESS_VELOCITY", "EXCESS_ROM"]` [source: 20_screening_outputs/worked_example_screening.csv].
    *   *Repetitions 7–10*: Flexion margins ranged from **$11.24^\circ$ to $23.67^\circ$**; ROM margins ranged from **$1.18^\circ$ to $13.54^\circ$**. Fired: `["EXCESS_DEPTH", "EXCESS_ROM"]` [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.2. Lunge Screening Results (Subject `PM_104`)
*   **Baseline Means (Reps 1–2)**: Peak flexion = **$84.66^\circ$**, ROM = **$76.78^\circ$**, velocity = **$32.68^\circ/\text{s}$** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Gating Thresholds**: `EXCESS_DEPTH` $< \mathbf{72.68^\circ}$; `EXCESS_ROM` $> \mathbf{99.95^\circ}$; `EXCESS_VELOCITY` $> \mathbf{73.54^\circ/\text{s}}$ [source: 20_screening_outputs/worked_example_screening.csv].
*   **Quiet-Test Reps (Reps 3–5)**: Returned **`NOT_FLAGGED`** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Firing-Test Reps (Reps 6–10)**: All incorrect reps returned **`SCREENING_POSITIVE`**, triggering `["EXCESS_DEPTH", "EXCESS_ROM"]` [source: 20_screening_outputs/worked_example_screening.csv]. Peak flexion margins ranged from **$8.92^\circ$ to $19.99^\circ$**; ROM margins ranged from **$7.65^\circ$ to $21.85^\circ$** [source: 20_screening_outputs/worked_example_screening.csv]. Velocity stayed within noise floor ($73.54^\circ/\text{s}$), so it did not fire [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.3. Ground Truth Alignment Note
Alignment with dataset ground-truth labels (100% agreement across test reps) represents a coincidental validation check using the dataset's labelling scheme. It does **not** indicate that the screening layer classifies "correctness" or issues form quality verdicts. The screening layer's operational role is strictly to detect and report kinematic deviations exceeding camera noise, not to judge performance quality [source: 20_screening_outputs/screening_rules_design.md].

---

## 10.6. Boundaries and What This Layer Does NOT Claim

To maintain scientific integrity and align with screening scope across this dissertation:
*   **No Diagnostic Verdicts**: Screening flags (e.g., `SCREENING_POSITIVE`) are kinematic classifications representing baseline shifts, not clinical or medical diagnoses.
*   **No Clinical Cut-Offs**: Thresholds (such as $\pm 11.99^\circ$) are camera-uncertainty heuristics derived from empirical distributions, not validated clinical diagnostic thresholds [source: 20_screening_outputs/screening_rules_design.md].
*   **Not a Trained ML Model**: The layer uses no machine learning weights or neural networks. It is a deterministic, rule-based logic gate, fully explainable by construction [source: 20_screening_outputs/screening_rules_design.md].
*   **No Injury Forecasting**: The layer detects active movement deviations; it does not forecast future injury likelihood or compute clinical risk scores.
