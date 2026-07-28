# Chapter 5: Lunge Kinematic Screening

This chapter presents the markerless kinematic screening results for the lunge exercise, evaluating form discrimination under unilateral loading, tracking failure modes arising from asymmetric self-occlusion, and the cross-exercise kinematic divergence between lunge and squat ascent dynamics. Statistical methods follow Chapter 2.

---

## 5.1. Cohort and Methodological Setup

Lunges were analyzed using the REHAB24-6 physical therapy dataset, filtering for the lunge exercise (`exercise_id == 5`), front-facing orthogonal camera placement (`cam17_orientation == 'front'`), and error-free motion capture reference (`mocap_erroneous == 0`) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]:

1.  **Assembled Cohort**: **$88$ lunge repetitions** across **$8$ subjects** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
2.  **Usable Analytical Cohort**: After quality filtering and phase-identification validation, **$61$ repetitions** ($25$ correct, $36$ incorrect) across **$7$ subjects** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].

### 5.1.1. Pose-Pipeline Failure Modes and Exclusions
Unlike the squat exercise (100% tracking completion rate in REHAB24-6), the lunge resulted in **$27$ repetitions ($30.68\%$)** failing the phase-identification validation gate due to tracking loss exceeding 30% of repetition duration [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Failures were concentrated in two subjects:
*   **Subject 8 (`PM_112`)**: $12/12$ repetitions failed ($100.0\%$) — subject dropped entirely [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].
*   **Subject 5 (`PM_042`)**: $12/13$ repetitions failed ($92.3\%$) — one usable repetition retained [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt].

The mechanism is **contralateral leg self-occlusion**. Because the lunge is an asymmetric exercise, the loaded front leg (`exercise_subtype`: `'front leg left'` or `'front leg right'`) [source: 15_rehab24_lunge_outputs/metadata/rehab24_lunge_sagittal_manifest.csv] is frequently occluded by the trailing limb during deep flexion when positioned as the far leg relative to the camera. Unlike the squat, no contralateral fallback is permissible for unilateral screening, so this occlusion causes catastrophic tracking loss.

### 5.1.2. Coordinate Convention
Consistent with Chapter 4 [source: 22_dissertation_writing/results_squat_v1.md], lunges use the **included-angle convention** ($\approx 180^\circ$ = standing extension; smaller values = deeper flexion). Subject-clustered bootstrapping (5,000 iterations, subject-level resampling) produces 95% bootstrap CIs following the procedure described in Chapter 2.

---

## 5.2. Headline Screening Findings (Form Discrimination)

Incorrect lunge form was characterized by **excessive knee flexion depth, a faster descent phase, an elevated jerk profile, and a rapid concentric ascent** [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]. Table 5.1 summarizes the results.

### Table 5.1: Correct vs. Incorrect Lunge Kinematic Comparison ($n = 61$ reps)

| Biomarker | Correct Mean ($n=25$) | Incorrect Mean ($n=36$) | Cohen's $d$ | 95% CI | Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Peak Flexion ($^\circ$)** | $89.66^\circ \pm 8.33^\circ$ | $68.03^\circ \pm 15.11^\circ$ | $+1.6904$ | $[0.8317, 3.4525]$ | **Highly Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **ROM ($^\circ$)** | $59.02^\circ \pm 20.94^\circ$ | $90.30^\circ \pm 27.00^\circ$ | $-1.2653$ | $[-2.8682, -0.5852]$ | **Highly Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **Peak Descent Velocity ($^\circ$/fr)** | $-2.87^\circ \pm 0.80^\circ$ | $-5.31^\circ \pm 2.68^\circ$ | $+1.1453$ | $[0.7512, 2.0354]$ | **Highly Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **Mean Descent Velocity ($^\circ$/fr)** | $-1.01^\circ \pm 0.28^\circ$ | $-1.75^\circ \pm 0.80^\circ$ | $+1.1563$ | $[0.2863, 2.6316]$ | **Highly Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **Jerk Proxy SD** | $0.46 \pm 0.11$ | $1.07 \pm 0.78$ | $-1.0070$ | $[-1.3663, -0.6526]$ | **Highly Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **Peak Ascent Velocity ($^\circ$/fr)** | $3.85^\circ \pm 1.57^\circ$ | $6.95^\circ \pm 3.93^\circ$ | $-0.9721$ | $[-1.6403, -0.6554]$ | **Discriminative** [source: phase5c_effect_sizes_ci.csv] |
| **Mean Ascent Velocity ($^\circ$/fr)** | $1.26^\circ \pm 0.47^\circ$ | $1.87^\circ \pm 0.91^\circ$ | $-0.7962$ | $[-2.0731, -0.0807]$ | **Discriminative (Marginal)** [source: phase5c_effect_sizes_ci.csv] |
| **Peak Extension ($^\circ$)** | $148.68^\circ \pm 18.09^\circ$ | $158.33^\circ \pm 20.25^\circ$ | $-0.4972$ | $[-1.7633, 0.1533]$ | **Non-Discriminative** (CI crosses zero) [source: phase5c_effect_sizes_ci.csv] |
| **Tempo Ratio** | $0.88 \pm 0.28$ | $1.04 \pm 0.47$ | $-0.3796$ | $[-0.7240, 0.1386]$ | **Non-Discriminative (Precise Null)** [source: phase5c_effect_sizes_ci.csv] |

### 5.2.1. Flexion Depth and Joint Excursion
Incorrect lunges reached a mean peak included angle of $\mathbf{68.03^\circ \pm 15.11^\circ}$ versus $\mathbf{89.66^\circ \pm 8.33^\circ}$ for correct repetitions — a large effect ($d = 1.6904$, 95% CI: $[0.8317, 3.4525]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv]. The deeper descent directly enlarged joint excursion: incorrect ROM was $\mathbf{90.30^\circ \pm 27.00^\circ}$ versus $\mathbf{59.02^\circ \pm 20.94^\circ}$ for correct repetitions ($d = -1.2653$, 95% CI: $[-2.8682, -0.5852]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv]. The negative $d$ is directionally consistent with the included-angle convention and parallels the squat ROM finding ($d = -1.4484$), aligning with the `EXCESS_ROM` screening rule [source: 22_dissertation_writing/results_squat_v1.md].

### 5.2.2. Trajectory Case-Study Verification
The cohort-level depth shift is confirmed by Subject 7 (`PM_125`) comparing correct repetition 14 (peak flexion $99.87^\circ$, ROM $51.31^\circ$, $110$ frames) versus incorrect repetition 16 (peak flexion $57.04^\circ$, ROM $102.88^\circ$, $111$ frames) [source: 15_rehab24_lunge_outputs/biomarkers_per_rep/rehab24_lunge_per_rep_biomarkers.csv / figures_publication/figure_data_provenance.csv]. This single-subject trajectory comparison confirms the cohort-level shift is not driven by statistical outliers. All 5 subjects contributing both correct and incorrect repetitions (Subjects 2, 4, 6, 7, 9) displayed consistent negative peak flexion shifts ($-24.14^\circ$ to $-29.35^\circ$) and positive ROM shifts ($+24.44^\circ$ to $+52.87^\circ$) during incorrect lunges [source: 15_rehab24_lunge_outputs/metadata/phase5c_per_subject_shifts.csv].

### 5.2.3. Descent Velocity and Jerk
All three descent-phase biomarkers were highly discriminative. Peak descent velocity: correct $-2.87^\circ/\text{frame} \pm 0.80^\circ/\text{frame}$ vs. incorrect $-5.31^\circ/\text{frame} \pm 2.68^\circ/\text{frame}$ ($d = 1.1453$, 95% CI: $[0.7512, 2.0354]$). Mean descent velocity: correct $-1.01^\circ/\text{frame} \pm 0.28^\circ/\text{frame}$ vs. incorrect $-1.75^\circ/\text{frame} \pm 0.80^\circ/\text{frame}$ ($d = 1.1563$, 95% CI: $[0.2863, 2.6316]$). Jerk proxy: correct $0.46 \pm 0.11$ vs. incorrect $1.07 \pm 0.78$ ($d = -1.0070$, 95% CI: $[-1.3663, -0.6526]$) [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt / phase5c_effect_sizes_ci.csv]. Positive descent $d$ values reflect physically slower correct-group descent; the negative jerk $d$ indicates smoother correct repetitions.

---

## 5.3. Cross-Exercise Divergence (The Distinctive Ascent Finding)

A major finding of this multi-exercise evaluation is the behavior of the concentric ascent phase, which reveals a distinct biomechanical divergence between squats and lunges.

### 5.3.1. Ascent Velocity Discrimination in Lunges
Unlike squats — where both ascent velocity metrics had confidence intervals crossing zero and were non-discriminative [source: 22_dissertation_writing/results_squat_v1.md] — **both ascent velocity biomarkers discriminated lunge execution quality** with confidence intervals that exclude zero:
*   **Peak Ascent Velocity**: correct $3.85^\circ/\text{frame} \pm 1.57^\circ/\text{frame}$ vs. incorrect $6.95^\circ/\text{frame} \pm 3.93^\circ/\text{frame}$ ($d = -0.9721$, 95% CI: $[-1.6403, -0.6554]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].
*   **Mean Ascent Velocity**: correct $1.26^\circ/\text{frame} \pm 0.47^\circ/\text{frame}$ vs. incorrect $1.87^\circ/\text{frame} \pm 0.91^\circ/\text{frame}$ ($d = -0.7962$, 95% CI: $[-2.0731, -0.0807]$) [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv].

The negative Cohen's $d$ values reflect that correct lunges exhibited slower (smaller) ascent velocities than incorrect lunges. Mean ascent velocity is classified as **Discriminative (Marginal)** because its CI upper bound approaches zero ($-0.0807$), but the interval excludes zero, confirming reliability.

### 5.3.2. Explicit Contrast with Squat Kinematics and Biomechanical Explanation
In the squat cohort, peak ascent velocity ($d = -0.5049$, 95% CI: $[-1.4838, +0.0848]$) and mean ascent velocity ($d = -0.4996$, 95% CI: $[-1.7017, +0.1301]$) both crossed zero — non-discriminative [source: 14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv]. In the lunge cohort, both were discriminative. This divergence has a clear biomechanical basis: the squat is bilateral, with body mass supported symmetrically, allowing a controlled concentric ascent. The lunge is an asymmetric unilateral propulsion task — from an excessively deep bottom position, the subject must generate a forceful concentric push-off from the front leg alone to recover standing balance. This rapid spring-back propulsion is a direct kinematic consequence of the deeper, more biomechanically disadvantaged bottom position, and represents an additional form-deviation indicator absent in bilateral squats.

### 5.3.3. Statistical Nulls and Rigor Guardrails
Two biomarkers were non-discriminative: `peak_extension_deg` ($d = -0.4972$, 95% CI: $[-1.7633, 0.1533]$) and `tempo_ratio` ($d = -0.3796$, 95% CI: $[-0.7240, 0.1386]$), both crossing zero [source: 15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv]. The `tempo_ratio` represents a precise null: relative descent-to-ascent timing remains constant even as absolute speeds diverge.

---

## 5.4. Discussion and Clinical Screening Guardrails

### 5.4.1. Clinical Interpretation of Depth and Ascent Faults
Excessive lunge depth increases patellofemoral compressive force and tibiofemoral shear stress beyond the parallel position. The rapid concentric ascent observed in incorrect repetitions represents a dynamic compensation: when joint stability is compromised at deep flexion, subjects rely on a forceful spring-back to recover standing balance. This rapid loading-and-unloading pattern amplifies joint shear stress and is associated with patellofemoral irritation [CITE: Powers_2003].

### 5.4.2. Screening-not-Prediction Framing
As established in Chapter 4, this framework is a **kinematic screening layer** that identifies deviations from a subject's baseline movement template. It does not diagnose clinical pathology or predict injury probability; it flags kinematic patterns biomechanically associated with elevated risk per published literature.

---

## 5.5. Limitations

1.  **Occlusion Exclusions**: Subject 8 ($12/12$ reps failed) and Subject 5 ($12/13$ reps failed) were excluded due to contralateral self-occlusion [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt], representing a systematic monocular tracking limitation for asymmetric movements.
2.  **Small Cohort Size**: Only $n = 61$ repetitions across $7$ subjects [source: 15_rehab24_lunge_outputs/metadata/phase5b_integration_summary.txt]; reported effect sizes should not be generalized to broader populations.
3.  **No Cross-Cohort Validation**: Unlike the squat chapter, which compared the lab-based cohort to an in-the-wild Penn Action cohort [CITE: Zhang_Penn_Action_2013], the lunge evaluation was restricted to the REHAB24-6 dataset. No Penn Action-equivalent check was performed for lunges, representing an asymmetry in validation depth.
4.  **Sagittal-Plane Restriction**: Monocular tracking is blind to frontal-plane errors — knee valgus and pelvic drop — which are heavily associated with ACL injury risk.

---

## 5.6. Figures and Provenance

Publication-ready figures; data provenance in `figures_publication/figure_data_provenance.csv` [source: 15_rehab24_lunge_outputs/figures_publication/figure_data_provenance.csv]:

*   **Figure 5.1: Knee Flexion Distributions — Correct vs. Incorrect Lunges**
    *   `fig_L1_correct_vs_incorrect.png` — histograms of peak flexion and ROM for correct ($n=25$) and incorrect ($n=36$) repetitions, illustrating the deep-flexion shift.
*   **Figure 5.2: Forest Plot of Cohen's $d$ Effect Sizes and 95% CIs**
    *   `fig_L2_effect_sizes.png` — all lunge biomarker effect sizes; descent and ascent metrics both discriminative, non-discriminative nulls visible. *(Shared label-overprinting bug with squat plotting code; to be resolved in final compilation.)*
*   **Figure 5.3: Cross-Exercise Ascent Velocity Comparison**
    *   `fig_L3_cross_exercise_distributions.png` — side-by-side forest plot of lunge vs. squat ascent-velocity effects, highlighting the exercise divergence where lunge CIs exclude zero and squat CIs cross zero.
*   **Figure 5.4: Representative Correct vs. Incorrect Lunge Trajectories**
    *   `fig_L4_representative_trajectories.png` — time-series overlay of correct (Subject 7, rep 14, $110$ frames) and incorrect (Subject 7, rep 16, $111$ frames) lunge repetitions, illustrating excessive depth and rapid concentric ascent in the incorrect execution.
