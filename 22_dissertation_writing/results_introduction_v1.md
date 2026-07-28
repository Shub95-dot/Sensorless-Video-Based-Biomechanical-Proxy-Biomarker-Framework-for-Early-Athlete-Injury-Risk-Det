# Chapter 1: Introduction

Sports injury-risk screening represents a critical component of athletic preparation and musculoskeletal rehabilitation, aimed at identifying movement deviations before they manifest as clinical pathologies [CITE: Bahr_2016]. Traditional biomechanical screening protocols depend heavily on laboratory-grade instrumentation—such as multi-camera optoelectronic motion capture, force plates, or body-worn inertial sensors—to extract precise joint kinematics and kinetics [CITE: Mundt_2019]. While highly accurate, these technologies are limited by high equipment costs, time-intensive calibration procedures, and the need for specialized personnel, confining their use to elite laboratories and research settings [CITE: Guess_2020]. Consequently, high-throughput, routine movement screening is non-scalable to everyday athletic training environments and community physical therapy clinics. In recent years, monocular, sensorless, markerless video pose estimation has emerged as a potentially transformative alternative, leveraging deep convolutional neural networks to extract joint center coordinates from standard 2D video recorded on consumer-grade devices [CITE: OpenCap_2022] [CITE: MP_2020]. However, because these single-camera systems estimate 3D movements from a flat 2D perspective, their coordinate tracking is subject to systematic geometric distortions and tracking noise [CITE: Colyer_2018]. Validating the physical measurement accuracy of these markerless systems against laboratory gold standards is an essential prerequisite before they can be trusted for clinical screening applications [CITE: open_source_poses_2021].

This dissertation establishes a validated markerless kinematic screening framework, but we must define its clinical boundaries immediately: **this work delivers a movement screening framework, not an injury prediction or clinical diagnostic system**. The primary objective of kinematic screening is to identify significant coordinate deviations from established baseline templates, qualifying these deviations relative to the measurement uncertainty of the tracking system. Screening requires no longitudinal injury-outcome data, as its utility lies in characterizing execution anomalies compared to standard movement patterns [CITE: Bahr_2016]. In contrast, injury prediction or diagnostic classification requires prospective tracking of injury occurrence, clinical outcomes, and long-term cohort follow-ups—which are absent in this project. By explicitly scoping this work to a screening framework, we establish a mathematically bounded and transparent pipeline that avoids the ungrounded clinical claims common in black-box sports machine learning models [CITE: Halilaj_2018].

---

## 1.1. Technical Motivation: The Screening Gap

The central limitation preventing the widespread adoption of markerless pose estimation in physical therapy is the absence of integrated, transparent error characterisation. Existing commercial and open-source pose estimation models typically output raw joint coordinate sequences without indicating their underlying spatial or temporal precision [CITE: MP_2020]. In a clinical setting, this makes it impossible to distinguish between a genuine biomechanical movement deviation (such as a knee loading asymmetry or an excessive flexion depth) and tracking noise (such as camera perspective foreshortening or coordinate jitter).

To address this gap, this dissertation is structured around a continuous validation-to-screening chain. In Chapter 6, we execute a rigorous, frame-by-frame optoelectronic and force-plate validation comparison using dynamic drop-jump landing trials, establishing the limits of agreement (LoA) for sagittal knee flexion biomarkers [source: Chapter 6]. In Chapter 8, we decompose these validated error bounds to isolate perspective-based projection errors from landing-speed motion errors, establishing inverse-variance uncertainty weights for squats and lunges [source: Chapter 8]. This validation-derived foundation ensures that downstream personalised tracking (Chapter 9) and rule-based screening (Chapter 10) are bounded by empirical measurements of pipeline precision, ensuring that noisy biomarkers are down-weighted and false alarms are suppressed.

---

## 1.2. Scope and Modality-Independent Approach

The clinical utility of the screening framework is demonstrated across three fundamental athletic movements, representing a progression in loading complexity:
1.  **Bilateral Squat (Chapter 4)**: A slow, controlled, symmetric movement where load is distributed evenly between both limbs, serving as a baseline evaluation of sagittal flexion depth and eccentric speed [source: Chapter 4].
2.  **Unilateral Lunge (Chapter 5)**: A slow, controlled, asymmetric loading task that requires unilateral propulsion and recovery, testing the pipeline's capability under asymmetric coordinates [source: Chapter 5].
3.  **Dynamic Drop-Jump Landing (Chapter 6)**: A high-velocity, rapid-impact bilateral task where movement speed and ground impact generate extreme joint angular velocities [source: Chapter 6].

Crucially, the drop-jump landing cohort serves **exclusively as a ground-truth measurement validation benchmark**, comparing the single-camera markerless pipeline directly to synchronized laboratory motion capture and force-plate references under dynamic conditions [source: Section 6.1]. The drop-jump is not analyzed as a form-quality classification task. By using the drop-jump as a validation anchor, we qualify the systematic projection biases (such as deep flexion overestimation) inherent in monocular sagittal-view tracking, enabling these characterized errors to be integrated directly into the squat and lunge screening layers.

---

## 1.3. Preview of the Four Novelty Contributions

This dissertation presents a cross-cutting biomechanical architecture organized around four core novelty contributions, which are fully synthesized and discussed in Chapter 14:
*   **Contribution 1: Cross-Exercise Integration under a Unified Pipeline**: We integrate squats, lunges, and drop-jumps under a unified coordinate convention, enabling direct cross-exercise comparisons of joint depth, velocity, and range of motion [source: Section 14.1.1].
*   **Contribution 2: Failure-Mode-Aware Pose Extraction (Taxonomy)**: We reject the "black-box" validation approach by formalizing a four-part failure-mode taxonomy (occlusion, recording limits, projection bias, and data-scale mismatch) that maps pose-tracking degradation to specific physical and technical sources [source: Section 14.1.2 / Section 14.2].
*   **Contribution 3: Uncertainty-Weighted Screening Transfer**: We develop a mathematical transfer spine that converts ground-truth limits of agreement into statistical variances, propagating inverse-variance weights to qualify and gate screening decisions on unvalidated datasets [source: Section 14.1.3].
*   **Contribution 4: Counterfactual XAI on Deterministic Rules**: We implement a glass-box explainability layer that explains rule-based screening flags through exact physical joint margins, guaranteeing zero approximation error and rendering SHAP/LIME surrogate models obsolete [source: Section 14.1.4].

---

## 1.4. The Project Origin Story (Evolution Seed)

A key methodological contribution of this research is the scientific maturation of its clinical scope. The project was initially conceived around a highly ambitious injury-prediction framework, reflecting a long-term research vision designed to classify physical injury risk using temporal sequence networks and self-supervised representation learning. 

During the technical implementation, however, a critical mismatch became apparent: while the single-camera pipeline could rigorously extract and validate sagittal kinematics, the available dataset lacked prospective injury outcomes, clinical diagnostic labels, and multi-week longitudinal follow-up. Forcing an injury-prediction claim under these constraints would have required training ungrounded black-box classifiers on small-subject cohorts, leading to severe subject-memorisation overfitting. Recognizing this limitation, the dissertation deliberately scoped the active pipeline to a validated, transparent kinematic screening foundation. The advanced components of the broader vision—specifically, self-supervised pretraining, temporal sequence modeling, and longitudinal twin tracking—are explicitly positioned as future research directions grounded in the empirical sequence modeling results of Chapter 13. The reflective payoff and methodological defense of this scoping transition are detailed in Chapter 15.

---

## 1.5. Dissertation Structure Overview

The remainder of this dissertation is organized as follows:
*   **Chapter 2 (Methods)**: Details the monocular camera configuration, the coordinate conventions, the MediaPipe-based pose estimation pipeline, and the subject-clustered bootstrapping statistical procedures [source: methods_v2.md].
*   **Chapter 3 (Reserved - Literature Review)**: Reserved for a consolidated Literature Review. In this dissertation, literature engagement is distributed contextually across the results chapters, where each finding is positioned against relevant prior work at its point of use. This is a deliberate methodological choice for a project this methodologically dense, where contextual placement provides greater interpretive value to the reader than a front-loaded survey.
*   **Chapter 4 (Squat Kinematic Screening)**: Presents the results of the squat screening evaluation, focusing on eccentric-localized form discrimination and laboratory-vs-Penn Action reproducibility [CITE: Zhang_Penn_Action_2013] [source: Chapter 4].
*   **Chapter 5 (Lunge Kinematic Screening)**: Documents lunge kinematics, highlighting the concentric-ascent velocity divergence from squats [source: Chapter 5].
*   **Chapter 6 (Drop-Jump Validation)**: Presents the ground-truth optoelectronic validation results, characterizing constant deep-flexion projection biases and lag-anchoring stability [source: Chapter 6].
*   **Chapter 7 (Reserved - Framework Overview)**: Reserved for a Framework Overview. The framework's components (uncertainty weighting, personalised baseline, digital twin, rule-based screening, and counterfactual XAI) are introduced and synthesised individually in Chapters 8-12, with their integrated relationships treated fully in the Discussion (Chapter 14, Section 14.1).
*   **Chapter 8 (Uncertainty-Weighted Screening Framework)**: Details the variance conversion, projection/motion decomposition, and the inverse-variance transfer weights [source: Chapter 8].
*   **Chapter 9 (Personalised Session-to-Session Baselines)**: Demonstrates the gated baseline tracking engine under pseudo-session sequences [source: Chapter 9].
*   **Chapter 10 (Rule-Based Screening Layer)**: Documents the deterministic, literature-grounded decision rules and screening flags [source: Chapter 10].
*   **Chapter 11 (Biomechanical Digital Twin)**: Details continuous-update reference evolution and explainable exclusion gating [source: Chapter 11].
*   **Chapter 12 (Counterfactual Explainable AI (XAI))**: Presents the exact-margin counterfactual explanations and Minimal Kinematic Intervention (MKI) coupling logic [source: Chapter 12].
*   **Chapter 13 (Temporal Sequence Model + Self-Supervised Future Work)**: Evaluates within-repetition trajectory shape modeling and LSTM overfitting diagnostics under LOSO cross-validation [source: Chapter 13].
*   **Chapter 14 (General Discussion)**: Synthesizes the four novelty contributions and details the Failure-Mode Taxonomy [source: Chapter 14].
*   **Chapter 15 (Conclusion)**: Summarizes the dissertation findings, consolidates future research directions, and delivers the closing evolution reflection.
