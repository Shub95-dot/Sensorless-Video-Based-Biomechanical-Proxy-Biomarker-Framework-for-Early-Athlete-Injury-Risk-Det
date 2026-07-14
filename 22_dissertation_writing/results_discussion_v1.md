# Chapter 14: General Discussion

This chapter presents a cross-cutting synthesis and critical evaluation of the markerless kinematic screening framework. Rather than evaluating individual pipeline steps in isolation, this discussion synthesizes the findings across the entire processing chain—from raw pose estimation validation to rule-based screening and explainable feedback. First, we present a synthesis of the framework's four core novelty contributions, detailing how they construct a unified methodological spine. Second, we establish a formal, evidence-grounded failure-mode taxonomy that categorizes and diagnoses the systematic technical and physical boundaries of monocular pose estimation identified in this work.

*(Note: Additional sections covering broader clinical translations, future research directories, and final conclusions will be appended in subsequent drafting passes.)*

---

## 14.1. Synthesis of the Four Novelty Contributions

The architecture developed in this dissertation is characterized by four interconnected novelty contributions. Rather than representing isolated engineering modules, these contributions form a continuous, validated method chain that directly addresses the spatial and temporal limitations of monocular video-based screening.

### 14.1.1. Contribution 1: Cross-Exercise Integration under a Unified Pipeline
The first contribution is the establishment of a single processing pipeline capable of extracting comparable sagittal-plane kinematics across three distinct movement modalities: squats, lunges, and drop-jumps [source: Chapter 4 / Chapter 5 / Chapter 6]. Traditional markerless studies typically evaluate a single exercise in isolation. By integrating these three movements under a unified coordinate convention (the included-angle convention for squats and lunges, and the clinical flexion convention for drop-jumps) [source: Section 4.1.1 / Section 5.1.2 / Section 6.6.4], the framework enables direct cross-exercise comparisons of movement velocity, excursion, and joint depth. This integration reveals how different loading demands—such as the bilateral symmetry of the squat compared to the unilateral propulsion requirements of the lunge—affect Pose-estimation tracking stability and form discrimination [source: Section 4.2 / Section 5.3].

### 14.1.2. Contribution 2: Failure-Mode-Aware Pose Extraction
Rather than claiming universal tracking accuracy, the second core contribution is the explicit characterisation and categorization of where, when, and why monocular pose-tracking fails. We reject the "black-box" assumption of commercial pose-estimation tools by documenting the specific physical and environmental conditions that degrade joint coordinate quality. This characterisation is formalized as a four-part taxonomy detailed in Section 14.2, mapping tracking loss to specific biomechanical and dataset design factors.

### 14.1.3. Contribution 3: The Continuous Validation-to-Screening Uncertainty Transfer Chain
The methodological spine of this thesis is the continuous mathematical chain that links ground-truth optoelectronic validation to baseline gating and sequence modeling. This chain operates through five sequential stages:
1.  **Ground-Truth Validation**: In Chapter 6, we compared single-camera video against synchronized 3D motion capture and force-plate ground truth across $n = 48$ drop-jump landing trials, establishing the 95% Limits of Agreement (LoA) for each knee biomarker [source: Section 6.1 / Section 6.3].
2.  **Variance Decomposition**: In Chapter 8, we converted these LoA bounds into statistical variances and decomposed the total error into a transferable projection component ($\sigma^2_{\text{proj}}$, systematic perspective foreshortening) and a non-transferable motion component ($\sigma^2_{\text{mot}}$, dynamic landing jitter) [source: Section 8.2 / Section 8.3].
3.  **Inverse-Variance Weighting**: Applying inverse-variance weighting to the transferable projection components yielded normalized weights that define the relative trustworthiness of each biomarker (Peak Flexion: $57.15\%$, Start Flexion: $22.63\%$, Range of Motion: $15.30\%$, Joint Descent Velocity: $4.92\%$) [source: Section 8.4].
4.  **Empirical Gating Confirmation**: In Chapter 9 and Chapter 11, these weights were transferred to squats and lunges to gate personalised deviation screening. The empirical behavior of the baseline tracking engine directly confirmed the validation splits: gating decisions were driven by high-confidence peak flexion (which has a tight $\pm 11.99^\circ$ noise floor), while low-confidence descent velocity (which has a wide $\pm 40.86^\circ/\text{s}$ noise floor) remained quiet and did not false-alarm [source: Section 9.3 / Section 11.2]. The velocity channel triggered only during a genuine, large velocity surge of $110.62^\circ/\text{s}$ on squat Repetition 6 [source: Section 9.3].
5.  **Independent Experimental Re-Confirmation**: In Chapter 13, we conducted a controlled Leave-One-Subject-Out (LOSO) cross-validation comparison to evaluate whether sequence models (LSTMs) could extract useful signals from within-repetition trajectory shape [source: Section 13.2.1 / Section 13.3]. The experiment independently confirmed the dominance of static peak flexion: a simple logistic regression classifier trained on peak flexion alone achieved a balanced accuracy of **$81.36\%$** on squats and **$81.50\%$** on lunges, whereas the LSTM sequence models collapsed to or below the majority baseline [source: Section 13.3].

The convergence of two completely independent pathways—the empirical gating behavior of the personalised baselines (Chapters 9/11) and the sequence model classification experiment (Chapter 13)—on the same dominant biomarker (peak knee flexion) strongly validates the transferability of the drop-jump validation weights, establishing a rigorous mathematical foundation for the screening layer rules in Chapter 10.

### 14.1.4. Contribution 4: Counterfactual XAI on Deterministic Rules
The fourth contribution is the development of a transparent, glass-box explainability layer (Chapter 12) designed to explain the decisions of the rule-based screening layer (Chapter 10) [source: Section 10.1 / Section 12.1]. Because the screening layer is deterministic and rule-based, the counterfactual explanations are **faithful by construction** [source: Section 12.2 / Section 12.3]. They calculate the exact physical joint margins ($M_i$) by which a repetition crossed a threshold, guaranteeing zero approximation error [source: Section 12.3]. This led to the deprecation of local surrogate models (such as SHAP or LIME), which perturb inputs to approximate black-box decision boundaries and introduce explanation infidelity [source: Section 12.2]. The counterfactual engine translates these margins into descriptive statements and resolves multi-variable coupling through Minimal Kinematic Intervention (MKI) arithmetic [source: Section 12.4 / Section 12.5].

---

## 14.2. The Failure-Mode Taxonomy

Rather than presenting tracking errors as isolated anomalies, this section establishes a formal **Failure-Mode Taxonomy** (Contribution #2) [source: Section 5.5 / Section 6.6]. We categorize the pipeline's failure modes into four named types, detailing their technical and biomechanical mechanisms based on empirical evidence from the completed chapters.

### 14.2.1. Occlusion Failure (Sagittal Self-Occlusion)
*   **Mechanism**: A physical loss of line-of-sight between the camera sensor and the target joint center caused by intervening body segments during unilateral or asymmetric movement.
*   **Evidence**: 
    1.  *Lunge Exclusions (Chapter 5)*: Unilateral lunge tracking resulted in a $30.68\%$ tracking loss across the assembled dataset, heavily concentrated in Subject 8 (`PM_112`, **$100.0\%$ failure rate**, 12/12 reps failed) and Subject 5 (`PM_042`, **$92.3\%$ failure rate**, 12/13 reps failed) [source: Section 5.1.1]. Because the loaded leg was positioned as the far leg relative to the single sagittal camera sensor, it was completely occluded by the trailing leg and torso during deep flexion, causing a catastrophic tracking failure [source: Section 5.1.1].
    2.  *Drop-Jump Occlusion (Chapter 6)*: During the landing absorption phase of asymmetric drop-jumps, the closer leg completely occluded the farther leg, reducing its sagittal tracking visibility to **$\sim 0\%$** [source: Section 6.6.2]. Consequently, bilateral inter-limb asymmetry could not be validated or screened using monocular video [source: Section 6.6.2].
*   **Synthesis**: This demonstrates that occlusion is a systematic limitation of single-camera setups during asymmetric movements. While bilateral squats allow a contralateral limb fallback to maintain a $100\%$ tracking completion rate [source: Section 5.1.1], unilateral loading tasks (lunges, asymmetric drop-jumps) are highly susceptible to sagittal self-occlusion, defining a clear physical boundary for monocular screening.

### 14.2.2. Recording-Limit Failure (Data Truncation)
*   **Mechanism**: An operational limitation where the duration of the raw data recording is shorter than the physical time-series window required to calculate a biomarker.
*   **Evidence**:
    1.  *Drop-Jump Time-to-Stabilisation (Chapter 6)*: The dynamic Time-to-Stabilisation (TTS) biomarker was dropped because the video files in the OpenCap dataset truncated abruptly between **$0.05\text{ s}$ and $0.2\text{ s}$** after final landing contact (IC2) [source: Section 6.6.1]. Because evaluating stabilisation requires a $0.5$ s quiet-stance window (30 frames at 60 FPS) to confirm that kinematic standard deviation remains below $1.5^\circ$, the short trial lengths made the calculation mathematically impossible [source: Section 6.6.1].
*   **Synthesis**: This failure mode is a data-collection and dataset design constraint rather than an algorithmic or software defect. It highlights the necessity of designing recording protocols with sufficient pre- and post-movement buffers to support the window requirements of dynamic stabilization metrics.

### 14.2.3. Projection-Bias Failure (Spatial Foreshortening)
*   **Mechanism**: A systematic geometric distortion where a 2D camera sensor overestimates or underestimates a 3D joint angle as the limb moves out of the camera's orthogonal plane.
*   **Evidence**:
    1.  *Deep-Flexion Overestimation (Chapter 6)*: Validation against 3D motion capture revealed a constant peak overestimation bias of **$+10.52^\circ$** (timing-clean) and **$+19.72^\circ$** (peak-to-peak) during deep landing flexion, contrasted with a shallow-flexion underestimation bias of **$-6.69^\circ$** at initial contact [source: Section 6.2.1 / Section 6.2.3 / Section 6.3].
    2.  *Bias Source (Chapter 6)*: Diagnostic lag tests ruled out timing synchronization as the cause: peak-matching worsened the mean absolute error from **$14.80^\circ$** to **$20.15^\circ$** [source: Section 6.5.1]. Software modeling tests also ruled out modeling definition mismatches (only **$1.64^\circ$** mean offset) [source: Section 6.5.2]. This confirmed that the bias is purely spatial in origin, driven by perspective projection foreshortening as the flexing joint deviates from the orthogonal camera axis [source: Section 6.5].
*   **Synthesis**: While projection bias represents a systematic spatial distortion, it behaves as a stable, characterised offset. Consequently, Chapter 10's personalised-deviation screening layer (Option B) successfully neutralizes this bias: because the perspective angle remains constant within a subject's session, the offset cancels out mathematically when subtracting the test rep from the subject's own baseline mean [source: Section 10.3].

### 14.2.4. Data-Scale / Model-Mismatch Failure (Overfitting)
*   **Mechanism**: A performance collapse that occurs when a high-capacity machine learning model memorizes subject-specific noise and calibration offsets on small datasets rather than generalizing the underlying kinematic boundary.
*   **Evidence**:
    1.  *LSTM Trajectory Classification (Chapter 13)*: When evaluating whether trajectory shape details could classify form quality under LOSO cross-validation, the regularized LSTM collapsed completely to the naive baseline under Scheme B (stripping amplitude), returning exactly **$50.00\%$ Balanced Accuracy** on squats [source: Section 13.3]. Under Scheme A (amplitude kept), the LSTM reached only **$53.79\%$** balanced accuracy on squats and **$53.78\%$** on lunges, performing far below the single-feature peak flexion classifier (**$81.36\%$** on squats, **$81.50\%$** on lunges) [source: Section 13.3].
*   **Synthesis**: The LSTM's failure to capture a highly discriminative amplitude signal that was easily extracted by a single logistic regression threshold is a classic sign of small-cohort overfitting. With only 7 to 9 subjects, the neural network's parameter capacity leads it to memorize subject-specific calibration and tracking patterns, causing a complete failure to generalize across subjects. This establishes a generalizable lesson: complex deep sequence models are poorly suited for biomechanical screening at small cohort scales.

---

### 14.2.5. Synthesis of the Taxonomy
Categorizing these failures into named, mechanistically-understood categories—rather than treating them as isolated, random tracking anomalies—represents a major methodological contribution. This taxonomy provides future developers and clinical users of markerless biomechanical pipelines with a predictive roadmap: it outlines exactly where tracking failures will occur (far-limb unilateral joints), why spatial biases are introduced (projection foreshortening at deep angles), and how model architectures must be constrained (simplifying models to match data scale) to maintain generalizability across different datasets and exercises.

---

## 14.3. Cross-Exercise Kinematic Divergence

A key finding of this multi-exercise integration is that kinematic form discrimination is highly task-dependent, revealing that form deviations do not manifest uniformly across exercises.

### 14.3.1. Descent-Localized vs. Ascent-Discriminative Kinematics
*   **Squat Form Discrimination (Descent-Localized)**: Group-level statistical analysis of the squat cohort in Chapter 4 demonstrated that form-quality discrimination is strictly localized to the eccentric descent phase [source: Section 4.2]. Peak flexion depth ($d = 1.7306$), range of motion ($d = -1.4484$), and peak descent velocity ($d = 1.6375$) successfully differentiated correct and incorrect execution [source: Section 4.2]. In contrast, the concentric ascent velocities did not discriminate form, with both peak ascent velocity ($d = -0.5049$, 95% CI: $[-1.4838, +0.0848]$) and mean ascent velocity ($d = -0.4996$, 95% CI: $[-1.7017, +0.1301]$) having confidence intervals that crossed zero [source: Section 4.2 / Section 4.3.1].
*   **Lunge Form Discrimination (Ascent-Discriminative)**: In contrast, lunge form discrimination in Chapter 5 extended into the concentric ascent phase [source: Section 5.3]. In addition to descent depth and velocity, both lunge peak ascent velocity ($d = -0.9721$, 95% CI: $[-1.6403, -0.6554]$) and mean ascent velocity ($d = -0.7962$, 95% CI: $[-2.0731, -0.0807]$) reliably discriminated between form groups, with bootstrap confidence intervals excluding zero [source: Section 5.2 / Section 5.3.1].

### 14.3.2. Biomechanical Interpretation of Divergence
This divergence is explained by the physical loading differences between the tasks:
*   The squat is a bilateral, symmetric movement where the body's mass is supported equally by both limbs, allowing for a controlled, symmetric recovery phase that does not systematically vary with descent faults [source: Section 5.3.2].
*   The lunge is an asymmetric, unilateral task. In an incorrect lunge—which is characterized by an excessively deep bottom position—the subject is in a biomechanically disadvantaged posture at maximum depth [source: Section 5.3.2]. Returning to a standing position requires a forceful concentric push-off from the front leg, resulting in a rapid, less-controlled concentric propulsion step to recover standing balance [source: Section 5.3.2].

### 14.3.3. Methodological Significance
This finding demonstrates that the discriminative kinematic signal for form screening is phase-specific and exercise-specific. Evaluating a single exercise in isolation (such as only squats or only lunges) would have failed to reveal this task-dependent behavior. This comparative insight provides empirical justification for Contribution 1: integrating multiple movements under a unified pipeline is necessary to characterize the full kinematic profile of an athlete's movement deviations.

---

## 14.4. What the Validated Framework Enables

The principal practical payoff of the continuous validation-to-screening uncertainty chain (Section 14.1.3) is that it bounds the dissertation's clinical screening claims with ground-truth-validated precision.

### 14.4.1. Bounded Screening Claims
Rather than simply asserting that a joint angle has deviated from a baseline, every biomarker evaluated in this framework carries a quantified confidence bound:
*   Peak flexion deviations are monitored with high confidence ($\sigma^2_{\text{proj}} = 37.4132$, yielding a 95% measurement confidence bound of $\pm 11.99^\circ$) [source: Section 8.2.2 / Section 8.6.1].
*   Joint descent velocities are monitored with lower confidence ($\sigma^2_{\text{proj}} = 434.6253$, yielding a 95% measurement confidence bound of $\pm 40.86^\circ/\text{s}$) [source: Section 8.2.2 / Section 8.6.1].

This statistical qualification ensures that the clinical screening layer does not over-interpret noisy joint angle metrics, gating velocity deviations to prevent false-alarm triggers while confidently flagging changes in depth.

### 14.4.2. Contrast with Weak Validation Paradigms
This approach represents a major advancement over typical markerless pose-estimation studies, which rely on weaker validation paradigms. We distinguish two levels of validation:
*   *Internal Consistency / Cross-Cohort Agreement (Weaker)*: Asserting measurement accuracy because two independent cohorts demonstrate similar kinematic means (such as the squat laboratory-vs-YouTube cohort agreement in Section 4.5.3, or the lunge statistical consistency in Section 5.5.3). While useful for demonstrating reproducibility, cross-cohort consistency cannot detect systematic coordinate offsets or characterize individual trial variance [source: Section 6.1].
*   *Ground-Truth Optoelectronic Validation (Stronger)*: Synchronized, frame-by-frame coordinate comparison against optoelectronic motion capture and force-plate ground truth [source: Section 6.1]. 

By executing a ground-truth validation on drop-jumps (Chapter 6) and decomposing the error to isolate the transferable projection component (Chapter 8), this framework moves beyond qualitative consistency, enabling quantitative uncertainty bounds to be propagated directly to unvalidated datasets.

---

## 14.5. Limitations of the Thesis as a Whole

To maintain scientific rigor, we consolidate the limitations of individual chapters into five thesis-level themes:

1.  **Cohort Size Constraints**: The datasets evaluated were restricted to small subject counts (9 squat subjects, 7 lunge subjects, and 8 drop-jump subjects) [source: Section 4.1.1 / Section 5.1.1 / Section 6.1]. The LSTM sequence classification experiment in Chapter 13 provides direct empirical proof of the limitations of this scale: the deep network failed to generalize and overfitted to subject identities (scoring $\approx 54\%$ balanced accuracy under Scheme A), whereas a simple, single-feature peak flexion threshold achieved $81.36\%$ balanced accuracy [source: Section 13.3]. This confirms that complex deep learning sequence models are not generalizable at this cohort scale.
2.  **Sagittal-Camera-Only Design**: Restricting the pipeline to a single sagittal camera view makes contralateral occlusion a recurring limitation. This design choice is the direct cause of the lunge subject exclusions (Subject 8/`PM_112` and Subject 5/`PM_042` dropped due to occlusion) and the exclusion of the drop-jump inter-limb asymmetry biomarker (visibility reduced to $\sim 0\%$ on the far limb) [source: Section 14.2.1]. Monocular sagittal setups are blind to frontal-plane movements, preventing the evaluation of valgus or pelvic drop.
3.  **Exercise Battery Scope**: The framework evaluated only three exercises (squat, lunge, drop-jump) [source: Section 14.1.1]. Multi-planar athletic maneuvers such as running, cutting, and pivoting remain unaddressed. While vertical jump trajectory extraction was planned, it was scoped out of the dissertation timeline due to external data access dependencies.
4.  **Track B Architectural Status**: The personalised baseline (Chapter 9) and digital twin (Chapter 11) architectures are Track B demonstrations evaluated on repetition sequences (pseudo-sessions), not live, longitudinal deployments tracked over weeks or months. The adaptation rates and aberration-rejection gates are mockups demonstrating coordinate flow, rather than clinically verified physiological trends.
5.  **Screening-not-Prediction Boundary**: The screening thresholds and baseline gating rules are statistical heuristics grounded in cohort distributions and literature-associated risk factors; they are **not** clinically validated diagnostic cut-offs. The framework identifies coordinate deviations matching movement templates; it cannot predict injury risk or estimate clinical probabilities.

---

## 14.6. Consolidated Future Work

To guide subsequent developments, we consolidate the future-work axes identified across the completed chapters:

*   **Expanded Exercise Battery**: Integrating vertical jump trajectories by securing access to the Bath BioCV dataset, expanding the pipeline to high-velocity vertical propulsion.
*   **Longitudinal Digital Twin Validation**: Collecting multi-session datasets (10–14 testing sessions per subject spaced over multiple weeks) to validate baseline update templates. Real baseline data collection was deferred in this study due to ethics-gating and dissertation timeline constraints.
*   **Motion-Error Validation for Slow Movements**: Conducting ground-truth optoelectronic validation for squats and lunges to directly measure their motion-error component ($\sigma^2_{\text{mot}}$), replacing the projection-only transfer assumption currently implemented in Chapter 8 [source: Section 8.5.4].
*   **Temporal Twin Logic**: Implementing temporal persistence logic for the digital twin (Chapter 11) to distinguish transient movement aberrations from sustained physiological shifts (such as strength adaptation or fatigue) [source: Section 11.3].
*   **Representation Learning at Scale**: Implementing self-supervised pretraining (contrastive learning, masked autoencoders) once larger multi-subject datasets are compiled, allowing deep sequence models to generalize joint coordinate representations without overfitting [source: Section 13.5].
*   **Large-Cohort Sequence Modeling**: Evaluating within-repetition trajectory shape modeling (Chapter 13) on cohorts of hundreds of subjects to determine if temporal shapes contain discriminative signals when model capacity matches data scale [source: Section 13.5].

---

## 14.7. Closing Statement

In summary, this dissertation delivers a sensorless, monocular markerless kinematic screening framework that extracts comparable biomarkers across squats, lunges, and drop-jumps. By mapping limits of agreement to a transferable projection uncertainty, the framework propagates validated confidence bounds to qualify screening decisions, while providing faithful-by-construction counterfactual explanations for rule-based flags. 

Consistent with the writeup plan's must-include flags, the project's evolution narrative—detailing the transition from a predictive injury classifier to a validated screening framework—is placed exclusively in Chapter 15 (Conclusion) as a final reflective note on methodological maturity [source: writeup_plan.md line 554]. Chapter 14 has established the cross-exercise findings, quantified uncertainty weights, and failure-mode taxonomy that support this screening architecture.

