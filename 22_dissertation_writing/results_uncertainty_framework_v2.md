# Chapter 8: Uncertainty-Weighted Screening Framework

This chapter presents the design and demonstration of an uncertainty-weighted kinematic screening framework. Markerless pose-estimation pipelines capture multi-joint kinematics across several exercises, but measurement accuracy across joint angle biomarkers is unequal. To address this, we present an architectural framework that weights each screening biomarker inversely proportional to its ground-truth-validated measurement uncertainty. First, we outline the purpose and design motivation. Second, we convert the drop-jump limits of agreement (LoA) validated in Chapter 6 into statistical variances. Third, we present the projection/motion error decomposition that isolates geometry-general perspective errors from drop-jump-specific timing sensitivity. Fourth, we apply inverse-variance weighting to establish cross-exercise transfer weights. Finally, we demonstrate the framework's behavior through worked examples in squats and lunges. The full mathematical derivation is provided in Appendix A.

---

## 8.1. Purpose and Design Motivation

Monocular, single-camera biomechanical screening offers significant scalability over marker-based laboratory systems. However, single-camera tracking is subject to several error components—including perspective foreshortening, self-occlusion, sub-frame synchronization mismatch, and motion blur. In Chapter 6, we conducted a ground-truth validation pass comparing monocular video-derived drop-jump biomarkers against 3D optical motion capture, establishing the 95% Limits of Agreement (LoA) for each metric [source: 22_dissertation_writing/results_dropjump_validation_v1.md].

The primary motivation of this chapter is converting those validated measurement error bounds into a per-biomarker weighting scheme that qualifies how much to trust each joint angle metric during multi-exercise screening. Rather than treating all extracted joint angles with equal confidence, the screening framework propagates these validated uncertainties to the squat and lunge evaluations discussed in Chapters 4 and 5.

### 8.1.1. Hard Architectural Constraints and Scope
To prevent misinterpretation, we establish strict scope boundaries for this framework:
1.  **No Risk Scoring**: The framework does not calculate a risk index or predict clinical outcomes. It is strictly an architectural characterisation of measurement uncertainty.
2.  **No Repetition Classification**: It does not classify individual repetitions or label movement as "good" or "bad".
3.  **Architectural Demonstration Only**: It is a design demonstration showing how validated measurement uncertainties propagate across exercises, not a deployed clinical software system.

---

## 8.2. Uncertainty Source and Variance Conversion

The source of truth for measurement uncertainty is the drop-jump cohort validation agreement table ([phase6_agreement_final.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv)), validating $n = 48$ drop-jump trials across $9$ subjects [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv].

### 8.2.1. Converted Biomarker Variances
Assuming normally distributed errors ($3.92 \text{ SD} = \text{LoA}_{\text{upper}} - \text{LoA}_{\text{lower}}$), validated drop-jump LoA bounds convert into the following statistical variances ($\sigma^2_{\text{total}}$) [source: 17_uncertainty_framework_outputs/framework_design.md]:

1.  **#1 contact_flexion**: 95% LoA $[-26.7742^\circ, 13.3913^\circ]$ (Width: $40.1655^\circ$, Bias: $-6.6914^\circ$) $\implies \text{SD} = 10.2463^\circ$, $\sigma^2_{\text{total}} = \mathbf{104.9867}$ [source: 17_uncertainty_framework_outputs/framework_design.md].
2.  **#2 peak_landing_flexion**: 95% LoA $[7.7285^\circ, 31.7057^\circ]$ (Width: $23.9772^\circ$, Bias: $+19.7171^\circ$) $\implies \text{SD} = 6.1166^\circ$, $\sigma^2_{\text{total}} = \mathbf{37.4132}$ [source: 17_uncertainty_framework_outputs/framework_design.md].
3.  **#3 landing_rom**: 95% LoA $[2.3373^\circ, 50.4798^\circ]$ (Width: $48.1425^\circ$, Bias: $+26.4086^\circ$) $\implies \text{SD} = 12.2813^\circ$, $\sigma^2_{\text{total}} = \mathbf{150.8291}$ [source: 17_uncertainty_framework_outputs/framework_design.md].
4.  **#6 loading_rate**: 95% LoA $[-115.9179^\circ/\text{s}, 142.5125^\circ/\text{s}]$ (Width: $258.4304^\circ/\text{s}$, Bias: $+13.2973^\circ/\text{s}$) $\implies \text{SD} = 65.9261^\circ/\text{s}$, $\sigma^2_{\text{total}} = \mathbf{4346.2534}$ [source: 17_uncertainty_framework_outputs/framework_design.md].

### 8.2.2. Exclusion of Asymmetry
Biomarker #5 (landing asymmetry) is a 3D-only reference metric. Monocular sagittal video suffers complete contralateral occlusion of the far leg during deep landing absorption, precluding ground-truth validation against motion capture [source: 22_dissertation_writing/results_dropjump_validation_v1.md]. It is therefore excluded from the video uncertainty framework [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 8.3. Projection/Motion Error Decomposition

To transfer validated drop-jump uncertainty bounds to other sagittal movements, we decompose total measurement variance ($\sigma^2_{\text{total}}$) into two underlying components [source: 17_uncertainty_framework_outputs/framework_design.md]:
$$\sigma^2_{\text{total}} = \sigma^2_{\text{proj}} + \sigma^2_{\text{mot}}$$

### 8.3.1. Rationale for Variance Splitting
The physical rationale for splitting variance rests on measurement geometry:
1.  **Projection Error ($\sigma^2_{\text{proj}}$)**: Systematic geometric distortion caused by 2D camera sensor projection of out-of-plane joint rotation. Dictated by perspective foreshortening, this component is general to monocular sagittal pose estimation and transfers to any sagittal movement where the knee flexes in plane (such as squats and lunges) [source: 17_uncertainty_framework_outputs/framework_design.md].
2.  **Motion Error ($\sigma^2_{\text{mot}}$)**: Dynamic timing-sensitivity error caused by sub-frame synchronization lag and motion blur. This component is specific to the rapid-landing impact window of drop-jumps and does not transfer to slow, controlled movements like squats and lunges [source: 17_uncertainty_framework_outputs/framework_design.md].

### 8.3.2. Decomposed Biomarker Components
Decomposing each biomarker based on landing biomechanics yields [source: 17_uncertainty_framework_outputs/framework_design.md]:
*   **Peak Landing Flexion (#2)**: Measured at peak absorption where knee angular velocity is near zero ($\omega \approx 0$). Static peak error is purely spatial: $\sigma^2_{\text{proj}} = \mathbf{37.4132}$ ($100.0\%$), $\sigma^2_{\text{mot}} = \mathbf{0.0000}$ ($0.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
*   **Contact Flexion (#1)**: Measured at landing contact near full extension. Assuming a $90/10$ split yields $\sigma^2_{\text{proj}} = \mathbf{94.4880}$ ($90.0\%$), $\sigma^2_{\text{mot}} = \mathbf{10.4987}$ ($10.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
*   **Flexion Loading Rate (#6)**: Rapid impact velocity metric dominated by sub-frame contact timing. Assuming a $10/90$ split yields $\sigma^2_{\text{proj}} = \mathbf{434.6253}$ ($10.0\%$), $\sigma^2_{\text{mot}} = \mathbf{3911.6281}$ ($90.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
*   **Landing ROM (#3)**: Propagated from peak (#2) and contact (#1) endpoints ($\sigma^2_{\text{proj, ROM}} = 37.4132 + 94.4880 = 131.9012$). Scaled to observed total ($150.8291$), this gives a $92.62\% / 7.38\%$ split: $\sigma^2_{\text{proj}} = \mathbf{139.7047}$, $\sigma^2_{\text{mot}} = \mathbf{11.1244}$ [source: 17_uncertainty_framework_outputs/framework_design.md].

Sensitivity analysis confirmed weight ordering stable across assumed projection/motion splits, with weights varying less than 8.6%; full sweep details are in Appendix A [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## 8.4. Cross-Exercise Weight Transfer and Inverse-Variance Weighting

To aggregate measurements of unequal precision, we apply standard **inverse-variance weighting** [CITE: Borenstein_2013], where each raw weight is $w_i = 1 / \sigma_i^2$ and normalized weight is $\bar{w}_i = w_i / \sum w_j$.

### 8.4.1. Transfer Rule and Biomarker Mapping
Slow, controlled movements—such as squats and lunges—occur at low joint angular velocities where dynamic timing jitter ($\sigma^2_{\text{mot}}$) is biomechanically negligible. When transferring uncertainty weights to squats and lunges, we discard non-transferable motion variance and use **only the transferable projection component** ($\sigma^2_{\text{proj}}$) [source: 17_uncertainty_framework_outputs/framework_design.md]:
$$w_{\text{proj}, i} = \frac{1}{\sigma^2_{\text{proj}, i}}$$

This transfer maps drop-jump biomarkers to squat/lunge equivalents based on shared sagittal biomechanics [source: 17_uncertainty_framework_outputs/framework_design.md]:
*   `contact_flexion` $\leftrightarrow$ `start_flexion`: Both capture shallow flexion near full extension ($180^\circ$) where perspective error is minimal.
*   `loading_rate` $\leftrightarrow$ `descent_velocity`: Both capture angular flexion velocity ($\circ/\text{s}$).

### 8.4.2. Transferable Squat and Lunge Weights
Computing inverse-variance weights from projection variances ($\sigma^2_{\text{proj}}$) yields normalized cross-exercise transfer weights [source: 17_uncertainty_framework_outputs/framework_design.md]:
1.  **Peak Flexion**: **$57.15\%$** (Dominates screening characterisation due to low projection variance)
2.  **Start Flexion**: **$22.63\%$**
3.  **Range of Motion (ROM)**: **$15.30\%$**
4.  **Joint Descent Velocity**: **$4.92\%$** (Down-weighted due to higher projection uncertainty)

---

## 8.5. Worked Example Demonstration

The framework was demonstrated using representative correct and incorrect reps from the REHAB24-6 dataset [source: 17_uncertainty_framework_outputs/worked_example.csv]:
*   **Squat Reps**: Subject `PM_008` (Subject 1) rep 2 (correct) and rep 17 (incorrect) [source: 17_uncertainty_framework_outputs/worked_example.csv].
*   **Lunge Reps**: Subject `PM_021` (Subject 2) rep 2 (correct) and rep 7 (incorrect) [source: 17_uncertainty_framework_outputs/worked_example.csv].

### 8.5.1. Validated Noise Floors
For each biomarker, $95\%$ measurement confidence half-widths (noise floors) around raw video values are calculated using transferable projection standard deviations ($\text{SD}_{\text{proj}} = \sqrt{\sigma^2_{\text{proj}}}$) [source: 17_uncertainty_framework_outputs/worked_example.csv]:
*   **`start_flexion` floor**: $1.96 \times \sqrt{94.4880} = \mathbf{\pm 19.05^\circ}$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`peak_flexion` floor**: $1.96 \times \sqrt{37.4132} = \mathbf{\pm 11.99^\circ}$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`rom` floor**: $1.96 \times \sqrt{139.7047} = \mathbf{\pm 23.17^\circ}$ [source: 17_uncertainty_framework_outputs/worked_example.csv]
*   **`velocity` floor**: $1.96 \times \sqrt{434.6253} = \mathbf{\pm 40.86^\circ/\text{s}}$ [source: 17_uncertainty_framework_outputs/worked_example.csv]

These bounds represent the markerless system's validated physical measurement precision, remaining constant across repetitions by construction [source: 17_uncertainty_framework_outputs/framework_design.md].

### 8.5.2. Worked Example Data
Table 8.1 presents raw video measurements alongside validated uncertainty bounds and normalized weights [source: 17_uncertainty_framework_outputs/worked_example.csv]:

### Table 8.1: Worked Example Repetitions for Squat and Lunge Modalities

| Exercise | Video ID | Rep | Form | start_flexion ($^\circ$) | peak_flexion ($^\circ$) | rom ($^\circ$) | velocity ($^\circ$/s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Squat** | `PM_008` | 2 | Correct | $0.82^\circ \pm 19.05^\circ$ | $62.16^\circ \pm 11.99^\circ$ | $117.02^\circ \pm 23.17^\circ$ | $58.51^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Squat** | `PM_008` | 17 | Incorrect | $2.23^\circ \pm 19.05^\circ$ | $50.03^\circ \pm 11.99^\circ$ | $127.73^\circ \pm 23.17^\circ$ | $105.18^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Lunge** | `PM_021` | 2 | Correct | $21.42^\circ \pm 19.05^\circ$ | $83.53^\circ \pm 11.99^\circ$ | $75.05^\circ \pm 23.17^\circ$ | $27.12^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |
| **Lunge** | `PM_021` | 7 | Incorrect | $18.51^\circ \pm 19.05^\circ$ | $54.65^\circ \pm 11.99^\circ$ | $106.84^\circ \pm 23.17^\circ$ | $69.57^\circ/\text{s} \pm 40.86^\circ/\text{s}$ |

This demonstration highlights how the framework down-weights joint velocity ($4.92\%$) relative to peak flexion depth ($57.15\%$). Peak depth deviations are characterized with high confidence (narrower CI of $\pm 11.99^\circ$), whereas velocity deviations carry wider relative uncertainty ($\pm 40.86^\circ/\text{s}$).
Figure 8.1 illustrates the worked example of the uncertainty-weighted biomarker framework across the four biomarkers.

---

## 8.6. Empirical Confirmation Across Dissertation Components

The theoretical prediction of peak flexion dominance ($57.15\%$ weight) is independently confirmed by two subsequent empirical chapters:
1.  **Personalised Longitudinal Baselines (Chapter 9)**: Repetition-level screening gating demonstrated that screening triggers are overwhelmingly driven by peak flexion deviations beyond the tight $\pm 11.99^\circ$ noise floor, while velocity remains quiet due to its broad $\pm 40.86^\circ/\text{s}$ floor [source: 22_dissertation_writing/results_baseline_v1.md].
2.  **Temporal Sequence Models (Chapter 10)**: Leave-One-Subject-Out (LOSO) cross-validation established that peak flexion alone achieves optimal classification performance ($81.36\%$ squat / $81.50\%$ lunge balanced accuracy), outperforming complex trajectory shape models [source: 22_dissertation_writing/results_temporal_model_v1.md].

---

## 8.7. What This Framework Does NOT Claim

To maintain scientific integrity, we define explicit boundaries for the framework:
*   **No Diagnostic Claims**: Does not predict ACL injury, patellofemoral pain, or pathology.
*   **No Injury Risk Scoring**: Does not synthesize weighted biomarkers into a risk score or hazard ratio.
*   **No Repetition Classification**: Does not label repetitions as "passed" or "failed".
*   **No Validation of Squat/Lunge Motion Error**: Motion error validation for slow exercises remains future work.
*   **Methodological Demonstration Only**: Worked examples illustrate uncertainty propagation rather than a clinical diagnostic tool.

---

## 8.8. Figures and Provenance

Publication-ready framework figures support this chapter [source: 17_uncertainty_framework_outputs/worked_example_weights.png]:
*   **Figure 8.1: Worked example of the uncertainty-weighted biomarker framework**, showing each biomarker's validated 95% confidence bounds and derived inverse-variance weight. Peak flexion has the tightest bounds (±11.99°) and receives the largest weight (57.15%); descent velocity has the widest bounds (±40.86°/s) and receives the smallest weight (4.92%). [source: 17_uncertainty_framework_outputs/worked_example_weights.png]
