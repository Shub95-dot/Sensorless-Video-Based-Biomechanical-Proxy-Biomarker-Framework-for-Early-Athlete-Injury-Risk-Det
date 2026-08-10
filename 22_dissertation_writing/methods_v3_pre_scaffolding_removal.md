# Methodology Chapter Draft (v3)
## Part 1 — Research Design and Pipeline Architecture

This chapter describes the research design, data pipelines, validation methodologies, and analytical frameworks developed to implement the markerless kinematic screening and explainable baseline tracking systems. The methodology is structured in three core layers: a physical pose estimation and validation layer (Track A Core), an uncertainty-weighting framework (Track B Transfer), and a personalised progression and explainable screening layer (Track A XAI). The framework is designed and validated strictly as a kinematic screening system to characterize biomechanical execution deviations from baseline states; it does not classify, predict, or diagnose physical injury risk, nor does it require longitudinal injury-outcome data.

---

## 2.1 Markerless Kinematic Extraction Pipeline

### 2.1.1 Pose Estimation and Camera Model
The pipeline processes monocular video sequences recorded at cohort-specific frame rates: 30 fps for the REHAB24-6 squat and lunge cohorts [source: 11_scripts/phase5a_rehab24_integration.py, filename convention `*-30fps-transposed.mp4`] and 60 fps for the OpenCap drop-jump validation cohort [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Penn Action squat sequences are processed from extracted JPEG frame stacks at the dataset-native extraction rate [CITE: Zhang_Penn_Action_2013]. 2D markerless pose estimation is executed using the MediaPipe Pose tracking engine (Heavy variant), computing the spatial coordinates of 33 keypoints [source: 11_scripts/phase3_pose_extraction.py].

> **Convention Note:** Squats and lunges use the **included angle** convention ($\approx 180^\circ$ = standing extension, smaller angle = deeper flexion), whereas the drop-jump validation uses the **clinical flexion** convention ($0^\circ$ = full extension, larger angle = deeper flexion). Raw joint angle values are not directly comparable; the uncertainty framework transfers validated *error magnitudes* (LoA widths) rather than raw joint angles.

For squats and lunges, the sagittal knee angle ($\theta$) is computed from hip, knee, and ankle MediaPipe landmarks using the 2D dot-product included-angle trigonometric model:
$$\theta = \arccos \left( \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\| \|\mathbf{v}\|} \right)$$
where $\mathbf{u}$ represents the thigh segment (knee-to-hip) and $\mathbf{v}$ represents the shank segment (knee-to-ankle) [source: 11_scripts/phase4a_knee_angle_extraction.py].

### 2.1.2 Trajectory Smoothing and Outlier Filtering
Raw coordinates are filtered in three steps to reduce high-frequency jitter and tracking spikes:
1.  **Outlier Gating:** Joint angles are constrained a priori to $[40.0^\circ, 185.0^\circ]$; values outside are flagged as tracking failures [source: 11_scripts/phase4a_knee_angle_extraction.py].
2.  **Smoothing Cascades:** Input trajectories are smoothed via a 5-frame centred median filter followed by a second-order Savitzky-Golay filter (window length 7) [CITE: Savitzky_Golay_1964], isolating voluntary motion while preserving peak morphology [source: 11_scripts/phase4e_trajectory_smoothing.py, lines 53–55 and 74–84].
3.  **Pose Quality Stratification:** Subjects with tracking spike rates $> 5.0\%$ are flagged for manual review [source: 11_scripts/phase4e_trajectory_smoothing.py].

### 2.1.3 Repetition Segmentation & Phase Detection
Trajectories are segmented into repetitions based on angular velocity numerical differentiation. Descent begins at a negative velocity zero-crossing and repetition ends when ascent velocity returns to zero [source: 11_scripts/phase4g_rep_segmentation.py]. Minor postural changes are ignored using a minimum joint excursion depth gate, and each valid rep is split into descent (start to peak flexion) and ascent (peak to end) phases [source: 11_scripts/phase4g_rep_segmentation.py].

---

## 2.2 Cohort Assembly and Experimental Datasets

Pipeline evaluation utilizes three cohorts:

### 2.2.1 The OpenCap Drop-Jump Validation Cohort
To establish ground-truth tracking accuracy under high-speed, dynamic impact landing conditions, we utilize the OpenCap Drop-Jump dataset (8 subjects, 48 trials, 60 fps) [source: 16_opencap_dropjump_outputs/phase6_final_report.md, source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Marker-Based Reference:** Captured via synchronized 10-camera 3D optoelectronic motion capture and two force plates [CITE: OpenCap_2022].
*   **Markerless Reference:** Recorded via sagittal camera and processed using the MediaPipe Heavy pipeline [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
This high-speed task establishes upper-bound measurement uncertainty limits for the monocular pipeline.

### 2.2.2 The REHAB24-6 Cohort
The primary cohort for baseline tracking, rule screening, and XAI validation is the `REHAB24-6` dataset (30 fps) [source: 18_personalised_baseline_outputs/baseline_design.md]:
*   **Squats:** 9 subjects, 98 repetitions (72 correct, 26 incorrect/deviated form featuring excess depth or rapid descent) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   **Lunges:** 8 subjects, 88 repetitions. Filtering leaves 61 reps from 7 usable subjects (25 correct, 36 incorrect) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Two subjects were excluded due to self-occlusion/tracking failures: Subject 5 (PM_042, 12/13 reps failed) and Subject 8 (PM_112, 12/12 reps failed) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
Correct/incorrect labels serve strictly as validation anchors for gating rules.

### 2.2.3 The Penn Action Exploratory Cohort
An exploratory cohort of 10 single-repetition Penn Action squat sequences [CITE: Zhang_Penn_Action_2013] — sourced from the Penn Action dataset (Zhang, Zhu & Derpanis, ICCV 2013), sequence IDs 1659–1889, squat class, filtered from 230 raw sequences to 10 included subjects via a documented gold/bronze/excluded quality audit [source: 3_metadata/squats_temporal_inclusion.csv] — evaluates qualitative monocular tracking failure modes under unconstrained in-the-wild conditions (varying camera angles, lighting, and resolution) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].

---

## 2.3 OpenCap Drop-Jump Ground Truth Validation

We validate knee flexion measurements against 3D optoelectronic ground truth across the 48 drop-jump trials using Bland-Altman 95% Limits of Agreement ($\text{Bias} \pm 1.96 \cdot \text{SD}$) [CITE: Bland_Altman_1986] [source: 16_opencap_dropjump_outputs/phase6_final_report.md]:
1.  **Peak landing flexion:** Mean bias $+19.72^\circ$ (95% LoA: $[7.73^\circ, 31.71^\circ]$, Pearson $r = 0.8238$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
2.  **Contact flexion:** Mean bias $-6.69^\circ$ (95% LoA: $[-26.77^\circ, 13.39^\circ]$, Pearson $r = 0.3209$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
3.  **Landing range of motion (ROM):** Mean bias $+26.41^\circ$ (95% LoA: $[2.34^\circ, 50.48^\circ]$, Pearson $r = 0.4020$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
4.  **Loading rate:** Mean bias $+13.30^\circ/\text{s}$ (95% LoA: $[-115.92^\circ/\text{s}, 142.51^\circ/\text{s}]$, Pearson $r = 0.6076$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 2.3.1 Deep-Flexion Constant Bias Isolation (Timing-Clean)
Static camera projection error is isolated from dynamic lag by analyzing joint angles at peak landing absorption ($n = 96$ static points, joint velocity $\approx 0$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. The peak flexion bias is $+10.52^\circ$ (95% LoA: $[-5.54^\circ, 26.58^\circ]$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Error magnitude correlation vs depth is not statistically significant (Pearson $r = -0.1568$, $p = 0.1271$; Spearman $\rho = -0.1905$, $p = 0.0631$) in the $70^\circ\text{--}120^\circ$ landing range, confirming that deep flexion tracking error behaves as a **constant systematic positive bias** rather than a depth-dependent slope [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 2.3.2 Robustness to Movement Conditions
Peak flexion bias is virtually identical between symmetric landings ($+10.36^\circ$, SD: $6.89^\circ$, $n=48$ points) and asymmetric landings ($+10.68^\circ$, SD: $9.39^\circ$, $n=48$ points) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This demonstrates that tracking errors are driven by monocular camera placement and projection geometry rather than movement loading symmetry [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 2.3.3 Contralateral Occlusion Limitation
Contralateral self-occlusion prevents monocular video validation of inter-limb asymmetry (Biomarker #5); it is demoted to a 3D reference (mocap mean: $2.07^\circ$, SD: $2.06^\circ$) and excluded from monocular screening rules [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## 2.4 Uncertainty Aggregation and Variance Decomposition

To link validation results to screening rules, drop-jump Limits of Agreement widths are converted into standard deviations and total variances via $SD_i = (LoA_{i,\text{upper}} - LoA_{i,\text{lower}})/3.92$ and $\sigma^2_{i,\text{total}} = (SD_i)^2$:
*   `contact_flexion` total variance: **$104.9867$** ($SD = 10.2463^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `peak_landing_flexion` total variance: **$37.4132$** ($SD = 6.1166^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `landing_rom` total variance: **$150.8291$** ($SD = 12.2813^\circ$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   `loading_rate` total variance: **$4346.2534$** ($SD = 65.9261^\circ/\text{s}$) [source: 17_uncertainty_framework_outputs/framework_design.md]

### 2.4.1 Projection and Motion Decompositions
We partition total variance into projection error ($\sigma^2_{i, \text{proj}}$) and dynamic motion error ($\sigma^2_{i, \text{mot}}$) via $\sigma^2_{i, \text{total}} = \sigma^2_{i, \text{proj}} + \sigma^2_{i, \text{mot}}$:
1.  **Peak Flexion:** Static landmark alignment yields a 100.0% projection, 0.0% motion split ($\sigma^2_{\text{proj}} = 37.4132$, $\sigma^2_{\text{mot}} = 0.0000$) [source: 17_uncertainty_framework_outputs/framework_design.md].
2.  **Contact Flexion:** A 90% projection, 10% motion split is assigned due to low entry velocity ($\sigma^2_{\text{proj}} = 94.4880$, $\sigma^2_{\text{mot}} = 10.4987$) [source: 17_uncertainty_framework_outputs/framework_design.md].
3.  **Loading Rate:** A 10% projection, 90% motion split is assigned due to extreme sensitivity to sub-frame timing lag ($\sigma^2_{\text{proj}} = 434.6253$, $\sigma^2_{\text{mot}} = 3911.6281$) [source: 17_uncertainty_framework_outputs/framework_design.md].
4.  **Range of Motion (ROM):** Propagating contact and peak variance endpoints yields a 92.62% projection, 7.38% motion split ($\sigma^2_{\text{proj}} = 139.7047$, $\sigma^2_{\text{mot}} = 11.1244$) [source: 17_uncertainty_framework_outputs/framework_design.md].

### 2.4.2 Inverse-Variance Weighting & Cross-Exercise Transfer Weights
Because motion-timing errors ($\sigma^2_{\text{mot}}$) are negligible in slow squats and lunges, transfer weighting uses only projection variance ($\sigma^2_{i, \text{proj}}$). Inverse-variance weights ($w_i = 1/\sigma^2_{i, \text{proj}}$) are normalized to:
*   **Peak Flexion:** **$57.15\%$** ($w \approx 0.0267$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Start/Contact Flexion:** **$22.63\%$** ($w \approx 0.0106$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Range of Motion (ROM):** **$15.30\%$** ($w \approx 0.0072$) [source: 17_uncertainty_framework_outputs/framework_design.md]
*   **Joint Velocity:** **$4.92\%$** ($w \approx 0.0023$) [source: 17_uncertainty_framework_outputs/framework_design.md]

A 9-configuration sensitivity sweep proves weight stability: across all permutations, Peak Flexion dominates ($50.01\%\text{--}58.59\%$) and velocity is heavily down-weighted ($2.30\%\text{--}9.38\%$), confirming that assumed splits do not corrupt framework decisions [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 2.5 Personalised Baseline and Digital Twin Demonstrations

We track changes relative to the individual's baseline.

### 2.5.1 Baseline Initialization
A per-subject baseline mean ($\mu_{\text{base}, i}$) is calculated from correct repetitions 1 and 2:
$$\mu_{\text{base}, i} = \frac{1}{2} (x_{1, i} + x_{2, i})$$
Baseline standard error is recorded for descriptive context but omitted from decision rules due to small-sample instability [source: 18_personalised_baseline_outputs/baseline_design.md].

### 2.5.2 Conditional Digital Twin Update Rule
The digital twin updates the reference mean dynamically across a sequence of repetitions. To prevent baseline contamination from abnormal movements, updates use a conditional update rule:
*   Calculate absolute deviation: $\Delta_i = |x_{t+1, i} - \mu_{t, i}|$ [source: 19_digital_twin_outputs/twin_design.md].
*   Compare to the validated 95% Noise Floor ($NF_i$):
    *   **If $\Delta_i \le NF_i$ (Within-Noise):** $\mu_{t+1, i} = (N_{t, i} \cdot \mu_{t, i} + x_{t+1, i})/(N_{t, i} + 1)$ and $N_{t+1, i} = N_{t, i} + 1$ [source: 19_digital_twin_outputs/twin_design.md].
    *   **If $\Delta_i > NF_i$ (Deviation Detected):** Lock reference: $\mu_{t+1, i} = \mu_{t, i}$ and $N_{t+1, i} = N_{t, i}$ [source: 19_digital_twin_outputs/twin_design.md].
Exclusions are counted and logged to prevent update drift while tracking baseline transitions [source: 19_digital_twin_outputs/twin_design.md].

---

## 2.6 Rule-Based Kinematic Screening Layer

### 2.6.1 Modality Choice: Personalised-Deviation Screening (Option B)
We select Option B (Personalised-Deviation Screening), flagging a repetition only if it deviates from the subject's own baseline mean ($\mu_{\text{base}, i}$) beyond the validated noise floor ($NF_i$). This controls for individual anatomy and systematic camera perspective offsets, rejecting fixed population thresholds (Option A).

### 2.6.2 Personalised Screening Rules
The noise floors ($NF_i$) are set at 95% confidence intervals ($1.96 \cdot SD_{\text{proj}, i}$):
*   $NF_{\text{peak}} = \pm 11.9885^\circ$ [source: 20_screening_outputs/screening_rules_design.md]
*   $NF_{\text{rom}} = \pm 23.1666^\circ$ [source: 20_screening_outputs/screening_rules_design.md]
*   $NF_{\text{velocity}} = \pm 40.8615^\circ/\text{s}$ [source: 20_screening_outputs/screening_rules_design.md]

Three screening rules are defined:
1.  **EXCESS_DEPTH:** $x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - 11.9885^\circ$ [source: 20_screening_outputs/screening_rules_design.md] (included-angle convention: smaller values indicate deeper flexion).
2.  **EXCESS_ROM:** $x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + 23.1666^\circ$ [source: 20_screening_outputs/screening_rules_design.md].
3.  **EXCESS_VELOCITY:** $x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + 40.8615^\circ/\text{s}$ [source: 20_screening_outputs/screening_rules_design.md].

Violations trigger `SCREENING_POSITIVE` and record active rules and numeric deviation margins [source: 20_screening_outputs/screening_rules_design.md].

---

## 2.7 Counterfactual Explainable AI (XAI)

### 2.7.1 Faithfulness by Construction
Unlike post-hoc local approximations (e.g., SHAP or LIME) that introduce local fit errors, our explanations are **faithful by construction** because the rules *are* the decision boundaries [source: 21_xai_outputs/xai_design.md]. The margins ($M_i$) are calculated directly:
*   $M_{\text{depth}} = (\mu_{\text{base}, \text{peak}} - 11.9885) - x_{\text{peak}}$ [source: 11_scripts/phase11_counterfactual_xai.py]
*   $M_{\text{rom}} = x_{\text{rom}} - (\mu_{\text{base}, \text{rom}} + 23.1666)$ [source: 11_scripts/phase11_counterfactual_xai.py]
*   $M_{\text{velocity}} = x_{\text{velocity}} - (\mu_{\text{base}, \text{velocity}} + 40.8615)$ [source: 11_scripts/phase11_counterfactual_xai.py]

### 2.7.2 Templates & Descriptive Guardrail
Templates describe the mathematical state required to clear flags (e.g., for `EXCESS_DEPTH`: `"Had the peak flexion angle been at least T_depth° (representing a shallower bend of M_depth° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/xai_design.md]). This avoids prescriptive coaching advice.

### 2.7.3 Multi-Rule Coupling & Minimal Kinematic Intervention (MKI)
If both `EXCESS_DEPTH` and `EXCESS_ROM` fire, we resolve physical coupling by assuming range of motion scales directly with peak flexion depth (constant standing start point). The MKI calculates the maximum flexion adjustment:
$$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$
This is reported as a set of descriptive conditions; an independent rule violation (e.g., `EXCESS_VELOCITY`) is appended as a separate condition (e.g., requiring descent velocity to be $M_{\text{velocity}}^\circ/\text{s}$ slower) [source: 21_xai_outputs/xai_design.md].

### 2.7.4 Confidence Buffers
Explanations evaluate the margin $M_i$ against a confidence boundary $0.5 \cdot NF_i$; deviations within this buffer are marked `LOW CONFIDENCE (Near Noise Floor)` [source: 21_xai_outputs/xai_design.md].

---

## 2.8 Statistical Analysis Methods

### 2.8.1 Cluster-Aware Bootstrapping
To calculate robust confidence intervals when subjects perform multiple repetitions, we implement **cluster-aware bootstrapping** [CITE: Field_Welsh_2007], which resamples subjects with replacement (including all their reps) rather than individual repetitions, preserving the intra-subject correlation.

### 2.8.2 Effect Size Calculations
Cohen's d [CITE: Cohens_d_1988] is computed as $d = (\bar{X}_1 - \bar{X}_2)/SD_{\text{pooled}}$, where $SD_{\text{pooled}} = \sqrt{((n_1-1)s_1^2 + (n_2-1)s_2^2)/(n_1+n_2-2)}$. Squat peak flexion yields $d = 1.7306$ ($n=72$ correct, $26$ incorrect) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. Lunge peak flexion yields $d = 1.6904$ ($n=25$ correct, $36$ incorrect) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

### 2.8.3 Classification Performance Metrics
Classification model performance in this dissertation is reported as balanced accuracy (the unweighted mean of per-class recall, equivalent to the mean of sensitivity and specificity), not raw accuracy. This choice is motivated by class imbalance in both exercise cohorts: the REHAB24-6 squat cohort contains 72 correct and 26 incorrect repetitions (73.47% correct-class prevalence) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt], and the lunge cohort contains 25 correct and 36 incorrect repetitions (40.98% correct-class prevalence) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Under these imbalances, a trivial majority-class classifier would achieve 73.47% raw accuracy on squats without learning any discriminative signal, making raw accuracy an unreliable indicator of true model performance. Balanced accuracy corrects for this by weighting each class equally, so a majority-class classifier scores 50.00% regardless of imbalance. This distinction is empirically visible in Chapter 13, where the LSTM under Scheme B produces 73.47% raw accuracy but 50.00% balanced accuracy on squats — the latter correctly revealing that the model has collapsed to majority-class prediction [source: 23_temporal_model_outputs/temporal_model_comparison.csv].
