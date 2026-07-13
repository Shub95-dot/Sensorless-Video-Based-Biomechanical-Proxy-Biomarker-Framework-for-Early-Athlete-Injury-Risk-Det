# Chapter 5: Lunge Kinematic Screening

This chapter presents the results of the markerless kinematic screening framework applied to the lunge exercise. We evaluate the framework's capacity to extract biomechanically plausible joint angles and discriminate between correct and incorrect movement execution during a unilateral loading task. First, we outline the cohort characteristics and pose-tracking failure modes, documenting the biomechanical mechanisms of self-occlusion. Second, we present the headline statistical findings, focusing on the biomarkers that successfully discriminate lunge form. Third, we establish the cross-exercise kinematic divergence by comparing lunge ascent dynamics directly to the squat results drafted in Chapter 4. Finally, we discuss the clinical interpretation of these kinematic patterns and outline the chapter's limitations.

---

## 5.1. Cohort and Methodological Setup

Lunges were analyzed using the REHAB24-6 physical therapy dataset. The filtering and pose-estimation pipeline was structured to assess unilateral sagittal loading under orthogonal camera tracking:

1.  **Assembled Cohort**: Segmented and assembled from the REHAB24-6 master database based on the presence of the lunge exercise (`exercise_id == 5`), front-facing orthogonal camera placement (`cam17_orientation == 'front'`), and error-free ground-truth motion capture reference (`mocap_erroneous == 0`) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. This yielded an initial cohort of **$88$ lunge repetitions** across **$8$ subjects** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
2.  **Usable Analytical Cohort**: After quality filtering and phase-identification validation, a final usable cohort of **$61$ repetitions** was established, consisting of **$25$ correct repetitions** and **$36$ incorrect repetitions** across **$7$ subjects** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].

### 5.1.1. Pose-Pipeline Failure Modes and Exclusions
Unlike the bilateral squat exercise, which demonstrated a $100\%$ tracking completion rate in the REHAB24-6 manifest [source: 14_rehab24_outputs/metadata/phase5a_integration_summary.txt], the lunge exercise resulted in a high rate of tracking failures. A total of **$27$ repetitions ($30.68\%$ of the assembled data)** failed the phase-identification validation gate due to tracking loss exceeding $30\%$ of the repetition duration [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. These failures were heavily concentrated in two specific subjects:
*   **Subject 8 (`PM_112`)**: Had $12$ of $12$ repetitions fail the validation gate, resulting in a **$100.0\%$ failure rate** and the subject being dropped entirely from the processed cohort [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   **Subject 5 (`PM_042`)**: Had $12$ of $13$ repetitions fail, resulting in a **$92.3\%$ failure rate** and leaving only $1$ successfully processed repetition [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. This single repetition was included in the pooled cohort statistics but effectively excluded this subject from the within-subject shift analysis.

The biomechanical mechanism driving these failures is **contralateral leg self-occlusion**. In bilateral squats, the symmetry of the movement allows the tracking pipeline to implement a left-to-right contralateral fallback (if one knee is occluded, the tracker can estimate depth from the visible limb) [source: 22_dissertation_writing/results_squat_v1.md]. However, the lunge is fundamentally asymmetric. The pipeline must monitor the loaded front leg (designated by the `exercise_subtype` attribute as either `'front leg left'` or `'front leg right'`) [source: 15_rehab24_lunge_outputs/metadata/rehab24_lunge_sagittal_manifest.csv]. When the loaded front leg is positioned as the far leg relative to the sagittal camera sensor, it is completely occluded by the trailing limb or the subject's torso during deep flexion. Because no contralateral fallback is permissible for unilateral screening, this occlusion leads to a catastrophic loss of tracking.

### 5.1.2. Coordinate Convention and Statistics
Consistent with the squat chapter (Chapter 4) [source: 22_dissertation_writing/results_squat_v1.md], lunges were evaluated using the **included-angle convention**:
*   A value of $\approx 180^\circ$ represents full standing extension.
*   Smaller joint angles represent deeper flexion bends (e.g., $90^\circ$ represents a parallel lunge, and $60^\circ$ represents a deep lunge).

To address the hierarchical structure of the data (nested repetitions within subjects), we replicated the subject-clustered bootstrapping statistical procedure developed for the squat pipeline. Resampling was conducted at the subject level with replacement over $5,000$ iterations to compute $95\%$ bootstrap confidence intervals (CIs). The Cohen's $d$ effect sizes were calculated using the usable cohort's pooled standard deviation.

---

## 5.2. Headline Screening Findings (Form Discrimination)

Statistical analysis of correct ($n = 25$) and incorrect ($n = 36$) lunge repetitions in the REHAB24-6 cohort demonstrated that incorrect form was characterized by **excessive knee flexion depth (deeper bend), a faster descent phase, an elevated jerk profile, and a rapid concentric ascent phase** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Table 5.1 summarizes the group means, standard deviations, and Cohen's $d$ effect sizes with bootstrapped 95% confidence intervals.

### Table 5.1: Correct vs. Incorrect Lunge Kinematic Comparison ($n = 61$ reps)

| Biomarker | Correct Mean ($n=25$) | Incorrect Mean ($n=36$) | Cohen's $d$ Effect Size | 95% Bootstrap Confidence Interval (CI) | Form Discrimination Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Peak Flexion ($^\circ$)** | $89.66^\circ \pm 8.33^\circ$ | $68.03^\circ \pm 15.11^\circ$ | $+1.6904$ | $[0.8317, 3.4525]$ | **Highly Discriminative** (deeper included angle in incorrect) [source: phase5c_effect_sizes_ci.csv] |
| **ROM ($^\circ$)** | $59.02^\circ \pm 20.94^\circ$ | $90.30^\circ \pm 27.00^\circ$ | $-1.2653$ | $[-2.8682, -0.5852]$ | **Highly Discriminative** (larger ROM/excursion in incorrect) [source: phase5c_effect_sizes_ci.csv] |
| **Peak Descent Velocity ($^\circ$/fr)** | $-2.87^\circ \pm 0.80^\circ$ | $-5.31^\circ \pm 2.68^\circ$ | $+1.1453$ | $[0.7512, 2.0354]$ | **Highly Discriminative** (faster descent in incorrect) [source: phase5c_effect_sizes_ci.csv] |
| **Mean Descent Velocity ($^\circ$/fr)** | $-1.01^\circ \pm 0.28^\circ$ | $-1.75^\circ \pm 0.80^\circ$ | $+1.1563$ | $[0.2863, 2.6316]$ | **Highly Discriminative** (faster mean descent in incorrect) [source: phase5c_effect_sizes_ci.csv] |
| **Jerk Proxy Standard Deviation** | $0.46 \pm 0.11$ | $1.07 \pm 0.78$ | $-1.0070$ | $[-1.3663, -0.6526]$ | **Highly Discriminative** (elevated jerk/reduced smoothness) [source: phase5c_effect_sizes_ci.csv] |
| **Peak Ascent Velocity ($^\circ$/fr)** | $3.85^\circ \pm 1.57^\circ$ | $6.95^\circ \pm 3.93^\circ$ | $-0.9721$ | $[-1.6403, -0.6554]$ | **Discriminative** (faster ascent in incorrect) [source: phase5c_effect_sizes_ci.csv] |
| **Mean Ascent Velocity ($^\circ$/fr)** | $1.26^\circ \pm 0.47^\circ$ | $1.87^\circ \pm 0.91^\circ$ | $-0.7962$ | $[-2.0731, -0.0807]$ | **Discriminative (Marginal)** (CI upper limit near zero) [source: phase5c_effect_sizes_ci.csv] |
| **Peak Extension ($^\circ$)** | $148.68^\circ \pm 18.09^\circ$ | $158.33^\circ \pm 20.25^\circ$ | $-0.4972$ | $[-1.7633, 0.1533]$ | **Non-Discriminative** (CI crosses zero) [source: phase5c_effect_sizes_ci.csv] |
| **Tempo Ratio** | $0.88 \pm 0.28$ | $1.04 \pm 0.47$ | $-0.3796$ | $[-0.7240, 0.1386]$ | **Non-Discriminative (Precise Null)** [source: phase5c_effect_sizes_ci.csv] |

### 5.2.1. Flexion Depth and Joint Excursion
Incorrect repetitions were characterized by a highly significant increase in lunge depth, as demonstrated by the peak flexion included angle:
*   Correct lunges achieved a mean peak included angle of **$89.66^\circ \pm 8.33^\circ$**, representing a standard parallel lunge [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   Incorrect lunges reached a mean peak included angle of **$68.03^\circ \pm 15.11^\circ$**, representing a deeper lunge [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   This difference represents a large effect size of **$d = 1.6904$** (95% CI: $[0.8317, 3.4525]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

Correspondingly, the joint range of motion (ROM) was significantly larger in incorrect repetitions:
*   Correct lunges had a mean ROM of **$59.02^\circ \pm 20.94^\circ$** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   Incorrect lunges had a mean ROM of **$90.30^\circ \pm 27.00^\circ$** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   This yielded a large negative effect size of **$d = -1.2653$** (95% CI: $[-2.8682, -0.5852]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

The Cohen's $d$ is negative because the correct group mean is smaller than the incorrect group mean ($M_{\text{correct}} < M_{\text{incorrect}}$). This result is physically and mathematically consistent: because incorrect lunges achieved a deeper bottom position (smaller peak included angle), the total joint excursion from standing to the bottom was substantially larger. This matches the squat ROM effect size direction ($d = -1.4484$) and aligns with the screening layer's `EXCESS_ROM` rule [source: 22_dissertation_writing/results_squat_v1.md].

### 5.2.2. Trajectory Case-Study Verification
This cohort-level deeper flexion finding is clearly illustrated by the representative trajectory comparison of Subject 7 (`PM_125`) correct repetition 14 vs. incorrect repetition 16 [source: 15_rehab24_lunge_outputs/figures_publication/figure_data_provenance.csv]:
*   **Correct Repetition 14**: Achieved a peak flexion included angle of **$99.87^\circ$** and a ROM of **$51.31^\circ$** over a $110$-frame duration [source: 15_rehab24_lunge_outputs/biomarkers_per_rep/rehab24_lunge_per_rep_biomarkers.csv / figures_publication/figure_data_provenance.csv].
*   **Incorrect Repetition 16**: Dropped to a peak flexion included angle of **$57.04^\circ$** and a ROM of **$102.88^\circ$** over a $111$-frame duration [source: 15_rehab24_lunge_outputs/biomarkers_per_rep/rehab24_lunge_per_rep_biomarkers.csv / figures_publication/figure_data_provenance.csv].

This single-subject trajectory comparison confirms that the cohort-level shift is not driven by statistical outliers but represents a consistent, physical change in joint kinematics. Subject-specific shift analysis verified that all $5$ subjects contributing both correct and incorrect processed reps (Subjects 2, 4, 6, 7, and 9) displayed negative peak flexion shifts (ranging from $-24.14^\circ$ to $-29.35^\circ$) and positive ROM shifts (ranging from $+24.44^\circ$ to $+52.87^\circ$) during incorrect repetitions [source: 15_rehab24_lunge_outputs/metadata/phase5c_per_subject_shifts.csv].

### 5.2.3. Descent Velocity and Jerk
Similar to the squat cohort, velocity and movement quality biomarkers successfully discriminated lunge execution form:
*   **Peak Descent Velocity**: Correct lunges had a peak descent rate of **$-2.87^\circ/\text{frame} \pm 0.80^\circ/\text{frame}$**, compared to **$-5.31^\circ/\text{frame} \pm 2.68^\circ/\text{frame}$** for incorrect lunges ($d = 1.1453$, 95% CI: $[0.7512, 2.0354]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv].
*   **Mean Descent Velocity**: Correct lunges averaged **$-1.01^\circ/\text{frame} \pm 0.28^\circ/\text{frame}$**, compared to **$-1.75^\circ/\text{frame} \pm 0.80^\circ/\text{frame}$** for incorrect lunges ($d = 1.1563$, 95% CI: $[0.2863, 2.6316]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv].
*   **Movement Jerk**: Correct lunges exhibited a jerk proxy of **$0.46 \pm 0.11$**, compared to **$1.07 \pm 0.78$** for incorrect lunges ($d = -1.0070$, 95% CI: $[-1.3663, -0.6526]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv].

Velocity values are negative because the included angle decreases during descent. The positive Cohen's $d$ values reflect that correct lunges had an algebraically larger (slower) descent velocity than incorrect lunges (which were more negative, representing a faster physical descent speed). The negative Cohen's $d$ for jerk proxy indicates that correct reps were smoother than incorrect reps, which displayed elevated jerk values.

---

## 5.3. Cross-Exercise Divergence (The Distinctive Ascent Finding)

A major finding of this multi-exercise evaluation is the behavior of the concentric ascent phase, which highlights a distinct biomechanical divergence between squats and lunges.

### 5.3.1. Ascent Velocity Discrimination in Lunges
Unlike squats, where ascent velocities did not reliably discriminate between form groups [source: 22_dissertation_writing/results_squat_v1.md], both ascent velocity biomarkers successfully differentiated lunge execution quality:
*   **Peak Ascent Velocity**: Correct lunges had a peak ascent rate of **$3.85^\circ/\text{frame} \pm 1.57^\circ/\text{frame}$**, while incorrect lunges reached **$6.95^\circ/\text{frame} \pm 3.93^\circ/\text{frame}$** ($d = -0.9721$, 95% CI: $[-1.6403, -0.6554]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv].
*   **Mean Ascent Velocity**: Correct lunges averaged **$1.26^\circ/\text{frame} \pm 0.47^\circ/\text{frame}$**, while incorrect lunges averaged **$1.87^\circ/\text{frame} \pm 0.91^\circ/\text{frame}$** ($d = -0.7962$, 95% CI: $[-2.0731, -0.0807]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv].

The Cohen's $d$ is negative because correct lunges exhibited a smaller (slower) ascent velocity than incorrect lunges ($M_{\text{correct}} < M_{\text{incorrect}}$). Because the bootstrap confidence intervals for both peak ascent velocity ($[-1.6403, -0.6554]$) and mean ascent velocity ($[-2.0731, -0.0807]$) exclude zero, these findings represent reliable indicators of form quality. The mean ascent velocity is classified as reliable but marginal due to the upper bound of its interval approaching zero ($ -0.0807 $) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

### 5.3.2. Explicit Contrast with Squat Kinematics
This finding contrasts directly with the squat results presented in Chapter 4 [source: 22_dissertation_writing/results_squat_v1.md]:
*   In the squat cohort, peak ascent velocity ($d = -0.5049$, 95% CI: $[-1.4838, +0.0848]$) and mean ascent velocity ($d = -0.4996$, 95% CI: $[-1.7017, +0.1301]$) both had confidence intervals that crossed zero, confirming they were non-discriminative [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv].
*   In the lunge cohort, both peak and mean ascent velocities were significantly faster for incorrect repetitions [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

Biomechanically, this divergence is plausible. The squat is a bilateral exercise where the body's mass is supported symmetrically by both limbs. In contrast, the lunge is an asymmetric, unilateral propulsion task. In an incorrect lunge—which is characterized by an excessively deep bottom position—the subject is in a biomechanically disadvantaged posture. Returning to a standing position from a deep, unilateral stance requires a forceful concentric push-off from the front leg. This leads to a rapid, less-controlled spring-back step (propulsion phase) to recover standing balance. This rapid propulsion represents an additional biomechanical indicator of form deviation that is completely absent in bilateral squats.

### 5.3.3. Statistical Nulls and Rigor Guardrails
To maintain statistical rigor, only CI-reliable effects are presented as discriminative. The biomarkers `peak_extension_deg` ($d = -0.4972$, 95% CI: $[-1.7633, 0.1533]$) and the `tempo_ratio` ($d = -0.3796$, 95% CI: $[-0.7240, 0.1386]$) both have confidence intervals that cross zero, indicating they do not reliably differentiate form quality [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv]. The `tempo_ratio` represents a precise null, indicating that the relative timing of the descent and ascent phases remains constant even when the absolute speeds change.

---

## 5.4. Discussion and Clinical Screening Guardrails

The kinematic signature identified in the lunge cohort—excessive depth, a rapid descent phase, an elevated jerk proxy, and a rapid, propulsive ascent—provides a comprehensive profile of movement deviation.

### 5.4.1. Clinical Interpretation of Depth and Ascent Faults
Clinically, lunge depth is a two-sided quality. While insufficient depth limits quad activation, excessive depth past parallel increases patellofemoral compressive force and tibiofemoral shear stress. Because the incorrect repetitions in this cohort shifted consistently toward greater depth, this finding reflects the specific instructed errors performed by the subjects (e.g., placing the front knee too far forward, dropping past comfort). 

Furthermore, the rapid concentric ascent velocity represents a dynamic compensation strategy. When joint stability is compromised at deep flexion, subjects rely on a rapid, spring-back propulsion to recover. This rapid loading and unloading pattern is associated with increased joint shear stress and patellofemoral irritation [CITE: Powers_2002] [CITE: FEA_2023].

### 5.4.2. Screening-not-Prediction Framing
As established in Chapter 4, this framework is a **kinematic screening layer**, designed to identify deviations from a baseline movement template, rather than an injury prediction model. The framework identifies kinematic patterns that are biomechanically associated with elevated risk in scientific literature; it does not claim to diagnose clinical pathology or predict the statistical probability of injury occurrence.

---

## 5.5. Limitations

Several limitations of this lunge evaluation must be noted:
1.  **Occlusion Exclusions**: The monocular sagittal view resulted in the exclusion of Subject 8 (12/12 reps failed) and Subject 5 (12/13 reps failed) due to contralateral self-occlusion [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. These exclusions represent a systematic limitation of monocular tracking during asymmetric movements, feeding the monocular failure-mode taxonomy.
2.  **Small Cohort Size**: The usable analytical cohort contained only $n = 61$ repetitions across $7$ subjects [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. The reported effect sizes and confidence intervals represent the characteristics of this specific cohort and should not be used to make population-level generalizations.
3.  **No Cross-Cohort Validation**: Unlike the squat chapter, which compared the lab-based cohort to an in-the-wild YouTube cohort, the lunge evaluation was restricted to the REHAB24-6 dataset. No YouTube-equivalent check was performed for lunges, representing an asymmetry in validation depth.
4.  **Sagittal-Plane Restriction**: Monocular sagittal-view tracking is blind to frontal-plane errors, such as knee valgus or pelvic drop, which are heavily associated with ACL injury risk.

---

## 5.6. Figures and Provenance

The findings presented in this chapter are supported by the following publication-ready figures, with data provenance detailed in `figures_publication/figure_data_provenance.csv` [source: 15_rehab24_lunge_outputs/figures_publication/figure_data_provenance.csv]:

*   **Figure 5.1: Knee Flexion Angle Distributions for Correct vs. Incorrect Lunge Repetitions**
    *   *Source file*: `15_rehab24_lunge_outputs/figures_publication/fig_L1_correct_vs_incorrect.png`
    *   *Description*: Histograms comparing the distribution of peak flexion and range of motion for correct ($n=25$) and incorrect ($n=36$) repetitions, illustrating the deep-flexion shift in the incorrect group.
*   **Figure 5.2: Forest Plot of Cohen's $d$ Effect Sizes and 95% Confidence Intervals for Lunge Biomarkers**
    *   *Source file*: `15_rehab24_lunge_outputs/figures_publication/fig_L2_effect_sizes.png`
    *   *Description*: Cohen's $d$ effect size plot showing significant effects for peak flexion, ROM, descent velocities, jerk proxy, and ascent velocities.
    *   *Note*: A known label-overprinting bug exists in the background "small/medium/large" guide-labels in this figure, which is shared with the squat plotting code.
*   **Figure 5.3: Cross-Exercise Ascent Velocity Comparison**
    *   *Source file*: `15_rehab24_lunge_outputs/figures_publication/fig_L3_cross_exercise_distributions.png`
    *   *Description*: Side-by-side forest plot comparison highlighting the lunge-squat ascent-velocity divergence, where lunge ascent velocities discriminate form and squat ascent velocities cross zero.
*   **Figure 5.4: Representative Correct vs. Incorrect Knee Flexion Trajectories for Lunges**
    *   *Source file*: `15_rehab24_lunge_outputs/figures_publication/fig_L4_representative_trajectories.png`
    *   *Description*: Time-series overlay of representative correct (Subject 7, rep 14, $110$ frames) and incorrect (Subject 7, rep 16, $111$ frames) lunge repetitions, illustrating the excessive flexion depth and rapid concentric ascent of incorrect execution.
