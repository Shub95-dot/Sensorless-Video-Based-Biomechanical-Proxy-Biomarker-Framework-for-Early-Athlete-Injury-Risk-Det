# Chapter 4: Squat Kinematic Screening

This chapter presents the markerless kinematic screening results for the squat exercise. We evaluate form discrimination between correct and incorrect repetitions, cross-cohort pipeline reproducibility, and the clinical interpretation of the kinematic signatures identified. Statistical methods (Cohen's $d$, cluster-aware bootstrapping) are described in full in Chapter 2.

---

## 4.1. Cohort and Methodological Setup

Squats were analyzed across two distinct cohorts:

1.  **Penn Action Cohort (In-the-Wild)**: $n = 10$ subjects, each performing a single squat repetition under unconstrained, real-world conditions (varying camera perspectives, backgrounds, and clothing) [CITE: Zhang_Penn_Action_2013] [source: 4_pose_outputs/temporal/squats_biomarkers.csv]. Sequences were drawn from the Penn Action dataset (Zhang, Zhu & Derpanis, ICCV 2013), filtered from 230 raw squat sequences (IDs 1659–1889) to 10 included subjects via a gold/bronze/excluded quality audit [source: 3_metadata/squats_temporal_inclusion.csv]. This cohort served as a test of pipeline generalization and descriptive baseline consistency.
2.  **REHAB24-6 Cohort (Controlled Laboratory)**: $n = 9$ subjects, $98$ processed repetitions ($72$ correct, $26$ incorrect), recorded in a controlled laboratory setting with correctness labeled by expert clinical observers based on form deviations (excessive squat depth and rapid loading) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].

### 4.1.1. Kinematic Coordinate Convention
Squats in this chapter use the **included-angle convention** ($\approx 180^\circ$ = full standing extension; smaller values = deeper flexion), defined as:
$$\theta_{\text{included}} = 180.0^\circ - \theta_{\text{clinical\_flexion}}$$
This differs from the clinical flexion convention used in the drop-jump validation (Chapter 6) [source: 22_dissertation_writing/results_dropjump_validation_v1.md]. Raw angular values are not directly comparable across chapters; the uncertainty framework (Chapter 8) transfers validated projection error variances ($\sigma^2_{\text{proj}}$) rather than raw coordinates [source: 17_uncertainty_framework_outputs/framework_design.md].

### 4.1.2. Knee-Flexion Biomarkers
For each squat repetition, the following knee-flexion biomarkers were extracted from the smoothed sagittal-view trajectory [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]:
1.  **Peak Flexion Angle ($^\circ$)**: The minimum included knee angle reached during the repetition, representing the deepest point of the squat.
2.  **Range of Motion (ROM, $^\circ$)**: The angular excursion computed as the difference between the peak extension angle at standing and the peak flexion angle at the squat bottom.
3.  **Descent Duration (frames)**: The frame count of the eccentric descent phase (from movement initiation to peak flexion).
4.  **Ascent Duration (frames)**: The frame count of the concentric ascent phase (from peak flexion to return to standing).
5.  **Peak/Mean Descent Velocity ($^\circ$/frame)**: The maximum and average rate of change of the included angle during the descent phase.
6.  **Peak/Mean Ascent Velocity ($^\circ$/frame)**: The maximum and average rate of change of the included angle during the ascent phase.
7.  **Jerk Proxy Standard Deviation**: The standard deviation of the third time-derivative of the knee flexion trajectory, serving as a proxy for movement roughness and neuromuscular control.

---

## 4.2. Headline Screening Findings (Form Discrimination)

Statistical comparison between correct ($n = 72$) and incorrect ($n = 26$) squat repetitions in the REHAB24-6 cohort demonstrated that incorrect form was characterized by **excessive knee flexion depth, a faster descent phase, and a rougher (jerkier) movement profile** [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt]. Table 4.1 summarizes group means, standard deviations, Cohen's $d$ effect sizes, and bootstrapped 95% confidence intervals (CIs).

### Table 4.1: Correct vs. Incorrect Squat Kinematic Comparison ($n = 98$ reps)

| Biomarker | Correct Mean ($n=72$) | Incorrect Mean ($n=26$) | Cohen's $d$ | 95% CI | Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Peak Flexion ($^\circ$)** | $60.85^\circ \pm 12.72^\circ$ | $41.14^\circ \pm 6.20^\circ$ | $+1.7306$ | $[1.2438, 2.4726]$ | **Highly Discriminative** [source: phase5b_effect_sizes_ci.csv] |
| **ROM ($^\circ$)** | $111.19^\circ \pm 18.06^\circ$ | $134.31^\circ \pm 7.23^\circ$ | $-1.4484$ | $[-2.2198, -1.0052]$ | **Highly Discriminative** [source: phase5b_effect_sizes_ci.csv] |
| **Peak Descent Velocity ($^\circ$/fr)** | $-5.85^\circ \pm 1.75^\circ$ | $-7.24^\circ \pm 1.52^\circ$ | $+0.8216$ | $[0.1385, 1.7403]$ | **Discriminative** [source: phase5b_effect_sizes_ci.csv] |
| **Mean Descent Velocity ($^\circ$/fr)** | $-2.23^\circ \pm 0.74^\circ$ | $-2.77^\circ \pm 0.54^\circ$ | $+0.7768$ | $[0.1855, 1.5539]$ | **Discriminative** [source: phase5b_effect_sizes_ci.csv] |
| **Jerk Proxy SD** | $0.75 \pm 0.19$ | $0.85 \pm 0.15$ | $-0.5319$ | $[-1.3246, -0.0325]$ | **Discriminative** [source: phase5b_effect_sizes_ci.csv] |
| **Peak Ascent Velocity ($^\circ$/fr)** | $6.86^\circ \pm 2.22^\circ$ | $7.91^\circ \pm 1.54^\circ$ | $-0.5049$ | $[-1.4838, 0.0848]$ | **Non-Discriminative** (CI crosses zero) [source: phase5b_effect_sizes_ci.csv] |
| **Mean Ascent Velocity ($^\circ$/fr)** | $2.33^\circ \pm 0.88^\circ$ | $2.73^\circ \pm 0.46^\circ$ | $-0.4996$ | $[-1.7017, 0.1301]$ | **Non-Discriminative** (CI crosses zero) [source: phase5b_effect_sizes_ci.csv] |
| **Descent Duration (frames)** | $49.60 \pm 13.98$ | $47.50 \pm 9.51$ | $+0.1657$ | N/A | **Non-Discriminative** [source: phase5a_integration_summary.txt] |
| **Ascent Duration (frames)** | $50.85 \pm 14.01$ | $47.96 \pm 6.51$ | $+0.2289$ | N/A | **Non-Discriminative** [source: phase5a_integration_summary.txt] |

### 4.2.1. Flexion Depth and Joint Excursion
Incorrect repetitions reached a mean peak included angle of $\mathbf{41.14^\circ \pm 6.20^\circ}$, compared to $\mathbf{60.85^\circ \pm 12.72^\circ}$ for correct repetitions — a large effect ($d = 1.7306$, 95% CI: $[1.2438, 2.4726]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. The deeper descent position directly enlarged joint excursion: incorrect squats had a mean ROM of $\mathbf{134.31^\circ \pm 7.23^\circ}$ versus $\mathbf{111.19^\circ \pm 18.06^\circ}$ for correct repetitions ($d = -1.4484$, 95% CI: $[-2.2198, -1.0052]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. The negative Cohen's $d$ for ROM is directionally consistent with the included-angle convention: because incorrect squats achieved a deeper bottom position (smaller peak included angle), the total joint excursion from standing to the bottom was substantially larger, with the correct group mean ($111.19^\circ$) being smaller than the incorrect group mean ($134.31^\circ$). This relationship directly triggers the `EXCESS_ROM` screening rule [source: 20_screening_outputs/screening_rules_design.md].

### 4.2.2. Descent-Phase Temporal Localization
A key finding is that form discrimination is heavily localized to the eccentric descent phase. Peak descent velocity was $-7.24^\circ/\text{frame} \pm 1.52^\circ/\text{frame}$ for incorrect versus $-5.85^\circ/\text{frame} \pm 1.75^\circ/\text{frame}$ for correct repetitions ($d = 0.8216$, 95% CI: $[0.1385, 1.7403]$); mean descent velocity showed a comparable pattern ($-2.77^\circ/\text{frame} \pm 0.54^\circ/\text{frame}$ vs. $-2.23^\circ/\text{frame} \pm 0.74^\circ/\text{frame}$; $d = 0.7768$, 95% CI: $[0.1855, 1.5539]$) [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt / phase5b_effect_sizes_ci.csv]. Velocity values are negative because the included angle decreases during descent. The positive Cohen's $d$ values ($0.8216$ and $0.7768$) reflect that the correct group's velocity was algebraically larger (i.e., closer to zero, representing a physically slower descent) than the incorrect group's velocity, which was more negative, representing a faster physical descent speed.

### 4.2.3. Non-Discriminative Ascent Phase
In direct contrast to the descent phase, the concentric ascent phase did not reliably discriminate between form groups. Both ascent metrics produced bootstrapped CIs spanning zero — peak ascent: $d = -0.5049$ ($[-1.4838, 0.0848]$); mean ascent: $d = -0.4996$ ($[-1.7017, 0.1301]$) — confirming the ascent is statistically non-discriminative for squats [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. This is an important cross-exercise contrast: as shown in Chapter 5, the lunge ascent phase is highly discriminative due to the concentric propulsion requirements of spring-back recovery, whereas squat ascent kinematics do not systematically differentiate movement quality.

### 4.2.4. Movement Smoothness (Jerk Proxy)
Incorrect repetitions exhibited a higher jerk proxy SD ($0.85 \pm 0.15$) than correct repetitions ($0.75 \pm 0.19$), with a moderate effect ($d = -0.5319$, 95% CI: $[-1.3246, -0.0325]$) [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. The negative $d$ sign indicates that correct repetitions were smoother; the elevated jerk in incorrect executions reflects reduced eccentric motor control and increased trajectory wobble or instability during the descent phase. Consequently, this jerk proxy serves as a robust marker for evaluating the quality of neuromotor regulation during demanding eccentric loading.

---

## 4.3. Cross-Cohort Consistency and Generalisation

Descriptive kinematics from the controlled REHAB24-6 cohort were compared to the in-the-wild Penn Action cohort [CITE: Zhang_Penn_Action_2013], with both producing overlapping, biomechanically plausible ranges for knee joint angles across diverse lighting, clothing, and camera conditions:
*   **Penn Action** ($n = 10$ subjects, single-rep): mean peak flexion $78.84^\circ \pm 30.76^\circ$, mean ROM $99.27^\circ \pm 31.12^\circ$, jerk proxy $1.42 \pm 0.65$ [source: 4_pose_outputs/temporal/squats_biomarkers.csv statistical run].
*   **REHAB24-6** ($n = 98$ reps): mean peak flexion $55.62^\circ \pm 14.31^\circ$, mean ROM $117.32^\circ \pm 18.91^\circ$, jerk proxy $0.78 \pm 0.18$ [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt].

### 4.3.1. Cohort-Level Biomechanical Differences
REHAB24-6 shows systematically deeper peak flexion ($55.62^\circ$ vs. $78.84^\circ$) and larger ROM ($117.32^\circ$ vs. $99.27^\circ$), reflecting laboratory instructions to perform deep squats and deliberately introduce form errors. Penn Action sequences represent unconstrained real-world execution, where squat depth is typically self-selected and more restricted. The elevated Penn Action jerk proxy ($1.42 \pm 0.65$ vs. $0.78 \pm 0.18$) reflects increased tracking noise from compressed in-the-wild video footage rather than poorer neuromuscular control.

### 4.3.2. Methodological Role of Generalisation
This cross-cohort comparison is a **reproducibility finding**: the pipeline generates biologically plausible kinematics across widely differing recording environments and confirms that the extraction pipeline is not artificially tuned to laboratory conditions. Cohort consistency does not, however, establish tracking accuracy. Absolute accuracy is quantified in Chapter 6, where single-camera values are compared directly against optoelectronic and force-plate ground truth [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

---

## 4.4. Discussion and Clinical Screening Guardrails

The kinematic signature identified in the REHAB24-6 cohort — characterized by deeper knee flexion, a faster eccentric descent phase, and an elevated jerk proxy — carries important biomechanical implications for injury risk screening.

### 4.4.1. Clinical Risk Interpretation
The identified signature — deep knee flexion, rapid eccentric descent, and elevated jerk — reflects an eccentric control deficit in which the subject relies on passive osteoligamentous structures rather than active musculature to arrest momentum at the squat bottom. Rapid descent increases patellofemoral joint reaction forces and tibiofemoral shear stress [CITE: Powers_2003]; deep flexion past parallel ($\theta_{\text{included}} < 60^\circ$) under dynamic loading amplifies patellofemoral compressive stress [CITE: Wallace_2002]; and elevated jerk reflects neuromuscular instability and compensatory movement adjustments [CITE: Farrokhi_2008].

### 4.4.2. Screening-not-Prediction Framing
This framework is a **kinematic screening layer** that identifies deviations from a subject's own movement baseline — it does not diagnose clinical pathology or predict statistical injury probability. The framework flags kinematic patterns that are biomechanically associated with elevated risk per published literature; inferring clinical injury outcomes requires longitudinal data with prospective injury endpoints, which lies outside the scope of this study.

---

## 4.5. Limitations

1.  **Small Incorrect Sample Size**: Only $n = 26$ incorrect repetitions limits the statistical power of the bootstrapped CIs, particularly for the moderate-effect biomarkers (descent velocities, jerk proxy).
2.  **Sagittal-Plane Restriction**: Monocular tracking cannot resolve out-of-plane kinematics. Critical injury-associated movements — knee valgus (coronal plane projection) and tibial rotation (transverse plane) — are invisible to a single sagittal camera and cannot be captured in this framework.
3.  **Error Heterogeneity**: The "incorrect" label pooled multiple deviation types (excessive depth, rapid descent, knee-wobble). Separating specific error sub-types requires a larger, multi-class cohort.
4.  **Reproducibility-vs-Accuracy**: Cross-cohort generalisation does not validate tracking accuracy. The single-camera pipeline's systematic overestimation bias at deep flexion ($+10.52^\circ$ timing-clean, $+19.72^\circ$ peak-to-peak) must be applied when evaluating absolute joint angles [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

---

## 4.6. Figures and Provenance

The following publication-ready figures support this chapter; data provenance is detailed in `figures_publication/figure_data_provenance.csv` [source: 14_rehab24_outputs/figures_publication/figure_data_provenance.csv]:

*   **Figure 4.1: Knee Flexion Angle Distributions — Correct vs. Incorrect**
    *   `fig1_correct_vs_incorrect.png` — histograms of peak flexion and ROM for correct ($n=72$) and incorrect ($n=26$) repetitions, illustrating the deep-flexion shift.
*   **Figure 4.2: Forest Plot of Cohen's $d$ Effect Sizes and 95% CIs**
    *   `fig2_effect_sizes.png` — effect sizes for all squat biomarkers; discriminative descent metrics and non-discriminative ascent metrics clearly separated. *(Known label-overprinting bug in background guide-labels; to be resolved in final compilation.)*
*   **Figure 4.3: Cross-Cohort Kinematic Distribution Comparison**
    *   `fig3_cross_cohort_distributions.png` — overlay of Penn Action ($n=10$ subjects) [CITE: Zhang_Penn_Action_2013] and REHAB24-6 ($n=98$ reps) joint angle distributions, demonstrating biomechanical range generalisation.
*   **Figure 4.4: Representative Correct vs. Incorrect Knee Flexion Trajectories**
    *   `fig4_representative_trajectories.png` — time-series overlay of correct (Subject 1, rep 2, $121$ frames) and incorrect (Subject 1, rep 17, $91$ frames) squat repetitions, illustrating rapid eccentric descent and excessive depth in the incorrect execution.
