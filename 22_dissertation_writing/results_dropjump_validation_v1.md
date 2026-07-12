# Chapter 6: Drop-Jump Validation (OpenCap)

This chapter presents the results of the ground-truth validation pass executed on the OpenCap Drop-Jump landing dataset [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. The primary objective is to establish the physical measurement accuracy of the monocular camera pipeline (MediaPipe Heavy variant) against synchronized 3D optoelectronic motion capture and force-plate ground truth under dynamic, high-velocity movement conditions.

---

## 6.1. Temporal Synchronization and Event Detection

To ensure rigorous kinematic comparisons, continuous joint trajectories from standard video and 3D motion capture were temporally aligned. All 48 processed trials (comprising 24 symmetric and 24 asymmetric landing trials across 8 subjects) utilized Ground Reaction Force (GRF)-anchored lag alignment [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md].

### 6.1.1. Synchronization Methodology
The temporal synchronization anchor was defined by matching the physical landing contact event—measured at the instant the vertical ground reaction force ($F_y$) exceeded a threshold of $20$ N on the force plates—to the kinematic onset of landing flexion in the video profile, which corresponds to the local knee extension minimum [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. The data streams were captured at their native sample rates:
*   Synced video frame rate: **60.0000 FPS** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   Optoelectronic Mocap IK sample rate: **100.0000 Hz** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   Force plate sample rate: **2000.0000 Hz** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

### 6.1.2. Biomarker Mapping
Following temporal alignment, discrete biomechanical events were identified using combined force plate and kinematic velocity thresholds:
1.  **Initial Contact (IC1)**: The first frame where vertical GRF exceeded $20$ N [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
2.  **Peak Absorption (PA1)**: The frame containing the maximum knee flexion angle reached between initial contact (IC1) and takeoff (TO1) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
3.  **Takeoff (TO1)**: The first frame where vertical GRF dropped below $10$ N after IC1 [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
4.  **Final Landing Contact (IC2)**: The first frame where vertical GRF exceeded $20$ N following the jump flight phase [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

These events mapped directly to the primary knee flexion biomarkers:
*   **Contact Flexion (Biomarker #1)**: Knee flexion angle at **IC1** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Peak Landing Flexion (Biomarker #2)**: Knee flexion angle at **PA1** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Landing Range of Motion (ROM) (Biomarker #3)**: The angular excursion computed as $\text{ROM} = \text{PA1} - \text{IC1}$ [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Flexion Loading Rate (Biomarker #6)**: The average angular velocity of knee flexion during the early landing phase ($IC1 \rightarrow \text{early absorption}$) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

---

## 6.2. Headline Finding: Deep-Flexion Constant Bias (Timing-Clean)

A key finding of this validation is that the monocular measurement error does not scale monotonically with flexion depth across the landing phase. To isolate static coordinate measurement errors from dynamic temporal synchronization lag, we analyzed knee flexion values strictly at the peak landing absorption frames (PA1), where joint angular velocity is approximately zero ($\omega \approx 0$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.1. Static-Peak Error Analysis
This timing-clean analysis was performed across $n = 96$ peak flexion values (48 trials $\times$ 2 limbs) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]:
*   **Mean Deep-Flexion Bias (Video - IK)**: **$+10.52^\circ$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **95% Limits of Agreement (LoA)**: **$[-5.54^\circ, 26.58^\circ]$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.2. Error-vs-Depth Correlation
To determine if this systematic overestimation is depth-dependent within the active landing window ($70^\circ\text{--}120^\circ$ of flexion), we ran two correlation tests between the true 3D Mocap joint angle and the corresponding measurement error:
*   Pearson product-moment correlation: $r = -0.1568$ ($p = 0.1271$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   Spearman rank correlation: $\rho = -0.1905$ ($p = 0.0631$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

Because neither correlation was statistically significant ($p > 0.05$), the measurement error behaves as a **constant systematic positive bias** within the landing flexion band rather than a depth-dependent slope [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.3. Shallow flexion Contrast
In contrast to the deep overestimation, at initial contact (Biomarker #1, shallow flexion), the monocular pipeline exhibits an underestimation bias of **$-6.69^\circ$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This confirms that the systematic $+10.52^\circ$ overestimation is specific to the deep flexion range, representing a static, correctable geometric offset.

---

## 6.3. Per-Biomarker Agreement (Bland-Altman Analysis)

To evaluate the overall cohort agreement, Bland-Altman statistics (mean bias, 95% Limits of Agreement, and Pearson correlation coefficients) were calculated across all $n = 48$ trials [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Table 6.1 summarizes the agreement metrics.

### Table 6.1: Bland-Altman Agreement Summary for Knee Flexion Biomarkers ($n = 48$ trials)

| Biomarker | Video Mean | IK Mean | Bias (Video - IK) | 95% Limits of Agreement (LoA) | Pearson Correlation ($r$) | Trustworthiness Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1 Contact Flexion** | $13.51^\circ$ | $20.20^\circ$ | $-6.69^\circ$ | $[-26.77^\circ, 13.39^\circ]$ | $0.3209$ | accurate (low bias, moderate variance) [source: phase6_agreement_final.csv] |
| **#2 Peak Landing Flexion** | $120.23^\circ$ | $100.51^\circ$ | $+19.72^\circ$ | $[7.73^\circ, 31.71^\circ]$ | $0.8238$ | biased-systematic (constant overestimation, low variance) [source: phase6_agreement_final.csv] |
| **#3 Landing ROM** | $106.72^\circ$ | $80.31^\circ$ | $+26.41^\circ$ | $[2.34^\circ, 50.48^\circ]$ | $0.4020$ | biased-systematic (constant overestimation, high variance) [source: phase6_agreement_final.csv] |
| **#6 Flexion Loading Rate** | $286.14^\circ/\text{s}$ | $272.84^\circ/\text{s}$ | $+13.30^\circ/\text{s}$ | $[-115.92^\circ/\text{s}, 142.51^\circ/\text{s}]$ | $0.6076$ | high-variance (moderate bias, extremely high variance) [source: phase6_agreement_final.csv] |
| **#5 Asymmetry (IK-only)** | N/A | $2.07^\circ$ | N/A | N/A | N/A | **IK-only, not video-validated (far-leg occlusion)**; mean=$2.07^\circ$ (SD=$2.06^\circ$) [source: phase6_agreement_final.csv] |

### 6.3.1. Peak-to-Peak vs. Timing-Clean Bias Reconciliation
A critical comparison emerges between the **$+10.52^\circ$ timing-clean peak bias** (reported in Section 6.2) and the **$+19.72^\circ$ peak-to-peak bias** reported in Table 6.1 [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   *Timing-Clean peak bias ($+10.52^\circ$)*: Evaluates the frame-matched error at the exact peak time ($t_{\text{peak}}$) of the reference 3D motion capture signal [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *Peak-to-Peak bias ($+19.72^\circ$)*: Compares the absolute maximum value of the video trajectory to the absolute maximum of the Mocap trajectory, regardless of timing alignment [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. 

Because monocular 2D pose estimators are subject to frame-rate limitations and dynamic joint-tracking overshoot during high-velocity impact landings, the peak-to-peak method captures this temporal overshoot, inflating the apparent measurement bias by $+9.20^\circ$. For slower, controlled sagittal movements (squats, lunges) where landing impact velocities are absent, the timing-clean peak bias of $+10.52^\circ$ represents the transferable projection coordinate error [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 6.4. Robustness to Movement Conditions

To determine whether tracking accuracy is affected by movement loading patterns, we stratified and compared the static peak flexion errors between symmetric and asymmetric landing trials [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.4.1. Symmetric vs. Asymmetric Landing Bias
*   **Symmetric Landings ($n = 48$ points)**: Mean peak overestimation bias of **$+10.36^\circ$** (SD: $6.89^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Asymmetric Landings ($n = 48$ points)**: Mean peak overestimation bias of **$+10.68^\circ$** (SD: $9.39^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.4.2. Methodological Implications
The difference between the two conditions is negligible ($\Delta 0.32^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This near-identical error distribution demonstrates that the measurement bias is independent of physical movement loading or landing asymmetry. Instead, the error is driven by camera placement and perspective projection geometry (sagittal-view camera profile). Because the bias behaves as a stable property of the measurement method rather than a kinetic confound, it can be treated as a constant, correctable offset in downstream screening layers [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## 6.5. Establishing the Bias Is Projection Error, Not Timing Artefact

To confirm that the peak overestimation represents a genuine spatial projection distortion rather than a temporal synchronization artefact or software modeling mismatch, three diagnostic tests were conducted [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

### 6.5.1. Dynamic Lag Test
We evaluated whether temporal misalignment between the video and Mocap trajectories caused the deep-flexion error. If timing lag were the primary source of error, aligning the peak frames of the two signals (peak-matching) should reduce disagreement:
*   *Frame-matched (GRF-aligned) Mean Absolute Error (MAE)*: **$14.80^\circ$** (RMSE: $15.53^\circ$) [source: 11_scripts/phase6_timing_vs_projection_diagnostics.py task-73 output].
*   *Peak-matched Mean Absolute Error (MAE)*: **$20.15^\circ$** (RMSE: $20.98^\circ$) [source: 11_scripts/phase6_timing_vs_projection_diagnostics.py task-73 output].

Artificially forcing peak alignment worsened the MAE by $5.35^\circ$ and increased the RMSE by $5.45^\circ$ [source: 11_scripts/phase6_timing_vs_projection_diagnostics.py task-73 output]. This result rules out timing lag as the cause of peak overestimation: peak-alignment forces the video's dynamic overshoot to match the Mocap peak, increasing the overall trajectory error and confirming that the overestimation is spatial in origin.

### 6.5.2. Software Modeling Defect Test
To rule out coordinate definition mismatches between the clinical OpenSim anatomical model and superficial marker geometry, we compared:
1.  OpenSim joint coordinates read directly from the inverse kinematics output file [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
2.  A superficial 3-point marker trigonometric model computed from the hip, knee, and ankle markers, converted to clinical flexion [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

The mean offset between the two modeling definitions was **$1.64^\circ$** (RMSE: $21.79^\circ$ vs. $22.93^\circ$ against video) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. This negligible modeling difference rules out software definition mismatches as the source of the $10.52^\circ$ overestimation.

### 6.5.3. Sync Method Stability Analysis
We compared the stability of the force-plate-based **GRF-anchored alignment** against a mathematical **RMSE-minimisation alignment** (which shifts the video timeline to minimize squared difference):
*   *subject2 DJ1*: GRF lag = **3.00 ms (0 frames)** vs. RMSE lag = **-33.33 ms (-2 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *subject2 DJAsym1*: GRF lag = **-191.17 ms (-11 frames)** vs. RMSE lag = **200.00 ms (12 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *subject8 DJ1*: GRF lag = **-157.17 ms (-9 frames)** vs. RMSE lag = **33.33 ms (2 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

Because the Mocap IK dataset is trimmed to a short window ($\sim 1.0$ s), the RMSE-minimization method is highly unstable, choosing out-of-phase alignments (e.g., $+12$ frames, shifting the video peak $0.4$ s before the mocap peak) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. By contrast, GRF-anchoring directly anchors the physical impact event, remaining stable across all trials. Consequently, the GRF method was adopted as the validated standard, and the frame-level pooled trajectory error-vs-depth curve (Pearson $r = 0.3491$, $n = 3046$ frames) [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md] was demoted to a cautionary supplementary figure due to curve-fitting instabilities.

Collectively, these diagnostic checks confirm that the deep-flexion overestimation is caused by **sagittal-plane projection foreshortening**. As the knee flexes deeply and moves out of the camera's pure orthogonal plane, the 2D projection on the camera sensor systematically inflates the apparent knee flexion angle.

---

## 6.6. Limitations

Several limitations of the validation dataset and camera configuration must be documented:

### 6.6.1. Dataset Recording Truncation (Stabilisation Time)
The dynamic stabilisation biomarker (Biomarker #4, Time-to-Stabilisation) could not be computed. The video recordings in this dataset truncate abruptly between **$0.05\text{ s}$ and $0.2\text{ s}$** after the final landing contact (IC2) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because evaluating movement stabilisation requires a $0.5$ s quiet-stance window (30 frames at 60 FPS) to confirm the standard deviation remains $< 1.5^\circ$, the short trial lengths make this check mathematically impossible [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. This represents a data collection limit of the raw dataset, not an algorithmic pipeline failure.

### 6.6.2. Contralateral Occlusion (Asymmetry)
Inter-limb asymmetry (Biomarker #5) cannot be resolved via monocular sagittal video. During the deep landing absorption phase, the closer leg (with $\sim 100\%$ tracking visibility) completely occludes the farther leg, reducing its visibility to $\sim 0\%$ [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because monocular tracking cannot resolve the occluded knee joint, inter-limb asymmetry is demoted to a 3D Mocap-only reference (Mocap mean: $2.07^\circ$, SD: $2.06^\circ$) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv] and excluded from the video-only decision rules.

### 6.6.3. Time-Series Pooling Warnings
The pooled frame-level error-vs-depth curve exhibits high timing-contamination and non-monotonic behavior, displaying a low correlation ($r = 0.3491$) [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md]. It is demoted to a supplementary warning against naive time-series pooling in single-camera validation.

### 6.6.4. Kinematic Angle Conventions
This chapter evaluates knee flexion angles using the **clinical flexion** convention ($0^\circ$ = standing extension, deeper bend = larger angle) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. This is the exact opposite of the **included angle** convention ($\approx 180^\circ$ = standing, deeper bend = smaller angle) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md] used in the squat and lunge chapters. Raw joint angle values are not directly comparable across chapters. The uncertainty-weighting framework (Chapter 8) resolves this discrepancy by transferring validated error variances ($\sigma^2_{\text{proj}}$) rather than raw joint values [source: 17_uncertainty_framework_outputs/framework_design.md].
