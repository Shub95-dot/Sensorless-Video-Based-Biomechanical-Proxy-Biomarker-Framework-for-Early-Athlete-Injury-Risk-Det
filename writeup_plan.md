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

---

## COMPONENT: Personalised Baseline (Track B demo)
**STRUCTURE:** purpose → method → result (both-sides) → cross-component finding → personalised-not-group → limitation → does-not-claim

### § Purpose
*   **Role:** An architectural demonstration of tracking kinematics relative to an individual's own baseline, with deviation detection gated by a validated measurement-noise floor.
*   **Time Model:** Utilizes pseudo-timepoints (within-session repetition order) to represent sequence progression. It is **not** a longitudinal baseline tracking system.
*   **Source:** [18_personalised_baseline_outputs/baseline_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/18_personalised_baseline_outputs/baseline_design.md).

### § Method
*   **Baseline Initialization:** Established using the mean of the first two correct repetitions of the session:
    $$\mu_{\text{base}, i} = \frac{x_{1, i} + x_{2, i}}{2}$$
    The standard error ($SD$) is recorded for descriptive consistency but is **not** used to set threshold gates due to small-sample instability.
*   **Noise-Gating Rule:** Test repetitions are gated per-biomarker against the Phase 7 projection-transferred noise floors ($NF_i$):
    *   Peak flexion noise floor: **$\pm 11.99^\circ$** [source: baseline_design.md / phase8_personalised_baseline.py].
    *   ROM noise floor: **$\pm 23.17^\circ$** [source: baseline_design.md].
    *   Descent velocity noise floor: **$\pm 40.86^\circ/\text{s}$** [source: baseline_design.md / phase8_personalised_baseline.py].
*   **Deviation Rule:** A test repetition triggers a flag if the absolute difference exceeds the biomarker's floor:
    $$\Delta_i = |x_{\text{test}, i} - \mu_{\text{base}, i}| > NF_i$$

### § Result (Both-Sides Demonstration)
*   **Evaluation Subjects:** Demonstrated on Squat PM_113 and Lunge PM_104 [source: worked_example_baseline.csv].
*   **Quiet Side (No False Alarms):** Correct repetitions 3–5 remain within the noise floors (squat deviations $\Delta$ range between $2.0^\circ\text{--}9.3^\circ$). This includes a minor propulsive wobble in the lunge that is correctly classified as within-noise, showing **no false alarms** on normal movement variability.
*   **Firing Side (Deviation Detected):** Incorrect repetitions 6–10 successfully exceed the noise floors (squat peak flexion deviations $\Delta$ of $21.0^\circ\text{--}36.0^\circ$).
*   **Analysis:** The noise floor sits precisely in the "clean gap" between natural biomechanical variation and a genuine movement deviation. Showing both sides (preventing false alarms while catching real changes) is the primary value.
*   **Source Data:** [worked_example_baseline.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/18_personalised_baseline_outputs/worked_example_baseline.csv) and `baseline_tracking.png`.

### § Cross-Component Finding (Payoff of Weighting)
*   **Biomarker Roles:** The baseline tracking illustrates the uncertainty weights designed in Phase 7:
    *   *Peak Flexion:* Dominates the detection layer because it has a tight noise floor ($\pm 11.99^\circ$) and high projection weight ($57.15\%$).
    *   *Descent Velocity:* Has a wide noise floor ($\pm 40.86^\circ/\text{s}$) due to high monocular measurement uncertainty ($SD_{\text{proj}} = 20.85^\circ/\text{s}$) and carries a low projection weight ($4.92\%$). It does **not** independently trigger any flags, except for a single large, genuine velocity spike on Squat PM_113 rep 6 ($110.0^\circ/\text{s}$), where the deviation is large enough to exceed the wide noise floor.
*   **Wording Guardrail:** Velocity's wide noise floor does **not** "actively suppress noise"; it is simply a low-confidence biomarker that is correctly down-weighted by a wide noise gate to reflect its measurement uncertainty.

### § Personalised-Not-Group (The Distinction)
*   **Unit of Analysis:** The system compares the individual to their own baseline state, not to a group average or cohort classification.
*   **Flag Meaning:** A fired flag means the movement exhibits a **real kinematic deviation beyond monocular measurement noise**, not a clinical pathology or a "bad repetition."

### § Limitations
*   **Floor Width:** Subtle, sub-floor movement progression (changes $<12^\circ$ in flexion) is masked by the wide monocular measurement uncertainty.
*   **Temporal Limits:** Utilizes single-session repetitions as pseudo-timepoints; longitudinal baseline tracking across weeks is deferred.

### § Does-Not-Claim
*   Does not evaluate longitudinal progression across sessions, does not predict joint pathology, does not classify repetitions, and does not represent a clinically deployed system.

### § MUST-INCLUDE Flags
*   Include the **both-sides demonstration** (quiet correct reps vs. firing incorrect reps) to prove that the noise floors prevent false alarms.
*   Link this demo directly to the **Phase 7 uncertainty weights** (flexion dominance vs. velocity down-weighting).
*   Maintain the **personalised vs. group** analysis distinction to avoid reading as a squat-chapter repeat.
*   Frame a fired flag as a **deviation-beyond-measurement-noise**, never as a "bad rep" or pathology.

---

## COMPONENT: Digital Twin (Track B demo)
**STRUCTURE:** purpose → mechanism → result → exclusion explanation (design feature) → transient-vs-sustained (future work) → does-not-claim

### § Purpose
*   **Role:** An architectural demonstration of continuous-update personalization. It extends the Phase 8 baseline tracking by updating the subject's reference state dynamically as repetitions are ingested.
*   **Modeling Identity:** Non-predictive; it is **not** a learned machine learning model (no parameters, training loops, or learning rates) and does not represent real longitudinal tracking across weeks.
*   **Source:** [19_digital_twin_outputs/twin_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/19_digital_twin_outputs/twin_design.md).

### § Mechanism
*   **State Representation:** The twin state is defined as the running reference mean ($\mu_{t, i}$) paired with the fixed Phase 7 projection-based noise floor ($NF_i$).
*   **Conditional Update Rule:**
    *   *Within-Noise:* If absolute deviation is within the noise floor ($\Delta_i \le NF_i$), the repetition is absorbed. The reference updates:
        $$\mu_{t+1, i} = \frac{N_t \mu_{t, i} + x_{t+1, i}}{N_t + 1}$$
    *   *Out-of-Noise:* If absolute deviation exceeds the noise floor ($\Delta_i > NF_i$), the repetition is rejected (aberration rejection) to prevent reference drift. The state locks:
        $$\mu_{t+1, i} = \mu_{t, i}$$
    *   *Flagging:* Excluded repetitions are counted, flagged, and explained in the output, never discarded silently.
*   **Algorithm Characteristics:** Simple, parameter-free arithmetic update, adhering to clinical transparency requirements.
*   **Source Code:** `phase9_digital_twin.py`.

### § Result
*   **Evaluation Subject:** Demonstrated on Squat PM_113 [source: worked_example_twin.csv].
*   **Tracking Drift:** The peak flexion reference evolves dynamically from $72.98^\circ$ to $69.21^\circ$ across repetitions 3–5, absorbing the subject's natural baseline drift.
*   **Locking Flat:** The reference locks flat at $69.21^\circ$ for repetitions 6–10 when incorrect reps deviate past the noise gate.
*   **Tracking Band:** The noise floor band is not static; it dynamically tracks the evolving reference line, stepping down and locking in tandem with the reference mean.
*   **Independent Gating:** Gating is computed independently per biomarker. For a single repetition, peak flexion can exceed its threshold and lock, while velocity remains within its threshold and continues to update. Highlight this behavior explicitly so it does not read as a tracking inconsistency.
*   **Source Data:** [worked_example_twin.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/19_digital_twin_outputs/worked_example_twin.csv) and `twin_tracking.png`.

### § Exclusion Explanation (Design Feature)
*   **Transparency Output:** When a repetition is excluded, the twin outputs a measurement-based justification rather than a quality verdict:
    *   *"Repetition N has deviated from your baseline reference beyond monocular measurement uncertainty. The twin reference has locked and will not update from this observation. From a single repetition, the twin cannot distinguish a transient movement deviation from a genuine sustained shift in baseline state."*
*   **Epistemic Humility:** Explains what the monocular pipeline can mathematically justify (measurement uncertainty boundaries) without labeling the movement as "bad" or "incorrect." Verified on Squat PM_113 rep 6.

### § Transient-vs-Sustained (Future Work)
*   **Current Logic Constraint:** Rejects all out-of-noise repetitions to protect baseline state, which is correct for transient form breakdowns.
*   **Downstream Limitation:** It cannot distinguish a temporary aberration from a permanent transition to a new baseline (e.g. if the subject permanently shifts their depth profile).
*   **Longitudinal Future Work:** A deployed clinical twin requires multi-session tracking: if a deviation persists across sessions, it should be absorbed as a sustained shift; if it is isolated, it remains classified as a transient deviation.
*   **Motivation:** The exclusion explanation itself provides the biomechanical argument for this future-work extension.

### § Does-Not-Claim
*   Does not forecast future performance, does not output correct/incorrect form labels (only flags baseline deviations), does not utilize learned parameters, does not represent multi-session longitudinal tracking, does not evaluate joint pathology or injury risk, and does not represent a clinically deployed system.

### § MUST-INCLUDE Flags
*   Explicitly mention **independent per-biomarker gating** (e.g., peak locks while velocity updates on the same rep) to clarify the twin's tracking logic.
*   Present the **exclusion explanation** as a design feature representing epistemic humility, not simply error-handling text.
*   Connect the **transient-vs-sustained limitation** directly to the future-work section, using the twin's output text as the motivating argument.

---

## COMPONENT: Rule-Based Screening Layer (Step 10, Track A CORE — not a demo)
**STRUCTURE:** purpose → distinction from Phase 8/9 → screening modality choice → rules & grounding → convention → result → does-not-claim

### § Purpose
*   **Role:** The screening decision layer that translates raw monocular joint measurements into named, clinically meaningful screening flags (e.g. EXCESS_DEPTH, EXCESS_ROM, EXCESS_VELOCITY).
*   **Pipeline Status:** A core Track A pipeline deliverable (not a demo), representing the decision logic that the Counterfactual XAI (Step 11) is designed to explain.
*   **Source:** [20_screening_outputs/screening_rules_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/20_screening_outputs/screening_rules_design.md).

### § Distinction from Phase 8/9 (Uncertainty & Baseline)
*   **Phase 8/9 baseline:** Evaluates generic, unnamed kinematic deviation relative to the subject's baseline state (answering: *"has the movement changed beyond monocular measurement noise?"*).
*   **Step 10 screening:** Assigns named, clinically grounded rules on top of those deviations (answering: *"this deviation is EXCESS_DEPTH, representing a kinematic profile linked to joint loading in literature"*).
*   **Relation:** Phase 8/9 is the noise-gating engine; Step 10 is the clinical screening interpretation layer.

### § Screening Modality Choice
*   **Option B (Personalised-Deviation Screening):** A repetition is flagged only if it deviates from the subject's personal session baseline mean ($\mu_{\text{base}, i}$) beyond the validated monocular noise floor ($NF_i$).
*   **Justification:** Neutralizes individual anatomical variations and camera perspective/geometry offsets (which are constant within a subject's video session).
*   **Rejected Option A:** Fixed population-based thresholds were rejected as unvalidated claims of universal biomechanical normality.

### § Rules & Grounding
Threshold gates ($NF_i$) are defined at a 95% confidence interval ($1.96 \cdot SD_{\text{proj}, i}$). Every rule direction is empirically grounded in cohort distributions:
1.  **EXCESS_DEPTH (Knee Flexion Depth):**
    *   *Rule:* Fires if $x_{\text{peak}} < \mu_{\text{base}, \text{peak}} - 11.99^\circ$.
    *   *Squat Grounding:* Correct reps ($60.85^\circ \pm 12.72^\circ$) vs. Incorrect reps ($41.14^\circ \pm 6.20^\circ$) [source: phase5a_integration_summary.txt]. Incorrect reps have smaller angles (deeper flexion bend).
    *   *Lunge Grounding:* Correct reps ($89.66^\circ \pm 8.33^\circ$) vs. Incorrect reps ($68.03^\circ \pm 15.11^\circ$) [source: phase5c_effect_sizes_ci.csv]. Incorrect is deeper.
2.  **EXCESS_ROM (Range of Motion Excursion):**
    *   *Rule:* Fires if $x_{\text{rom}} > \mu_{\text{base}, \text{rom}} + 23.17^\circ$ (direction corrected; incorrect reps exhibit larger joint excursion).
    *   *Squat Grounding:* Correct reps ($111.19^\circ \pm 18.06^\circ$) vs. Incorrect reps ($134.31^\circ \pm 7.23^\circ$) [source: phase5a_integration_summary.txt].
    *   *Lunge Grounding:* Correct reps ($59.02^\circ \pm 20.94^\circ$) vs. Incorrect reps ($90.30^\circ \pm 27.00^\circ$) [source: phase5c_effect_sizes_ci.csv].
3.  **EXCESS_VELOCITY (Uncontrolled Descent Speed):**
    *   *Rule:* Fires if $x_{\text{velocity}} > \mu_{\text{base}, \text{velocity}} + 40.86^\circ/\text{s}$ (where raw biomarker $^\circ/\text{frame}$ is multiplied by $30.0\text{ FPS}$ to convert to physical velocity).

### § Convention Check
*   **Squat/Lunge Convention:** Included-angle convention ($\approx 180^\circ$ = standing extension, smaller angle = deeper flexion). Therefore, a smaller peak flexion angle value physically represents more flexion depth (reconciled with the `EXCESS_DEPTH` negative sign in the rule).
*   **Contrast:** Differs from drop-jump's clinical flexion convention ($0^\circ$ = extension), which is flagged for Zotero/Chapter harmonization during the week-16 sweep.

### § Result
*   **Application:** Run on Squat PM_113 and Lunge PM_104 [source: worked_example_screening.csv].
*   **Performance:** Correct reps are classified as `NOT_FLAGGED`. Incorrect reps are flagged as `SCREENING_POSITIVE` with the active rule list and numeric deviation margins ($M_i$).
*   **Verification:** These margins ($M_i$) are saved to the output CSV and serve as the input targets consumed by the Counterfactual XAI (Step 11) layer.
*   **Validation Aside:** Flags align with the validation labels of this dataset, but this alignment is coincidental to the experimental design, not a claim of algorithmic diagnostic validation.

### § Does-Not-Claim
*   Outputs screening characterisations, not clinical diagnoses; rules act as heuristic risk association indicators, not diagnostic cut-offs; not a trained model; screening-not-prediction.

### § MUST-INCLUDE Flags
*   Clearly maintain the **Phase 8/9 vs. Step 10 distinction** (deviation detection engine vs. named screening decision layer) to prevent redundancy.
*   Confirm the **empirical direction of `EXCESS_ROM`** is correct (incorrect reps have larger joint range of motion).
*   Specify that the output records **numeric deviation margins** ($M_i$) for every fired rule, which is the data Step 11 XAI consumes.

---

## COMPONENT: Counterfactual XAI (Step 11, Track A CORE — NOVELTY CONTRIBUTION #4)
**STRUCTURE:** purpose → faithfulness argument → templates → MKI → confidence grading → verified example → does-not-claim

### § Purpose
*   **Role:** Computes counterfactual explanations for Step 10's screening flags by specifying the exact physical boundary changes that would have prevented the flags from firing.
*   **Novelty Status:** Novelty contribution #4 of the thesis. Prior to this build, the workspace contained only empty folders scaffolding post-hoc feature importance frameworks (SHAP/LIME), which were deprecated as the incorrect approach for rule-based screening.
*   **Source:** [21_xai_outputs/xai_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/21_xai_outputs/xai_design.md).

### § Faithfulness Argument (The Key Defensible Advantage)
*   **Faithfulness by Construction:** Feature importance methods (SHAP/LIME) are post-hoc approximations of a black-box model's local decision boundary, introducing approximation error. In our framework, the screening rules *are* the actual decision boundaries. 
*   **Exact Margins:** The counterfactual engine calculates the exact margin distance ($M_i$) to the decision boundaries directly from the biomarker inputs with **zero approximation error**. The explanations are thus faithful by construction.
*   **Deprecation:** The placeholder directories `8_xai_outputs/` (SHAP/LIME) are deprecated, establishing that model-agnostic feature importance is inappropriate for transparent, rule-based screening decision systems.

### § Counterfactual Templates
*   **Descriptive Wording:** Explanations are framed as descriptive conditions (describing the mathematical coordinates required to clear the flag) rather than prescriptive instructions to the subject (e.g. telling the user how to move).
*   **Convention Match:** Squat peak flexion (included-angle) is verified:
    *   *Values:* Squat PM_113 rep 6 peak flexion $= 43.22^\circ$ vs. threshold $= 60.99^\circ$ [source: worked_example_explanations.json].
    *   *Text:* *"Had the peak flexion angle been at least 60.99° (representing a shallower bend of 17.77° less depth), the EXCESS_DEPTH flag would not have fired."* The numeric direction matches the biomechanical convention (larger angle = shallower).

### § MKI (Minimal Kinematic Intervention)
*   **Coupled Adjustments:** If both `EXCESS_DEPTH` and `EXCESS_ROM` fire on a repetition, the MKI resolves their physical coupling. Under the explicit biomechanical assumption that range of motion scales directly with peak flexion depth (assuming a constant standing extension start point), the MKI computes the maximum of the two required depth changes:
    $$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$
    This determines the single flexion adjustment that will simultaneously satisfy both rules.
*   **Task Verification:** Verified on the lunge dataset, where the ROM margin exceeded the depth margin, and the `max()` operator correctly selected the larger ROM constraint to clear both flags.
*   **Independent Rules:** Uncoupled rules (such as `EXCESS_VELOCITY`) are reported as separate independent conditions in a set (e.g. *"and descent speed had been at least 19.82°/s slower"*), rather than folded into the single MKI flexion value. Stated as descriptive conditions rather than prescriptive advice.

### § Confidence Grading (Ties to Phase 7 Validation)
*   **Uncertainty Buffer:** Counterfactual margins are evaluated against a confidence buffer defined as half the biomarker's validated noise floor ($0.5 \cdot NF_i$):
    *   If $M_i \le 0.5 \cdot NF_i$, a `LOW CONFIDENCE (Near Noise Floor)` caution is appended, indicating the deviation is close to monocular measurement uncertainty limits.
*   **Scientific Integration:** Ties the explanation certainty directly back to the physical ground-truth validation (Drop-Jump LoAs), threading measurement discipline through the final output.

### § Verified Worked Example
*   **Subject:** Squat PM_113 rep 6 [source: worked_example_explanations.json].
    *   *EXCESS_DEPTH:* Margin $= 17.77^\circ > 5.99^\circ$ buffer $\implies$ `HIGH CONFIDENCE`.
    *   *EXCESS_ROM:* Margin $= 7.83^\circ \le 11.58^\circ$ buffer $\implies$ `LOW CONFIDENCE (Near Noise Floor)`.
*   *Explanation Set:* The coupled depth/ROM flags would not have fired if flexion depth had been $17.77^\circ$ shallower (high confidence) AND descent velocity had been $19.82^\circ/\text{s}$ slower (high confidence).

### § Does-Not-Claim
*   Explains only the mathematical rule-firing decisions (why a flag was raised based on inputs); it does **not** explain clinical injury causation, biomechanical injury mechanisms, or predict clinical outcomes. No prescriptive advice or diagnostic claims are made.

### § MUST-INCLUDE Flags
*   Highlight **faithfulness-by-construction** as the primary defensible advantage over SHAP/LIME (crucial for defending the novelty of Track A contribution #4).
*   Document the **descriptive-not-prescriptive wording change** and its clinical rationale (screening output vs. professional coaching advice).
*   State the **MKI coupling assumption** explicitly as a stated simplification, not an absolute biomechanical law.
*   Note the development timeline: this component was built from scratch after establishing Step 10's screening rules, replacing the empty SHAP/LIME scaffolding.

---

## COMPONENT: Temporal Sequence Model + Self-Supervised (future work)
**STRUCTURE:** purpose → design → results → interpretation → self-supervised future-work link → does-not-claim

### § Purpose
*   **Role:** A controlled comparison to evaluate whether within-repetition joint-angle trajectory shape carries discriminative form screening signal beyond simple static endpoint biomarkers (peak flexion, ROM), and whether a complex sequence model (LSTM) adds value over a simple shape baseline at this cohort scale.
*   **Time Model:** Evaluates within-repetition frame-by-frame joint trajectories; it is **not** an across-session longitudinal model.
*   **Source:** [23_temporal_model_outputs/temporal_model_design.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/23_temporal_model_outputs/temporal_model_design.md) and [temporal_model_evaluation_report.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/23_temporal_model_outputs/temporal_model_evaluation_report.md).

### § Design (The Evaluation Rigor)
*   **LOSO CV:** Leave-One-Subject-Out cross-validation (9 squat folds, 7 lunge folds). No subject reps leak across train/test splits.
*   **Anti-Leakage Normalization:** Evaluates two schemes to isolate the signal:
    *   *Scheme A (Offset-Subtracted):* $\theta(t) - \theta(0)$, which preserves angular amplitude.
    *   *Scheme B (Min-Max Scaled):* Scales between 0.0 and 1.0 to isolate pure shape timing/velocity profiles independent of range.
*   **Fair Baseline Feature Mapping:** Handcrafted shape features are computed on the same normalized trajectory as the LSTM sees, denying the baseline classifier absolute amplitude whenever the LSTM is.
*   **Baselines:** Majority-class zero-rule guesser, and a Logistic Regression classifier fit only on `peak_flexion_deg`.
*   **Pre-Registration:** All three potential outcome scenarios were pre-registered in the design file **before** running the training, establishing a null/tie result as a rigorous scientific finding rather than an engineering failure.
*   **Balance:** Class weighting used to prevent gradient updates favoring the majority class.

### § Results
*   **Naive Floors (Majority Guess):**
    *   *Squat:* $73.47\%$ Accuracy / $50.00\%$ Balanced Accuracy.
    *   *Lunge:* $59.02\%$ Accuracy / $50.00\%$ Balanced Accuracy.
*   **Peak Flexion Baseline (Winner):**
    *   *Squat:* **$81.36\%$ Balanced Accuracy** (Accuracy: $81.63\%$, AUC-ROC: $0.9038$).
    *   *Lunge:* **$81.50\%$ Balanced Accuracy** (Accuracy: $80.33\%$, AUC-ROC: $0.8289$).
*   **Shape Feature Baseline:**
    *   *Squat:* **$33.76\%$ Balanced Accuracy** (sub-chance score verified as a genuine statistical artifact of class weighting on zero-signal noise).
    *   *Lunge:* **$58.39\%$ Balanced Accuracy**.
*   **LSTM Model A (Scheme B — Pure Shape):**
    *   *Squat:* **$50.00\%$ Balanced Accuracy** (reverts completely to majority guessing).
    *   *Lunge:* **$39.17\%$ Balanced Accuracy** (below chance).
*   **LSTM Model A (Scheme A — Amplitude Preserved):**
    *   *Squat:* **$53.79\%$ Balanced Accuracy** (barely above chance).
    *   *Lunge:* **$53.78\%$ Balanced Accuracy** (barely above chance).
*   **Result Source:** [temporal_model_comparison.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/23_temporal_model_outputs/temporal_model_comparison.csv) and `temporal_model_evaluation_report.md`.

### § Interpretation (Outcome 3 — Endpoint Dominance)
*   **Finding:** Validates **Outcome 3 (Endpoint Dominance)**. Flexion depth is the dominant discriminative kinematic signal. Frame-by-frame shape details do not carry useful independent information for form classification on this dataset.
*   **LSTM Failure Mode:** Even when amplitude is kept (Scheme A), the LSTM fails to extract it, scoring $\approx 54\%$ vs. the single-feature baseline's $\approx 81\%$. This represents a classic manifestation of **small-data overfitting/subject-memorisation**: the high parameter capacity of the LSTM network leads it to memorize subject-specific calibration offsets on our 9/7 subject cohorts, rather than generalizing the depth boundary.
*   **Step 10 Validation:** Retroactively validates Step 10's screening layer design, confirming that transparent, simple rules based on peak flexion and ROM endpoints are optimal.

### § Self-Supervised Pretraining (Reasoned Future Work)
*   **Reasoning:** Self-supervised pretraining aims to learn representations to aid downstream deep models. Since:
    1.  The downstream screening task is solved by a single static endpoint biomarker (peak flexion), and
    2.  Deep sequence models overfit and fail to generalize at this cohort scale,
    Self-supervised pretraining is highly unlikely to yield downstream gains on this dataset.
*   **Framing:** Pretraining is documented as evidence-grounded future work requiring substantially larger multi-subject cohorts, where representation learning could help before endpoint saturation. It represents a pre-accepted time-boxed null scoping outcome.
*   **Source:** [dissertation_writeup_index.md](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL ANALYSIS OF INJURY/dissertation_writeup_index.md) Chapter 12 entry.

### § Does-Not-Claim
*   Does not claim that trajectory shape never contains signal, specifically that it is not warranted at this cohort scale; does not claim pretraining is generally without value, specifically that it cannot yield gains given the demonstrated ceiling here.

### § MUST-INCLUDE Flags
*   Clearly state that the outcome scenarios were **pre-registered in the design document before training** to establish the null result as scientific rigor.
*   Frame the LSTM results as **subject-memorisation overfitting** rather than a generic underperformance note.
*   Present the **retroactive validation of Step 10's endpoint rules** as a key cross-component thread.
*   Directly ground the **self-supervised pretraining future work omission** in the empirical LSTM results.

---

## CHAPTER: General Discussion + Failure-Mode Taxonomy (cross-cutting synthesis — write LAST among content chapters)
**STRUCTURE:** synthesis of contributions → cross-exercise findings → the failure-mode taxonomy → what the uncertainty framework enables → limitations of the whole thesis → future work → closing statement

### § Synthesis of the Four Novelty Contributions
1.  **Cross-Exercise Integration (Modality-Independent Processing):** Demonstrates that a single monocular video pipeline can extract comparable biomechanical biomarkers across squats (slow bilateral), lunges (slow unilateral), and drop-jumps (rapid dynamic landing impact).
2.  **Failure-Mode-Aware Pose Extraction (Contribution #2):** Departs from traditional "black-box" validation. The thesis explicitly maps **where and why** the pose-tracking pipeline fails (occlusion, camera angles, movement velocities), establishing a formalized taxonomy of monocular limitations.
3.  **Uncertainty-Weighted Screening Transfer (The Methodological Spine):** Connects the ground-truth Mocap validation directly to the screening layer by decomposing observed error into transferable projection vs. non-transferable motion components, enabling inverse-variance weighting of clinical biomarkers.
4.  **Counterfactual XAI on Rule-Based Flags (Novelty #4):** Replaces model-approximating feature importance (SHAP/LIME placeholders) with a faithful-by-construction explanation engine that outputs the exact numeric margins needed to satisfy clinical rules.

### § Cross-Exercise Findings (The Comparative Story)
*   **Squat:** Kinematic form deviations are strictly localized to the eccentric phase. Peak flexion depth and ROM dominate discrimination, whereas ascent-phase velocities do not discriminate (bootstrap CIs cross zero).
*   **Lunge:** Parallels the squat on flexion depth, but exhibits **ascent velocity divergence**. Peak ascent velocity ($d = -0.97$) and mean ascent velocity ($d = -0.80$) are highly discriminative, representing rapid concentric propulsion.
*   **Drop-Jump:** Serves as the validation anchor, qualifying baseline camera projection errors under high-velocity landing conditions.
*   **Synthesis Finding:** Different exercises expose form screening signals in different phases of movement (squat = descent only, lunge = descent + ascent).

### § The Failure-Mode Taxonomy (Contribution #2)
Rather than a list of unrelated anomalies, monocular tracking limits are synthesized into four categorized failure types:
1.  **Sagittal self-occlusion (Occlusion failure):** Direct cause of lunge subject exclusions (Subject 5: 92% phase-ID failure; Subject 8: 100% failure) and the drop-jump asymmetry exclusion. Far-leg tracking is occluded by the near leg in the sagittal camera plane.
2.  **Dataset recording truncation (Temporal limit):** Dropping the Time-to-Stabilisation (TTS) biomarker in the drop-jump validation due to videos cutting off $0.05\text{--}0.2\text{ s}$ post-impact. This is identified as a data collection boundary, not an algorithmic pipeline failure.
3.  **Camera projection geometry bias (Projection bias):** A constant $+10.52^\circ$ overestimation bias at peak flexion, shown to be depth-independent in the landing band.
4.  **Small-cohort model mismatch (Data-scale-model mismatch):** LSTM sequence models memorizing subject identities (overfitting) rather than generalizing flexion rules across 9/7 subjects. Represents a general lesson in deep model complexity vs. data limits.

### § What the Uncertainty Framework Enables (The Connective Payoff)
The validation metrics propagate through a unified mathematical chain:
1.  **Validation:** Establish absolute limits of agreement (LoA) against optoelectronic ground truth (Drop-Jump).
2.  **Uncertainty Quantification:** Decompose total variance to extract the transferable projection error.
3.  **Weighting:** Apply inverse-variance weighting ($w_i = 1/\sigma^2_{i, \text{proj}}$) to down-weight unreliable markers.
4.  **Screening Design Choice:** Establish personalized-deviation noise floors ($NF_i$) that cancel out constant subject-specific projection offsets in the screening rules.
5.  **Empirical Confirmation:** Personalised baseline and digital twin demonstrations confirm that high-confidence markers (peak flexion) drive detection, while low-confidence markers (velocity) are gated.

### § Limitations of the Thesis as a Whole
*   **Cohort Size:** Small subject counts (9 squats, 7 lunges), which directly limits the applicability of deep sequence learning.
*   **Camera Count:** Sagittal-only monocular configuration makes contralateral occlusion a recurring limitation.
*   **Movement Breadth:** Evaluates only three exercise modalities; multi-planar athletic movements (cutting, pivoting) are deferred.
*   **Implementation Depth:** Track B personalisation components are architectural mockups utilizing repetition sequences, not clinically deployed longitudinal tracking.
*   **Clinical Standing:** Screening thresholds are grounded in cohort statistics and literature associations, **not** validated diagnostic diagnostic cut-offs (reiterating the screening-not-prediction guardrail).

### § Consolidated Future Work
*   **Dataset Expansion:** Integrating vertical jump trajectories (securing Bath BioCV dataset access).
*   **Longitudinal Baselines:** Collecting 10–14 sessions over multiple weeks to validate true longitudinal digital twin updates (ethics-gated; deferred due to timeframe limitations).
*   **Scale Representation Learning:** Implementing self-supervised pretraining once larger multi-subject cohorts are compiled, preventing the overfitting observed in Phase 12.
*   **Motion Validation:** Conducting ground-truth motion error validation for slow movements to transfer motion-based noise floors.
*   **Digital Twin Logic:** Implementing temporal persistence checks to distinguish transient aberrations from sustained shifts.

### § Closing Statement (Evolution Narrative)
*   **Thesis Claim:** A sensorless, markerless pipeline that extracts screening-relevant kinematic patterns, with validated, quantified monocular measurement uncertainty, and transparent, counterfactually explainable screening decisions.
*   **The Evolution Note:** The project was originally conceived as an injury-prediction system. However, empirical validation demonstrated that while the evidence could support robust, transparent **screening** of kinematics, it could not support predictive clinical claims. Matured into a validated screening framework, demonstrating scientific rigor and epistemic humility.

### § MUST-INCLUDE Flags
*   Format the **Failure-Mode Taxonomy** strictly as categorized failure types (Contribution #2).
*   State the **validation $\rightarrow$ uncertainty $\rightarrow$ weighting $\rightarrow$ screening** pipeline chain as a single cohesive methodological argument.
*   Link the **occlusion failure modes** in lunges and drop-jumps as a systematic monocular pattern.
*   Provide a clear, definitive statement on the **screening-not-prediction** guardrail.
*   Incorporate the **prediction-to-screening evolution narrative** as a strong concluding thesis-defense argument.

---

## CHAPTERS: Introduction, Abstract, Conclusion (write LAST — after everything else is drafted)

### § Introduction
*   **Opening:** Address the clinical assessment gap in sports biomechanics. Existing laboratory-grade methods (3D motion capture, force plates) do not scale for high-throughput athletic screening. Monocular, sensorless, markerless video pose estimation represents a scale opportunity but lacks integrated, transparent error-characterization.
*   **The Thesis Claim (PARAGRAPH ONE boundary):** Define the scope immediately as a **screening framework** that characterizes movement deviations associated with loading and risk in literature. State explicitly that it is **not** an injury prediction system or a clinical diagnostic tool.
*   **Scope:** Focuses on three athletic exercises (bilateral squat, unilateral lunge, dynamic drop-jump) utilizing a single, consumer-grade sagittal camera validated against 3D optoelectronic and force ground truth.
*   **Preview of the Four Contributions:** 
    1.  *Cross-exercise integration:* Modality-independent pose extraction pipeline.
    2.  *Failure-mode taxonomy:* Mapping systematic geometric and occlusion failure points.
    3.  *Uncertainty-weighted transfer:* Transferring validated measurement boundaries to qualify screening decisions.
    4.  *Counterfactual XAI:* Providing exact-margin, faithful-by-construction explanations for rule decisions.
*   **Evolution Seed:** Mention briefly in the introduction that this work began as an attempt to build a machine-learning-based injury *prediction* model but was systematically scoped to a validated *screening* framework once measurement uncertainty bounds were quantified. This establishes the narrative thread early.

### § Abstract (Write ABSOLUTELY last)
*   *Length:* $\approx 250\text{--}300$ words.
*   *Context:* The sports screening scalability gap and the opportunity of consumer video.
*   *Method:* Monocular markerless pipeline tested across squats, lunges, and drop-jumps, validated against laboratory ground truth.
*   *Headline Numbers (MUST RE-VERIFY AT POLISH):*
    *   *Validation:* Peak landing overestimation bias of $+10.52^\circ$ (timing-clean) vs. peak-to-peak bias of $+19.72^\circ$ (containing temporal overshoot); contact underestimation bias of $-6.69^\circ$. Decomposed projection-based noise floors (peak flexion $\pm 11.99^\circ$, ROM $\pm 23.17^\circ$, velocity $\pm 40.86^\circ/\text{s}$).
    *   *Exercise Findings:* Squats show descent-phase-only form discrimination ($d = 1.7306$ peak, $d = -1.4484$ ROM), whereas lunges show both descent and Concentric Ascent propulsion divergence ($d = -0.9721$ peak ascent velocity).
    *   *Explainability & Modeling:* Explainability is exact-margin faithful. Temporal sequence modeling (LSTM) overfits at this scale, reverting to guessing ($50.00\%$ balanced accuracy) when amplitude is stripped, whereas simple peak flexion baseline achieves $81.36\%$ balanced accuracy.
*   *Honesty Guardrails:* Emphasize the screening-not-prediction stance, the small analytical cohorts ($N=9$ squats, $N=7$ lunges), and the Track B status of the baseline/twin updates.
*   *Contribution:* Deliver a sensorless screening spine grounded in validated measurement uncertainty and faithful explainability.

### § Conclusion
*   **Thesis Claim:** Restate clearly that the thesis delivers a sensorless screening framework with validated, quantified measurement uncertainty boundaries and faithful explainability, not a diagnostic or prognostic injury classifier.
*   **Chapter Summaries:** One paragraph summarizing the findings of the Drop-Jump validation (systematic overestimation offset), one for the Squat (descent-localized deviations), one for the Lunge (propulsive ascent divergence), and one for the explainability/temporal modeling (endpoint dominance and LSTM data-scale mismatch).
*   **Delivered Contributions:** Summarize the four contributions.
*   **Consolidated Future Work:** Condense the future work items: vertical jump trajectory integration (Bath BioCV), multi-session longitudinal baselines, scale pretraining on large cohorts, motion-component error validation for slow movements, and twin temporal persistence logic.
*   **Closing Reflection (The Evolution Narrative Payoff):** Conclude with the reflection on the project's evolution. Transitioning from injury prediction to validated screening is framed as a maturation of the scientific contribution—recognizing that clinical utility is best served by transparent, explainable bounds rather than ungrounded black-box risk projections.

### § MUST-INCLUDE Flags
*   **First-Paragraph Boundary:** The screening-not-prediction boundary must be stated explicitly in the very first paragraph of the introduction to set the reading posture.
*   **Evolution Narrative Mapping:** Plant the evolution seed in the introduction, and place the final reflective payoff **exclusively in the Conclusion** as a closing reflection (do not repeat it verbatim in the discussion chapter).
*   **Abstract Number Audit:** Flag all abstract numbers for independent verification against raw CSV/manifest files at final polish to prevent copy-paste drift.










