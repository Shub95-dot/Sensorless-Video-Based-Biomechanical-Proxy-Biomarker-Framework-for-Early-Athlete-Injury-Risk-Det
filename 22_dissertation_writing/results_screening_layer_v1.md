# Chapter 10: Rule-Based Screening Layer

This chapter presents the design, implementation, and verification of the rule-based screening layer (Step 10 of the biomechanical processing pipeline). While lower layers of the pipeline track raw joint coordinate data and calculate kinematics, clinical application requires interpreting these measurements into structured screening decisions. This chapter details a screening layer that converts joint angle deviations into named screening flags representing known, literature-grounded kinematic compensation patterns. First, we outline the purpose and framing of the screening layer as a core pipeline deliverable. Second, we establish the critical distinction between generic tracking and named-rule screening. Third, we justify the selection of a personalised-deviation screening modality over population-wide thresholds based on camera projection geometry. Fourth, we define the screening rules and ground their directions in cohort distributions. Finally, we demonstrate the applied results using squat and lunge worked examples and establish the boundaries of the screening layer's claims.

---

## 10.1. Purpose and Core Deliverable Framing

The rule-based screening layer represents Step 10 of the primary pipeline architecture [source: 20_screening_outputs/screening_rules_design.md]. It is a core **Track A deliverable**, differentiating it from the Track B architectural demonstrations (such as the digital twin sequence models) [source: 20_screening_outputs/screening_rules_design.md]. 

The primary purpose of this layer is to act as the transparent decision-making foundation of the clinical screening tool. It ingests kinematics (joint angles, ranges of motion, and velocities) and outputs a binary screening status (`SCREENING_POSITIVE` or `NOT_FLAGGED`) along with the specific list of rules that were triggered [source: 20_screening_outputs/screening_rules_design.md]. Because the screening checks are structured as deterministic, explicit logical statements, this layer remains completely transparent. This transparency is essential because it forms the exact decision layer that the subsequent Counterfactual Explainable AI (XAI) component (Step 11) is designed to explain, providing clinical users with clear, mathematical justifications for every screening outcome.

---

## 10.2. Critical Distinction: Screening vs. Tracking

To prevent clinical misinterpretation, it is essential to distinguish this screening layer (Step 10) from the personalised tracking baselines presented in Chapters 9 and 11 [source: 22_dissertation_writing/results_baseline_v1.md / results_digital_twin_v1.md]:
*   **Generic Tracking (Chapters 9 and 11)**: Evaluates a generic mathematical question: *"Has this repetition shifted from the subject's reference by an amount exceeding measurement uncertainty?"* [source: 22_dissertation_writing/results_baseline_v1.md]. This check is directional-agnostic and biomechanically-blind; it simply flags any statistically significant signal change as a generic deviation.
*   **Named-Rule Screening (Chapter 10)**: Ingests the raw deviations detected by the tracking engine and maps them to **Named Screening Rules** (such as `EXCESS_DEPTH`, `EXCESS_ROM`, and `EXCESS_VELOCITY`) with direction-specific thresholds [source: 20_screening_outputs/screening_rules_design.md]. It evaluates: *"Does this deviation match a known kinematic pattern associated with elevated injury risk or technique compensation?"* [source: 20_screening_outputs/screening_rules_design.md]. 

Tracking asks "did something change," whereas screening asks "does this change represent a specific, predefined movement restriction." This chapter defines the clinical screening logic that sits on top of the underlying tracking mechanism.

---

## 10.3. Screening Modality Choice (Option B)

When designing a marklerless pose estimation screening layer, two primary modalities can be implemented to evaluate joint kinematics [source: 20_screening_outputs/screening_rules_design.md]:
1.  **Option A (Fixed Population Thresholds)**: Gating joint values against absolute, cohort-wide normal values (e.g., flagging any squat where knee flexion exceeds $60^\circ$).
2.  **Option B (Personalised-Deviation Screening)**: Gating deviations against the subject's own baseline mean plus the validated measurement noise floor [source: 20_screening_outputs/screening_rules_design.md].

We selected **Option B (Personalised-Deviation Screening)** and rejected Option A [source: 20_screening_outputs/screening_rules_design.md]. This choice is justified by the camera projection characteristics validated in Chapter 6 [source: 22_dissertation_writing/results_dropjump_validation_v1.md]:
*   Monocular pose estimation is subject to systematic projection bias (overestimation or underestimation) caused by the angle between the subject's sagittal plane and the camera's optical axis [source: 22_dissertation_writing/results_dropjump_validation_v1.md].
*   Because this perspective angle is constant within a single subject's testing session, the resulting projection bias is also constant (systematic offset) [source: 22_dissertation_writing/results_dropjump_validation_v1.md].
*   By calculating deviations relative to the subject's own session baseline, this systematic projection bias is mathematically subtracted:
    $$\Delta_i = |x_{\text{test}} - \mu_{\text{base}}| = |(x_{\text{true}} + \text{bias}) - (\mu_{\text{true}} + \text{bias})| = |x_{\text{true}} - \mu_{\text{true}}|$$
*   This makes Option B highly robust to camera perspective offsets. In contrast, population-wide absolute thresholds (Option A) would false-alarm or fail to detect deviations because perspective offsets vary between subjects, making a universal absolute threshold unviable for monocular video [source: 20_screening_outputs/screening_rules_design.md].

---

## 10.4. Rules Definition and Cohort-Level Grounding

To design clinically relevant screening rules, we analyze joint angle conventions and cohort-level correct-vs-incorrect distributions from Chapters 4 and 5 [source: 20_screening_outputs/screening_rules_design.md].

### 10.4.1. Joint Angle Convention and Directional Meaning
Sagittal knee joint angles are defined as the angle between the thigh and shank segments:
*   collinear extension corresponds to $\approx 180^\circ$ [source: 20_screening_outputs/screening_rules_design.md].
*   Flexion decreases the joint angle (approaching $0^\circ$) [source: 20_screening_outputs/screening_rules_design.md].
*   Therefore, a **lower joint angle** represents **more knee flexion (physically deeper)**, while a **higher joint angle** represents **less knee flexion (physically shallower)** [source: 20_screening_outputs/screening_rules_design.md].

### 10.4.2. Grounding Rules in Cohort Distributions
Comparing the correct (Label 1) and incorrect (Label 0) distributions in the `REHAB24-6` squat (n=98 reps) and lunge (n=61 reps) cohorts grounds the direction of each rule [source: 20_screening_outputs/screening_rules_design.md]:

1.  **Peak Knee Flexion (`peak_flexion`)**:
    *   *Squat Cohort*: Correct reps mean = $60.85^\circ \pm 12.72^\circ$; Incorrect reps mean = $41.14^\circ \pm 6.08^\circ$ (representing correct reps having a larger joint angle, Cohen's d = $+1.7306$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Lunge Cohort*: Correct reps mean = $89.66^\circ \pm 8.33^\circ$; Incorrect reps mean = $68.03^\circ \pm 15.11^\circ$ (effect size d = $1.6904$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Interpretation*: Incorrect repetitions in both exercises exhibit a smaller knee angle, which physically represents a shift towards **excessive flexion depth (deeper movement)** (Mean Shifts: $-19.71^\circ$ for squats, $-21.63^\circ$ for lunges) [source: 20_screening_outputs/screening_rules_design.md]. 
    *   *Rule Grounding*: This grounds the **EXCESS_DEPTH** rule, which fires when knee flexion angle drops below baseline:
        $$x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - NF_{\text{peak}}$$
2.  **Range of Motion (`rom`)**:
    *   *Squat Cohort*: Correct mean = $111.19^\circ \pm 18.06^\circ$; Incorrect mean = $134.31^\circ \pm 7.23^\circ$ (Mean Shift: $+23.13^\circ$, Cohen's d = $-1.4484$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Lunge Cohort*: Correct mean = $59.02^\circ \pm 20.94^\circ$; Incorrect mean = $90.30^\circ \pm 27.00^\circ$ (Mean Shift: $+31.28^\circ$, effect size d = $-1.2653$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Interpretation*: Because incorrect repetitions achieve excessive depth, they cover a **greater joint range of motion** [source: 20_screening_outputs/screening_rules_design.md].
    *   *Rule Grounding*: This grounds the **EXCESS_ROM`** rule, which fires when the movement excursion exceeds baseline:
        $$x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + NF_{\text{rom}}$$
3.  **Descent Velocity (`descent_velocity`)**:
    *   *Squat Cohort*: Correct mean = $66.94^\circ/\text{s} \pm 22.24^\circ/\text{s}$; Incorrect mean = $83.14^\circ/\text{s} \pm 16.22^\circ/\text{s}$ (Mean Shift: $+16.20^\circ/\text{s}$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Lunge Cohort*: Correct mean = $30.39^\circ/\text{s} \pm 8.26^\circ/\text{s}$; Incorrect mean = $52.64^\circ/\text{s} \pm 24.04^\circ/\text{s}$ (Mean Shift: $+22.25^\circ/\text{s}$) [source: 20_screening_outputs/screening_rules_design.md].
    *   *Biomechanical Interpretation*: Incorrect reps are performed with a **faster eccentric descent** [source: 20_screening_outputs/screening_rules_design.md].
    *   *Rule Grounding*: This grounds the **EXCESS_VELOCITY** rule, which fires when the speed exceeds baseline:
        $$x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + NF_{\text{velocity}}$$

It is critical to note that these thresholds are **screening heuristics** derived from this cohort's empirical distributions, not validated clinical diagnostic cut-offs. They represent logical filters designed to screen for deviations, not diagnostic criteria.

### 10.4.3. Validated Noise Floors
The gating noise floors ($NF_i$) transferred from Chapter 8 are [source: 20_screening_outputs/screening_rules_design.md]:
*   $NF_{\text{peak}} = \mathbf{11.99^\circ}$
*   $NF_{\text{rom}} = \mathbf{23.17^\circ}$
*   $NF_{\text{velocity}} = \mathbf{40.86^\circ/\text{s}}$

---

## 10.5. Applied Results

The screening rules were executed on Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) from the `REHAB24-6` dataset [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.1. Squat Screening Results (Subject `PM_113`)
*   **Baseline (Reps 1–2)**: Established the baseline means: peak flexion = **$72.98^\circ$**, ROM = **$105.50^\circ$**, and descent velocity = **$49.94^\circ/\text{s}$** [source: 20_screening_outputs/worked_example_screening.csv]. 
*   **Gating Thresholds**:
    *   `EXCESS_DEPTH` fires if $x_{\text{peak}} < \mathbf{60.99^\circ}$ ($72.98^\circ - 11.99^\circ$) [source: 20_screening_outputs/worked_example_screening.csv].
    *   `EXCESS_ROM` fires if $x_{\text{rom}} > \mathbf{128.67^\circ}$ ($105.50^\circ + 23.17^\circ$) [source: 20_screening_outputs/worked_example_screening.csv].
    *   `EXCESS_VELOCITY` fires if $x_{\text{velocity}} > \mathbf{90.80^\circ/\text{s}}$ ($49.94^\circ/\text{s} + 40.86^\circ/\text{s}$) [source: 20_screening_outputs/worked_example_screening.csv].
*   **Quiet-Test Reps (Reps 3–5)**: All correct repetitions stayed within noise limits, returning a status of **`NOT_FLAGGED`** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Firing-Test Reps (Reps 6–10)**: All five incorrect repetitions triggered screening flags, returning **`SCREENING_POSITIVE`** [source: 20_screening_outputs/worked_example_screening.csv]:
    *   *Repetition 6*: Peak flexion was $43.22^\circ$ (margin: **$17.77^\circ$**), ROM was $136.50^\circ$ (margin: **$7.83^\circ$**), and velocity reached $110.62^\circ/\text{s}$ (margin: **$19.82^\circ/\text{s}$**) [source: 20_screening_outputs/worked_example_screening.csv]. Fired: `["EXCESS_DEPTH", "EXCESS_VELOCITY", "EXCESS_ROM"]`.
    *   *Repetitions 7–10*: All reps exceeded depth and ROM noise floors. Fired: `["EXCESS_DEPTH", "EXCESS_ROM"]` [source: 20_screening_outputs/worked_example_screening.csv]. Flexion margins ranged from **$11.24^\circ$ to $23.67^\circ$**, while ROM margins ranged from **$1.18^\circ$ to $13.54^\circ$** [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.2. Lunge Screening Results (Subject `PM_104`)
*   **Baseline (Reps 1–2)**: Established baseline means: peak flexion = **$84.66^\circ$**, ROM = **$76.78^\circ$**, velocity = **$32.68^\circ/\text{s}$** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Gating Thresholds**:
    *   `EXCESS_DEPTH` fires if $x_{\text{peak}} < \mathbf{72.68^\circ}$ [source: 20_screening_outputs/worked_example_screening.csv].
    *   `EXCESS_ROM` fires if $x_{\text{rom}} > \mathbf{99.95^\circ}$ [source: 20_screening_outputs/worked_example_screening.csv].
    *   `EXCESS_VELOCITY` fires if $x_{\text{velocity}} > \mathbf{73.54^\circ/\text{s}}$ [source: 20_screening_outputs/worked_example_screening.csv].
*   **Quiet-Test Reps (Reps 3–5)**: Correct repetitions stayed within noise floors, returning **`NOT_FLAGGED`** [source: 20_screening_outputs/worked_example_screening.csv].
*   **Firing-Test Reps (Reps 6–10)**: All incorrect reps returned **`SCREENING_POSITIVE`**, triggering `["EXCESS_DEPTH", "EXCESS_ROM"]` [source: 20_screening_outputs/worked_example_screening.csv]. Peak flexion margins ranged from **$8.92^\circ$ to $19.99^\circ$**, and ROM margins ranged from **$7.65^\circ$ to $21.85^\circ$** [source: 20_screening_outputs/worked_example_screening.csv]. Velocity remained within the wide noise floor ($73.54^\circ/\text{s}$), so it did not fire [source: 20_screening_outputs/worked_example_screening.csv].

### 10.5.3. Ground Truth Validation Aside
The screening layer's flags aligned with the dataset's ground truth correct/incorrect labels (100% agreement across the test reps). It is critical to state that this alignment represents a coincidental validation check using the dataset's labelling scheme. It does **not** indicate that the screening layer classifies "correctness" or issues form quality verdicts. The screening layer's role is strictly to detect and report kinematic deviations exceeding camera noise, not to judge performance quality [source: 20_screening_outputs/screening_rules_design.md].

---

## 10.6. Does Not Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of the screening layer:
*   **No Diagnostic Verdicts**: The screening flags (e.g., `SCREENING_POSITIVE`) are kinematic classifications representing shifts beyond baseline, not clinical or medical diagnoses.
*   **No Clinical Cut-Offs**: The thresholds (such as the $\pm 11.99^\circ$ noise floor) are camera-uncertainty heuristics derived from the cohort's distributions, not validated clinical diagnostic thresholds [source: 20_screening_outputs/screening_rules_design.md].
*   **Not a Trained ML Model**: The screening layer does not utilize machine learning weights, neural networks, or optimization algorithms. It is a deterministic, rule-based logic gate that is fully explainable by construction [source: 20_screening_outputs/screening_rules_design.md].
*   **No Injury Forecasting**: The layer detects active movement deviations; it does not forecast future injury likelihood or compute clinical risk scores.
