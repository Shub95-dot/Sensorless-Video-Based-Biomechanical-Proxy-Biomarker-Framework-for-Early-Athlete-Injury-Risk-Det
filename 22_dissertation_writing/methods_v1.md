# Methodology Chapter Draft (v1)
## Part 1 — Research Design and Pipeline Architecture

This chapter describes the research design, data pipelines, validation methodologies, and analytical frameworks developed to implement the marklerless kinematic screening and explainable baseline tracking systems. The methodology is structured in three core layers: a physical pose estimation and validation layer (Track A Core), an uncertainty-weighting framework (Track B Transfer), and a personalised progression and explainable screening layer (Track A XAI).

---

## 1. Markerless Kinematic Extraction Pipeline

To capture joint kinematics in uncontrolled environments, we implement a multi-stage software pipeline that transforms 2D video sequences into smoothed, segmented joint angle trajectories.

### 1.1 Pose Estimation and Camera Model
The pipeline ingests video sequences recorded at cohort-specific frame rates: 30 fps for the REHAB24-6 squat and lunge cohorts [source: 11_scripts/phase5a_rehab24_integration.py, filename convention `*-30fps-transposed.mp4`] and 60 fps for the OpenCap drop-jump validation cohort [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. YouTube wild-type videos have variable frame rates depending on the source upload. 2D markerless pose estimation is executed using the MediaPipe Pose tracking engine (Heavy variant), which computes the spatial coordinates of 33 keypoints [source: 11_scripts/phase3_pose_extraction.py].

> **Convention Note:** The squat/lunge chapters and the drop-jump validation chapter use different knee flexion angle conventions. Squats and lunges use the **included angle** convention ($\approx 180^\circ$ = standing extension, smaller angle = deeper flexion). The OpenCap drop-jump validation uses the **clinical flexion** convention ($0^\circ$ = full extension, larger angle = deeper flexion). Raw joint angle values are not directly comparable across these chapters; the uncertainty framework transfers validated *error magnitudes* (LoA widths), not raw angle values.

For sagittal-plane exercises (squats and lunges), joint angles are computed using a 2D trigonometric model. The knee flexion-extension joint angle ($\theta$) is calculated as the included angle formed by the hip (proximal), knee (vertex), and ankle (distal) joint centers:
$$\theta = \arccos \left( \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} \right)$$
where $\mathbf{u}$ is the thigh segment vector (knee to hip) and $\mathbf{v}$ is the shank segment vector (knee to ankle) [source: 11_scripts/phase4a_knee_angle_extraction.py].

### 1.2 Trajectory Smoothing and Outlier Filtering
Raw coordinates from monocular video are affected by high-frequency landmark jitter and occasional tracking spikes. The pipeline filters these anomalies in two sequential steps:
1.  **Outlier Gating:** Plausible joint angle boundaries are defined a priori between $40.0^\circ$ and $185.0^\circ$ [source: 11_scripts/phase4a_knee_angle_extraction.py]. Values outside this range represent landmark tracking failures and are flagged for quality auditing [source: 11_scripts/phase4a_knee_angle_extraction.py].
2.  **Smoothing Cascades:** Joint angle trajectories are smoothed in two stages: first, a 5-frame centred median filter to eliminate impulsive landmark spikes; second, a Savitzky-Golay polynomial filter (window length 7, polynomial order 2) to isolate the underlying voluntary motion trajectory while preserving peak morphology [source: 11_scripts/phase4e_trajectory_smoothing.py, lines 53–55 and 74–84].
3.  **Pose Quality Stratification:** Subjects with tracking spike rates exceeding 5.0% of total frames are flagged for manual quality review in the dissertation's discussion [source: 11_scripts/phase4e_trajectory_smoothing.py].

### 1.3 Repetition Segmentation & Phase Detection
To extract discrete biomarkers, continuous joint trajectories are segmented into individual repetitions. The segmentation algorithm operates as follows:
*   **Velocity Zero-Crossings:** Joint angular velocity is computed via numerical differentiation. Repetition descent begins when angular velocity drops below zero and terminates when velocity returns to zero after the ascent phase [source: 11_scripts/phase4g_rep_segmentation.py].
*   **Depth Filtering:** A repetition is accepted only if the joint excursion exceeds a minimum threshold (e.g., peak flexion depth must reach a significant change from standing extension) to avoid segmenting minor postural adjustments [source: 11_scripts/phase4g_rep_segmentation.py].
*   **Phase Splitting:** Each repetition is partitioned into a descent phase (standing extension to peak knee flexion) and an ascent phase (peak knee flexion to terminal extension) [source: 11_scripts/phase4g_rep_segmentation.py].

---

## 2. Cohort Assembly and Experimental Datasets

The experimental validation and demonstration of this pipeline utilize three independent cohorts representing different levels of environmental control and label availability.

### 2.1 The OpenCap Drop-Jump Validation Cohort
To establish the physical ground-truth accuracy of the monocular camera pipeline, we utilize the OpenCap Drop-Jump landing dataset [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This cohort comprises 8 subjects performing a total of 48 drop-jump trials, recorded at 60 fps [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Marker-Based Reference:** Ground truth kinematics were captured simultaneously using a synchronized 3D optoelectronic motion capture system (10 cameras) and two force plates [CITE: OpenCap_Validation].
*   **Markerless Reference:** 2D videos were recorded from a sagittal camera and processed through the MediaPipe Heavy pipeline [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Biomechanical Purpose:** Because drop-jumps involve high-speed, dynamic impact landings, they represent a worst-case testing condition for markerless tracking, allowing us to establish upper-bound measurement uncertainty limits.

### 2.2 The REHAB24-6 Cohort
The primary cohort for baseline tracking, rule-based screening, and XAI validation is the `REHAB24-6` dataset [source: 18_personalised_baseline_outputs/baseline_design.md].
*   **Squat Dataset:** Contains 9 subjects and a total of 98 processed repetitions, all recorded at 30 fps [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]. The dataset is partitioned into 72 correct repetitions (normal form) and 26 incorrect repetitions (characterized by excess flexion depth or rapid descent) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   **Lunge Dataset:** Contains 8 assembled subjects and a total of 88 repetitions in the manifest, all recorded at 30 fps. After phase-identification quality filtering, 61 repetitions from 7 usable subjects were successfully processed (25 correct, 36 incorrect) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Two subjects were excluded from the analytical cohort: Subject 5 (PM_042, 12 of 13 reps failed phase identification) and Subject 8 (PM_112, all 12 reps failed due to occlusion/tracking failure) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   **Wording & Definition:** Correctness is used strictly as a validation marker to test if our personalised gating rules successfully fire on deviated form.

### 2.3 The YouTube Wild-Type Exploratory Cohort
To evaluate the pipeline's robustness in "in-the-wild" environments, we assembled an exploratory cohort of 10 subjects performing single-repetition squats downloaded from YouTube [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]. These videos represent diverse camera angles, lighting conditions, resolutions, and clothing types, serving to document qualitative pipeline failure modes under unconstrained conditions.

---

## 3. OpenCap Drop-Jump Ground Truth Validation

Before transferring joint angle measurements to screening tasks, we validate the monocular pipeline's knee flexion measurements against the 3D Mocap ground truth across the 48 drop-jump trials [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 3.1 Bland-Altman Limits of Agreement (LoA)
We assess agreement using Bland-Altman Limits of Agreement (LoA) at 95% confidence intervals ($\text{Bias} \pm 1.96 \cdot \text{SD}$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
1.  **Peak landing flexion:** Video overestimates peak landing flexion by a mean bias of $+19.72^\circ$, with 95% LoA of $[7.73^\circ, 31.71^\circ]$ (Pearson $r = 0.8238$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
2.  **Contact flexion:** Underestimates angle at contact (shallow flexion) by a mean bias of $-6.69^\circ$, with 95% LoA of $[-26.77^\circ, 13.39^\circ]$ (Pearson $r = 0.3209$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
3.  **Landing range of motion (ROM):** Overestimates ROM by a mean bias of $+26.41^\circ$, with 95% LoA of $[2.34^\circ, 50.48^\circ]$ (Pearson $r = 0.4020$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
4.  **Loading rate:** Overestimates joint velocity rate by a mean bias of $+13.30^\circ/\text{s}$, with 95% LoA of $[-115.92^\circ/\text{s}, 142.51^\circ/\text{s}]$ (Pearson $r = 0.6076$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 3.2 Deep-Flexion Constant Bias Isolation (Timing-Clean)
To separate static camera projection error from dynamic frame-rate lag, we analyze joint angles at the peak landing absorption frames where joint angular velocity is approximately zero:
*   **Dataset size:** $n = 96$ points (48 trials $\times$ 2 limbs) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Peak Flexion Bias:** Mean bias of $+10.52^\circ$, with 95% LoA of $[-5.54^\circ, 26.58^\circ]$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Correlation-vs-Depth Test:** Correlation between error magnitude and joint angle is not statistically significant (Pearson $r = -0.1568$, $p = 0.1271$; Spearman $\rho = -0.1905$, $p = 0.0631$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   *Methodological Finding:* Because the error does not scale monotonically with flexion depth in the $70^\circ\text{--}120^\circ$ landing range, we model the peak flexion error as a **constant systematic positive bias** rather than a depth-dependent slope [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 3.3 Robustness to Movement Conditions
We evaluate whether landing symmetry affects tracking errors. The mean peak flexion biases are virtually identical:
*   **Symmetric Landings:** Mean bias of $+10.36^\circ$ (SD: $6.89^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Asymmetric Landings:** Mean bias of $+10.68^\circ$ (SD: $9.39^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   *Methodological Finding:* Markerless monocular coordinate tracking is robust to movement loading asymmetries, indicating that errors are driven by camera placement and projection geometry rather than kinetic variability [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 3.4 Contralateral Occlusion Limitation
Inter-limb asymmetry (Biomarker #5) could not be validated on monocular sagittal video due to far-leg occlusion during deep flexion [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Thus, asymmetry is demoted to a 3D-only reference value (mocap mean: $2.07^\circ$, SD: $2.06^\circ$) and excluded from the video-only screening rules [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## 4. Uncertainty Aggregation and Variance Decomposition

To transfer measurement uncertainty from the drop-jump landing validation task to squats and lunges, we develop a mathematical variance decomposition framework.

### 4.1 Variance Conversion from LoA
For each biomarker $i$, the validated 95% Limits of Agreement width is converted into standard deviation ($SD_i$) and total variance ($\sigma^2_{i, \text{total}}$):
$$SD_i = \frac{LoA_{i, \text{upper}} - LoA_{i, \text{lower}}}{3.92}$$
$$\sigma^2_{i, \text{total}} = (SD_i)^2$$
This yields:
*   `contact_flexion` total variance: **$104.9867$** ($SD = 10.2463^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `peak_landing_flexion` total variance: **$37.4132$** ($SD = 6.1166^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `landing_rom` total variance: **$150.8291$** ($SD = 12.2813^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `loading_rate` total variance: **$4346.2534$** ($SD = 65.9261^\circ/\text{s}$) [source: 17_uncertainty_framework_outputs/framework_design.md]

### 4.2 Projection and Motion Decompositions
We decompose the total measurement variance into two independent physical components:
$$\sigma^2_{i, \text{total}} = \sigma^2_{i, \text{proj}} + \sigma^2_{i, \text{mot}}$$
where $\sigma^2_{i, \text{proj}}$ represents systematic projection/perspective error (generalizable to monocular sagittal kinematics) and $\sigma^2_{i, \text{mot}}$ represents dynamic motion/timing error (specific to the high-speed drop-jump task).

The decomposition splits are derived individually for each biomarker:
1.  **Peak Flexion:** Derived from timing-aligned static peak frames.
    *   *Projection:* $100.0\%$ ($\sigma^2_{\text{proj}} = 37.4132$) [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Motion:* $0.0\%$ ($\sigma^2_{\text{mot}} = 0.0000$) [source: 17_uncertainty_framework_outputs/framework_design.md]
2.  **Contact Flexion (Assumed Split):** Measured at landing contact where joint speed is low, indicating minimal timing error. We assign a 90% projection, 10% motion split:
    *   *Projection:* $90.0\%$ ($\sigma^2_{\text{proj}} = 94.4880$) [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Motion:* $10.0\%$ ($\sigma^2_{\text{mot}} = 10.4987$) [source: 17_uncertainty_framework_outputs/framework_design.md]
3.  **Loading Rate (Assumed Split):** Calculated as a velocity rate over a fast landing phase, making it highly sensitive to sub-frame contact time errors. We assign a 10% projection, 90% motion split:
    *   *Projection:* $10.0\%$ ($\sigma^2_{\text{proj}} = 434.6253$) [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Motion:* $90.0\%$ ($\sigma^2_{\text{mot}} = 3911.6281$) [source: 17_uncertainty_framework_outputs/framework_design.md]
4.  **Range of Motion (ROM) (Propagated Split):** ROM is calculated as $\text{ROM} = \text{peak\_flexion} - \text{contact\_flexion}$. The projection and motion components are propagated from the contact and peak endpoints:
    *   *Propagated Projection:* $37.4132 + 94.4880 = 131.9012$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Propagated Motion:* $0.0000 + 10.4987 = 10.4987$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   The propagated components are scaled proportionally to sum to the observed ROM variance ($150.8291$), yielding a 92.62% projection, 7.38% motion split:
        *   *Projection:* $92.62\%$ ($\sigma^2_{\text{proj}} = 139.7047$) [source: 17_uncertainty_framework_outputs/framework_design.md]
        *   *Motion:* $7.38\%$ ($\sigma^2_{\text{mot}} = 11.1244$) [source: 17_uncertainty_framework_outputs/framework_design.md]

### 4.3 Inverse-Variance Weighting & Cross-Exercise Transfer Weights
For slow, controlled squats and lunges, velocity is low, rendering motion-timing errors ($\sigma^2_{\text{mot}}$) negligible. Therefore, when evaluating squats and lunges, the weighting framework relies solely on the **projection-based variance** ($\sigma^2_{\text{proj}}$).

The raw weights are computed using the inverse-variance rule:
$$w_i = \frac{1}{\sigma^2_{i, \text{proj}}}$$
The normalized weights ($\bar{w}_i$) are:
*   **Peak Flexion:** **$57.15\%$** ($w \approx 0.0267$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Start/Contact Flexion:** **$22.63\%$** ($w \approx 0.0106$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Range of Motion (ROM):** **$15.30\%$** ($w \approx 0.0072$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Joint Velocity:** **$4.92\%$** ($w \approx 0.0023$) [source: 17_uncertainty_framework_outputs/framework_design.md]

A sensitivity analysis across 9 configurations verified the robustness of these weights: under all permutations, Peak Flexion remains the dominant biomarker ($50.01\%\text{--}58.59\%$), and velocity remains heavily down-weighted ($2.30\%\text{--}9.38\%$), validating that the choice of assumed splits does not change the framework hierarchy [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 5. Personalised Baseline and Digital Twin Demonstrations

Rather than relying on generic population references, we implement a personalised progression framework that tracks changes relative to the individual's own baseline.

### 5.1 Baseline Initialization
A per-subject baseline mean reference value ($\mu_{\text{base}, i}$) is established using correct repetitions 1 and 2 of the exercise session:
$$\mu_{\text{base}, i} = \frac{1}{2} (x_{1, i} + x_{2, i})$$
The baseline standard deviation ($SD_{\text{base}, i}$) is recorded as descriptive context for movement consistency, but is not used in decision rules to avoid small-sample instability [source: 18_personalised_baseline_outputs/baseline_design.md].

### 5.2 Conditional Digital Twin Update Rule
The "Digital Twin" represents a continuous-update extension of the baseline. As new repetitions are ingested in pseudo-sessions, the twin updates its reference state dynamically using a **conditional update rule** to prevent baseline contamination:
*   Calculate the absolute deviation: $\Delta_i = |x_{t+1, i} - \mu_{t, i}|$ [source: 19_digital_twin_outputs/twin_design.md].
*   Compare to the validated 95% Noise Floor ($NF_i$):
    *   **If $\Delta_i \le NF_i$ (WITHIN-NOISE):** The rep represents normal movement variation. The reference is updated:
        $$\mu_{t+1, i} = \frac{N_{t, i} \cdot \mu_{t, i} + x_{t+1, i}}{N_{t, i} + 1}$$
        $$N_{t+1, i} = N_{t, i} + 1$$
    *   **If $\Delta_i > NF_i$ (DEVIATION DETECTED):** The rep represents a kinematic aberration. The twin rejects this repetition from the update to prevent baseline drift, locking the reference state:
        $$\mu_{t+1, i} = \mu_{t, i}$$
        $$N_{t+1, i} = N_{t, i}$$
        This allows the twin to absorb natural baseline drift while remaining robust to abnormal repetitions [source: 19_digital_twin_outputs/twin_design.md].

---

## 6. Rule-Based Kinematic Screening Layer

To turn joint coordinate measurements into screening flags, we develop a transparent, rule-based screening layer that evaluates test repetitions against personalised thresholds.

### 6.1 Screening Modality Choice: Personalised-Deviation Screening (Option B)
The screening layer implements **Option B (Personalised-Deviation Screening)**:
*   *Mechanism:* A repetition is flagged only if it deviates from the subject's own baseline mean ($\mu_{\text{base}, i}$) beyond the validated Phase 7 noise floor ($NF_i$).
*   *Justification:* Replaces fixed population thresholds (Option A) that make unvalidated claims of universal biomechanical normality. It controls for individual anatomy and systematic camera perspective offsets.

### 6.2 Personalised Screening Rules
The noise floor thresholds ($NF_i$) are defined at a 95% confidence interval ($1.96 \cdot SD_{\text{proj}, i}$):
*   $NF_{\text{peak}} = \pm 11.9885^\circ$ (SD: $6.1166^\circ$) [source: 20_screening_outputs/screening_rules_design.md]
*   $NF_{\text{rom}} = \pm 23.1666^\circ$ (SD: $11.8197^\circ$) [source: 20_screening_outputs/screening_rules_design.md]
*   $NF_{\text{velocity}} = \pm 40.8615^\circ/\text{s}$ (SD: $20.8477^\circ/\text{s}$) [source: 20_screening_outputs/screening_rules_design.md]

Three rules are applied for squats and lunges:
1.  **Rule 1: Excess Knee Flexion Depth (EXCESS_DEPTH)**
    *   *Fires if:* $x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - 11.9885^\circ$ [source: 20_screening_outputs/screening_rules_design.md]
    *   *Rationale:* In this cohort, incorrect reps have smaller peak joint angles, physically representing an increase in flexion depth (deeper movement).
2.  **Rule 2: Excess Knee Excursion (EXCESS_ROM)**
    *   *Fires if:* $x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + 23.1666^\circ$ [source: 20_screening_outputs/screening_rules_design.md]
    *   *Rationale:* Incorrect deep reps exhibit a corresponding increase in range of motion.
3.  **Rule 3: Uncontrolled Joint descent Speed (EXCESS_VELOCITY)**
    *   *Fires if:* $x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + 40.8615^\circ/\text{s}$ [source: 20_screening_outputs/screening_rules_design.md]
    *   *Rationale:* Rapid descent speed indicates a loss of eccentric control.

If any rule fires, the repetition is flagged as `SCREENING_POSITIVE`, and the names of the fired rules are logged [source: 20_screening_outputs/screening_rules_design.md].

---

## 7. Counterfactual Explainable AI (XAI)

To provide explanations for the screening flags, we develop a counterfactual XAI layer that describes the exact conditions under which the screening flags would not have fired.

### 7.1 Faithfulness by Construction
Unlike SHAP or LIME, which approximate a black-box model's decision boundary, our explanations are **faithful by construction** [source: 21_xai_outputs/xai_design.md]. The rules are the decision boundaries. The counterfactual margin ($M_i$) is calculated directly:
*   $M_{\text{depth}} = (\mu_{\text{base}, \text{peak}} - 11.9885) - x_{\text{peak}}$ [source: 11_scripts/phase11_counterfactual_xai.py]
*   $M_{\text{rom}} = x_{\text{rom}} - (\mu_{\text{base}, \text{rom}} + 23.1666)$ [source: 11_scripts/phase11_counterfactual_xai.py]
*   $M_{\text{velocity}} = x_{\text{velocity}} - (\mu_{\text{base}, \text{velocity}} + 40.8615)$ [source: 11_scripts/phase11_counterfactual_xai.py]

### 7.2 Counterfactual Wording & Descriptive Guardrail
The counterfactual templates are framed as descriptive statements rather than physical advice:
*   `EXCESS_DEPTH`: `"Had the peak flexion angle been at least T_depth° (representing a shallower bend of M_depth° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/xai_design.md].
*   *Descriptive Guardrail:* Explanations describe the mathematical state required to clear the flag, avoiding prescriptive training advice (e.g., they do not state "the subject should squat shallower") [source: 21_xai_outputs/xai_design.md].

### 7.3 Multi-Rule Coupling & Minimal Kinematic Intervention (MKI)
If both `EXCESS_DEPTH` and `EXCESS_ROM` fire, we resolve their physical coupling. Under the explicit assumption that range of motion scales directly with peak flexion depth (assuming a constant standing extension start point), the MKI computes the exact maximum of the required depth changes:
$$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$
The MKI is stated descriptively as a set of conditions: the coupled depth/ROM flags would not have fired if peak flexion angle had been at least $\Delta \theta_{\text{MKI}}^\circ$ shallower. If `EXCESS_VELOCITY` also fires, its velocity reduction margin is listed as a separate independent condition (the flags would also have required descent velocity to be at least $M_{\text{velocity}}^\circ/\text{s}$ slower). The MKI thus represents a set of kinematic conditions, not a single adjustment [source: 21_xai_outputs/xai_design.md].

### 7.4 Uncertainty-Aware Confidence buffers
Explanations evaluate the deviation margin ($M_i$) against a confidence boundary ($0.5 \cdot NF_i$). Deviations that fall within this buffer are flagged as `LOW CONFIDENCE (Near Noise Floor)` [source: 21_xai_outputs/xai_design.md].

---

## 8. Statistical Analysis Methods

### 8.1 Cluster-Aware Bootstrapping
Because the `REHAB24-6` dataset contains multiple repetitions per subject, standard independent bootstrap sampling would violate standard error assumptions by treating reps as independent observations. To calculate robust confidence intervals for group means and effect sizes:
*   We implement **cluster-aware bootstrapping**, resampling at the **subject level** (with replacement) rather than the repetition level [CITE: Clustering_Bootstrap].
*   For each bootstrap iteration, we select $N$ subjects, extract all of their repetitions, and calculate the mean and standard error, preserving the intra-subject correlation structure.

### 8.2 Effect Size Calculations
We compute standard Cohen's d effect sizes to quantify the magnitude of differences between correct and incorrect repetitions:
$$d = \frac{\bar{X}_1 - \bar{X}_2}{SD_{\text{pooled}}}$$
$$SD_{\text{pooled}} = \sqrt{\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}$$
For peak knee flexion in squats, the cohort shift yields $d = 1.7306$ ($n=72$ correct vs $n=26$ incorrect) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. For lunges, peak flexion yields $d = 1.6904$ ($n=25$ correct vs $n=36$ incorrect) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

### 8.3 "Screening-Not-Prediction" Framing
In compliance with the project's clinical boundaries, all statistical results are framed as movement characterisations. We report associations, deviations, and measurement margins. No diagnostic models, injury likelihoods, or clinical predictions are evaluated or implied.
