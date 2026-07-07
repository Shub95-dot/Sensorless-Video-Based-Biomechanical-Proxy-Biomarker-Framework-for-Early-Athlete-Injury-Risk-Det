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

6. **Chapter 9: Personalised Session-to-Session Baselines (Track B Demo)**

## Component — Personalised Baseline (Track B demo) · ANALYSIS DONE / WRITEUP DEFERRED
- Purpose — architectural demonstration of personalised progression tracking: per-subject baseline + deviation detection gated by validated measurement-noise floor. Pseudo-timepoints (within-session rep order); NOT real longitudinal tracking. Source: `18_personalised_baseline_outputs/baseline_design.md`.
- Method — baseline from correct reps 1-2 (mean; SD descriptive only); test reps gated per-biomarker vs phase-7 projection-transferred noise floor (peak ±11.99°, velocity ±40.86°/s). Deviation flagged if |test − baseline mean| > that biomarker's floor. Source: `baseline_design.md` + `phase8_personalised_baseline.py`.
- Result — both sides demonstrated cleanly. Squat PM_113 + Lunge PM_104: quiet correct reps stay within floor (incl. an upward lunge wobble correctly read within-noise); incorrect reps fire on peak flexion (Δ 21-36°). Source: `worked_example_baseline.csv` + `baseline_tracking.png`.
- Cross-component finding — detection is DRIVEN BY PEAK FLEXION (tight floor, high phase-7 weight); descent velocity (wide floor, low weight, high measurement uncertainty) does not independently flag the deviations except one large genuine velocity spike (squat rep 6, 110°/s). Visibly confirms the phase-7 uncertainty-weighting: high-confidence biomarker drives screening, low-confidence one contributes little. Source: `baseline_design.md` §7 + figure.
- Personalised-not-group — unit of analysis is the individual's own baseline + own noise-gated deviation, NOT cohort correct-vs-incorrect. Firing = "real kinematic deviation beyond measurement uncertainty," never "bad rep." Source: `baseline_design.md`.
- LIMITATION — only deviations exceeding the wide monocular measurement floor are detectable; subtle sub-floor progression is not distinguishable from measurement noise (direct consequence of the OpenCap-validated camera uncertainty). Source: `baseline_design.md`.
- Does NOT claim — no real longitudinal progression, no injury prediction, no rep good/bad classification, no group re-analysis, not deployed. Source: `baseline_design.md`.

7. **Chapter 10: Temporal Sequence Models (LSTM)**
   - **Section 9.1: Sequence Classification & Biomarker Validation**: Planned.

8. **Chapter 11: Biomechanical Digital Twin**
   - **Section 10.1: Continuous-Update Infrastructure Design**: Planned.

9. **Chapter 12: Self-Supervised Pretraining**
   - **Section 11.1: Pretraining Framework and Sample Constraints**: Planned.

## Dissertation Chapter Drafts

10. **Methods Chapter** · **DRAFTED** (`22_dissertation_writing/methods_v2.md`)
    - Covers: pipeline architecture, cohort assembly (REHAB24-6 + OpenCap + YouTube), OpenCap validation, uncertainty decomposition & transfer, personalised baseline & digital twin, rule-based screening (Step 10), counterfactual XAI (Step 11), statistical methods. ~2,950 words. Every number carries an inline `[source:]` tag. Results deferred.
    - Status: First chapter section drafted. Distinct from deferred results/discussion sections.

## Component — Digital Twin (Track B demo) · ANALYSIS DONE / WRITEUP DEFERRED
- Purpose — architectural demonstration of continuous-update personalisation: extends the Phase 8 baseline so the per-subject reference UPDATES as pseudo-sessions arrive. Non-predictive; NOT a learned model; NOT real longitudinal. Source: `19_digital_twin_outputs/twin_design.md`.
- Mechanism — twin state = running reference mean + Phase-7 noise floor. Within-noise reps update the reference (running mean); deviation reps are excluded (aberration rejection) but counted, flagged, and explained. Simple arithmetic update, no learned parameters. Source: `twin_design.md` + `phase9_digital_twin.py`.
- Result — reference evolves on clean reps (squat PM_113: 72.98→69.21° across reps 3-5), locks when incorrect reps deviate past floor. Noise band tracks the evolving reference. Source: `worked_example_twin.csv` + `twin_tracking.png`.
- Exclusion explanation (design feature) — on exclusion, twin outputs a MEASUREMENT-BASED reason: deviation exceeded validated measurement uncertainty; from a single observation, transient fluctuation vs genuine sustained change cannot be distinguished. Epistemic humility, not quality judgment. Source: `twin_design.md`.

## Component — Rule-Based Screening Layer (Step 10, Track A core) · ANALYSIS DONE / WRITEUP DEFERRED
- Purpose — named-rule screening layer turning validated biomarkers into screening flags with clinical meaning. Personalised-deviation rules grounded in Phase 7 noise floors. Source: `20_screening_outputs/screening_rules_design.md`.
- Rules — EXCESS_DEPTH (peak < baseline − 11.99°), EXCESS_ROM (ROM > baseline + 23.17°), EXCESS_VELOCITY (velocity > baseline + 40.86°/s). Source: `screening_rules_design.md` + `phase10_rule_screening.py`.
- Result — correct reps 3-5 gated NOT_FLAGGED; incorrect reps 6-10 fire SCREENING_POSITIVE. Source: `worked_example_screening.csv`.

## Component — Counterfactual XAI (Step 11, Track A novelty #4) · ANALYSIS DONE / WRITEUP DEFERRED
- Purpose — counterfactual explanation of rule-based screening flags: faithful by construction (exact margin calculations, not post-hoc approximations). Source: `21_xai_outputs/xai_design.md`.
- Templates — descriptive (not prescriptive) counterfactual statements per rule. MKI as a descriptive set of conditions. Confidence grading via 0.5×NF buffer. Source: `xai_design.md` + `phase11_counterfactual_xai.py`.
- Result — explanations rendered for PM_113 (squat) and PM_104 (lunge). Source: `worked_example_explanations.json`.

---

## Pending Reference Compilation (Week-16 Reference Sweep)

The following `[CITE:]` markers in the methods draft require formal bibliographic entries:
- `[CITE: OpenCap_Validation]` — Uhlrich et al., OpenCap markerless motion capture validation paper.
- `[CITE: Clustering_Bootstrap]` — Cluster/subject-level bootstrap methods reference (e.g., Cameron, Gelbach & Miller, or Field & Welsh).
- Squat/lunge clinical threshold references — pending from earlier squat chapter review.
