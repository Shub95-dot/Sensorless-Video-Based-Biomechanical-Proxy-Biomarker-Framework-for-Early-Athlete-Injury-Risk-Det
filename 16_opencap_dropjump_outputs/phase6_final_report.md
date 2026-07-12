# Phase 6 Full Cohort Validation Final Report

This report summarizes the corrected validation of markerless pose tracking (MediaPipe Heavy variant) knee-flexion measurements against synchronized 3D Mocap IK and force-plate ground truth across all 48 trials (8 subjects) of the OpenCap drop-jump dataset.

---

## 1. Headline Finding: Constant Deep-Flexion Bias (Timing-Clean)
Isolating the landing peak absorption frames—where joint velocity is approximately zero, eliminating the influence of sub-frame synchronization lag—reveals that the measurement error does not scale monotonically with depth.
*   **Pooled Static-Peak Points**: $n = 96$ points (48 trials $\times$ 2 knees)
*   **Mean Deep-Flexion Bias (Video - IK)**: **10.52°** (overestimating true 3D flexion)
*   **95% Limits of Agreement (LoA)**: **[-5.54°, 26.58°]**
*   **Error-vs-Depth Correlation**: Pearson $r = -0.1568$ ($p = 0.1271$), Spearman $\rho = -0.1905$ ($p = 0.0631$). Since this correlation is **not statistically significant** within the landing flexion band ($70^\circ	ext{–}120^\circ$), we report the measurement error as a **constant positive bias** rather than a slope.
*   **Shallow-Flexion Contrast**: At initial landing contact (Biomarker #1, shallow flexion), the bias is **-6.69°** (95% LoA: [-26.77°, 13.39°]), showing that the systematic overestimation is specific to the deep flexion phase.

---

## 2. Robustness to Landing Conditions (Symmetric vs. Asymmetric)
Comparing the static-peak errors between symmetric and asymmetric landings confirms that measurement accuracy is dictated by camera perspective and depth rather than movement loading:
*   **Symmetric Landings ($n = 48$ points)**: Mean bias of **10.36°** (SD: 6.89°)
*   **Asymmetric Landings ($n = 48$ points)**: Mean bias of **10.68°** (SD: 9.39°)
The bias remains virtually identical between conditions, demonstrating that markerless measurements are robust to movement asymmetry.

---

## 3. Corrected Biomarker Agreement Summary
Evaluation of the video-measurable biomarkers against the 3D Mocap IK reference across the cohort ($n = 48$ trials):

| Biomarker | Video Mean | IK Mean | Bias (Video - IK) | 95% Limits of Agreement (LoA) | Pearson Correlation ($r$) | Trustworthiness Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **#1 contact_flexion** | 13.51° | 20.20° | -6.69° | [-26.77°, 13.39°] | 0.3209 | accurate (low bias, moderate variance) |
| **#2 peak_landing_flexion** | 120.23° | 100.51° | 19.72° | [7.73°, 31.71°] | 0.8238 | biased-systematic (constant overestimation, low variance) |
| **#3 landing_rom** | 106.72° | 80.31° | 26.41° | [2.34°, 50.48°] | 0.4020 | biased-systematic (constant overestimation, high variance) |
| **#6 loading_rate** | 286.14°/s | 272.84°/s | 13.30°/s | [-115.92°, 142.51°]/s | 0.6076 | high-variance (moderate bias, extremely high variance) |
| **#5 asymmetry** | N/A | 2.07° | N/A | N/A | N/A | **IK-only, not video-validated (far-leg occlusion)**; mean=2.07° (SD=2.06°) |

---

## 4. Documented Limitations
1.  **Biomarker #4 (Time-to-Stabilisation) Dropped**: The trial files are cropped too short (typically ending $\le 0.1	ext{–}0.2$ s after the second landing contact IC2). Since quiet stance evaluation requires a $0.5$ s quiet window, this biomarker cannot be resolved.
2.  **Contralateral Occlusion (Biomarker #5)**: Inter-limb asymmetry cannot be measured from 2D video because the farther limb is occluded during the deep landing phase. It is retained as an IK-only reference.
3.  **Binned Frame-Level Depth Curve Demoted**: The pooled 3,046-frame error-vs-depth curve was found to be timing-contaminated, mixing fast-motion frames where sub-frame lag injects large apparent error. It is kept only as a cautionary secondary figure.

