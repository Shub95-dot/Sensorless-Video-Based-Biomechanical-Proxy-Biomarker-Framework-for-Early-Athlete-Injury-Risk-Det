# Chapter 4: Squat Kinematic Screening

This chapter presents the results of the markerless kinematic screening framework applied to the squat exercise. We evaluate the framework's capacity to extract biomechanically plausible joint angles and discriminate between correct and incorrect movement execution. First, we outline the cohort characteristics and the coordinate convention used for kinematic calculations. Second, we present the headline statistical findings, focusing on the biomarkers that successfully discriminate movement quality. Third, we evaluate cross-cohort consistency by comparing a controlled laboratory dataset to an in-the-wild video cohort, establishing pipeline reproducibility. Finally, we discuss the clinical interpretation of these kinematic patterns and outline the framework's limitations.

---

## 4.1. Cohort and Methodological Setup

To evaluate the generalization and discriminative capability of the monocular pose estimation pipeline, squats were analyzed across two distinct cohorts:

1.  **YouTube Cohort (In-the-Wild)**: Consisted of $n = 10$ subjects, with each subject performing a single squat repetition under unconstrained, real-world conditions (varying camera perspectives, backgrounds, and clothing) [source: 4_pose_outputs/temporal/squats_biomarkers.csv]. This cohort served as a test of pipeline generalization and descriptive baseline consistency.
2.  **REHAB24-6 Cohort (Controlled Laboratory)**: Consisted of $n = 9$ subjects performing a total of $98$ processed repetitions ($72$ correct and $26$ incorrect repetitions) in a controlled laboratory setting [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]. Movement correctness was labeled by expert clinical observers based on the presence of form deviations (specifically, excessive squat depth and rapid loading).

### 4.1.1. Kinematic Coordinate Convention
In contrast to the clinical flexion convention ($0^\circ$ representing full standing extension) adopted in the drop-jump validation chapter (Chapter 6) [source: 22_dissertation_writing/results_dropjump_validation_v1.md], squats in this chapter were analyzed using the **included-angle convention**. Under this convention:
*   A value of $\approx 180^\circ$ represents full standing extension.
*   Smaller joint angles represent deeper flexion bends (e.g., a $90^\circ$ angle represents a right-angle knee bend, and a $50^\circ$ angle represents deep flexion).
*   Mathematically, the relationship is defined as:
    $$\theta_{\text{included}} = 180.0^\circ - \theta_{\text{clinical\_flexion}}$$

This distinction is critical when comparing joint angles across chapters. Direct comparisons of raw angular values between Chapter 6 (Drop-Jump) and Chapter 4 (Squat) will read as contradictory without accounting for this convention inversion. The uncertainty-weighted framework (Chapter 8) handles this by transferring validated error variances ($\sigma^2_{\text{proj}}$) rather than raw coordinate values [source: 17_uncertainty_framework_outputs/framework_design.md].

### 4.1.2. Knee-Flexion Biomarkers
For each squat repetition, the following knee-flexion biomarkers were extracted from the smoothed sagittal-view trajectory [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]:
1.  **Peak Flexion Angle ($^\circ$)**: The minimum included knee angle reached during the repetition (representing the deepest point of the squat).
2.  **Range of Motion (ROM, $^\circ$)**: The angular excursion computed as the difference between the peak extension angle at standing and the peak flexion angle at the bottom of the squat.
3.  **Descent Duration (frames)**: The frame count of the eccentric descent phase (from movement initiation to peak flexion).
4.  **Ascent Duration (frames)**: The frame count of the concentric ascent phase (from peak flexion to return to standing).
5.  **Peak/Mean Descent Velocity ($^\circ$/frame)**: The maximum and average rate of change of the included angle during the descent phase.
6.  **Peak/Mean Ascent Velocity ($^\circ$/frame)**: The maximum and average rate of change of the included angle during the ascent phase.
7.  **Jerk Proxy Standard Deviation**: The standard deviation of the third time-derivative of the knee flexion trajectory, serving as a proxy for movement roughness and lack of neuromuscular control.

---

## 4.2. Headline Screening Findings (Form Discrimination)

Statistical comparison between correct ($n = 72$) and incorrect ($n = 26$) squat repetitions in the REHAB24-6 cohort demonstrated that incorrect form was characterized by **excessive knee flexion depth (deeper bend), a faster descent phase, and a rougher (jerkier) movement profile** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]. Table 4.1 summarizes the group means, standard deviations, and Cohen's $d$ effect sizes with bootstrapped 95% confidence intervals (CIs).

### Table 4.1: Correct vs. Incorrect Squat Kinematic Comparison ($n = 98$ reps)

| Biomarker | Correct Mean ($n=72$) | Incorrect Mean ($n=26$) | Cohen's $d$ Effect Size | 95% Bootstrap Confidence Interval (CI) | Form Discrimination Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Peak Flexion ($^\circ$)** | $60.85^\circ \pm 12.72^\circ$ | $41.14^\circ \pm 6.20^\circ$ | $+1.7306$ | $[1.2438, 2.4726]$ | **Highly Discriminative** (deeper included angle in incorrect) [source: phase5b_effect_sizes_ci.csv] |
| **ROM ($^\circ$)** | $111.19^\circ \pm 18.06^\circ$ | $134.31^\circ \pm 7.23^\circ$ | $-1.4484$ | $[-2.2198, -1.0052]$ | **Highly Discriminative** (larger ROM/excursion in incorrect) [source: phase5b_effect_sizes_ci.csv] |
| **Peak Descent Velocity ($^\circ$/fr)** | $-5.85^\circ \pm 1.75^\circ$ | $-7.24^\circ \pm 1.52^\circ$ | $+0.8216$ | $[0.1385, 1.7403]$ | **Discriminative** (faster descent in incorrect) [source: phase5b_effect_sizes_ci.csv] |
| **Mean Descent Velocity ($^\circ$/fr)** | $-2.23^\circ \pm 0.74^\circ$ | $-2.77^\circ \pm 0.54^\circ$ | $+0.7768$ | $[0.1855, 1.5539]$ | **Discriminative** (faster mean descent in incorrect) [source: phase5b_effect_sizes_ci.csv] |
| **Jerk Proxy Standard Deviation** | $0.75 \pm 0.19$ | $0.85 \pm 0.15$ | $-0.5319$ | $[-1.3246, -0.0325]$ | **Discriminative** (elevated jerk/reduced smoothness) [source: phase5b_effect_sizes_ci.csv] |
| **Peak Ascent Velocity ($^\circ$/fr)** | $6.86^\circ \pm 2.22^\circ$ | $7.91^\circ \pm 1.54^\circ$ | $-0.5049$ | $[-1.4838, 0.0848]$ | **Non-Discriminative** (CI crosses zero) [source: phase5b_effect_sizes_ci.csv] |
| **Mean Ascent Velocity ($^\circ$/fr)** | $2.33^\circ \pm 0.88^\circ$ | $2.73^\circ \pm 0.46^\circ$ | $-0.4996$ | $[-1.7017, 0.1301]$ | **Non-Discriminative** (CI crosses zero) [source: phase5b_effect_sizes_ci.csv] |
| **Descent Duration (frames)** | $49.60 \pm 13.98$ | $47.50 \pm 9.51$ | $+0.1657$ | N/A | **Non-Discriminative** [source: phase5a_integration_summary.txt] |
| **Ascent Duration (frames)** | $50.85 \pm 14.01$ | $47.96 \pm 6.51$ | $+0.2289$ | N/A | **Non-Discriminative** [source: phase5a_integration_summary.txt] |

### 4.2.1. Flexion Depth and Joint Excursion
Incorrect repetitions were characterized by a highly significant increase in squat depth, as demonstrated by the peak flexion included angle:
*   Correct squats achieved a mean peak included angle of **$60.85^\circ \pm 12.72^\circ$**, representing a standard parallel or slightly sub-parallel squat [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   Incorrect squats reached a mean peak included angle of **$41.14^\circ \pm 6.20^\circ$**, representing an excessively deep squat [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   This difference represents a large effect size of **$d = 1.7306$** (95% CI: $[1.2438, 2.4726]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv].

Correspondingly, the joint range of motion (ROM) was significantly larger in incorrect repetitions:
*   Correct squats had a mean ROM of **$111.19^\circ \pm 18.06^\circ$** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   Incorrect squats had a mean ROM of **$134.31^\circ \pm 7.23^\circ$** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   This yielded a large negative effect size of **$d = -1.4484$** (95% CI: $[-2.2198, -1.0052]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv].

The Cohen's $d$ is negative because the correct group mean is smaller than the incorrect group mean ($M_{\text{correct}} < M_{\text{incorrect}}$). This result is physically and mathematically consistent: because incorrect squats achieved a deeper bottom position (smaller peak included angle), the total joint excursion from standing to the bottom was substantially larger. This aligns perfectly with the screening layer's `EXCESS_ROM` rule [source: 20_screening_outputs/screening_rules_design.md].

### 4.2.2. Descent-Phase Temporal Localization
A key finding of this chapter is that form discrimination is heavily localized to the eccentric descent phase of the squat. Both descent velocity metrics were significantly elevated for incorrect repetitions:
*   **Peak Descent Velocity**: Correct squats had a peak descent rate of **$-5.85^\circ/\text{frame} \pm 1.75^\circ/\text{frame}$**, compared to **$-7.24^\circ/\text{frame} \pm 1.52^\circ/\text{frame}$** for incorrect squats ($d = 0.8216$, 95% CI: $[0.1385, 1.7403]$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt / phase5b_effect_sizes_ci.csv].
*   **Mean Descent Velocity**: Correct squats had an average descent rate of **$-2.23^\circ/\text{frame} \pm 0.74^\circ/\text{frame}$**, compared to **$-2.77^\circ/\text{frame} \pm 0.54^\circ/\text{frame}$** for incorrect squats ($d = 0.7768$, 95% CI: $[0.1855, 1.5539]$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt / phase5b_effect_sizes_ci.csv].

Velocity values are negative because the included angle decreases during descent. The positive Cohen's $d$ values ($0.8216$ and $0.7768$) reflect that the correct group's velocity was algebraically larger (i.e., closer to zero, representing a slower physical descent speed) than the incorrect group's velocity (which was more negative, representing a faster physical descent speed).

### 4.2.3. Non-Discriminative Ascent Phase
In direct contrast to the descent phase, the concentric ascent phase did not reliably discriminate between form groups:
*   **Peak Ascent Velocity**: Correct squats had a peak ascent rate of **$6.86^\circ/\text{frame} \pm 2.22^\circ/\text{frame}$**, while incorrect squats reached **$7.91^\circ/\text{frame} \pm 1.54^\circ/\text{frame}$** ($d = -0.5049$, 95% CI: $[-1.4838, 0.0848]$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt / phase5b_effect_sizes_ci.csv].
*   **Mean Ascent Velocity**: Correct squats averaged **$2.33^\circ/\text{frame} \pm 0.88^\circ/\text{frame}$**, while incorrect squats averaged **$2.73^\circ/\text{frame} \pm 0.46^\circ/\text{frame}$** ($d = -0.4996$, 95% CI: $[-1.7017, 0.1301]$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt / phase5b_effect_sizes_ci.csv].

Because both ascent velocity confidence intervals cross zero ($[-1.4838, +0.0848]$ and $[-1.7017, +0.1301]$), the ascent velocity is statistically non-discriminative for squats [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. This represents an important cross-exercise contrast: as demonstrated in Chapter 5, the ascent phase of a lunge is highly discriminative due to the concentric propulsion requirements of spring-back recovery, whereas squat ascent kinematics do not systematically differentiate movement quality.

### 4.2.4. Movement Smoothness (Jerk Proxy)
Neuromuscular control and movement smoothness were evaluated using the jerk proxy standard deviation:
*   Correct repetitions exhibited a jerk proxy of **$0.75 \pm 0.19$** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   Incorrect repetitions exhibited a jerk proxy of **$0.85 \pm 0.15$** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].
*   This difference was statistically significant, with a moderate effect size of **$d = -0.5319$** (95% CI: $[-1.3246, -0.0325]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv].

The negative effect size indicates that correct repetitions had a lower jerk proxy (were smoother) than incorrect repetitions, which displayed elevated jerk proxy values. This reflects reduced eccentric motor control and increased trajectory wobble in incorrect executions.

---

## 4.3. Cross-Cohort Consistency and Generalisation

To evaluate the generalization of the markerless pose-extraction pipeline, descriptive kinematics from the controlled REHAB24-6 cohort were compared to the in-the-wild YouTube cohort. Both cohorts produced overlapping, biomechanically plausible ranges for knee joint angles, demonstrating that the software pipeline generalizes across diverse lighting, clothing, and camera profiles:
*   The YouTube cohort ($n = 10$ subjects, single-rep) had a mean peak flexion angle of **$78.84^\circ \pm 30.76^\circ$**, a mean ROM of **$99.27^\circ \pm 31.12^\circ$**, and a mean jerk proxy of **$1.42 \pm 0.65$** [source: 4_pose_outputs/temporal/squats_biomarkers.csv statistical run].
*   The REHAB24-6 cohort ($n = 98$ reps) had an overall mean peak flexion angle of **$55.62^\circ \pm 14.31^\circ$**, a mean ROM of **$117.32^\circ \pm 18.91^\circ$**, and a mean jerk proxy of **$0.78 \pm 0.18$** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].

### 4.3.1. Cohort-Level Biomechanical Differences
The systematically deeper peak flexion (smaller included angle: $55.62^\circ$ vs. $78.84^\circ$) and larger ROM ($117.32^\circ$ vs. $99.27^\circ$) in the REHAB24-6 cohort reflect the difference in cohort constraints and movement instructions:
*   The REHAB24-6 trials were performed in a biomechanics laboratory under explicit instructions to perform deep squats and to deliberately introduce form errors (such as deep flexion beyond parallel) for clinical training.
*   The YouTube videos captured recreational squatters performing self-selected repetitions under varied physical constraints, where joint extension and flexion depth were typically more restricted.
*   The elevated jerk proxy in the YouTube cohort ($1.42 \pm 0.65$ vs. $0.78 \pm 0.18$) reflects the increased tracking noise inherent in lower-quality, compressed in-the-wild video recordings rather than poorer neuromuscular control.

### 4.3.2. Methodological Role of Generalisation
The cross-cohort consistency check represents a **reproducibility finding**, demonstrating that the pose-extraction pipeline generates biologically plausible kinematic values across widely differing environments. However, cohort consistency is not a proof of tracking accuracy. The absolute accuracy of the monocular coordinate tracking is established in the Drop-Jump Validation Chapter (Chapter 6), where single-camera values are directly compared against optoelectronic and force-plate ground truth [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

---

## 4.4. Discussion and Clinical Screening Guardrails

The kinematic signature identified in the REHAB24-6 cohort—characterized by deeper knee flexion, a faster eccentric descent phase, and an elevated jerk proxy—carries important biomechanical implications for injury risk screening. 

### 4.4.1. Clinical Risk Interpretation
In clinical biomechanics, a rapid descent velocity combined with deep flexion indicates an eccentric control deficit. The subject is essentially "dropping" into the squat, relying on passive osteoligamentous structures rather than active musculature to arrest momentum at the bottom of the movement.
*   Rapid descent velocity increases the peak impact forces at the bottom turnaround point, generating high patellofemoral joint reaction forces and tibiofemoral shear stresses [CITE: Powers_2002] [CITE: FEA_2023].
*   Deep flexion past parallel ($\theta_{\text{included}} < 60^\circ$) coupled with dynamic loading is associated with elevated patellofemoral compressive stress [CITE: PMC_12736615].
*   The elevated jerk proxy standard deviation indicates a loss of movement smoothness, reflecting micro-instabilities and compensatory movement adjustments that occur when neuromuscular control is compromised [CITE: Farrokhi_2011].

### 4.4.2. Screening-not-Prediction Framing
It is crucial to maintain a strict clinical guardrail regarding the interpretation of these findings. This framework is a **kinematic screening layer**, designed to identify deviations from a baseline movement template, rather than an injury prediction model. The framework identifies kinematic patterns that are biomechanically associated with elevated risk in scientific literature; it does not claim to diagnose clinical pathology or predict the statistical probability of injury occurrence.

---

## 4.5. Limitations

Several limitations of this cohort evaluation must be noted:
1.  **Small Incorrect Sample Size**: The REHAB24-6 cohort contained only $n = 26$ incorrect repetitions, restricting the statistical power of the bootstrapped confidence intervals.
2.  **Sagittal-Plane Restriction**: Monocular sagittal-view tracking cannot resolve out-of-plane movements. Critical injury-associated kinematics, such as knee valgus (coronal plane projection) and tibial rotation (transverse plane), cannot be captured by a single sagittal camera.
3.  **Error Heterogeneity**: The "incorrect" label pooled multiple types of form deviations (excessive depth, rapid descent, knee-wobble). A larger cohort is required to train multi-class classifiers capable of separating specific error sub-types.
4.  **Reproducibility-vs-Accuracy**: While the cross-cohort generalisation demonstrates reproducibility, it does not validate tracking accuracy. The single-camera pipeline's spatial overestimation bias at deep flexion ($+10.52^\circ$ timing-clean, $+19.72^\circ$ peak-to-peak) must be subtracted when absolute joint angles are evaluated [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

---

## 4.6. Figures and Provenance

The findings presented in this chapter are supported by the following publication-ready figures, with data provenance detailed in `figures_publication/figure_data_provenance.csv` [source: 14_rehab24_outputs/figures_publication/figure_data_provenance.csv]:

*   **Figure 4.1: Knee Flexion Angle Distributions for Correct vs. Incorrect Squat Repetitions**
    *   *Source file*: `14_rehab24_outputs/figures_publication/fig1_correct_vs_incorrect.png`
    *   *Description*: Histograms comparing the distribution of peak flexion and range of motion for correct ($n=72$) and incorrect ($n=26$) repetitions, illustrating the deep-flexion shift in the incorrect group.
*   **Figure 4.2: Forest Plot of Cohen's $d$ Effect Sizes and 95% Confidence Intervals for Squat Biomarkers**
    *   *Source file*: `14_rehab24_outputs/figures_publication/fig2_effect_sizes.png`
    *   *Description*: Cohen's $d$ effect size plot showing significant effects for peak flexion, ROM, descent velocities, and jerk proxy, while ascent velocities cross zero.
    *   *Note*: A known label-overprinting bug exists in the background "small/medium/large" guide-labels in this figure, which will be resolved in the final compilation.
*   **Figure 4.3: Cross-Cohort Kinematic Distribution Comparison**
    *   *Source file*: `14_rehab24_outputs/figures_publication/fig3_cross_cohort_distributions.png`
    *   *Description*: Overlay of joint angle distributions comparing the YouTube cohort ($n=10$ subjects) and the REHAB24-6 cohort ($n=98$ reps), showing generalisation of biomechanical ranges across diverse settings.
*   **Figure 4.4: Representative Correct vs. Incorrect Knee Flexion Trajectories**
    *   *Source file*: `14_rehab24_outputs/figures_publication/fig4_representative_trajectories.png`
    *   *Description*: Time-series overlay of representative correct (Subject 1, rep 2, $121$ frames) and incorrect (Subject 1, rep 17, $91$ frames) squat repetitions, illustrating the rapid eccentric descent and excessive flexion depth of incorrect execution.
