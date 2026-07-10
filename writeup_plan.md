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

---

## CHAPTER: Lunge (mirrors squat structure; distinctive finding = ascent-velocity divergence)
**STRUCTURE:** cohort & methods → headline finding → cross-exercise divergence → discussion → limitations → figures

### § Cohort & Methods
*   **REHAB24-6 Lunge Dataset:** 88 repetitions in the manifest [source: phase5b_integration_summary.txt].
*   **Usable Analytical Cohort:** 61 repetitions across 7 usable subjects (25 correct, 36 incorrect) successfully processed after quality filtering [source: phase5b_integration_summary.txt].
*   **Cohort Exclusions:** Two subjects were excluded from the usable dataset due to far-leg self-occlusion during the lunge movement:
    *   Subject 5 (PM_042): 12 of 13 repetitions failed phase identification (92.3% failure rate).
    *   Subject 8 (PM_112): All 12 repetitions failed phase identification (100% failure rate).
    *   *Systematic Link:* These exclusions are direct failure modes that feed the monocular camera occlusion taxonomy.
*   **Angle Convention:** Included-angle convention (consistent with the squat chapter).
*   **Statistical Methodology:** The cluster-aware subject-level bootstrapping procedure is replicated (written from scratch, not imported) from the squat analysis, as documented in the methods chapter.

### § Headline Finding
*   **Kinematic Signature of Deviation:** Incorrect lunge repetitions exhibit **increased peak flexion depth (deeper bend) and a larger joint range of motion (ROM)**, mirroring the squat chapter's overall behavior.
*   **Peak Flexion Effect Size:** Large effect size showing deeper flexion for incorrect repetitions ($d = 1.6904$, $n=25$ correct vs. $36$ incorrect) [source: phase5c_effect_sizes_ci.csv].
    *   *Correction Verification:* An earlier draft contained a calculation error ($d = 1.4944$); the corrected value is strictly $d = 1.6904$.
*   **Visual Proof:** Incorrect deeper flexion is visibly confirmed via time-series overlay of Subject 7 (PM_125) correct repetition 14 vs. incorrect repetition 16.
*   **ROM Effect Size:** Correspondingly larger joint range of motion for incorrect reps ($d = -1.2653$, correct mean = $59.02^\circ$ vs. incorrect mean = $90.30^\circ$) [source: phase5c_effect_sizes_ci.csv].

### § Cross-Exercise Divergence (The Distinctive Finding)
*   **Ascent Velocity Discrimination:** Unlike the squat (where ascent velocities do not discriminate between form groups), **lunge ascent velocities are highly discriminative**:
    *   Peak ascent velocity ($d = -0.9721$, correct mean = $3.85^\circ/\text{frame}$ vs. incorrect mean = $6.95^\circ/\text{frame}$) is a reliable indicator [source: phase5c_effect_sizes_ci.csv].
    *   Mean ascent velocity ($d = -0.7962$, correct mean = $1.26^\circ/\text{frame}$ vs. incorrect mean = $1.87^\circ/\text{frame}$) is a reliable-marginal indicator [source: phase5c_effect_sizes_ci.csv].
*   **MUST-LINK TO SQUAT:** Connect these findings explicitly to the squat chapter. The fact that the lunge's ascent phase is a primary indicator of form deviation (representing a rapid, less-controlled propulsion or spring-back step) whereas the squat's ascent phase carries zero discriminative signal is a core cross-exercise finding.
*   **CAUTION — Overclaim Correction:** Ensure the text does not overclaim. Earlier drafts claimed significance for all ascent metrics; only report those where the bootstrap confidence intervals exclude zero (peak ascent velocity $d=-0.97$, mean ascent velocity $d=-0.80$). Exclude metrics with zero-crossing CIs (e.g., peak extension $d = -0.4972$, tempo ratio $d = -0.3796$) from significance claims.

### § Discussion
*   **Screening-not-prediction:** Kinematic markers (like ascent propulsion) are evaluated as movement characterisations, not as diagnostic classifiers.
*   **Cross-Exercise Value:** Different exercises expose discriminative signals in different movement phases. Squats reveal form deviations exclusively in the eccentric descent phase, whereas lunges reveal form deviations in both descent (eccentric) and ascent (propulsive concentric spring-back) phases.

### § Limitations
*   **Occlusion Exclusions:** 2 subjects fully excluded due to far-side occlusion on monocular sagittal camera view.
*   **Sample Constraints:** Small usable cohort size (7 subjects, 61 repetitions).
*   **Geometric Boundaries:** Sagittal-only tracking limits valgus/rotation analysis.

### § Figures (4)
*   **Figure L1 (Distributions):** Histograms comparing correct vs. incorrect repetitions.
*   **Figure L2 (Forest Plot):** Cohen's d effect sizes and 95% confidence intervals for lunge biomarkers [source: fig_L2_effect_sizes.png / fig_L2_effect_sizes.svg].
    *   *KNOWN BUG:* Same guide-label overprint bug as the squat forest plot; to be resolved in the week-16 sweep.
*   **Figure L3 (Cross-Exercise):** Side-by-side forest plot comparison highlighting the lunge-squat ascent-velocity divergence.
*   **Figure L4 (Representative Trajectories):** Representative time-series overlay of Subject 7 (PM_125) showing lunge repetition trajectories (rep 14 vs. rep 16).

### § MUST-INCLUDE Flags
*   **Ascent-Velocity Divergence:** Ensure this finding is highlighted as the primary biomechanical difference between squats and lunges.
*   **Overclaim Correction:** Verify that only CI-reliable effects (peak ascent velocity $d=-0.97$, mean ascent velocity $d=-0.80$) are presented as significant.
*   **Occlusion Failure Modes:** Explicitly connect the Subject 5 and Subject 8 exclusions to the monocular camera occlusion taxonomy.

---

## COMPONENT: Uncertainty-Weighted Screening Framework (Track B demo)
**STRUCTURE:** purpose → uncertainty source → projection/motion decomposition → inverse-variance weighting → cross-exercise transfer → worked example → does-not-claim

### § Purpose
*   **Role:** An architectural demonstration of combining multi-biomarker screening signals weighted dynamically by their ground-truth-validated measurement uncertainty.
*   **Framework Identity:** It represents a weighting methodology, **not** a risk score generator or a repetition classifier.
*   **Scientific Value:** Serves as the "connective tissue" of the thesis, directly linking the Drop-Jump Mocap validation results to the downstream squat/lunge screening layers.
*   **Source:** [17_uncertainty_framework_outputs/framework_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/17_uncertainty_framework_outputs/framework_design.md).

### § Uncertainty Source
*   **Variance Calculation:** Error standard deviations ($SD_i$) and total variances ($\sigma^2_{i, \text{total}}$) are derived directly from the Drop-Jump 95% Limits of Agreement width:
    $$SD_i = \frac{LoA_{i, \text{upper}} - LoA_{i, \text{lower}}}{2 \cdot 1.96}$$
    $$\sigma^2_{i, \text{total}} = (SD_i)^2$$
*   **Source Data:** [phase6_agreement_final.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv).
*   **Asymmetry Excluded:** Inter-limb asymmetry is excluded from monocular video transfer since it could not be validated on monocular video due to contralateral self-occlusion.

### § Projection/Motion Decomposition (Methodological Core)
*   **Variance Partitioning:** The total observed drop-jump variance is decomposed into two distinct physical components:
    $$\sigma^2_{i, \text{total}} = \sigma^2_{i, \text{proj}} + \sigma^2_{i, \text{mot}}$$
    where $\sigma^2_{i, \text{proj}}$ represents transferable camera projection/geometry error, and $\sigma^2_{i, \text{mot}}$ represents non-transferable dynamic motion/timing error (specific to drop-jump landings).
*   **Biomarker Splits:**
    *   *Peak Flexion:* $100\%$ projection, $0\%$ motion (directly measured at the static peak landing absorption frame where velocity $\approx 0$).
    *   *Range of Motion:* Mathematically propagated from the start (contact) and end (peak) points.
    *   *Contact Flexion & Loading Rate:* Split ratios are assumed based on movement dynamics.
*   **Sensitivity-Sweep Robustness:** A 9-configuration sensitivity sweep proves these assumed splits are **immaterial** to the framework. Across all permutations, peak flexion remains the dominant biomarker ($50.01\%\text{--}58.59\%$, a variance range $<8.6\%$) and velocity remains heavily down-weighted ($2.30\%\text{--}9.38\%$), validating weight stability [source: framework_design.md §4].

### § Inverse-Variance Weighting
*   **Concept:** Biomarker weights ($w_i$) are calculated as:
    $$w_i = \frac{1}{\sigma^2_{i, \text{proj}}}$$
    representing the textbook-optimal statistical combination for combining measurements with unequal precision.
*   **Result:** High-variance biomarkers (such as loading rate/descent velocity, which has an LoA width of $\approx \pm 130^\circ/\text{s}$) are heavily down-weighted (near-zero contribution), whereas low-variance biomarkers (contact flexion) are favored.

### § Cross-Exercise Transfer (The Honesty Point)
*   **Transfer Guardrail:** Only the **projection-based variance** ($\sigma^2_{i, \text{proj}}$) is transferred to slow, controlled sagittal squats and lunges. The dynamic motion-based timing error ($\sigma^2_{i, \text{mot}}$) is task-dependent and **not** transferred (unvalidated for slow movements, documented as future work).
*   **Transfer Weights:**
    *   Peak Flexion: **$57.15\%$** [source: framework_design.md §4].
    *   Start/Contact Flexion: **$22.63\%$** [source: framework_design.md §4].
    *   Range of Motion: **$15.30\%$** [source: framework_design.md §4].
    *   Joint Velocity (descent): **$4.92\%$** [source: framework_design.md §4].
*   **Biomechanical Mapping:** The parameter transfer is justified by kinematic function: squat/lunge starting flexion maps to drop-jump contact flexion (shallow extension); descent velocity maps to loading rate (angular rate, $^\circ/\text{s}$).

### § Worked Example
*   **Demonstration:** Projection weights applied to REHAB24-6 squat PM_008 and lunge PM_021 repetitions.
*   **Result:** Visually and numerically demonstrates peak flexion depth dominating the tracking, while velocity features are down-weighted to prevent noisy, high-uncertainty signals from corrupting the screening layer.
*   **MUST CLARIFY:** The uncertainty bounds represent the monocular pipeline's **measurement uncertainty** (constant across repetitions by construction), **not** the subject's baseline movement variability.
*   **Source Data:** [worked_example.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/17_uncertainty_framework_outputs/worked_example.csv) and `worked_example_weights.png`.

### § Does-Not-Claim
*   Does not output combined risk scores, does not evaluate injury probability, does not classify repetitions, does not transfer drop-jump landing motion-uncertainty, and does not represent a clinically deployed system.

### § MUST-INCLUDE Flags
*   Include the **$<8.6\%$ sensitivity-sweep robustness result** to demonstrate that the framework's weights are robust to assumed component splits.
*   Clearly maintain the distinction between **projection-transferable** and **motion-non-transferable** variance to protect the design against questions on task-variance transfer.
*   Emphasize that the error bounds represent **measurement uncertainty**, not physical joint range of motion variability.



