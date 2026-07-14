# Dissertation Writeup Index

This is the running one-line-per-section writeup map for the Sensorless Biomechanical Screening Framework. It is updated at the close of every phase to track the writeup status of each chapter and section.

## Exercise Modality Chapters

1. **Chapter 4: Squat Kinematic Screening**
   - **Section 4.1: YouTube Cohort Analysis (n=10)**: **DRAFTED** (`22_dissertation_writing/results_squat_v1.md`). Descriptive kinematics range established; exemplar profiles mapped.
   - **Section 4.2: REHAB24-6 Squat Integration (n=98 reps)**: **DRAFTED** (`22_dissertation_writing/results_squat_v1.md`). Form-discrimination validated (correct vs. incorrect difference in peak flexion, ROM, descent/ascent velocities, and jerk).
   - **Section 4.3: Cross-Cohort Squat Comparison**: **DRAFTED** (`22_dissertation_writing/results_squat_v1.md`). Verified pipeline generalization across YouTube in-the-wild and REHAB24-6 lab cohorts.

2. **Chapter 5: Lunge Kinematic Screening**
   - **Section 5.1: REHAB24-6 Lunge Cohort (n=61 reps)**: **DRAFTED** (`22_dissertation_writing/results_lunge_v1.md`). Form-discrimination validated (kinematic signature matches squats; ascent velocities discriminate propulsion).
   - **Section 5.2: Cross-Exercise Comparative Analysis**: **DRAFTED** (`22_dissertation_writing/results_lunge_v1.md`). Comparative forest plots and subject-clustered bootstrapping analysis completed.

3. **Chapter 6: Drop-Jump Validation (OpenCap)**
   - **Section 6.1: Synchronization and Event Detection**: **DRAFTED** (`22_dissertation_writing/results_dropjump_validation_v1.md`). GRF-anchored lag alignment verified and temporal events mapped.
   - **Section 6.2: Biomarker Agreement Summary**: **DRAFTED** (`22_dissertation_writing/results_dropjump_validation_v1.md`). 4+1 biomarker agreement table produced.
   - **Section 6.3: Projection Bias vs. Depth (Static Peak)**: **DRAFTED** (`22_dissertation_writing/results_dropjump_validation_v1.md`). Constant deep-flexion overestimation bias validated ($+10.52^\circ$ timing-clean; $+19.72^\circ$ peak-to-peak) and shown to be depth-independent in the landing band.
   - **Section 6.4: Robustness and Limitations**: **DRAFTED** (`22_dissertation_writing/results_dropjump_validation_v1.md`). Bias verified similar across symmetric/asymmetric landings. Documented TTS, contralateral occlusion, and timing-contamination limits.

4. **Chapter 7: Vertical Jump Pipeline**
   - **Section 7.1: Pose-Extraction and Event Identification**: *Next Active*.
   - **Section 7.2: Kinematic Analysis and Biomarkers**: *Next Active*.

## Architectural Demonstration Chapters (Track B Future Work)

5. **Chapter 8: Uncertainty-Weighted Screening Framework (Track B Demo)**
   - **Section 8.1: Purpose and Methodology**: **DRAFTED** (`22_dissertation_writing/results_uncertainty_framework_v1.md`). Framework designed for combining biomarkers weighted by validated measurement uncertainty (inverse-variance) without producing combined risk scores or rep classification.
   - **Section 8.2: Variance Decomposition & Provenance**: **DRAFTED** (`22_dissertation_writing/results_uncertainty_framework_v1.md`). Decomposed total uncertainty into transferable projection component and non-transferable motion component. Peak flexion split measured (static peak), ROM propagated (endpoints), contact flexion and loading rate splits assumed (immaterial via sensitivity sweep).
   - **Section 8.3: Cross-Exercise Weight Transfer**: **DRAFTED** (`22_dissertation_writing/results_uncertainty_framework_v1.md`). Projection component transfers to squat/lunge (peak 57%, contact 23%, ROM 15%, velocity 5%), motion-component validation deferred.
   - **Section 8.4: Worked Repetition Illustration**: **DRAFTED** (`22_dissertation_writing/results_uncertainty_framework_v1.md`). Projection-weighted characterisation run on REHAB24-6 squats (PM_008) and lunges (PM_021), illustrating peak flexion dominance.

6. **Chapter 9: Personalised Session-to-Session Baselines (Track B Demo)**
   - **Section 9.1: Purpose and Methodology**: **DRAFTED** (`22_dissertation_writing/results_baseline_v1.md`). Personalised longitudinal monitoring architecture demonstrated on within-session repetitions (pseudo-time axis). Gated deviation triggers only beyond camera measurement-noise floor.
   - **Section 9.2: Gated Detection Verification**: **DRAFTED** (`22_dissertation_writing/results_baseline_v1.md`). Both quiet correct reps (normal variations stay within floor) and firing incorrect reps (peak flexion deviations of 20-36° flagged) demonstrated for squat Subject `PM_113` and lunge Subject `PM_104`.
   - **Section 9.3: Uncertainty Gating Analysis**: **DRAFTED** (`22_dissertation_writing/results_baseline_v1.md`). Gating decisions driven by high-confidence peak flexion (tight ±11.99° floor); low-confidence descent velocity (wide ±40.86°/s floor) remains quiet except on a single genuine velocity surge ($110.62^\circ/\text{s}$). Empirically validates uncertainty weights.
   - **Section 9.4: Personalised-vs-Group Tracking**: **DRAFTED** (`22_dissertation_writing/results_baseline_v1.md`). Analytical contrast between group cohort comparisons and personalized tracking relative to own template. Gating floor constraint and timeline limits documented.urce: `baseline_design.md`.

7. **Chapter 10: Temporal Sequence Models (LSTM)**
   - **Section 9.1: Sequence Classification & Biomarker Validation**: **ANALYSIS DONE / WRITEUP DEFERRED** (Phase 12). Controlled LOSO comparison completed; Outcome 3 (Endpoint Dominance) validated.

8. **Chapter 11: Biomechanical Digital Twin**
   - **Section 11.1: Continuous-Update Infrastructure Design**: **DRAFTED** (`22_dissertation_writing/results_digital_twin_v1.md`). Developed incremental rolling mean update rules with conditional aberration rejection.
   - **Section 11.2: Reference Evolution & Gated Updates**: **DRAFTED** (`22_dissertation_writing/results_digital_twin_v1.md`). Validated reference evolution (PM_113: $72.98^\circ \rightarrow 69.21^\circ$) and locking behavior across correct and incorrect pseudo-sessions.
   - **Section 11.3: Explainable Exclusion & Humility Wording**: **DRAFTED** (`22_dissertation_writing/results_digital_twin_v1.md`). Implemented measurement-based exclusion messages with epistemic humility. Transient-vs-sustained adaptation limits analyzed.

9. **Chapter 12: Self-Supervised Pretraining**
   - **Section 11.1: Pretraining Framework and Sample Constraints**: **FUTURE WORK (evidence-grounded, not implemented)**. Trajectory classification overfitting (Phase 12) demonstrates that representation learning on deep sequence models is unlikely to generalize at this cohort scale ($N=9$ squats, $N=7$ lunges). Future work outlines requirements for larger cohorts.

## Dissertation Chapter Drafts

10. **Methods Chapter** · **DRAFTED** (`22_dissertation_writing/methods_v2.md`)
    - Covers: pipeline architecture, cohort assembly (REHAB24-6 + OpenCap + YouTube), OpenCap validation, uncertainty decomposition & transfer, personalised baseline & digital twin, rule-based screening (Step 10), counterfactual XAI (Step 11), statistical methods. ~2,950 words. Every number carries an inline `[source:]` tag. Results deferred.
    - Status: First chapter section drafted. Distinct from deferred results/discussion sections.

## Component — Digital Twin (Track B demo) · DRAFTED (`22_dissertation_writing/results_digital_twin_v1.md`)
- Purpose — architectural demonstration of continuous-update personalisation: extends the Phase 8 baseline so the per-subject reference UPDATES as pseudo-sessions arrive. Non-predictive; NOT a learned model; NOT real longitudinal. Source: `19_digital_twin_outputs/twin_design.md`.
- Mechanism — twin state = running reference mean + Phase-7 noise floor. Within-noise reps update the reference (running mean); deviation reps are excluded (aberration rejection) but counted, flagged, and explained. Simple arithmetic update, no learned parameters. Source: `twin_design.md` + `phase9_digital_twin.py`.
- Result — reference evolves on clean reps (squat PM_113: 72.98→69.21° across reps 3-5), locks when incorrect reps deviate past floor. Noise band tracks the evolving reference. Source: `worked_example_twin.csv` + `twin_tracking.png`.
- Exclusion explanation (design feature) — on exclusion, twin outputs a MEASUREMENT-BASED reason: deviation exceeded validated measurement uncertainty; from a single observation, transient fluctuation vs genuine sustained change cannot be distinguished. Epistemic humility, not quality judgment. Source: `twin_design.md`.

## Component — Rule-Based Screening Layer (Step 10, Track A core) · DRAFTED (`22_dissertation_writing/results_screening_layer_v1.md`)
- Purpose — named-rule screening layer turning validated biomarkers into screening flags with clinical meaning. Personalised-deviation rules grounded in Phase 7 noise floors. Source: `20_screening_outputs/screening_rules_design.md`.
- Rules — EXCESS_DEPTH (peak < baseline − 11.99°), EXCESS_ROM (ROM > baseline + 23.17°), EXCESS_VELOCITY (velocity > baseline + 40.86°/s). Source: `screening_rules_design.md` + `phase10_rule_screening.py`.
- Result — correct reps 3-5 gated NOT_FLAGGED; incorrect reps 6-10 fire SCREENING_POSITIVE. Source: `worked_example_screening.csv`.

## Component — Counterfactual XAI (Step 11, Track A novelty #4) · DRAFTED (`22_dissertation_writing/results_xai_v1.md`)
- Purpose — counterfactual explanation of rule-based screening flags: faithful by construction (exact margin calculations, not post-hoc approximations). Source: `21_xai_outputs/xai_design.md`.
- Templates — descriptive (not prescriptive) counterfactual statements per rule. MKI as a descriptive set of conditions. Confidence grading via 0.5×NF buffer. Source: `xai_design.md` + `phase11_counterfactual_xai.py`.
- Result — explanations rendered for PM_113 (squat) and PM_104 (lunge). Source: `worked_example_explanations.json`.

## Component — Temporal Sequence Models (Phase 12, Track B demo) · ANALYSIS DONE / WRITEUP DEFERRED
- Purpose — controlled comparison of within-rep knee-flexion trajectory shape classification (LSTM deep learning vs. shallow shape-feature baseline) against static endpoints under Leave-One-Subject-Out (LOSO) cross-validation to isolate value-add of sequence shape. Source: `23_temporal_model_outputs/temporal_model_design.md`.
- Method — linear interpolation to $100$-point sequence. Two normalizations: Scheme A (offset-subtracted, keeps amplitude), Scheme B (min-max scaled, shape-only). Models: Naive guess-majority (73.47% Squat / 59.02% Lunge), Peak Flexion Logistic Regression, regularized shape-feature Logistic Regression (6 amplitude-invariant features), and heavily regularized LSTM. Source: `temporal_model_design.md` + `phase12_temporal_sequence_model.py`.
- Result — validated **Outcome 3 (Endpoint Dominance)**. Peak flexion alone is the optimal classifier (Squat: 81.36% Balanced Accuracy; Lunge: 81.50% Balanced Accuracy). Trajectory shape features perform at or below chance (Squat: 33.76% Balanced Accuracy; Lunge: 58.39% Balanced Accuracy). Source: `temporal_model_comparison.csv` + `temporal_model_evaluation_report.md`.
- Overfitting Finding — under Scheme B (shape-only), the LSTM collapses completely to majority-class guessing (50.00% Balanced Accuracy for Squats). Under Scheme A (amplitude kept), the LSTM reaches only ~54% Balanced Accuracy, failing to reliably extract the amplitude signal that a simple peak flexion threshold captures (81.36%). A clear demonstration of high-capacity model overfitting on small-subject cohorts ($N=9$ squats / $N=7$ lunges). Source: `temporal_model_evaluation_report.md` §4.
- Does NOT claim — no diagnostic prediction, no injury risk classification, not clinically deployed.

## Component — Self-Supervised Pretraining (Track B) · FUTURE WORK (evidence-grounded, not implemented)
- Status — NOT implemented as an active pipeline component; written up as reasoned future work, grounded in the temporal model results. This represents a pre-accepted time-boxed null outcome.
- Reasoning — the temporal LSTM comparison (Phase 12) demonstrated that supervised deep models overfit at this cohort scale ($N=9$ squat / $N=7$ lunge subjects): the LSTM failed to extract even the amplitude signal that a single-feature peak-flexion classifier captures (LSTM ~54% vs peak-flexion 81.36% balanced accuracy). Since self-supervised pretraining's value is learning representations to aid downstream deep models, and since (a) the downstream screening task is solved by a single endpoint biomarker and (b) deep representations do not generalize at this subject count, pretraining is highly unlikely to yield downstream gains at this scale.
- Future-work framing — self-supervised pretraining is identified as future work requiring substantially larger multi-subject cohorts, where representation learning could plausibly help before endpoint saturation. Source: reasoning from Phase 12 temporal_model_evaluation_report.md.
- Does NOT claim — not that self-supervised representation learning is generally without value; specifically that at this cohort scale, with the demonstrated overfitting ceilings, it is not warranted.

---

## Pending Reference Compilation (Week-16 Reference Sweep)

The following `[CITE:]` markers in the methods draft require formal bibliographic entries:
- `[CITE: OpenCap_Validation]` — Uhlrich et al., OpenCap markerless motion capture validation paper.
- `[CITE: Clustering_Bootstrap]` — Cluster/subject-level bootstrap methods reference (e.g., Cameron, Gelbach & Miller, or Field & Welsh).
- Squat/lunge clinical threshold references — pending from earlier squat chapter review.
