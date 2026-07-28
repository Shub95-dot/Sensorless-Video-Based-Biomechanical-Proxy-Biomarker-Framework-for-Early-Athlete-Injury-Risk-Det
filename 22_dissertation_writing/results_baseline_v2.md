# Chapter 9: Personalised Session-to-Session Baselines

This chapter presents the design and empirical demonstration of an individualised kinematic progression-tracking framework. Group-level cohort analyses (Chapters 4 and 5) evaluate differences across populations, but clinical rehabilitation and performance tracking require monitoring an individual relative to their own baseline template. We describe an architecture that constructs a personalised baseline from a subject's initial correct repetitions and gates subsequent trials against the monocular pipeline's validated measurement-noise floor derived in Chapter 8.

---

## 9.1. Purpose and Design Motivation

Group-level cohort analyses demonstrate population-wide execution differences [source: 22_dissertation_writing/results_squat_v1.md / results_lunge_v1.md]. However, clinical therapy and athletic coaching are fundamentally individualised. Every athlete possesses unique anatomical constraints, prior injury histories, and movement habits that shift their baseline joint kinematics. Consequently, group-averaged templates are poor references for longitudinal tracking, as an individual's normal movement variation may fall outside cohort means without indicating movement pathology.

This framework shifts the unit of analysis from the cohort to the individual. By building a baseline from early correct trials, the framework monitors subsequent performance relative to the individual's "normal" template. Crucially, a shift is flagged as a real kinematic change only if it exceeds the monocular camera's validated measurement-noise floor (derived in Chapter 8), preventing false alarms from normal execution variability or camera perspective offsets.

### 9.1.1. Pseudo-Timepoint Axis and Scope
Because public physical therapy datasets (including REHAB24-6) are collected during a single laboratory session, we employ **within-session repetition order** as a **pseudo-time axis** [source: 18_personalised_baseline_outputs/baseline_design.md]: the first repetitions represent the baseline reference period, while subsequent repetitions represent observation points over pseudo-time. This pseudo-time axis demonstrates the gating architecture; the methodology generalizes directly to multi-session longitudinal tracking across days or weeks (future work) [source: 18_personalised_baseline_outputs/baseline_design.md].

---

## 9.2. Baseline Construction and Gating Rules

The framework operates in two sequential stages: baseline building and test sequence gating [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.1. Personalized Baseline Building
The baseline is constructed from a subject's first **2 correct repetitions** (Reps 1 and 2) [source: 18_personalised_baseline_outputs/baseline_design.md]. Selecting early correct repetitions establishes a clean reference template prior to the onset of movement fatigue or instructed form deviations:
*   **Baseline Mean Reference ($\mu_{\text{base}, i}$)**: Mean of biomarker $i$ computed across baseline repetitions:
    $$\mu_{\text{base}, i} = \frac{1}{2} (x_{1, i} + x_{2, i})$$
*   **Baseline Standard Deviation ($SD_{\text{base}, i}$) [Descriptive Only]**: Reported solely as descriptive context for early-session consistency ($SD_{\text{base}, i} = \sqrt{\frac{1}{1} \sum_{j=1}^2 (x_{j, i} - \mu_{\text{base}, i})^2}$). It is **not** used in gating because $n = 2$ is statistically unstable and would induce false flags [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.2. Deviation Gating Logic
Subsequent repetitions (Reps 3 to 10) form the **test sequence** [source: 18_personalised_baseline_outputs/baseline_design.md]. The absolute deviation ($\Delta_i = |x_{\text{test}, i} - \mu_{\text{base}, i}|$) is gated against the **95% Noise Floor ($NF_i = 1.96 \times SD_{\text{proj}, i}$)** transferred from drop-jump ground-truth validation (Chapter 8) [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]:
*   **`DEVIATION DETECTED`** ($\Delta_i > NF_i$): Shift exceeds single-camera measurement precision, indicating a genuine kinematic change relative to baseline [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **`WITHIN-NOISE`** ($\Delta_i \le NF_i$): Shift is smaller than or equal to measurement precision, remaining indistinguishable from monocular tracking noise [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.3. Applied Gating Thresholds
The 95% noise floors used for evaluation are [source: 18_personalised_baseline_outputs/baseline_design.md]:
1.  **Start Flexion (`start_flexion`)**: $NF = \mathbf{\pm 19.0522^\circ}$ ($SD_{\text{proj}} = 9.7205^\circ$)
2.  **Peak Flexion (`peak_flexion`)**: $NF = \mathbf{\pm 11.9885^\circ}$ ($SD_{\text{proj}} = 6.1166^\circ$)
3.  **Range of Motion (`rom`)**: $NF = \mathbf{\pm 23.1666^\circ}$ ($SD_{\text{proj}} = 11.8197^\circ$)
4.  **Joint Descent Velocity (`descent_velocity`)**: $NF = \mathbf{\pm 40.8615^\circ/\text{s}}$ ($SD_{\text{proj}} = 20.8477^\circ/\text{s}$)

---

## 9.3. Results -- Both-Sides Demonstration

Demonstrating both the "quiet side" (correct reps do not false-alarm) and the "firing side" (incorrect reps do fire) proves the noise floor acts as a selective filter rather than a permissive threshold [source: 18_personalised_baseline_outputs/baseline_design.md]. Evaluating correct repetitions establishes measurement specificity by verifying that normal variability remains within uncertainty bounds, while evaluating incorrect repetitions establishes tracking sensitivity by confirming that true kinematic shifts exceed the gating floor. Two clean subjects from REHAB24-6 with 10 continuous repetitions (Reps 1–5 correct, Reps 6–10 incorrect) were evaluated: Squat Subject 8 (`PM_113`, $0.0\%$ spike rate) and Lunge Subject 6 (`PM_104`, $0.0\%$ tracking failure) [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.3.1. Squat Demonstration (Subject `PM_113`)
Subject `PM_113` performed 5 correct squats followed by 5 restricted-depth squats [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   **Baseline (Reps 1–2)**: Mean peak knee flexion was **$72.98^\circ \pm 6.21^\circ$**; mean ROM was **$105.50^\circ \pm 5.96^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Quiet Sequence (Reps 3–5)**: Maximum peak flexion deviation was **$9.26^\circ$** (Rep 5, value: $63.72^\circ$), and maximum ROM deviation was **$8.90^\circ$** (Rep 5, value: $114.40^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Staying below noise floors ($\pm 11.99^\circ$ and $\pm 23.17^\circ$), all three reps were classified as `WITHIN-NOISE` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Firing Sequence (Reps 6–10)**: Restricted-depth reps reduced peak flexion angles, yielding baseline deviations from **$23.23^\circ$ to $35.66^\circ$** (Rep 10 peak flexion: $37.32^\circ$, delta: $35.66^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Exceeding the $\pm 11.99^\circ$ floor, all five reps were flagged as `DEVIATION DETECTED` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. ROM deviations similarly fired ($24.34^\circ\text{--}36.70^\circ > \pm 23.17^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].

### 9.3.2. Lunge Demonstration (Subject `PM_104`)
Subject `PM_104` performed 5 correct lunges followed by 5 restricted-depth lunges [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   **Baseline (Reps 1–2)**: Mean peak flexion was **$84.66^\circ \pm 4.57^\circ$**; mean ROM was **$76.78^\circ \pm 3.19^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Quiet Sequence (Reps 3–5)**: Peak flexion stayed close to baseline (max deviation **$6.77^\circ$** on Rep 5, value: $91.43^\circ$), remaining `WITHIN-NOISE` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Firing Sequence (Reps 6–10)**: Shallower lunges dropped peak flexion to $52.69^\circ\text{--}63.75^\circ$, producing baseline deviations of **$20.91^\circ$ to $31.98^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Exceeding the $\pm 11.99^\circ$ floor, all five reps were flagged as `DEVIATION DETECTED` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. ROM deviations similarly fired ($30.81^\circ\text{--}45.01^\circ > \pm 23.17^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].

---

## 9.4. Empirical Validation of Chapter 8 Uncertainty Weights

The empirical results confirm the uncertainty-weighting scheme developed in Chapter 8, which assigned peak flexion a high confidence weight (**$57.15\%$**) and joint descent velocity a low confidence weight (**$4.92\%$**) [source: 22_dissertation_writing/results_uncertainty_framework_v1.md].

This weighting manifests in their noise floors: peak flexion has a tight noise floor ($\pm 11.99^\circ$), whereas descent velocity has a wide noise floor ($\pm 40.86^\circ/\text{s}$) [source: 18_personalised_baseline_outputs/baseline_design.md]. During testing, this created distinct gating behaviors:
*   **Peak Flexion**: Primary driver of deviation detection, flagging all restricted-depth reps while remaining quiet on correct reps [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Joint Velocity**: Remained quiet across test sequences; for Lunge Subject `PM_104`, all 10 reps stayed within the $\pm 40.86^\circ/\text{s}$ floor [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Velocity Spike Exception**: Velocity only fired on **Rep 6** of Squat Subject `PM_113`, where descent velocity reached **$110.62^\circ/\text{s}$** (baseline: $49.94^\circ/\text{s}$, delta: **$60.68^\circ/\text{s} > \pm 40.86^\circ/\text{s}$**) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].

This confirms that low-confidence biomarkers contribute minimally to flagging due to large measurement uncertainty rather than active noise suppression, validating the Chapter 8 weighting architecture.

---

## 9.5. Personalised-Not-Group Distinction & Guardrails

In Chapters 4 and 5, repetitions were pooled across subjects to evaluate cohort-level group differences [source: 22_dissertation_writing/results_squat_v1.md / results_lunge_v1.md]. Here, each subject's data is compared strictly against their own baseline mean ($\mu_{\text{base}}$) established at the start of their session [source: 18_personalised_baseline_outputs/baseline_design.md]. A `DEVIATION DETECTED` flag denotes a kinematic shift exceeding single-camera measurement precision, not a cohort-level quality verdict or clinical diagnosis. This distinction separates qualitative pass/fail evaluation from quantitative baseline delta tracking, ensuring the system functions as a neutral measurement layer.

---

## 9.6. Limitations and Non-Claims

1.  **Pseudo-Time Axis**: Utilizing within-session repetition order validates gating logic, but multi-session longitudinal tracking across days or weeks remains unvalidated future work [source: 18_personalised_baseline_outputs/baseline_design.md].
2.  **Sensitivity Threshold Constraint**: Deviations below the monocular camera's noise floor (e.g., shifts $< \pm 11.99^\circ$ for peak flexion) are indistinguishable from tracking noise [source: 18_personalised_baseline_outputs/baseline_design.md].
3.  **Non-Claims**: The framework does not claim multi-session longitudinal clinical tracking, injury prediction, risk scoring, or rep pass/fail grading. It serves as a software architectural demonstration of baseline-building and uncertainty-gating logic.

---

## 9.7. Figures and Provenance

Publication-ready figures; data provenance in `18_personalised_baseline_outputs/` [source: 18_personalised_baseline_outputs/baseline_tracking.png]:

*   **Figure 9.1: Personalised Kinematic Progression Tracking with Uncertainty Gating**
    *   `18_personalised_baseline_outputs/baseline_tracking.png` — time-series plots for Squat `PM_113` and Lunge `PM_104` across 10 repetitions, showing baseline mean reference, shaded 95% projection noise floor bands, and individual test rep values.
