# REHAB24-6 Lunge Cohort Results

<!-- 
PROVENANCE NOTE:
- All Cohen's d effect sizes, group means, SDs, and sample sizes are sourced directly from phase5c_effect_sizes_ci.csv (verified).
- Subject-specific shifts are sourced from phase5c_per_subject_shifts.csv (verified).
- Trajectory direction was overlay-confirmed on subject 7 (rep 14 vs rep 16); depth magnitudes are from phase5c_effect_sizes_ci.csv.
- Figures L1 and L2 are placeholders pending the publication-quality generation pass.
- No speculative or unverified numbers have been introduced.
-->

## 1. Introduction and Methods Recap

This section presents the results of the markerless, monocular screening framework applied to the lunge exercise within the REHAB24-6 physical therapy dataset. The primary objective is to evaluate the framework's capacity to discriminate between correct and incorrect movement forms during a unilateral sagittal loading task using kinematics extracted from standard 2D video.

### 1.1. Cohort Assembly and Filtering
The assembled cohort was drawn from the REHAB24-6 dataset, focusing on sagittal-plane lunge recordings. We filtered the master segmentation manifest using three strict criteria:
1. Exercise selection: `exercise_id == 5` (signifying the lunge modality).
2. Camera orientation: `cam17_orientation == 'front'`, which guarantees that the secondary camera (`Camera 18`) is positioned orthogonally to capture a pure sagittal/side view.
3. Reference quality: `mocap_erroneous == 0`, ensuring the repetition is free of dataset-flagged capture errors.

This filtering process yielded an initial assembled cohort of **88 sagittal lunge repetitions** across **8 subjects**. The working leg for each repetition was determined directly from the `exercise_subtype` attribute (where `'front leg left'` maps to the left knee and `'front leg right'` maps to the right knee).

### 1.2. Kinematic Extraction Pipeline
The video processing pipeline adapted the squat methodology for bilateral tracking without contralateral fallbacks:
* **Pose Extraction**: Run frame-by-frame pose estimation using the MediaPipe Pose Landmarker Heavy variant.
* **Working Leg Selection**: Instead of employing the squat pipeline's left-to-right fallback mechanism (which prioritizes the limb with higher visibility), the lunge pipeline strictly tracks the knee corresponding to the designated working leg for that repetition, ensuring clinical fidelity to the loaded limb.
* **Temporal Smoothing**: Trajectories undergo a two-stage smoothing pass consisting of a 5-frame median filter (to suppress high-frequency transient tracking spikes) followed by a 7-frame, second-order Savitzky-Golay filter to reconstruct smooth kinematic velocities and accelerations.
* **Biomarker Extraction**: Standardized kinematic variables—including peak flexion angle, range of motion (ROM), descent and ascent phase velocities, and movement jerk—are extracted using the ground-truth repetition boundaries.

### 1.3. Statistical Framework
To respect the hierarchical nature of the dataset (where multiple repetitions are nested within subjects), we implemented subject-clustered bootstrapping. Resampling was performed at the subject level with replacement over 5,000 iterations to compute 95% confidence intervals (CIs). The primary contrast is defined as:
$$\text{Contrast} = \text{Correct} - \text{Incorrect}$$
Cohen's $d$ effect sizes were calculated using the pooled standard deviation across the usable cohort. This statistical procedure matches the squat analysis verbatim to maintain complete cross-exercise comparability. One bridging sentence is required here to note that while 88 repetitions were assembled, the final statistics were computed on the usable analytical cohort defined in Section 3 after pose-failure exclusions.

---

## 2. Cohort Descriptive Statistics

Prior to evaluating form-discrimination contrasts, we analyzed the global kinematic characteristics of the lunge cohort to establish baseline ranges for this exercise modality. Table L1 presents the descriptive statistics computed across all successfully processed lunge repetitions.

### Table L1: Descriptive Kinematic Statistics for the REHAB24-6 Lunge Cohort

| Biomarker | Minimum | Maximum | Mean | Median | Standard Deviation (SD) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `peak_flexion_deg` | 49.5473° | 113.0024° | 76.8940° | 80.9208° | 16.6133° |
| `rom_deg` | 27.3106° | 127.6300° | 77.4784° | 75.0464° | 29.0042° |
| `tempo_ratio` | 0.4390 | 2.5250 | 0.9747 | 0.8718 | 0.4047 |
| `jerk_proxy_std` | 0.2320 | 3.2984 | 0.8191 | 0.5335 | 0.6669 |

### 2.1. Comparison with Squat Kinematic Baselines
A comparison of these baseline ranges with the REHAB24-6 squat cohort reveals structural kinematic differences between the two exercise modalities. In the squat cohort, the mean peak flexion angle was $55.62^\circ \pm 14.31^\circ$ (representing a deeper squat depth), and the mean range of motion was $117.32^\circ \pm 18.91^\circ$. In contrast, the lunge cohort exhibits a shallower mean peak flexion angle of $76.89^\circ \pm 16.61^\circ$ and a smaller mean range of motion of $77.48^\circ \pm 29.00^\circ$. 

This shallower peak depth and restricted range of motion are highly consistent with the unilateral nature of the lunge. Unlike the bilateral squat, where the subject's center of mass is supported by a symmetric base of support, the lunge requires significant single-leg stability, pelvic control, and stride-length coordination. These kinematic differences represent baseline, exercise-specific constraints that must be separated from the within-exercise correctness contrasts discussed in Section 4.

---

## 3. Analytical Cohort and Pose-Pipeline Failure Modes

Markerless biomechanical screening frameworks must document not only their positive predictive capabilities but also their failure modes when applied to clinical or lab-based video. Of the 88 assembled lunge repetitions, **61 repetitions** successfully passed the phase-identification validation gate, forming the usable analytical cohort. This usable cohort consists of **25 correct repetitions** and **36 incorrect repetitions** across **7 subjects**.

### 3.1. Concentration of Pose-Pipeline Failures
The remaining **27 repetitions (30.68% of the assembled data)** failed the validation gate due to tracking errors that resulted in high rates of missing values (greater than 30% of the repetition duration) or invalid phase boundaries. Crucially, these failures were not distributed evenly across the cohort but were concentrated in two subjects:
* **Subject 8**: 12 of 12 repetitions failed the gate, resulting in the subject being dropped entirely from the analytical cohort.
* **Subject 5**: 12 of 13 repetitions failed, leaving only 1 usable repetition.
* **Other Subjects**: Only single-repetition failures occurred in Subject 2, Subject 3, and Subject 4, while Subjects 6, 7, and 9 had zero failures.

### 3.2. Biomechanical Mechanism of Occlusion Failure
This concentration of failures represents a direct extension of the pose-pipeline failure-mode taxonomy established in the squat chapter. In the squat cohort, pipeline tracking was highly robust because the symmetric nature of the movement allowed a contralateral fallback (if one knee was occluded, the tracker could fall back to the other knee to estimate depth). 

However, a sagittal lunge is fundamentally asymmetric. The clinical objective is to monitor the loaded front leg. If the front leg is positioned as the far leg relative to the camera, it is frequently occluded by the trailing leg or the subject's own torso during the descent. Because the lunge pipeline must track the working leg without a fallback, this far-side occlusion leads to catastrophic tracking loss. Documenting this interaction between exercise asymmetry and monocular view constraints is a key methodological contribution of this work, highlighting that camera placement must be adapted to the specific asymmetry of the movement.

---

## 4. Correct-vs-Incorrect Form Discrimination

The core analytical task of the Phase 5C pass is to evaluate whether the extracted biomarkers can discriminate between correct and incorrect lunge execution. Table L2 displays the biomarkers sorted by the magnitude of their Cohen's $d$ effect sizes, alongside their subject-clustered bootstrap 95% confidence intervals and reliability classifications.

### Table L2: Lunge Form-Discrimination Effect Sizes and Confidence Intervals

| Rank | Biomarker | Cohen's d | Bootstrap 95% CI Lower | Bootstrap 95% CI Upper | Reliability Tier |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 1 | `peak_flexion_deg` | 1.6904 | 0.8317 | 3.4525 | **`reliable`** |
| 2 | `rom_deg` | -1.2653 | -2.8682 | -0.5852 | **`reliable`** |
| 3 | `mean_descent_velocity_deg_per_frame` | 1.1563 | 0.2863 | 2.6316 | **`reliable`** |
| 4 | `peak_descent_velocity_deg_per_frame` | 1.1453 | 0.7512 | 2.0354 | **`reliable`** |
| 5 | `jerk_proxy_std` | -1.0070 | -1.3663 | -0.6526 | **`reliable`** |
| 6 | `peak_ascent_velocity_deg_per_frame` | -0.9721 | -1.6403 | -0.6554 | **`reliable`** |
| 7 | `mean_ascent_velocity_deg_per_frame` | -0.7962 | -2.0731 | -0.0807 | **`reliable_marginal`** |
| 8 | `peak_extension_deg` | -0.4972 | -1.7633 | 0.1533 | `not_reliable` |
| 9 | `tempo_ratio` | -0.3796 | -0.7240 | 0.1386 | `not_reliable` (Precise Null) |

### 4.1. Depth and Range of Motion
The framework identified the depth-related markers as the strongest discriminators of form quality. `peak_flexion_deg` exhibits a very large positive effect size ($d = 1.6904$, 95% CI $[0.8317, 3.4525]$), indicating that incorrect repetitions are characterized by a smaller knee angle (meaning a deeper lunge) by an average of $21.63^\circ$. 

Consistent with this increase in depth, the range of motion (`rom_deg`) was also significantly larger in the incorrect group ($d = -1.2653$, 95% CI $[-2.8682, -0.5852]$), showing an increase of $31.27^\circ$. Subject-specific shift analysis confirmed that this pattern was highly consistent: all five subjects who contributed both correct and incorrect reps (Subjects 2, 4, 6, 7, and 9) shifted toward greater depth and ROM during their incorrect repetitions, confirming that the cohort-level effect is not driven by a single outlier.

### 4.2. Descent Velocity and Jerk
Velocity and movement quality biomarkers also reliably discriminated between the two execution forms:
* **Descent Velocity**: Incorrect reps are characterized by a significantly faster descent. Both `mean_descent_velocity` ($d = 1.1563$, CI $[0.2863, 2.6316]$) and `peak_descent_velocity` ($d = 1.1453$, CI $[0.7512, 2.0354]$) were larger in magnitude, representing a rapid drop into the lunge.
* **Movement Jerk**: The standard deviation of the second derivative of the knee angle (`jerk_proxy_std`) was significantly higher in the incorrect repetitions ($d = -1.0070$, CI $[-1.3663, -0.6526]$), indicating a loss of movement smoothness.

Taken together, this signature—increased depth, faster descent, and elevated jerk—supports the "uncontrolled descent" kinematic profile. During incorrect execution, subjects drop rapidly into a deeper position and lose movement control, which is represented by a rougher trajectory.

### 4.3. Ascent Velocity Dynamics
A major finding in this cohort is the behavior of the ascent phase. In the squat cohort, ascent velocity differences crossed zero and did not reliably discriminate between forms. However, in the lunge cohort, both ascent biomarkers are reliable:
* **Peak Ascent Velocity**: Incorrect lunges exhibit a faster peak ascent ($d = -0.9721$, CI $[-1.6403, -0.6554]$), which clears zero.
* **Mean Ascent Velocity**: Incorrect lunges also show a faster mean ascent ($d = -0.7962$, CI $[-2.0731, -0.0807]$). This effect is classified as reliable but marginal, as its upper bound is close to zero.

This reliable ascent velocity difference indicates that incorrect-form lunges involve a rapid, uncontrolled spring back to the starting position. This is a key cross-exercise divergence from the squat results and likely reflects the distinct balance and propulsion strategies required to recover from a deep unilateral lunge.

### 4.4. Statistical Nulls
The biomarker `peak_extension_deg` did not reliably discriminate form quality ($d = -0.4972$, CI $[-1.7633, 0.1533]$). The `tempo_ratio` represents a precise null ($d = -0.3796$, CI $[-0.7240, 0.1386]$); its tight confidence interval around zero suggests that the relative timing of the descent and ascent phases remains constant, even when the absolute velocities and depths shift.

### 4.5. Clinical Interpretation of Depth Faults
Clinically, lunge depth is a two-sided quality: both excessive depth (which increases patellofemoral compressive force) and insufficient depth (which limits quad activation) are recognized movement faults. Because the incorrect repetitions in this cohort shifted consistently toward greater depth (lower knee angle), this finding reflects the specific instructed errors performed by the REHAB24-6 subjects (e.g., placing the knee too far forward). It does not imply that the pipeline is incapable of detecting shallow faults, but rather that the observed effect is a reflection of this cohort's specific error profile.

```
[Placeholder: Figure L1 - REHAB24-6 lunge form discrimination across the discriminating biomarkers]
[Placeholder: Figure L2 - Effect-size forest plot for nine lunge biomarkers]
```

---

## 5. Cross-Cohort Consistency with Squats

One of the primary contributions of this dissertation is the integration of multiple exercises into a unified biomechanical screening framework. This requires verifying whether kinematic signatures of incorrect form are consistent across different movements.

### 5.1. The Unified Kinematic Signature
The results from the REHAB24-6 lunge cohort demonstrate strong consistency with the squat cohort. In the squat cohort, incorrect form was characterized by a very large shift toward greater depth ($d = +1.73$) and faster descent. In the lunge cohort, we observe a nearly identical effect size for peak flexion ($d = +1.6904$, CI $[0.8317, 3.4525]$). 

This consistency suggests that the "uncontrolled deep descent" profile is a cross-exercise kinematic signature of poor form. Across both exercises, incorrect execution involves a failure to regulate descent velocity, leading to excessive joint flexion. This cross-exercise consistency provides empirical validation for the screening framework's core claim: the pipeline can detect stable kinematic indicators of form quality across distinct exercise modalities.

### 5.2. Exercise-Specific Divergence
We also observed a notable kinematic divergence. In squats, ascent velocity did not discriminate between correct and incorrect form ($d$ crossed zero). In lunges, however, both peak ascent velocity ($d = -0.9721$, reliable) and mean ascent velocity ($d = -0.7962$, reliable_marginal) were significantly faster in incorrect repetitions. 

This divergence is biomechanically plausible. The squat is a bilateral movement where recovery is assisted by symmetrical hip and knee extension. The lunge, however, is a unilateral propulsion task. Recovering from an excessively deep lunge may require a more forceful push-off from the front foot, plausibly increasing ascent velocity. This finding demonstrates that while the screening framework can leverage unified cross-exercise signatures (like descent velocity and depth), it must also accommodate exercise-specific nuances (like lunge ascent velocity) to build accurate movement profiles.

---

## 6. Discussion and Limitations

While the results support the framework's screening capabilities, several limitations must be noted to ensure a balanced interpretation.

### 6.1. Small and Imbalanced Sample Size
The usable analytical cohort contains **36 incorrect repetitions** from only **6 subjects** (Subjects 2, 3, 4, 6, 7, and 9). Because of this small sample, the findings must be treated as descriptive rather than inferential. The reported effect sizes and confidence intervals represent the characteristics of this specific cohort and should not be used to make population-level generalizations. 

Furthermore, subject-specific analysis revealed significant sample imbalances. Subject 3 contributed 10 incorrect repetitions and 0 correct repetitions, meaning this subject's data could inform the pooled contrast but was excluded from the within-subject shift analysis. Subject 5 was similarly limited, contributing only 1 usable incorrect repetition.

### 6.2. Heterogeneity of Movement Errors
A primary limitation of the REHAB24-6 dataset is the lack of detailed error labels. The dataset annotates correctness as a binary variable (correct/incorrect) but does not specify which movement fault was performed. 

Because incorrect form is a heterogeneous category (encompassing sagittal faults like excessive depth and frontal faults like knee valgus), grouping all incorrect repetitions into a single category limits the specificity of the analysis. A subject who performed a valgus error might show a different sagittal kinematic profile than a subject who performed a depth error. Future work must incorporate manual error-type annotations to enable multi-class classification. Because some incorrect repetitions may carry frontal-plane faults that the sagittal pipeline cannot observe, those repetitions add noise to the correct-vs-incorrect contrast rather than systematic bias.

### 6.3. Dimensional and Cohort Scope
Our analysis was restricted to the sagittal plane. Consequently, the pipeline is blind to frontal-plane errors, such as knee valgus or pelvic drop, which are heavily associated with ACL injury risk. Frontal-plane validation is queued as future work using the frontal `cam17` video files. 

Additionally, the lack of prospective injury outcome data means the framework cannot predict injury risk directly. Instead, it serves as a screening tool to identify kinematic features that have been linked to injury risk in prior clinical literature. Finally, future integration of the UI-PRMD dataset is planned to provide a Vicon-tracked reference cohort for near-ground-truth kinematic range comparison.
