import os
import re

v2_path = r'22_dissertation_writing/results_dropjump_validation_v2.md'
app_path = r'22_dissertation_writing/appendices/appendix_D_bland_altman_interpretation.md'
v1_path = r'22_dissertation_writing/results_dropjump_validation_v1.md'

os.makedirs(r'22_dissertation_writing/appendices', exist_ok=True)

v2_content = """# Chapter 6: Drop-Jump Validation (OpenCap)

This chapter presents ground-truth validation of the monocular camera pipeline (MediaPipe Heavy variant) on the OpenCap Drop-Jump dataset against synchronized 3D optoelectronic motion capture and force-plate ground truth [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## 6.1. Temporal Synchronization and Event Detection

Joint trajectories from video and 3D motion capture were aligned across 48 trials (24 symmetric, 24 asymmetric landings across 8 subjects) using Ground Reaction Force (GRF)-anchored lag alignment [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md].

### 6.1.1. Synchronization Methodology
The temporal anchor matched physical landing contact ($F_y > 20$ N) to kinematic flexion onset in video (local knee extension minimum) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Native sample rates:
*   Synced video frame rate: **60.0000 FPS** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   Optoelectronic Mocap IK sample rate: **100.0000 Hz** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   Force plate sample rate: **2000.0000 Hz** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

### 6.1.2. Biomarker Mapping
Biomechanical events were identified via force plate and kinematic thresholds:
1.  **Initial Contact (IC1)**: First frame where vertical GRF exceeded $20$ N [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
2.  **Peak Absorption (PA1)**: Frame containing maximum knee flexion between IC1 and takeoff (TO1) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
3.  **Takeoff (TO1)**: First frame where vertical GRF dropped below $10$ N after IC1 [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
4.  **Final Landing Contact (IC2)**: First frame where vertical GRF exceeded $20$ N post-flight [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

These events mapped to primary knee flexion biomarkers:
*   **Contact Flexion (Biomarker #1)**: Knee flexion angle at **IC1** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Peak Landing Flexion (Biomarker #2)**: Knee flexion angle at **PA1** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Landing Range of Motion (ROM) (Biomarker #3)**: Excursion $\\text{ROM} = \\text{PA1} - \\text{IC1}$ [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   **Flexion Loading Rate (Biomarker #6)**: Average angular velocity during early landing ($IC1 \\rightarrow \\text{early absorption}$) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

---

## 6.2. Headline Finding: Deep-Flexion Constant Bias (Timing-Clean)

Monocular measurement error does not scale monotonically with flexion depth across landing. Isolating static coordinate errors from dynamic synchronization lag, knee flexion was evaluated at peak absorption frames (PA1), where joint angular velocity is near zero ($\\omega \\approx 0$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.1. Static-Peak Error Analysis
Across $n = 96$ peak flexion points (48 trials $\\times$ 2 limbs) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]:
*   **Mean Deep-Flexion Bias (Video - IK)**: **$+10.52^\\circ$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **95% Limits of Agreement (LoA)**: **$[-5.54^\\circ, 26.58^\\circ]$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.2. Error-vs-Depth Correlation
To test if overestimation is depth-dependent within active landing ($70^\\circ\\text{--}120^\\circ$), correlations between 3D Mocap angle and error were evaluated:
*   Pearson correlation: $r = -0.1568$ ($p = 0.1271$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   Spearman correlation: $\\rho = -0.1905$ ($p = 0.0631$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

Because neither correlation was significant ($p > 0.05$), measurement error behaves as a **constant systematic positive bias** within the landing flexion band rather than a depth-dependent slope [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.2.3. Shallow Flexion Contrast
At initial contact (Biomarker #1, shallow flexion), the pipeline exhibits an underestimation bias of **$-6.69^\\circ$** [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This confirms systematic $+10.52^\\circ$ overestimation is specific to deep flexion, forming a static, correctable offset.

---

## 6.3. Per-Biomarker Agreement (Bland-Altman Analysis)

Bland-Altman statistics (mean bias, 95% LoA, Pearson $r$) across all $n = 48$ trials evaluate cohort agreement [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Table 6.1 summarizes metrics across validatable biomarkers.

### Table 6.1: Bland-Altman Agreement Summary for Knee Flexion Biomarkers ($n = 48$ trials)

| Biomarker | Video Mean | IK Mean | Bias (Video - IK) | 95% Limits of Agreement (LoA) | Pearson Correlation ($r$) | Trustworthiness Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1 Contact Flexion** | $13.51^\\circ$ | $20.20^\\circ$ | $-6.69^\\circ$ | $[-26.77^\\circ, 13.39^\\circ]$ | $0.3209$ | accurate (low bias, moderate variance) [source: phase6_agreement_final.csv] |
| **#2 Peak Landing Flexion** | $120.23^\\circ$ | $100.51^\\circ$ | $+19.72^\\circ$ | $[7.73^\\circ, 31.71^\\circ]$ | $0.8238$ | biased-systematic (constant overestimation, low variance) [source: phase6_agreement_final.csv] |
| **#3 Landing ROM** | $106.72^\\circ$ | $80.31^\\circ$ | $+26.41^\\circ$ | $[2.34^\\circ, 50.48^\\circ]$ | $0.4020$ | biased-systematic (constant overestimation, high variance) [source: phase6_agreement_final.csv] |
| **#6 Flexion Loading Rate** | $286.14^\\circ/\\text{s}$ | $272.84^\\circ/\\text{s}$ | $+13.30^\\circ/\\text{s}$ | $[-115.92^\\circ/\\text{s}, 142.51^\\circ/\\text{s}]$ | $0.6076$ | high-variance (moderate bias, high variance) [source: phase6_agreement_final.csv] |
| **#5 Asymmetry (IK-only)** | N/A | $2.07^\\circ$ | N/A | N/A | N/A | **IK-only, not video-validated (far-leg occlusion)**; mean=$2.07^\\circ$ (SD=$2.06^\\circ$) [source: phase6_agreement_final.csv] |

Across biomarkers, contact flexion (#1) achieves high accuracy with minor underestimation ($-6.69^\\circ$), whereas peak flexion (#2) and ROM (#3) carry systematic positive bias requiring calibration [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Loading rate (#6) exhibits high variance from sampling jitter, and asymmetry (#5) is restricted to 3D IK reference data due to contralateral limb occlusion [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. See Appendix D for detailed biomarker-level interpretation.

### 6.3.1. Peak-to-Peak vs. Timing-Clean Bias Reconciliation
A critical comparison emerges between the **$+10.52^\\circ$ timing-clean peak bias** (Section 6.2) and the **$+19.72^\\circ$ peak-to-peak bias** in Table 6.1 [source: 16_opencap_dropjump_outputs/phase6_final_report.md]:
*   *Timing-Clean peak bias ($+10.52^\\circ$)*: Frame-matched error at exact peak time ($t_{\\text{peak}}$) of reference 3D motion capture [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *Peak-to-Peak bias ($+19.72^\\circ$)*: Absolute maximum video trajectory value versus absolute maximum Mocap value, regardless of timing alignment [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. 

Because 2D pose estimators experience frame-rate limits and dynamic tracking overshoot during high-velocity impact landings, unaligned peak-to-peak comparison captures temporal overshoot, inflating apparent bias by $+9.20^\\circ$. For slower sagittal movements (squats, lunges) lacking impact velocities, this validation isolates the deep-flexion projection component ($\\sigma^2_{\\text{proj}}$), which the uncertainty-weighted framework (Chapter 8) transfers [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 6.4. Robustness to Movement Conditions

To evaluate whether tracking accuracy varies with movement loading, static peak flexion errors were compared between symmetric and asymmetric landings [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.4.1. Symmetric vs. Asymmetric Landing Bias
*   **Symmetric Landings ($n = 48$ points)**: Mean peak overestimation bias **$+10.36^\\circ$** (SD: $6.89^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
*   **Asymmetric Landings ($n = 48$ points)**: Mean peak overestimation bias **$+10.68^\\circ$** (SD: $9.39^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

### 6.4.2. Methodological Implications
The condition difference is negligible ($\\Delta 0.32^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This near-identical error distribution demonstrates measurement bias is independent of kinetic landing asymmetry. Operating as a stable measurement property rather than a kinetic confound, this bias can be treated as a constant, correctable offset in downstream screening [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## 6.5. Establishing the Bias Is Projection Error, Not Timing Artefact

To confirm peak overestimation represents spatial projection distortion rather than temporal synchronization artefact or software modeling mismatch, three diagnostic tests were conducted [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

### 6.5.1. Dynamic Lag Test
We tested whether temporal trajectory misalignment caused deep-flexion error:
*   *Frame-matched (GRF-aligned) MAE*: **$14.80^\\circ$** (RMSE: $15.53^\\circ$) [source: 16_opencap_dropjump_outputs/metadata/timing_vs_projection_error_comparison.json].
*   *Peak-matched MAE*: **$20.15^\\circ$** (RMSE: $20.98^\\circ$) [source: 16_opencap_dropjump_outputs/metadata/timing_vs_projection_error_comparison.json].

Forcing peak alignment worsened MAE by $5.35^\\circ$ and RMSE by $5.45^\\circ$ [source: 16_opencap_dropjump_outputs/metadata/timing_vs_projection_error_comparison.json]. This rules out timing lag: peak-alignment forces video overshoot to match Mocap peak, increasing error and confirming spatial projection origin.

### 6.5.2. Software Modeling Defect Test
To rule out coordinate mismatches between clinical OpenSim models and superficial marker geometry, we compared:
1.  OpenSim joint coordinates from inverse kinematics output [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
2.  Superficial 3-point marker trigonometric model (hip, knee, ankle) converted to clinical flexion [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

Mean offset between modeling definitions was **$1.64^\\circ$** (RMSE: $21.79^\\circ$ vs. $22.93^\\circ$ against video) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md], ruling out software definition mismatches as the source of $10.52^\\circ$ overestimation.

### 6.5.3. Sync Method Stability Analysis
Force-plate **GRF-anchored alignment** was compared against mathematical **RMSE-minimisation alignment**:
*   *subject2 DJ1*: GRF lag = **3.00 ms (0 frames)** vs. RMSE lag = **-33.33 ms (-2 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *subject2 DJAsym1*: GRF lag = **-241.17 ms (-14 frames)** vs. RMSE lag = **200.00 ms (12 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
*   *subject8 DJ1*: GRF lag = **-157.17 ms (-9 frames)** vs. RMSE lag = **33.33 ms (2 frames)** [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

Because Mocap IK windows are trimmed ($\\sim 1.0$ s), RMSE-minimization is unstable, choosing out-of-phase alignments (e.g., $+12$ frames, shifting video peak $0.4$ s before mocap peak) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Conversely, GRF anchoring directly anchors physical impact, remaining stable across trials. Thus, GRF anchoring was adopted as standard, and pooled frame-level error-vs-depth correlation ($r = 0.3491$, $n = 3046$ frames) [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md] was demoted to a cautionary supplementary figure.

Diagnostics confirm deep-flexion overestimation stems from **sagittal-plane projection foreshortening**: as the knee flexes deeply outside the orthogonal camera plane, 2D projection systematically inflates apparent knee flexion angle.

---

## 6.6. Limitations

Limitations of dataset recording and camera configuration are documented:

### 6.6.1. Dataset Recording Truncation (Stabilisation Time)
Dynamic stabilisation (Biomarker #4, Time-to-Stabilisation) could not be computed. Video recordings truncate **$0.05\\text{ s}$ to $0.2\\text{ s}$** after final landing contact (IC2) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Evaluating stabilisation requires a $0.5$ s quiet-stance window (30 frames at 60 FPS) with flexion standard deviation $< 1.5^\\circ$; short recording lengths render this check unfeasible [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. This represents raw dataset truncation rather than pipeline failure.

### 6.6.2. Contralateral Occlusion (Asymmetry)
Inter-limb asymmetry (Biomarker #5) cannot be resolved via monocular sagittal video. During deep landing absorption, the closer leg ($\\sim 100\\%$ tracking visibility) occludes the farther leg ($\\sim 0\\%$ visibility) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. As monocular tracking cannot resolve occluded joint landmarks, asymmetry is demoted to 3D Mocap reference data (Mocap mean: $2.07^\\circ$, SD: $2.06^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_agreement_final.csv] and excluded from video decision rules.

### 6.6.3. Time-Series Pooling Warnings
Pooled frame-level error-vs-depth displays high timing contamination and non-monotonic behavior ($r = 0.3491$) [source: 16_opencap_dropjump_outputs/metadata/phase6_cohort_report.md]. It serves as a supplementary warning against naive time-series pooling in single-camera validation.

### 6.6.4. Kinematic Angle Conventions
This chapter evaluates knee flexion using **clinical flexion** ($0^\\circ$ = extension, larger angle = deeper bend) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md], contrasting with the **included angle** convention ($\\approx 180^\\circ$ = extension, smaller angle = deeper bend) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md] in squat and lunge chapters. Raw angles are not directly comparable; the uncertainty-weighting framework (Chapter 8) resolves this by transferring validated error variances ($\\sigma^2_{\\text{proj}}$) rather than raw joint values [source: 17_uncertainty_framework_outputs/framework_design.md].
"""

app_content = """# Appendix D: Bland-Altman Biomarker Interpretation

This appendix provides detailed biomarker-level interpretation for the Bland-Altman agreement analysis on the OpenCap drop-jump dataset ($n = 48$ trials across 8 subjects), supplementing Chapter 6 (Section 6.3) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.1. Biomarker #1: Contact Flexion
* **Metrics**: Video Mean = $13.51^\\circ$, IK Mean = $20.20^\\circ$, Bias = $-6.69^\\circ$, 95% LoA = $[-26.77^\\circ, 13.39^\\circ]$, Pearson $r = 0.3209$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Accurate (low bias, moderate variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Initial contact occurs at shallow flexion ($\\sim 20^\\circ$). In this upright pose, 2D sagittal plane foreshortening is minimal compared to deep flexion, yielding a small systematic underestimation bias of $-6.69^\\circ$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. However, ground impact induces transient pose tracking jitter, causing moderate trial variance ($\\text{LoA} \\text{ width} = 40.16^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.2. Biomarker #2: Peak Landing Flexion
* **Metrics**: Video Mean = $120.23^\\circ$, IK Mean = $100.51^\\circ$, Bias = $+19.72^\\circ$ (peak-to-peak) / $+10.52^\\circ$ (static timing-clean), 95% LoA = $[7.73^\\circ, 31.71^\\circ]$, Pearson $r = 0.8238$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Biased-systematic (constant overestimation, low variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Peak landing flexion exhibits a strong linear correlation ($r = 0.8238$) between video and 3D motion capture, demonstrating that monocular tracking reliably preserves rank order across subjects [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. The measurement exhibits a systematic positive bias ($+19.72^\\circ$ uncorrected peak-to-peak; $+10.52^\\circ$ timing-clean static frame) driven by out-of-plane projection foreshortening as the knee flexes deeply ($\\sim 100^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Because error distribution is tightly bounded with low residual variance, this bias represents a predictable geometric artefact suitable for downstream calibration [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.3. Biomarker #3: Landing Range of Motion (ROM)
* **Metrics**: Video Mean = $106.72^\\circ$, IK Mean = $80.31^\\circ$, Bias = $+26.41^\\circ$, 95% LoA = $[2.34^\\circ, 50.48^\\circ]$, Pearson $r = 0.4020$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Biased-systematic (constant overestimation, high variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Landing ROM is calculated as $\\text{ROM} = \\text{PA1} - \\text{IC1}$ [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because peak flexion (PA1) is systematically overestimated ($+19.72^\\circ$) while contact flexion (IC1) is systematically underestimated ($-6.69^\\circ$), these opposing directional biases compound mathematically ($\\Delta = +19.72^\\circ - (-6.69^\\circ) = +26.41^\\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This offset propagation increases measurement variance ($\\text{LoA} \\text{ width} = 48.14^\\circ$), making raw uncalibrated monocular ROM estimates unreliable without baseline offset correction [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.4. Biomarker #6: Flexion Loading Rate
* **Metrics**: Video Mean = $286.14^\\circ/\\text{s}$, IK Mean = $272.84^\\circ/\\text{s}$, Bias = $+13.30^\\circ/\\text{s}$, 95% LoA = $[-115.92^\\circ/\\text{s}, 142.51^\\circ/\\text{s}]$, Pearson $r = 0.6076$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: High-variance (moderate bias, extremely high variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Flexion loading rate quantifies average angular velocity during early landing absorption ($IC1 \\rightarrow \\text{early absorption}$) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Although cohort mean velocity bias is small ($+13.30^\\circ/\\text{s}$), 95% limits of agreement span $258.43^\\circ/\\text{s}$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. High variance stems from sub-frame sampling differences between 60 FPS video and reference signals (100 Hz Mocap / 2000 Hz force plates), combined with numerical differentiation noise during rapid landing deceleration [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

---

## D.5. Biomarker #5: Inter-Limb Asymmetry
* **Metrics**: IK Mean = $2.07^\\circ$ (SD = $2.06^\\circ$); Video measurement = N/A [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: IK-only, not video-validated (far-leg contralateral occlusion) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Inter-limb asymmetry evaluates bilateral peak flexion differences [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. In single-camera sagittal video recordings, the ipsilateral (closer) limb maintains $\\sim 100\\%$ landmark tracking visibility, whereas the contralateral (farther) limb drops to $\\sim 0\\%$ visibility during deep landing absorption due to self-occlusion [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because monocular tracking cannot resolve occluded landmarks, asymmetry is demoted to a 3D Mocap IK reference metric and excluded from video-only evaluation rules [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
"""

with open(v2_path, 'w', encoding='utf-8') as f:
    f.write(v2_content)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

with open(v1_path, 'r', encoding='utf-8') as f:
    v1_content = f.read()

v1_wc = len(v1_content.split())
v2_wc = len(v2_content.split())
app_wc = len(app_content.split())

print(f"V1 Word Count: {v1_wc}")
print(f"V2 Word Count: {v2_wc} (Target: 1400-1600)")
print(f"Appendix Word Count: {app_wc} (Target: 400-600)")

required_numbers = [
    '10.52', '-5.54', '26.58',
    '-0.1568', '0.1271', '-0.1905', '0.0631',
    '-6.69', '10.36', '10.68', '0.32',
    '14.80', '15.53', '20.15', '20.98', '5.35', '5.45',
    '1.64', '21.79', '22.93',
    '3.00', '-33.33', '-241.17', '200.00', '-157.17', '33.33',
    '0.3491', '3046',
    '19.72', '26.41', '13.30', '2.07', '2.06',
    '60.0000', '100.0000', '2000.0000'
]

missing_in_v2 = [num for num in required_numbers if num not in v2_content]
print("Missing numbers in v2:", missing_in_v2)

v1_sources = set(re.findall(r'\[source:[^\]]+\]', v1_content))
v2_sources = set(re.findall(r'\[source:[^\]]+\]', v2_content))
app_sources = set(re.findall(r'\[source:[^\]]+\]', app_content))

print("v1 unique sources count:", len(v1_sources))
print("v2 unique sources count:", len(v2_sources))
print("Appendix unique sources count:", len(app_sources))
print("Combined sources missing from v1:", v1_sources - (v2_sources | app_sources))
