# Dissertation Writeup Plan

This document serves as the detailed assembly scaffold for the final writing of the dissertation. It contains the structure, key analytical notes, frozen data values with source citations, and critical implementation warnings/reconciliations for each chapter.

---

## CHAPTER: Drop-Jump Validation (validation backbone)
**STRUCTURE:** purpose → headline finding → per-biomarker agreement → robustness → timing/projection diagnostic → limitations → discussion

### § Purpose
*   **Role:** The validation backbone of the entire thesis. It qualifies every monocular knee-flexion biomarker used in subsequent chapters.
*   **Key Argument:** Reproducibility $\neq$ accuracy. The fact that monocular posture tracking yields consistent cross-cohort patterns (reproducibility) does not guarantee physical accuracy. Optoelectronic and force-plate ground truth is required to quantify measurement error bounds.
*   **Task Selection:** The drop-jump represents a deliberately selected "worst-case" validation task (extremely high joint angular velocity, dynamic impact loading, and deep flexion). By establishing errors under these conditions, we define the upper-bound uncertainty limits for slower, controlled sagittal movements (squats, lunges).

### § Headline Finding
*   **MUST FRAME:** The measurement error behaves as a **constant deep-flexion overestimation bias**, not a proportional scale error that grows with flexion depth.
*   **Timing-Clean Peak Bias:** Overestimation bias of $+10.52^\circ$ at the peak landing absorption frame (LoA: $[-5.54^\circ, +26.58^\circ]$, $n=96$ peak flexion values across 48 trials) [source: phase6_final_report.md / phase6_agreement_final.csv].
*   **Error-vs-Depth Test:** Correlation between flexion depth and measurement error in the $70^\circ\text{--}120^\circ$ landing band is not statistically significant:
    *   Pearson $r = -0.16$ ($p = 0.13$) [source: phase6_final_report.md]
    *   Spearman $\rho = -0.19$ ($p = 0.06$) [source: phase6_final_report.md]
*   **Contact Flexion Bias:** Underestimation bias of $-6.69^\circ$ at initial contact (shallow flexion) [source: phase6_agreement_final.csv].
*   **Interpretation:** The monocular pipeline is highly usable for relative/within-subject changes, but absolute kinematic comparison requires subtraction of the constant overestimation offset at deep flexion. The error is a characterized physical property of single-camera projection geometry, not a random pipeline defect.

### § Per-Biomarker Agreement (Bland-Altman)
*   **Contact Flexion (Landing Contact):** Mean bias of $-6.69^\circ$ (95% LoA: $[-26.77^\circ, +13.39^\circ]$, Pearson $r = 0.3209$) [source: phase6_agreement_final.csv]. Accurate but moderate tracking at low flexion angles.
*   **Peak Flexion (Landing Peak):** Mean bias of $+19.72^\circ$ (95% LoA: $[+7.73^\circ, +31.71^\circ]$, Pearson $r = 0.8238$) [source: phase6_agreement_final.csv]. Biased-systematic but exhibits strong linear tracking.
*   **Range of Motion (ROM):** Mean bias of $+26.41^\circ$ (95% LoA: $[+2.34^\circ, +50.48^\circ]$, Pearson $r = 0.4020$) [source: phase6_agreement_final.csv]. Biased high due to the coupling of contact underestimation and peak overestimation.
*   **Loading Rate (Mean Landing Velocity):** Mean bias of $+13.30^\circ/\text{s}$ (95% LoA: $[-115.92^\circ/\text{s}, +142.51^\circ/\text{s}]$, Pearson $r = 0.6076$) [source: phase6_agreement_final.csv]. Extremely high-variance; should not be used as an absolute kinematic metric.
*   **Asymmetry (Inter-limb):** Demoted to an OpenSim inverse kinematics (IK)-only reference (mean $2.07^\circ$, SD $9.39^\circ$) due to contralateral occlusion [source: phase6_final_report.md].
*   **MUST-INCLUDE RECONCILIATION:** Explain the difference between the **$+10.52^\circ$ timing-clean peak bias** (calculated at the exact physical peak frame of each individual signal) and the **$+19.72^\circ$ peak-to-peak bias** (calculated from the absolute maximum values of the unsynced curves, which contains video overshoot due to frame-rate dynamic lag). Failure to distinguish these will read as a contradiction.

### § Robustness
*   **Condition-Independence:** Overestimation bias is virtually identical between symmetric landings ($+10.36^\circ$, SD: $6.89^\circ$) and asymmetric landings ($+10.68^\circ$, SD: $9.39^\circ$) (a negligible difference of $\Delta 0.32^\circ$) [source: phase6_final_report.md].
*   **Finding:** The tracking error is fundamentally driven by monocular camera projection geometry (sagittal camera alignment), not the subject's physical movement asymmetry or load variability.

### § Timing/Projection Diagnostic
*   **Dynamic Lag Test:** Artificially shifting time to align peak frames (peak-matching) worsened error parameters (frame-by-frame MAE rose from $14.8^\circ$ to $20.1^\circ$ post-alignment) [source: phase6_final_report.md]. This proves that the peak overestimation is not a timing artifact but a physical projection coordinate distortion.
*   **Model Defect Test:** OpenSim anatomical model coordinate definitions compared to a 3-point marker trigonometric model show a negligible variation of only $1.6^\circ$ [source: phase6_final_report.md]. This rules out software definition mismatches.
*   **Temporal Calibration:** Ground Reaction Force (GRF)-anchored timing alignment remains stable, whereas mathematical RMSE-minimization temporal shifting is highly unstable. Thus, the pooled frame-level depth curves are demoted to a cautionary illustration.

### § Limitations
*   **Stabilisation Time (TTS):** Stabilisation metrics (such as Time-to-Stabilisation) were dropped because drop-jump video recordings truncate abruptly ($0.05\text{--}0.2\text{ s}$ post-landing), making stabilization checks mathematically impossible.
*   **Contralateral Occlusion:** Far-leg knee flexion cannot be tracked during deep flexion due to sagittal self-occlusion; asymmetry calculation is limited to optoelectronic 3D IK.
*   **Pooled Depth Curves:** The frame-by-frame pooled trajectory curves are highly timing-contaminated, non-monotonic, and show weak linear tracking (average $r = 0.35$). They are presented strictly as a warning against naive time-series pooling.
*   **Angle Convention:** The drop-jump chapter uses the **clinical flexion** convention ($0^\circ$ = standing extension, deeper bend = larger angle), whereas the squat and lunge chapters use the **included angle** convention ($\approx 180^\circ$ = standing extension, deeper bend = smaller angle). Stating this difference is mandatory to avoid erroneous raw value comparisons.

### § Discussion
*   **KEY THREAD:** Because the peak overestimation bias is shown to be a **constant systematic offset within each subject**, it does not degrade screening performance when using personalised baseline tracking. In **Option B (Personalised-Deviation Screening)**, the baseline subtraction step ($\mu_{\text{base}} - NF$) mathematically cancels out this static projection offset, fully validating the screening rules designed in Step 10.
*   The drop-jump validation establishes the mathematical foundation for the uncertainty propagation weights (Phase 8 baseline noise floors) utilized throughout the framework.

---

## CHAPTER: Squat (first exercise chapter — sets template for lunge)
**STRUCTURE:** cohort & methods → headline finding → cross-cohort consistency → discussion → limitations → figures

### § Cohort & Methods
*   **YouTube Cohort:** 10 subjects performing a single repetition under in-the-wild conditions [source: phase5a_integration_summary.txt / squat_results_v4.md].
*   **REHAB24-6 Cohort:** 9 subjects performing a total of 98 processed repetitions (72 correct, 26 incorrect) in a controlled laboratory environment [source: phase5a_integration_summary.txt].
*   **Convention Check:** Squats are analyzed using the **included-angle** convention ($\approx 180^\circ$ = standing extension, smaller angle = deeper flexion bend). This is the opposite of the clinical convention ($0^\circ$ = extension) used in the drop-jump validation chapter.
*   **Extracted Biomarkers:** Peak flexion angle, Range of Motion (ROM), descent and ascent phase frame durations, mean/peak descent and ascent velocities, and jerk proxy standard deviation [source: phase5a_integration_summary.txt].

### § Headline Finding
*   **Kinematic Signature of Deviation:** Incorrect squat form in this cohort is characterized by **excessive knee flexion depth (deeper bend), a faster descent phase, and a rougher (jerkier) movement profile**.
*   **Peak Flexion Effect Size:** Large effect size showing deeper flexion for incorrect repetitions ($d = 1.7306$, $n=72$ correct vs. $26$ incorrect) [source: phase5b_effect_sizes_ci.csv].
*   **ROM Effect Size:** Correspondingly larger joint range of motion for incorrect reps ($d = -1.4484$) [source: phase5b_effect_sizes_ci.csv].
*   **Descent-Phase Localization:** Form differences are heavily localized to the descent phase:
    *   Mean descent velocity ($d = 0.7768$) and peak descent velocity ($d = 0.8216$) both show statistically significant increases for incorrect reps [source: phase5b_effect_sizes_ci.csv].
    *   *Contrast with Ascent:* Ascent-phase velocity effect sizes show confidence intervals that cross zero (mean ascent velocity $d = -0.4996$, 95% CI: $[-1.7017, +0.1301]$; peak ascent velocity $d = -0.5049$, 95% CI: $[-1.4838, +0.0848]$), meaning the ascent phase is non-discriminative for squats [source: phase5b_effect_sizes_ci.csv]. This contrasts directly with lunges.

### § Cross-Cohort Consistency (Pipeline-Validation Finding)
*   **Biomechanical Ranges:** Both YouTube and REHAB24-6 cohorts yield overlapping, biomechanically plausible knee angle distributions, showing the extraction pipeline generalizes across diverse camera angles and lighting.
*   **Cohort Differences:** REHAB24-6 exhibits systematically deeper peak flexion and larger ROM than the YouTube cohort, reflecting the difference between laboratory execution and in-the-wild physical constraints.
*   **Methodological Role:** The cross-cohort analysis serves as a **reproducibility finding**, showing the software pipeline consistently extracts kinematics. It acts as a complement to, not a substitute for, the OpenCap 3D optoelectronic physical validation.

### § Discussion
*   **Clinical Risk Interpretation:** Deeper flexion depth paired with faster, jerkier descent indicates a compensation pattern (loss of eccentric control and rapid loading) associated with increased patellofemoral loading and joint shear stress in literature.
*   **Clinical Citation Chain:** Salem & Powers (2002), FEA (2023), PMC12736615, and Farrokhi (2011) — *PENDING: author/DOI verification in Zotero during the week-16 reference sweep*.
*   **Clinical Guardrail:** Kinematic deviations are framed strictly as screening indicators of movement pattern divergence, not as diagnostic predictive markers for injury occurrence.

### § Limitations
*   **Cohort Split:** Small sample size of incorrect repetitions ($n=26$).
*   **Geometric Limits:** Sagittal-only monocular tracking lacks multi-planar coverage (no valgus/rotation tracking).
*   **Analytical Role:** The cohort analysis demonstrates reproducibility and association; it cannot validate absolute measurement accuracy (which is deferred to the Drop-Jump Validation Chapter).

### § Figures (4)
*   **Figure 1 (Distributions):** Joint angle histograms for correct vs. incorrect repetitions.
*   **Figure 2 (Forest Plot):** Cohen's d effect sizes and 95% confidence intervals for the 10 biomarkers [source: fig2_effect_sizes.png / fig2_effect_sizes.svg].
    *   *KNOWN BUG:* Overprinting of "small/medium/large" guide-labels near the boundaries; to be resolved in the week-16 figure sweep.
*   **Figure 3 (Cross-Cohort):** Overlay comparison between YouTube and REHAB24-6 distributions.
*   **Figure 4 (Representative Trajectories):** Time-series plot of representative correct vs. incorrect knee-flexion profiles showing descent-localized slope differences.

### § MUST-INCLUDE Flags
*   Highlight that the **ascent phase does NOT discriminate** for squats (effect size CIs cross zero), which highlights the unique value of the lunge ascent phase.
*   Verify all Cohen's d values strictly against the frozen output [phase5b_effect_sizes_ci.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv).
*   Flag the 4 Zotero reference citations as pending verification during the week-16 sweep.

