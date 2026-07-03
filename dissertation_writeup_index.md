# Dissertation Writeup Index

This is the running one-line-per-section writeup map for the Sensorless Biomechanical Screening Framework. It is updated at the close of every phase to track the writeup status of each chapter and section.

## Exercise Modality Chapters

1. **Chapter 4: Squat Kinematic Screening**
   - **Section 4.1: YouTube Cohort Analysis (n=10)**: Draft complete. Descriptive kinematics range established; exemplar profiles mapped.
   - **Section 4.2: REHAB24-6 Squat Integration (n=98 reps)**: Draft complete (`14_rehab24_outputs/drafts/squat_results_v4.md`). Form-discrimination validated (correct vs. incorrect difference in peak flexion, ROM, descent/ascent velocities, and jerk).
   - **Section 4.3: Cross-Cohort Squat Comparison**: Draft complete. Verified pipeline generalization across YouTube in-the-wild and REHAB24-6 lab cohorts.

2. **Chapter 5: Lunge Kinematic Screening**
   - **Section 5.1: REHAB24-6 Lunge Cohort (n=61 reps)**: Draft complete (`15_rehab24_lunge_outputs/drafts/lunge_results_v1.md`). Form-discrimination validated (kinematic signature matches squats; ascent velocities discriminate propulsion).
   - **Section 5.2: Cross-Exercise Comparative Analysis**: Draft complete. Comparative forest plots and subject-clustered bootstrapping analysis completed.

3. **Chapter 6: Drop-Jump Validation (OpenCap)**
   - **Section 6.1: Synchronization and Event Detection**: **ANALYSIS COMPLETE / WRITEUP DEFERRED**. GRF-anchored lag alignment verified and temporal events mapped.
   - **Section 6.2: Biomarker Agreement Summary**: **ANALYSIS COMPLETE / WRITEUP DEFERRED**. 4+1 biomarker agreement final table produced (`16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv`).
   - **Section 6.3: Projection Bias vs. Depth (Static Peak)**: **ANALYSIS COMPLETE / WRITEUP DEFERRED**. Constant deep-flexion overestimation bias validated (+10.5° timing-clean; +19.7° peak-to-peak) and shown to be depth-independent in the landing band.
   - **Section 6.4: Robustness and Limitations**: **ANALYSIS COMPLETE / WRITEUP DEFERRED**. Bias verified similar across symmetric/asymmetric landings. Documented TTS, occlusion, and timing-contamination limits.

4. **Chapter 7: Vertical Jump Pipeline**
   - **Section 7.1: Pose-Extraction and Event Identification**: *Next Active*.
   - **Section 7.2: Kinematic Analysis and Biomarkers**: *Next Active*.

## Architectural Demonstration Chapters (Track B Future Work)

5. **Chapter 8: Uncertainty-Weighted Screening Framework (Track B Demo)**
   - **Section 8.1: Purpose and Methodology**: **ANALYSIS DONE / WRITEUP DEFERRED**. Framework designed for combining biomarkers weighted by validated measurement uncertainty (inverse-variance) without producing combined risk scores or rep classification.
   - **Section 8.2: Variance Decomposition & Provenance**: **ANALYSIS DONE / WRITEUP DEFERRED**. Decomposed total uncertainty into transferable projection component and non-transferable motion component. Peak flexion split measured (static peak), ROM propagated (endpoints), contact flexion and loading rate splits assumed (immaterial via sensitivity sweep).
   - **Section 8.3: Cross-Exercise Weight Transfer**: **ANALYSIS DONE / WRITEUP DEFERRED**. Projection component transfers to squat/lunge (peak 57%, contact 23%, ROM 15%, velocity 5%), motion-component validation deferred.
   - **Section 8.4: Worked Repetition Illustration**: **ANALYSIS DONE / WRITEUP DEFERRED**. Projection-weighted characterisation run on REHAB24-6 squats (PM_008) and lunges (PM_021), illustrating peak flexion dominance.

6. **Chapter 9: Personalised Session-to-Session Baselines**
   - **Section 9.1: Progression Tracking Architecture**: Planned.

7. **Chapter 10: Temporal Sequence Models (LSTM)**
   - **Section 9.1: Sequence Classification & Biomarker Validation**: Planned.

8. **Chapter 11: Biomechanical Digital Twin**
   - **Section 10.1: Continuous-Update Infrastructure Design**: Planned.

9. **Chapter 12: Self-Supervised Pretraining**
   - **Section 11.1: Pretraining Framework and Sample Constraints**: Planned.
