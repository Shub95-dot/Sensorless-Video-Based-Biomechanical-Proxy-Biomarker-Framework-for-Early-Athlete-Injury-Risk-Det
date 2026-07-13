# Chapter 8: Uncertainty-Weighted Screening Framework

This chapter presents the design and demonstration of an uncertainty-weighted kinematic screening framework. Markerless pose-estimation pipelines capture multi-joint kinematics across several exercises, but the measurement accuracy of individual joint angle biomarkers is unequal. To address this, we present an architectural framework that weights each screening biomarker inversely proportional to its ground-truth-validated measurement uncertainty. First, we outline the purpose and design motivation of the framework. Second, we convert the drop-jump limits of agreement (LoA) validated in Chapter 6 into statistical variances. Third, we describe the projection/motion error decomposition that isolates geometry-general perspective errors from drop-jump-specific timing sensitivity. Fourth, we apply the inverse-variance weighting scheme to establish cohort and cross-exercise transfer weights. Finally, we illustrate the framework's behavior through worked examples in squats and lunges.

---

## 8.1. Purpose and Design Motivation

Monocular, single-camera biomechanical screening offers significant scalability advantages over marker-based laboratory systems. However, single-camera tracking is subject to several source-level error components—including perspective foreshortening, self-occlusion, sub-frame synchronization mismatch, and motion blur. In Chapter 6, we conducted a rigorous validation pass comparing monocular video-derived drop-jump biomarkers against 3D optical motion capture ground truth, establishing the 95% Limits of Agreement (LoA) for each metric [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

The primary motivation of this chapter is to convert those validated measurement error bounds into a per-biomarker weighting scheme that qualifies how much to trust each joint angle metric during multi-exercise screening. Rather than treating all extracted joint angles with equal confidence, the screening framework propagates these validated uncertainties to the squat and lunge evaluations discussed in Chapters 4 and 5.

### 8.1.1. Hard Architectural Constraints and Scope
To prevent misinterpretation, we establish several strict scope boundaries for this framework:
1.  **No Risk Scoring**: The framework does not calculate a risk index, injury likelihood, or predict any clinical outcome. It is strictly an architectural characterisation of measurement uncertainty.
2.  **No Repetition Classification**: It does not classify individual repetitions or label movement as "good" or "bad".
3.  **Architectural Demonstration Only**: It is a design demonstration showing how validated measurement uncertainties can be mathematically propagated across exercises. It is not a deployed clinical software system.

---

## 8.2. Uncertainty Source and Variance Conversion

The source of truth for the measurement uncertainty is the drop-jump cohort validation agreement table ([phase6_agreement_final.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv)), which validated $n = 48$ drop-jump trials across $9$ subjects [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv].

### 8.2.1. Mathematical Conversion Formula
To convert the 95% limits of agreement (LoA) bounds into a statistical variance, we assume a normal distribution of measurement errors. Under normality, the width of the 95% limits of agreement corresponds to $2 \times 1.96 = 3.92$ standard deviations (SDs) of the error distribution:
$$\text{SD} = \frac{\text{LoA}_{\text{upper}} - \text{LoA}_{\text{lower}}}{3.92}$$
$$\text{Variance } (\sigma^2_{\text{total}}) = \text{SD}^2$$

### 8.2.2. Converted Biomarker Variances
Applying this conversion formula to the validated drop-jump biomarkers yields the following statistical variances [source: 17_uncertainty_framework_outputs/framework_design.md]:

1.  **#1 contact_flexion**:
    *   *95% LoA*: $[-26.7742^\circ, 13.3913^\circ]$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
    *   *LoA Width*: $40.1655^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Standard Deviation (SD)*: $10.2463^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Variance ($\sigma^2_{\text{total}}$)*: **$104.9867$** [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Bias*: $-6.6914^\circ$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
2.  **#2 peak_landing_flexion**:
    *   *95% LoA*: $[7.7285^\circ, 31.7057^\circ]$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
    *   *LoA Width*: $23.9772^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Standard Deviation (SD)*: $6.1166^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Variance ($\sigma^2_{\text{total}}$)*: **$37.4132$** [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Bias*: $+19.7171^\circ$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
3.  **#3 landing_rom**:
    *   *95% LoA*: $[2.3373^\circ, 50.4798^\circ]$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
    *   *LoA Width*: $48.1425^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Standard Deviation (SD)*: $12.2813^\circ$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Variance ($\sigma^2_{\text{total}}$)*: **$150.8291$** [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Bias*: $+26.4086^\circ$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
4.  **#6 loading_rate**:
    *   *95% LoA*: $[-115.9179^\circ/\text{s}, 142.5125^\circ/\text{s}]$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
    *   *LoA Width*: $258.4304^\circ/\text{s}$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Standard Deviation (SD)*: $65.9261^\circ/\text{s}$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Variance ($\sigma^2_{\text{total}}$)*: **$4346.2534$** [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Bias*: $+13.2973^\circ/\text{s}$ [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]

### 8.2.3. Exclusion of Asymmetry
Biomarker #5 (landing asymmetry) is a 3D-only reference. As established in Chapter 6, monocular sagittal-plane video is subject to complete contralateral occlusion of the far limb during a drop-jump landing, making it impossible to validate video-derived bilateral asymmetry against motion capture ground truth [source: 22_dissertation_writing/results_dropjump_validation_v1.md]. Because no corresponding video measurement could be validated, this biomarker is excluded from the video-weighting framework [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 8.3. Projection/Motion Decomposition

To enable the transfer of validated drop-jump uncertainty bounds to other sagittal exercises, we decompose the total measurement variance ($\sigma^2_{\text{total}}$) into two distinct sources:
1.  **Projection Error ($\sigma^2_{\text{proj}}$)**: The systematic geometric component caused by 2D camera projection of out-of-plane joint motion. Because this component is dictated by perspective foreshortening, it is general to monocular sagittal pose estimation and transfers to any sagittal exercise where the knee flexes in plane (such as squats and lunges) [source: 17_uncertainty_framework_outputs/framework_design.md].
2.  **Motion Error ($\sigma^2_{\text{mot}}$)**: The dynamic timing-sensitivity component caused by sub-frame synchronization lag and motion blur. This is highly specific to the high-velocity, rapid-landing window of the drop-jump task and does not transfer to slow, controlled exercises like squats and lunges [source: 17_uncertainty_framework_outputs/framework_design.md].

$$\sigma^2_{\text{total}} = \sigma^2_{\text{proj}} + \sigma^2_{\text{mot}}$$

### 8.3.1. Derivation of Per-Biomarker Splits
To prevent mathematical contradictions, splits are derived individually for each biomarker based on the biomechanics of where in the movement it is measured [source: 17_uncertainty_framework_outputs/framework_design.md]:

*   **#2 peak_landing_flexion [MEASURED]**: Because Chapter 6 evaluated the peak flexion version using the peak-matched Method b (which aligns the video and motion capture peaks independently, removing any temporal synchronization lag), this variance represents a timing-clean measurement [source: 22_dissertation_writing/results_dropjump_validation_v1.md]. Thus, its total validated variance of $37.4132$ is purely projection-based [source: 17_uncertainty_framework_outputs/framework_design.md]:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$)*: **$37.4132$** ($100.0\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$)*: **$0.0000$** ($0.0\%$)
*   **#1 contact_flexion [ASSUMED split]**: This is measured at the instant of landing contact. Because the knee joint is near extension and its angular velocity is slow, sub-frame timing errors introduce minimal kinematic error. Thus, the contact flexion uncertainty is predominantly projection-based. We assume a $90\text{--}10$ split [source: 17_uncertainty_framework_outputs/framework_design.md]:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$)*: **$94.4880$** ($90.0\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$)*: **$10.4987$** ($10.0\%$)
*   **#6 loading_rate [ASSUMED split]**: This is calculated as an average velocity over a very fast landing window (from contact to peak flexion). Because it is highly sensitive to sub-frame contact time errors, it is dominated by motion/timing sensitivity. We assume a $10\text{--}90$ split [source: 17_uncertainty_framework_outputs/framework_design.md]:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$)*: **$434.6253$** ($10.0\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$)*: **$3911.6281$** ($90.0\%$)
*   **#3 landing_rom [PROPAGATED split]**: Joint range of motion is calculated as $\text{ROM} = \text{peak\_flexion} - \text{contact\_flexion}$. We propagate its uncertainty from the peak (#2) and contact (#1) endpoints:
    *   *Propagated Projection*: $\sigma^2_{\text{proj, ROM}} = \sigma^2_{\text{proj, peak}} + \sigma^2_{\text{proj, contact}} = 37.4132 + 94.4880 = 131.9012$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Propagated Motion*: $\sigma^2_{\text{mot, ROM}} = \sigma^2_{\text{mot, peak}} + \sigma^2_{\text{mot, contact}} = 0.0000 + 10.4987 = 10.4987$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    *   *Total Propagated*: $142.4000$ [source: 17_uncertainty_framework_outputs/framework_design.md]
    
    To reconcile exactly with the observed total variance ($150.8291$), we scale the propagated components proportionally to sum to the observed total (maintaining a $92.62\%$ projection and $7.38\%$ motion split) [source: 17_uncertainty_framework_outputs/framework_design.md]:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$)*: **$139.7047$** ($92.62\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$)*: **$11.1244$** ($7.38\%$)

### 8.3.2. Sensitivity Analysis of Assumed Splits
Because the splits for contact flexion and loading rate are assumed based on biomechanical principles rather than direct empirical measurement, we conducted a 9-configuration sensitivity sweep [source: 17_uncertainty_framework_outputs/framework_design.md]. The contact split was varied between $90/10$, $80/20$, and $70/30$, while the loading rate split was varied between $10/90$, $20/80$, and $5/95$ [source: 17_uncertainty_framework_outputs/framework_design.md].

The sensitivity analysis demonstrated that:
*   **Complete Stability of the Hierarchy**: Across all 9 varied configurations, the dominance hierarchy remained completely stable: Peak Flexion ($\sim 50\text{--}59\%$) > Start Flexion ($\sim 21\text{--}27\%$) > ROM ($\sim 14\text{--}17\%$) > Joint Velocity ($\sim 2\text{--}9\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
*   **Immateriality of the Assumed Splits**: The resulting cross-exercise transfer weights varied by less than $8.6\%$ [source: 17_uncertainty_framework_outputs/framework_design.md]. The loading rate's split had negligible impact because its high base variance filters out its weight to near-zero levels. This mathematical stability justifies the assumed splits as robust parameters for cross-exercise transfer.

---

## 8.4. Inverse-Variance Weighting & Validation Weights

To combine multiple measurements of unequal precision, we employ standard **inverse-variance weighting** [CITE: inverse_variance_weighting]. This represents the mathematically optimal way to aggregate independent measurements by minimizing the variance of the weighted combination:
$$w_i = \frac{1}{\sigma_{i, \text{total}}^2}$$
The normalized weight ($\bar{w}_i$) for each biomarker is:
$$\bar{w}_i = \frac{w_i}{\sum_j w_j}$$

### 8.4.1. Converted Drop-Jump Weights
Using the total validated drop-jump variances ($\sigma^2_{\text{total}}$), we calculate the raw weights [source: 17_uncertainty_framework_outputs/framework_design.md]:
*   $w_{\#1} = \frac{1}{104.9867} \approx 0.0095$
*   $w_{\#2} = \frac{1}{37.4132} \approx 0.0267$
*   $w_{\#3} = \frac{1}{150.8291} \approx 0.0066$
*   $w_{\#6} = \frac{1}{4346.2534} \approx 0.0002$
*   $\sum w_j = 0.0431$

Normalized, these values yield the following drop-jump validation weights [source: 17_uncertainty_framework_outputs/framework_design.md]:
1.  **Peak Flexion**: **$62.00\%$** (Dominates the static validation pass due to low peak-matched variance)
2.  **Contact Flexion**: **$22.09\%$**
3.  **Landing ROM**: **$15.38\%$**
4.  **Loading Rate**: **$0.53\%$** (Extremely low weight reflecting high dynamic variance)

---

## 5.5. Cross-Exercise Transfer

Slow, controlled athletic movements—such as squats and lunges—occur at low joint angular velocities. Consequently, dynamic timing jitter and motion blur ($\sigma^2_{\text{mot}}$) are biomechanically negligible. 

### 5.5.1. The Transfer Rule
When transferring uncertainty weights to squats and lunges, we use **only the transferable projection component** of uncertainty ($\sigma^2_{\text{proj}}$) derived from the drop-jump validation ground truth [source: 17_uncertainty_framework_outputs/framework_design.md]. The motion component is discarded:
$$w_{\text{proj}, i} = \frac{1}{\sigma^2_{\text{proj}, i}}$$

### 5.5.2. Biomarker Mapping Justification
This transfer relies on mapping the drop-jump biomarkers to their squat and lunge equivalents. These mappings are biomechanically grounded rather than merely name-matched [source: 17_uncertainty_framework_outputs/framework_design.md]:
*   **Drop-Jump `contact_flexion` $\leftrightarrow$ Squat/Lunge `start_flexion`**: Both are measured in the shallow-flexion regime (standing position or initial descent), where joint angles are near $180^\circ$ and perspective projection errors are minimal.
*   **Drop-Jump `loading_rate` $\leftrightarrow$ Squat/Lunge `descent_velocity`**: Both are velocity/rate metrics that capture the speed of flexion, converted to consistent units ($\circ/\text{s}$) by scaling frames by the video frame rate ($30$ frames per second).

### 5.5.3. Transferable Squat and Lunge Weights
Using the projection variances ($\sigma^2_{\text{proj}}$), we compute the transferable weights [source: 17_uncertainty_framework_outputs/framework_design.md]:
*   $w_{\text{proj}, \#1} = \frac{1}{94.4880} \approx 0.0106$
*   $w_{\text{proj}, \#2} = \frac{1}{37.4132} \approx 0.0267$
*   $w_{\text{proj}, \#3} = \frac{1}{139.7047} \approx 0.0072$
*   $w_{\text{proj}, \#6} = \frac{1}{434.6253} \approx 0.0023$
*   $\sum w_{\text{proj}} = 0.0468$

Normalized, the final cross-exercise weights applied to squats and lunges are [source: 17_uncertainty_framework_outputs/framework_design.md]:
1.  **Peak Flexion**: **$57.15\%$** (Dominates the screening characterisation)
2.  **Start Flexion**: **$22.63\%$**
3.  **Range of Motion (ROM)**: **$15.30\%$**
4.  **Joint Descent Velocity**: **$4.92\%$**

### 5.5.4. Documented Limitation
While this transfer isolates systematic projection error, it represents a design compromise. Because squats and lunges lack optical ground-truth motion capture validation in the REHAB24-6 dataset, the motion-error component of uncertainty for these slow exercises remains unvalidated and is flagged as a future-work item [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 5.6. Worked Example Demonstration

The application of the uncertainty-weighting framework was demonstrated using representative correct and incorrect reps from the REHAB24-6 squat and lunge datasets [source: 17_uncertainty_framework_outputs/worked_example.csv]:
*   **Squat Reps**: Sourced from subject `PM_008` (Subject 1) rep 2 (correct form) and rep 17 (incorrect form) [source: 17_uncertainty_framework_outputs/worked_example.csv].
*   **Lunge Reps**: Sourced from subject `PM_021` (Subject 2) rep 2 (correct form) and rep 7 (incorrect form) [source: 17_uncertainty_framework_outputs/worked_example.csv].

### 5.6.1. Validated Uncertainty Bounds
For each biomarker, we calculate the $95\%$ confidence bounds around the raw video measurements using the transferable projection standard deviations ($\text{SD}_{\text{proj}} = \sqrt{\sigma^2_{\text{proj}}}$). The $95\%$ confidence interval half-widths are:
*   **`start_flexion` bounds**: $1.96 \times \sqrt{94.4880} = \pm 19.05^\circ$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`peak_flexion` bounds**: $1.96 \times \sqrt{37.4132} = \pm 11.99^\circ$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`rom` bounds**: $1.96 \times \sqrt{139.7047} = \pm 23.17^\circ$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`velocity` bounds**: $1.96 \times \sqrt{434.6253} = \pm 40.86^\circ/\text{s}$ [source: 17_uncertainty_framework_outputs/worked_example.csv]

These bounds represent the **pipeline's validated measurement uncertainty** (the measurement precision of the markerless system), which remains constant across repetitions by construction [source: 17_uncertainty_framework_outputs/framework_design.md]. They do not reflect the biomechanical variability of the subject's movement or the confidence in a specific repetition's execution.

### 5.6.2. Worked Example Data
Table 8.2 presents the raw video measurements alongside their validated uncertainty bounds and normalized weights for the selected repetitions [source: 17_uncertainty_framework_outputs/worked_example.csv]:

### Table 8.2: Worked Example Repetitions for Squat and Lunge Modalities

| Exercise | Video ID | Rep | Form | start_flexion ($^\circ$) | peak_flexion ($^\circ$) | rom ($^\circ$) | velocity ($^\circ$/s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Squat** | `PM_008` | 2 | Correct | $0.82^\circ \pm 19.05^\circ$ | $62.16^\circ \pm 11.99^\circ$ | $117.02^\circ \pm 23.17^\circ$ | $58.51^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Squat** | `PM_008` | 17 | Incorrect | $2.23^\circ \pm 19.05^\circ$ | $50.03^\circ \pm 11.99^\circ$ | $127.73^\circ \pm 23.17^\circ$ | $105.18^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Lunge** | `PM_021` | 2 | Correct | $21.42^\circ \pm 19.05^\circ$ | $83.53^\circ \pm 11.99^\circ$ | $75.05^\circ \pm 23.17^\circ$ | $27.12^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Lunge** | `PM_021` | 7 | Incorrect | $18.51^\circ \pm 19.05^\circ$ | $54.65^\circ \pm 11.99^\circ$ | $106.84^\circ \pm 23.17^\circ$ | $69.57^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |

This demonstration highlights how the framework down-weights joint velocity (weight $= 4.92\%$) relative to peak flexion depth (weight $= 57.15\%$). During screening, peak depth deviations are characterized with high confidence (narrower relative CI width of $\pm 11.99^\circ$), whereas joint velocity deviations are treated with high uncertainty (broader relative CI width of $\pm 40.86^\circ/\text{s}$), reflecting the higher error bounds validated in the ground-truth comparison.

---

## 8.7. What This Framework Does NOT Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of the framework:
*   **No Diagnostic Claims**: The framework does not predict ACL injury, patellofemoral pain, or any musculoskeletal pathology.
*   **No Injury Risk Scoring**: It does not synthesize the weighted biomarkers into a singular "risk score" or hazard ratio.
*   **No Repetition Classification**: It does not classify reps as "failed" or "passed" based on the uncertainty bounds.
*   **No Validation of Squat/Lunge Motion Error**: It does not assert that squat and lunge motion error is validated. Motion error validation remains a future-work item.
*   **Methodological Demonstration Only**: The worked examples illustrate how uncertainty weights affect the interpretation of kinematic screening profiles, rather than representing a clinical diagnostic system.
