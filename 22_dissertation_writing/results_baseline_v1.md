# Chapter 9: Personalised Session-to-Session Baselines

This chapter presents the design and demonstration of an individualised kinematic progression-tracking framework. Biomechanical screening typically relies on group-level cohort analysis to differentiate movement quality. However, clinical rehabilitation and performance tracking require monitoring an individual's kinematic changes over time relative to their own unique baseline. This chapter describes an architectural framework that builds a personalised baseline from a subject's correct repetitions, then gates subsequent trials against the monocular pipeline's validated measurement-noise floor. First, we outline the purpose and design motivation of the framework. Second, we present the mathematical rules for baseline construction and deviation gating. Third, we demonstrate the framework's behavior using real squat and lunge repetition sequences. Finally, we discuss how the empirical results validate the uncertainty-weighting scheme developed in Chapter 8 and outline the framework's limitations.

---

## 9.1. Purpose and Design Motivation

Group-level cohort analyses—such as the squat and lunge investigations presented in Chapters 4 and 5—are essential for validating that markerless pose estimation can detect cohort-wide differences in execution quality [source: 22_dissertation_writing/results_squat_v1.md / results_lunge_v1.md]. However, clinical therapy and athletic coaching are fundamentally individualised. Every athlete possesses unique anatomical constraints, prior injury histories, and movement habits that shift their baseline joint kinematics. Group-averaged templates are therefore poor references for longitudinal monitoring.

The primary objective of this chapter is to demonstrate an architectural framework that shifts the unit of analysis from the cohort to the individual. By building a baseline from a subject's own early correct trials, the framework monitors subsequent performance relative to the individual's "normal" template. Crucially, this monitoring incorporates the validated measurement-uncertainty bounds derived in Chapter 8. A deviation from baseline is only flagged as a "real change" if it exceeds the monocular camera's validated measurement-noise floor, preventing the system from false-alarming on normal execution variability or camera perspective offsets.

### 9.1.1. Pseudo-Timepoint Axis and Scope
Because public physical therapy datasets (including REHAB24-6) are collected during a single laboratory session, we employ **within-session repetition order** as a **pseudo-time axis** to demonstrate the progression-tracking software [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   The first repetitions represent the baseline reference period.
*   Subsequent repetitions represent subsequent observations over pseudo-time (observation points).
*   This pseudo-time axis serves to demonstrate the mathematical gating and flagging architecture. The methodology generalizes directly to true multi-session longitudinal tracking (such as tracking an athlete across days or weeks), which is identified as future work [source: 18_personalised_baseline_outputs/baseline_design.md].

---

## 9.2. Baseline Construction and Gating Rules

The progression-tracking framework operates in two stages: baseline building and test sequence gating [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.1. Personalized Baseline Building
For a given subject, the baseline is constructed from the first **2 correct repetitions** (Reps 1 and 2) of the session [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   **Baseline Mean Reference ($\mu_{\text{base}, i}$)**: The mean value of biomarker $i$ computed across the baseline repetitions:
    $$\mu_{\text{base}, i} = \frac{1}{2} (x_{1, i} + x_{2, i})$$
*   **Baseline Standard Deviation ($SD_{\text{base}, i}$) [DESCRIPTIVE ONLY]**: The standard deviation of the biomarker across the baseline repetitions [source: 18_personalised_baseline_outputs/baseline_design.md]:
    $$SD_{\text{base}, i} = \sqrt{\frac{1}{1} \sum_{j=1}^2 (x_{j, i} - \mu_{\text{base}, i})^2}$$
    This baseline spread is reported as descriptive context to represent early-session movement consistency. Crucially, it is **not** used in the gating or flagging decisions. Because a sample size of $n = 2$ is highly unstable, utilizing the baseline standard deviation to compute thresholds would lead to statistical false alarms or false negatives [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.2. Deviation Gating Rule
Subsequent repetitions (Reps 3 to 10) form the **test sequence** [source: 18_personalised_baseline_outputs/baseline_design.md]. For each test repetition, the framework calculates the absolute deviation ($\Delta_i$) of the test value ($x_{\text{test}, i}$) from the baseline mean [source: 18_personalised_baseline_outputs/baseline_design.md]:
$$\Delta_i = |x_{\text{test}, i} - \mu_{\text{base}, i}|$$

This deviation is gated against the **95% Noise Floor ($NF_i$)** derived in Chapter 8. The noise floor represents the projection-only component of measurement uncertainty (transferred from the drop-jump ground truth) [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]:
$$NF_i = 1.96 \times SD_{\text{proj}, i}$$

The classification gating logic is defined as:
*   **`DEVIATION DETECTED`** (if $\Delta_i > NF_i$): The shift exceeds the validated measurement precision of the single sagittal camera pipeline, indicating a genuine physical change in joint kinematics relative to the subject's baseline [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **`WITHIN-NOISE`** (if $\Delta_i \le NF_i$): The shift is smaller than or equal to the measurement precision floor, meaning it cannot be distinguished from monocular camera tracking noise or perspective offsets [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.2.3. Applied Gating Thresholds
The 95% noise floors used for the squat and lunge demonstration are [source: 18_personalised_baseline_outputs/baseline_design.md]:
1.  **Start Flexion (`start_flexion`)**: $NF_{\#1} = \mathbf{\pm 19.0522^\circ}$ (Projection SD: $9.7205^\circ$)
2.  **Peak Flexion (`peak_flexion`)**: $NF_{\#2} = \mathbf{\pm 11.9885^\circ}$ (Projection SD: $6.1166^\circ$)
3.  **Range of Motion (`rom`)**: $NF_{\#3} = \mathbf{\pm 23.1666^\circ}$ (Projection SD: $11.8197^\circ$)
4.  **Joint Descent Velocity (`descent_velocity`)**: $NF_{\#6} = \mathbf{\pm 40.8615^\circ/\text{s}}$ (Projection SD: $20.8477^\circ/\text{s}$)

---

## 9.3. Results -- Both-Sides Demonstration

To validate the framework, we selected two fully clean subjects from the REHAB24-6 cohort who contributed $10$ continuous repetitions (Reps 1–5 correct, Reps 6–10 incorrect), providing a balanced test set [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   **Squat Subject 8 (`PM_113`)**: Verified clean with $0.0\%$ spike rate and $100\%$ tracking completion [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **Lunge Subject 6 (`PM_104`)**: Verified clean with $0.0\%$ tracking failure [source: 18_personalised_baseline_outputs/baseline_design.md].

### 9.3.1. Squat Demonstration (Subject `PM_113`)
Subject `PM_113` performed $5$ correct squats followed by $5$ restricted-depth squats [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **Baseline Construction**: Built from Reps 1 and 2 (both correct). The baseline mean knee flexion was **$72.98^\circ \pm 6.21^\circ$**, and the baseline ROM was **$105.50^\circ \pm 5.96^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Quiet-Test Sequence (Reps 3–5)**: These correct repetitions represent normal movement variations. Across these three reps, the maximum peak flexion deviation was **$9.26^\circ$** (observed on Rep 5, value: $63.72^\circ$), and the maximum ROM deviation was **$8.90^\circ$** (observed on Rep 5, value: $114.40^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Because both deviations were smaller than their respective noise floors ($\pm 11.99^\circ$ and $\pm 23.17^\circ$), they were successfully flagged as `WITHIN-NOISE` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Firing-Test Sequence (Reps 6–10)**: These repetitions involved instructed restricted-depth faults (shallower squats). Across these five reps, peak flexion joint angles dropped, resulting in deviations from baseline ranging from **$23.23^\circ$ to $35.66^\circ$** (Rep 10 reached a peak flexion of $37.32^\circ$, delta: $35.66^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Because these deviations far exceeded the $\pm 11.99^\circ$ peak flexion noise floor, all five repetitions were flagged as `DEVIATION DETECTED` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. ROM deviations similarly fired, ranging from **$24.34^\circ$ to $36.70^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].

### 9.3.2. Lunge Demonstration (Subject `PM_104`)
Subject `PM_104` performed $5$ correct lunges followed by $5$ restricted-depth lunges [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **Baseline Construction**: Built from Reps 1 and 2. The baseline mean peak flexion was **$84.66^\circ \pm 4.57^\circ$**, and the baseline ROM was **$76.78^\circ \pm 3.19^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Quiet-Test Sequence (Reps 3–5)**: Across these reps, the peak flexion values remained close to baseline, with a maximum deviation of **$6.77^\circ$** on Rep 5 (value: $91.43^\circ$) [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. All repetitions were flagged as `WITHIN-NOISE` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Firing-Test Sequence (Reps 6–10)**: These reps involved shallower lunges. Peak flexion joint angles dropped to a range of $52.69^\circ\text{--}63.75^\circ$, yielding deviations from baseline ranging from **$20.91^\circ$ to $31.98^\circ$** [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. Because these exceeded the $\pm 11.99^\circ$ noise floor, all five reps were flagged as `DEVIATION DETECTED` [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. ROM deviations also fired, ranging from **$30.81^\circ$ to $45.01^\circ$**, exceeding the $\pm 23.17^\circ$ noise floor [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].

Demonstrating the quiet side is as methodologically important as the firing side. By confirming that correct repetitions do not trigger flags, the framework proves it does not false-alarm on ordinary joint angle variation. This justifies the noise floor as a meaningful, clinically relevant filter rather than a permissive threshold.

---

## 9.4. Cross-Component Finding (Empirical Validation of Chapter 8 Weights)

A major finding of this demonstration is the interaction between the biomarkers, which provides empirical confirmation of the uncertainty-weighting scheme developed in Chapter 8 [source: 22_dissertation_writing/results_uncertainty_framework_v1.md].

### 9.4.1. Peak Flexion vs. Joint Velocity Gating
In Chapter 8, peak flexion was identified as a high-confidence biomarker and assigned a weight of **$57.15\%$**, whereas joint descent velocity was identified as a low-confidence biomarker and assigned a weight of **$4.92\%$** [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]. This difference is reflected directly in their noise floors: peak flexion has a tight noise floor of $\pm 11.99^\circ$, while descent velocity has a very wide noise floor of $\pm 40.86^\circ/\text{s}$ [source: 18_personalised_baseline_outputs/baseline_design.md].

During the test sequences, this difference resulted in distinct gating behaviors:
*   **Peak Flexion**: Acted as the primary driver of deviation detection, successfully flagging all restricted-depth repetitions while staying quiet on all correct repetitions [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Joint Velocity**: Remained quiet across the firing sequence. For lunge Subject `PM_104`, all 10 repetitions stayed strictly within the $\pm 40.86^\circ/\text{s}$ velocity noise floor, meaning velocity did not independently flag the restricted-depth form [source: 18_personalised_baseline_outputs/worked_example_baseline.csv].
*   **Velocity Spike Exception**: Gating only fired on **Rep 6** of Squat subject `PM_113`, where the descent velocity reached **$110.62^\circ/\text{s}$** (baseline: $49.94^\circ/\text{s}$), representing a large deviation of **$60.68^\circ/\text{s}$** that exceeded the $\pm 40.86^\circ/\text{s}$ floor [source: 18_personalised_baseline_outputs/worked_example_baseline.csv]. All other squat test reps stayed within the velocity noise floor.

This behavior confirms that the gating logic operates exactly as designed. The low-confidence velocity biomarker contributes little to deviation flagging because its measurement uncertainty is large (±40.86°/s), rather than because of any active noise-suppression mechanism. This empirical finding validates the Chapter 8 weights: the biomarker predicted to dominate screening drives the tracking, while the high-noise biomarker is down-weighted to prevent false alarms.

---

## 9.5. Personalised-Not-Group Distinction

To prevent reading this chapter as a repeat of the squat and lunge cohort results (Chapters 4 and 5) [source: 22_dissertation_writing/results_squat_v1.md / results_lunge_v1.md], we highlight the distinct analytical lens of this framework:

### 9.5.1. The Individual as the Unit of Analysis
In Chapters 4 and 5, the unit of analysis was the cohort: we pooled repetitions across subjects to evaluate statistically significant group differences between correct and incorrect execution [source: 22_dissertation_writing/results_squat_v1.md / results_lunge_v1.md]. 

In this chapter, the unit of analysis is the individual:
*   We do not pool subjects or evaluate cohort-level group differences.
*   Each subject's data is compared strictly against their own baseline mean ($\mu_{\text{base}}$) established at the beginning of their own session [source: 18_personalised_baseline_outputs/baseline_design.md].
*   A "firing" flag does not signify a cohort-level quality verdict or label a rep as "bad." Instead, it denotes a **kinematic deviation from this specific person's baseline that exceeds the validated measurement precision of the single-camera tracker** [source: 18_personalised_baseline_outputs/baseline_design.md].

---

## 9.6. Limitations

Several limitations of this progression-tracking demonstration must be noted:
1.  **Pseudo-Time Axis**: Because the REHAB24-6 dataset consists of single-session laboratory collections, we utilized within-session repetition order as a pseudo-time axis [source: 18_personalised_baseline_outputs/baseline_design.md]. While this validates the gating architecture, true multi-session longitudinal validation (tracking an athlete across days or weeks) remains future work.
2.  **Sensitivity Threshold Constraint**: Only joint angle deviations that exceed the monocular camera's measurement noise floor (e.g., shifts larger than $\pm 11.99^\circ$ for peak flexion) are detectable [source: 18_personalised_baseline_outputs/baseline_design.md]. Subtle, sub-floor improvements or minor technique shifts are completely indistinguishable from camera tracking noise. This is a direct consequence of the single-camera measurement precision validated in Chapter 6 [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

---

## 9.7. What This Framework Does NOT Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of the framework:
*   **No Longitudinal Clinical Claims**: The framework does not claim to track real physiological progression or adaptation over time.
*   **No Injury Prediction or Risk Scoring**: It does not predict injury, score risk, or determine clinical outcomes.
*   **No Repetition Classification**: It does not classify reps as "failed" or "passed" based on quality.
*   **Not a Deployed Clinical System**: It is a software architectural demonstration of baseline-building and uncertainty-gating logic.

---

## 9.8. Figures and Provenance

The findings presented in this chapter are supported by the following publication-ready figure, with data provenance detailed in `18_personalised_baseline_outputs/` [source: 18_personalised_baseline_outputs/baseline_tracking.png]:

*   **Figure 9.1: Personalised Kinematic Progression Tracking with Uncertainty Gating**
    *   *Source file*: `18_personalised_baseline_outputs/baseline_tracking.png`
    *   *Description*: Time-series plots for squat subject `PM_113` and lunge subject `PM_104` across 10 repetitions, showing the baseline mean reference, the shaded 95% projection noise floor bands, and the individual test rep values, illustrating quiet correct reps and firing incorrect reps.
