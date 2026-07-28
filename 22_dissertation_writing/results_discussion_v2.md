# Chapter 14: General Discussion

This chapter presents a cross-cutting synthesis and critical evaluation of the markerless kinematic screening framework. Rather than evaluating individual pipeline steps in isolation, this discussion synthesizes findings across the entire processing chain—from raw pose estimation validation to rule-based screening and explainable feedback. First, we synthesize the framework's four core novelty contributions. Second, we establish a formal failure-mode taxonomy categorizing the technical and physical boundaries of monocular pose tracking. Third, we analyze the cross-exercise kinematic divergence revealed across movement tasks. Fourth, we consolidate thesis-level limitations and outline future work directions.

---

## 14.1. Synthesis of the Four Novelty Contributions

The framework developed in this dissertation is anchored by four interconnected novelty contributions that form a continuous, validated method chain addressing the spatial and temporal limits of monocular video screening.

### 14.1.1. Contribution 1: Cross-Exercise Integration under a Unified Pipeline
The first contribution is a single processing pipeline capable of extracting comparable sagittal-plane kinematics across three movement modalities: squats, lunges, and drop-jumps [source: Chapter 4 / Chapter 5 / Chapter 6]. Integrating these tasks under unified coordinate conventions (included-angle convention for squats/lunges, clinical flexion convention for drop-jumps) [source: Section 4.1.1 / Section 5.1.2 / Section 6.6.4] enables direct cross-exercise comparisons of excursion, velocity, and joint depth. This reveals how different loading demands—bilateral squat symmetry versus unilateral lunge propulsion—impact tracking stability and form discrimination [source: Section 4.2 / Section 5.3].

### 14.1.2. Contribution 2: Failure-Mode-Aware Pose Extraction
We reject the "black-box" accuracy assumptions of commercial pose estimation tools by explicitly characterising where, when, and why monocular tracking degrades. This characterisation is formalized as a four-part failure-mode taxonomy (detailed in Section 14.2) that maps tracking loss to specific physical, geometric, and data-scale mechanisms [source: Section 5.5 / Section 6.6].

### 14.1.3. Contribution 3: The Continuous Validation-to-Screening Uncertainty Transfer Chain
The methodological spine of this thesis is the continuous mathematical chain that connects optoelectronic ground-truth validation to baseline gating and sequence modeling across five sequential stages:
1.  **Ground-Truth Validation**: Chapter 6 evaluated single-camera video against synchronized 3D motion capture and force-plate ground truth across $n = 48$ drop-jump landing trials, establishing 95% Limits of Agreement (LoA) for knee biomarkers [source: Section 6.1 / Section 6.3].
2.  **Variance Decomposition**: Chapter 8 converted LoA bounds into statistical variances, decomposing total error into a transferable projection component ($\sigma^2_{\text{proj}}$, systematic perspective foreshortening) and a non-transferable motion component ($\sigma^2_{\text{mot}}$, landing jitter) [source: Section 8.2 / Section 8.3].
3.  **Inverse-Variance Weighting**: Inverse-variance weighting on transferable projection components defined the relative trustworthiness of each biomarker: Peak Flexion ($57.15\%$), Start Flexion ($22.63\%$), Range of Motion ($15.30\%$), and Joint Descent Velocity ($4.92\%$) [source: Section 8.4].
4.  **Empirical Gating Confirmation**: Chapters 9 and 11 transferred these weights to squats and lunges to gate personalised deviation screening. The baseline tracking engine directly confirmed the validation splits: gating was driven by high-confidence peak flexion (tight $\pm 11.99^\circ$ noise floor), while low-confidence descent velocity (wide $\pm 40.86^\circ/\text{s}$ noise floor) remained quiet except during a genuine velocity surge of $110.62^\circ/\text{s}$ on squat Repetition 6 [source: Section 9.3 / Section 11.2].
5.  **Independent Experimental Re-Confirmation**: Chapter 13 conducted Leave-One-Subject-Out (LOSO) cross-validation to evaluate whether sequence models (LSTMs) could extract discriminative signals from trajectory shape [source: Section 13.2.1]. A simple logistic regression classifier trained on peak flexion alone achieved balanced accuracies of **$81.36\%$** (squats) and **$81.50\%$** (lunges), whereas deep LSTM models collapsed to or below random guessing ($50.00\%$ squat, $39.17\%$ lunge) [source: Section 13.3].

#### Two Independent Confirmations & Bounded Screening
The convergence of two completely independent pathways—the empirical gating behavior of personalised baselines (Chapters 9/11) and the LOSO sequence classification experiment (Chapter 13)—on the exact same dominant biomarker (**peak knee flexion**) validates the transferability of the Chapter 8 weights. This uncertainty chain bounds all screening decisions with validated precision ($\pm 11.99^\circ$ peak flexion vs. $\pm 40.86^\circ/\text{s}$ descent velocity), advancing beyond weaker validation paradigms that rely solely on cross-cohort agreement (such as squat laboratory-vs-Penn Action cohort agreement in Section 4.3 [CITE: Zhang_Penn_Action_2013]) by providing ground-truth mathematical error propagation.

### 14.1.4. Contribution 4: Counterfactual XAI on Deterministic Rules
The fourth contribution is a glass-box explainability layer (Chapter 12) explaining the decisions of the rule-based screening layer (Chapter 10) [source: Section 10.1 / Section 12.1]. Because screening logic is deterministic, counterfactual explanations are **faithful by construction**, calculating exact physical joint margins ($M_i$) with zero approximation error [source: Section 12.3]. This led to the deprecation of local surrogate models (SHAP/LIME), which perturb inputs to approximate black boxes and introduce explanation infidelity [source: Section 12.2]. The engine renders descriptive counterfactual statements and resolves parameter coupling via Minimal Kinematic Intervention (MKI) arithmetic [source: Section 12.4 / Section 12.5].

---

## 14.2. The Failure-Mode Taxonomy

We categorize the pipeline's failure modes into four named categories based on empirical evidence across the thesis.

### 14.2.1. Occlusion Failure (Sagittal Self-Occlusion)
*   **Mechanism**: Loss of line-of-sight between camera sensor and target joint center caused by intervening body segments during unilateral or asymmetric movement.
*   **Evidence**: Unilateral lunge tracking (Chapter 5) suffered a $30.68\%$ tracking loss across the assembled cohort, concentrated in Subject 8 (`PM_112`, **$100.0\%$ failure rate**, 12/12 reps failed) and Subject 5 (`PM_042`, **$92.3\%$ failure rate**, 12/13 reps failed) due to the loaded leg being occluded by the trailing limb during deep flexion [source: Section 5.1.1]. Similarly, asymmetric drop-jump landing absorption (Chapter 6) occluded the far leg, reducing visibility to **$\sim 0\%$** [source: Section 6.6.2].
*   **Synthesis**: While bilateral squats permit contralateral limb fallback to maintain $100\%$ completion [source: Section 5.1.1], unilateral loading tasks are highly vulnerable to sagittal self-occlusion under monocular tracking.

### 14.2.2. Recording-Limit Failure (Data Truncation)
*   **Mechanism**: Operational data truncation where raw recording duration is shorter than the physical time window required to compute a biomarker.
*   **Evidence**: Drop-jump dynamic Time-to-Stabilisation (TTS) in Chapter 6 was dropped because OpenCap video files truncated abruptly **$0.05\text{ s}$ to $0.2\text{ s}$** after final landing contact (IC2), preventing evaluation over the required $0.5\text{ s}$ quiet-stance window [source: Section 6.6.1].
*   **Synthesis**: A dataset protocol design limitation highlighting the need for sufficient pre- and post-movement recording buffers.

### 14.2.3. Projection-Bias Failure (Spatial Foreshortening)
*   **Mechanism**: Geometric distortion where a 2D sensor over- or underestimates 3D joint angles as limbs move out of the camera's orthogonal plane.
*   **Evidence**: Validation against 3D motion capture (Chapter 6) revealed systematic peak overestimation bias of **$+10.52^\circ$** (timing-clean) and **$+19.72^\circ$** (peak-to-peak) during deep landing flexion, alongside shallow-flexion underestimation of **$-6.69^\circ$** [source: Section 6.2.1 / Section 6.3]. Lag tests ($14.80^\circ \rightarrow 20.15^\circ$ MAE under peak matching) and software definition tests ($1.64^\circ$ mean offset) confirmed the bias is purely spatial [source: Section 6.5].
*   **Synthesis**: Projection bias acts as a stable systematic offset. Consequently, Chapter 10's Option B baseline subtraction mathematically cancels this bias ($\Delta_i = |(x_{\text{true}} + \text{bias}) - (\mu_{\text{true}} + \text{bias})| = |x_{\text{true}} - \mu_{\text{true}}|$) within single-subject sessions [source: Section 10.3].

### 14.2.4. Data-Scale / Model-Mismatch Failure (Overfitting)
*   **Mechanism**: Performance collapse when a high-capacity model memorizes subject-specific calibration noise on small cohorts rather than generalizing kinematic boundaries.
*   **Evidence**: Evaluating trajectory shape via LOSO cross-validation (Chapter 13) caused the regularized LSTM to collapse to majority guessing under Scheme B ($50.00\%$ squat, $39.17\%$ lunge balanced accuracy) and perform near chance under Scheme A ($53.79\%$ squat, $53.78\%$ lunge), far below the single-feature peak flexion classifier ($81.36\%$ squat, $81.50\%$ lunge) [source: Section 13.3].
*   **Synthesis**: Demonstrates that complex deep sequence models are poorly suited for biomechanical screening at small cohort scales ($7\text{--}9$ subjects).

### 14.2.5. Taxonomy Value
This taxonomy provides developers with a predictive roadmap: outlining where tracking fails (far-limb unilateral joints), why spatial biases occur (projection foreshortening), and how model complexity must be constrained to match data scale.

---

## 14.3. Cross-Exercise Kinematic Divergence

Kinematic form discrimination is highly task-dependent, demonstrating that form deviations do not manifest uniformly across exercises.

### 14.3.1. Descent-Localized vs. Ascent-Discriminative Kinematics
*   **Squat Form Discrimination (Descent-Localized)**: Squat form quality in Chapter 4 is strictly localized to eccentric descent: peak flexion depth ($d = 1.7306$), ROM ($d = -1.4484$), and peak descent velocity ($d = 0.8216$) discriminated form, whereas concentric ascent velocities did not (peak ascent $d = -0.5049$, 95% CI: $[-1.4838, +0.0848]$; mean ascent $d = -0.4996$, 95% CI: $[-1.7017, +0.1301]$ crossed zero) [source: Section 4.2].
*   **Lunge Form Discrimination (Ascent-Discriminative)**: Lunge form discrimination in Chapter 5 extended strongly into concentric ascent: peak ascent velocity ($d = -0.9721$, 95% CI: $[-1.6403, -0.6554]$) and mean ascent velocity ($d = -0.7962$, 95% CI: $[-2.0731, -0.0807]$) reliably differentiated form groups [source: Section 5.2 / Section 5.3.1].

### 14.3.2. Biomechanical Mechanism of Divergence
This divergence reflects physical loading demands: squats are bilateral and symmetric, allowing controlled concentric recovery regardless of descent depth [source: Section 5.3.2]. Lunges are asymmetric and unilateral; incorrect lunges reach excessive depth, placing the subject in a biomechanically disadvantaged posture that demands a forceful, propulsive front-leg push-off to regain standing balance [source: Section 5.3.2].

### 14.3.3. Methodological Significance
Discriminative kinematic signals are phase- and task-specific. Evaluating a single exercise in isolation would have missed this divergence, justifying multi-exercise integration under a unified pipeline (Contribution 1).

---

## 14.4. Limitations of the Thesis as a Whole

We consolidate individual chapter limitations into five thesis-level themes:

1.  **Cohort Size Constraints**: Datasets were restricted to small subject counts (9 squat, 7 lunge, 8 drop-jump subjects) [source: Section 4.1.1 / Section 5.1.1 / Section 6.1]. Chapter 13 provides direct proof of this boundary: deep LSTMs overfitted to subject identities ($\approx 54\%$ balanced accuracy), whereas single-feature peak flexion achieved $81.36\%$ balanced accuracy [source: Section 13.3].
2.  **Sagittal-Camera-Only Setup**: Monocular sagittal views make contralateral occlusion a recurring boundary, causing lunge subject exclusions (Subjects 5 and 8 dropped) and preventing drop-jump inter-limb asymmetry tracking ($\sim 0\%$ far-limb visibility) [source: Section 14.2.1]. Single sagittal cameras cannot detect out-of-plane frontal movements (valgus or pelvic drop).
3.  **Exercise Battery Scope**: The pipeline evaluated three exercises (squat, lunge, drop-jump) [source: Section 14.1.1]. Multi-planar athletic maneuvers (cutting, pivoting) were not evaluated, and vertical jump trajectory extraction was scoped out due to data access dependencies.
4.  **Track B Architectural Status**: Personalised baselines (Chapter 9) and digital twins (Chapter 11) are Track B software demonstrations evaluated on within-session repetition sequences (pseudo-sessions), not live longitudinal deployments over weeks.
5.  **Screening-not-Prediction Boundary**: Screening thresholds and baseline gating rules are statistical heuristics grounded in empirical cohort distributions; they are **not** clinically validated diagnostic cut-offs. The framework identifies coordinate shifts relative to movement templates; it does not predict injury risk or calculate clinical probabilities.

---

## 14.5. Consolidated Future Work

We consolidate future work axes across the completed chapters:
*   **Expanded Exercise Battery**: Integrate vertical jump trajectories using the Bath BioCV dataset to evaluate high-velocity vertical propulsion.
*   **Longitudinal Digital Twin Deployment**: Collect multi-session datasets (10–14 sessions per subject over weeks) to validate baseline update templates in live deployments.
*   **Motion-Error Validation**: Conduct optoelectronic validation for squats and lunges to directly measure motion error ($\sigma^2_{\text{mot}}$), replacing the projection-only transfer assumption [source: Section 8.4.1].
*   **Temporal Persistence Twin Logic**: Implement temporal persistence rules in the digital twin (Chapter 11) to distinguish transient technique errors from sustained physiological adaptations [source: Section 11.3].
*   **Large-Cohort Sequence Pretraining**: Implement self-supervised pretraining (contrastive learning, masked autoencoding) on large multi-subject datasets (hundreds of subjects) where representation learning can extract coordination patterns without overfitting [source: Section 13.5].

---

## 14.6. Closing Statement

In summary, this dissertation delivers a monocular markerless kinematic screening framework extracting comparable biomarkers across squats, lunges, and drop-jumps. By mapping optoelectronic limits of agreement to transferable projection uncertainty, the framework propagates validated confidence bounds to qualify screening decisions, providing faithful-by-construction counterfactual explanations for rule-based flags.

Consistent with the writeup plan, the project's evolution narrative—detailing the transition from an initial predictive injury classifier ambition to a validated kinematic screening framework—is placed exclusively in Chapter 15 (Conclusion) as a final reflective note on methodological maturity [source: writeup_plan.md line 554]. Chapter 14 has established the cross-exercise findings, quantified uncertainty weights, and failure-mode taxonomy supporting this architecture.
