# Project State Handoff — Sensorless Biomechanical Screening Framework

> **How to use this document**: When starting a fresh chat with Claude, paste this entire document as the first message, then add: *"This is the current state of my dissertation project. Pick up from the 'Next immediate step' section at the bottom."* This brings the assistant up to speed without re-explaining the full project history.

---

## Project framing (committed)

**Title (working)**: A sensorless markerless screening framework for identifying kinematic patterns associated with elevated injury risk across multiple athletic exercises

**Claim**: The system identifies kinematic patterns from athletic exercise video that the published clinical biomechanics literature has associated with elevated injury risk. It provides explainable per-athlete screening reports with uncertainty quantification.

**This is NOT**:
- Injury outcome prediction (no injury labels available)
- Longitudinal personalised baseline (no multi-session per-athlete data)
- A digital twin in the continuous-update sense (no longitudinal data)

**The full 14-step vision** ("Self-Supervised Sensorless Multimodal Athlete Biomechanical Intelligence System for Early Injury Risk Detection") is preserved as the long-term research programme described in the dissertation's introduction and future-work sections. The dissertation implements the foundation layer.

**Two-track framework**:
- **Track A (dissertation deliverable)**: 14-step vision steps 1–6 (with caveats on temporal biomarkers in step 6), step 10 (rule-based version, not trained DL ensemble), step 11 (XAI), step 13 (screening report framing), step 14 (literature validation)
- **Track B (future work / architectural demonstration)**: Track A delivers the screening pipeline; the four Track B components—7 (personalised baseline), 8 (temporal LSTM), 9 (self-supervised), and 12 (digital twin)—are DEMONSTRATED AS ARCHITECTURE within this dissertation (not deployed as production systems), each documenting what full-scale deployment would require.

**Dissertation novelty contributions (4 committed, optional 5th)**:
1. Cross-exercise integration into per-athlete movement profiles
2. Methodological documentation of monocular pose limitations in in-the-wild athletic footage (failure-mode taxonomy)
3. Uncertainty-weighted biomarker aggregation propagating pose-pipeline confidence to risk flags
4. Counterfactual explanation applied to rule-based clinical screening
5. *(Optional)* Synthetic perturbation sensitivity analysis

**Realistic grade ceiling with excellent execution**: 85–93%

---

## Repository and environment

- **GitHub**: `Shub95-dot/Sensorless-Multimodal-Athlete-Intelligence-System`
- **Local path**: `c:/Users/shiro/OneDrive/Desktop/Python files/BIOMECHANICAL ANALYSIS OF INJURY/`
- **Python**: 3.10 (forced for MediaPipe Tasks API compatibility; Python 3.14 has binding issues)
- **Pose model**: MediaPipe Pose Landmarker, Heavy variant, `min_pose_detection_confidence=0.5`, `min_pose_presence_confidence=0.5`, `min_tracking_confidence=0.5`, `output_segmentation_masks=False`, `running_mode=IMAGE`. Model file at `12_models/pose_landmarker_heavy.task`.

---

## Squat pipeline — COMPLETE

### Cohort

- **Original sagittal cohort**: 15 subjects (1679, 1682, 1683, 1708, 1709, 1713, 1718, 1774, 1789, 1799, 1818, 1823, 1863, 1869, 1884)
- **Final included (10)**:
  - **Gold tier (8)**: 1679, 1713, 1718, 1799, 1818, 1823, 1863, 1884
  - **Bronze tier (2)**: 1682 (depth_truncated=True), 1774 (partial_depth_real=True)
- **Final excluded (5)**: 1683 (duplicate of 1682 + cat interference), 1708 (fragmented, no rep structure), 1709 (duplicate of 1713), 1789 (61.5% validity), 1869 (56.7% validity)
- **Post-Phase-4G rep correction**: All 10 included subjects reclassified to `single_rep` after visual audit revealed 4 false-positive `multi_rep` classifications (1682, 1774, 1823, 1884). Algorithm retained for future use on cleanly-segmented multi-rep datasets.

### Pipeline phases completed

| Phase | Description | Key output |
|---|---|---|
| 2 | Dataset metadata indexing | `3_metadata/dataset_metadata.csv` (21,526 indexed files) |
| 3 | MediaPipe pose extraction (single-frame) | `4_pose_outputs/squats/squats_pose_raw.csv` (88% detection) |
| 3B | Pose quality tier stratification | `3_metadata/squats_pose_quality_tiers.csv` |
| 4A | Single-frame knee angle computation | `4_pose_outputs/squats/squats_knee_angle.csv` |
| Camera-view audit | Manual classification of 91 frames | `3_metadata/squat_camera_view.csv` (15/91 sagittal) |
| 4B | Temporal frame manifest | `3_metadata/squats_temporal_manifest.csv` (1,396 frames) |
| 4C | Temporal pose extraction | `4_pose_outputs/temporal/squats_temporal_per_frame.csv` (1194 valid / 1396 = 85.5%) |
| 4D | Subject quality audit + inclusion manifest | `3_metadata/squats_temporal_inclusion.csv` |
| 4E | Trajectory smoothing | median window=5 + Savitzky-Golay window=7 polyorder=2, NaN-aware |
| 4F | Per-subject biomarker extraction | `4_pose_outputs/temporal/squats_biomarkers.csv` |
| 4G | Rep segmentation (with post-audit correction) | `4_pose_outputs/temporal/squats_rep_summary.csv` |

### Cohort findings — squats YouTube (descriptive, for dissertation)

**Spike rate stats (post-smoothing)**: Mean 3.12%, median 2.78%. Flagged >5%: 1863 (7.69%), 1679 (6.25%), 1682 (6.06%).

**Biomarker cohort stats (n=10)**:
| Biomarker | min | max | mean | median |
|---|---|---|---|---|
| peak_flexion_deg | 38.7 | 123.0 | 81.5 | 86.1 |
| peak_extension_deg | 174.5 | 179.9 | 178.1 | 178.0 |
| rom_deg | 55.1 | 140.8 | 96.6 | 91.5 |
| tempo_ratio | 0.85 | 2.03 | 1.14 | 0.98 |
| jerk_proxy_std | 0.84 | 3.08 | 1.46 | 1.34 |

### Subject-specific notes (YouTube cohort)

- **1713, 1884**: textbook clean deep squats (exemplars for results chapter)
- **1718, 1799, 1818, 1823**: competent moderate-depth squats
- **1679**: clean rep with environmental interference (dark gym, rack bars)
- **1863**: deep squat with high movement variability; complex post-bottom recovery
- **1682** (`depth_truncated=True`): real deep squat but pipeline under-reported peak depth; tempo/timing valid, peak_flexion_valid=False
- **1774** (`partial_depth_real=True`): genuine partial-depth squat (box mat exercise variant); all biomarkers valid

---

## REHAB24-6 integration — COMPLETE (Phase 5A)

### Cohort

- 9 subjects, 98 sagittal squat reps (only `cam18`/side-view videos used; `cam17` front-view files were deleted during initial setup)
- Filter applied: `exercise_id == 6` (squats), `cam17_orientation == 'front'` (means cam18 is sagittal), `mocap_erroneous == 0`
- Excluded: 97 half-profile reps where neither camera gave clean sagittal view

### Correctness breakdown

72 correct reps / 26 incorrect reps

| subject_id | video_id | total reps | correct | incorrect |
|---|---|---|---|---|
| 1 | PM_008 | 17 | 16 | 1 |
| 2 | PM_022 | 10 | 10 | 0 |
| 3 | PM_029 | 10 | 5 | 5 |
| 4 | PM_038 | 10 | 10 | 0 |
| 5 | PM_043 | 10 | 5 | 5 |
| 6 | PM_105 | 10 | 5 | 5 |
| 7 | PM_126 | 10 | 5 | 5 |
| 8 | PM_113 | 10 | 5 | 5 |
| 9 | PM_118 | 11 | 11 | 0 |

Subjects 3, 5, 6, 7, 8 each contributed 5 correct + 5 incorrect reps per the dataset's physiotherapist-instructed protocol with different specific errors per subject.

### Cohort biomarker statistics (n=98 reps)

| Biomarker | min | max | mean | median | std |
|---|---|---|---|---|---|
| peak_flexion_deg | 31.91 | 84.74 | 55.62 | 53.62 | 14.31 |
| rom_deg | 73.90 | 145.16 | 117.32 | 121.52 | 18.91 |
| tempo_ratio | 0.49 | 2.97 | 1.07 | 1.00 | 0.34 |
| jerk_proxy_std | 0.47 | 1.23 | 0.78 | 0.77 | 0.18 |

Zero subjects flagged with spike rate >5%. Zero phase_identification failures across all 98 reps.

### Headline finding — correct vs incorrect form

| Biomarker | Correct (n=72) | Incorrect (n=26) |
|---|---|---|
| peak_flexion_deg | 60.85 ± 12.72 | 41.14 ± 6.20 |
| peak_extension_deg | 172.03 ± 9.97 | 175.45 ± 5.20 |
| rom_deg | 111.19 ± 18.06 | 134.31 ± 7.23 |
| peak_descent_velocity (°/frame) | -5.85 ± 1.75 | -7.24 ± 1.52 |
| peak_ascent_velocity (°/frame) | 6.86 ± 2.22 | 7.91 ± 1.54 |
| mean_descent_velocity (°/frame) | -2.23 ± 0.74 | -2.77 ± 0.54 |
| mean_ascent_velocity (°/frame) | 2.33 ± 0.88 | 2.73 ± 0.46 |
| tempo_ratio | 1.07 ± 0.35 | 1.06 ± 0.29 |
| jerk_proxy_std | 0.75 ± 0.19 | 0.85 ± 0.15 |

**Pattern interpretation**: Incorrect-form reps in REHAB24-6 are characterised by *deeper depth (~20° greater), greater ROM (~23° greater), faster descent (~24% faster peak velocity), and rougher movement quality (~13% higher jerk)*. This pattern is consistent with *uncontrolled deep descent with grinding ascent* — biomechanically associated in literature with patellofemoral shock loading and meniscal stress. The pipeline detects a real, biomechanically interpretable signal that aligns with physiotherapist correctness labels.

**Sample visual verification (confirmed via overlay plots)**:
- PM_008 rep 2 (correct, peak 62.16°, ROM 117°, tempo 1.00): textbook smooth symmetric squat
- PM_022 rep 1 (correct, peak 55.23°, ROM 122.85°, tempo 0.93): clean with small pose-extraction gap mid-descent, handled correctly by NaN-aware smoothing
- PM_008 rep 17 (incorrect, peak 50.03°, ROM 127.73°, tempo 1.65): visibly faster descent, deeper depth, irregular ascent with two visible bumps — confirms biomarker pattern visually

### Important caveats for dissertation

1. Correct/incorrect labels are *heterogeneous* — each subject performed different specific errors per physiotherapist's instructions. Sagittal-only analysis cannot capture frontal-plane errors (e.g. valgus); the observed depth/velocity signal likely reflects the subset of errors involving depth control
2. 26 incorrect reps from 5 subjects is small — findings are *descriptive*, not statistically inferential
3. Subject 1 contributed 16 correct reps and only 1 incorrect rep, creating per-subject imbalance

### REHAB24-6 vs YouTube cross-cohort comparison

| Metric | YouTube (n=10) | REHAB24-6 (n=9 subjects, 98 reps) |
|---|---|---|
| Spike rate >5% subjects | 3 of 11 | 0 of 9 |
| Mean jerk_proxy_std | 1.46 | 0.78 |
| Mean peak_flexion | 81.5° | 55.6° |
| Mean ROM | 96.6° | 117.3° |
| Phase identification failure | 1 (subject 1708, excluded) | 0 |

REHAB24-6 produces dramatically cleaner pose extraction. Both cohorts produce biomechanically sensible biomarker ranges. Pipeline generalises across recording conditions. REHAB24-6 subjects show deeper squat depth and greater ROM than YouTube — consistent with controlled lab eliciting more consistent technique than in-the-wild gym footage.

### Outputs and Verification
- **Results Draft**: Written to `14_rehab24_outputs/drafts/squat_results_v4.md` (verified d/CI values, matching text with a four-reference clinical citation chain).
- **Figures**: Plotted to `14_rehab24_outputs/figures_publication/` (4 publication-quality figures: distributions, effect sizes, cross-cohort distributions, and representative trajectories).
- **Open Item**: Check author/DOI metadata of the four clinical references (User, to perform in reference manager).

### REHAB24-6 output files

```
14_rehab24_outputs/
├── metadata/
│   ├── rehab24_squat_sagittal_manifest.csv       (98-row filtered rep list)
│   ├── rehab24_squat_processing_log.csv
│   └── phase5a_integration_summary.txt
├── pose_per_video/
│   └── PM_XXX_pose_full.csv                      (9 per-video pose extractions)
├── smoothed_per_rep/
│   └── PM_XXX_rep_NN_smoothed.csv                (98 per-rep smoothed trajectories)
├── biomarkers_per_rep/
│   └── rehab24_squat_per_rep_biomarkers.csv      (98 rows, biomarkers + correctness label)
└── visualizations/
    └── PM_XXX_rep_NN_overlay.png                 (98 per-rep biomarker overlay plots)
```

### Source data location

- `1_raw_datasets/New Dataset for dissertation/REHAB24-6 integration/Squats/PM_XXX-Camera18-30fps-transposed.mp4` (9 video files)
- `1_raw_datasets/New Dataset for dissertation/REHAB24-6 integration/Segmentation.csv` (full dataset segmentation, 1072 rows)
- `1_raw_datasets/New Dataset for dissertation/REHAB24-6 integration/Segmentation.txt` (column schema reference)

### Citation required in dissertation

Černek, A., Sedmidubsky, J., Budikova, P.: REHAB24-6: Physical Therapy Dataset for Analyzing Pose Estimation Methods. 17th International Conference on Similarity Search and Applications (SISAP). Springer, 14 pages, 2024.

License: CC-BY-NC-4.0 (academic non-commercial use only).

---

## Lunge pipeline — COMPLETE

### Cohort and Filtering
- **Assembled Cohort**: 88 sagittal lunge repetitions across 8 subjects from `REHAB24-6` (`exercise_id == 5`, `cam17_orientation == 'front'`, `mocap_erroneous == 0`).
- **Usable Analytical Cohort**: 61 repetitions (7 subjects, 25 correct / 36 incorrect) after excluding Subjects 5 and 8 due to far-side occlusion-induced pose-pipeline failures (30.68% failure rate).

### Headline Findings
- **Kinematic Signature**: Parallels the squat cohort with a very large shift toward greater depth in incorrect reps (peak flexion $d = +1.69$).
- **Cross-Exercise Divergence**: Unlike squats (where ascent velocities did not discriminate), lunge ascent velocities discriminate reliably between correct and incorrect form, showing a faster peak ascent velocity ($d = -0.97$, reliable) and mean ascent velocity ($d = -0.80$, reliable-marginal). Incorrect lunges involve an uncontrolled, rapid spring-back propulsion strategy.

### Outputs and Verification
- **Results Draft**: Saved as `15_rehab24_lunge_outputs/drafts/lunge_results_v1.md` (verified statistics, wording-locked, utilizing descriptive kinematic screening language).
- **Figures**: Plotted to `15_rehab24_lunge_outputs/figures_publication/` (4 publication-quality PNG/SVG sibling figures: fig_L1 correct vs. incorrect, fig_L2 effect sizes, fig_L3 cross-exercise comparative forest plot, and fig_L4 Subject 7 trajectories, all validated with a figure data provenance CSV).

### Methods and Plotting Notes
- **Note for Methods Chapter**: Lunge statistics reuse the squat subject-clustered bootstrapping procedure verbatim (replicated with seed 42 and 5,000 resamples for consistency, not imported). The methods chapter should describe this as an identical procedure or refactor it into a shared utility script.
- **Cosmetic Logging Item**: The effect-size guide labels (small/medium/large) currently overprint/overlap across the forest plots in all figures. This needs to be resolved in the shared plotting code during the Week-16 figure-consistency sweep.

---

## Combined squat cohort (current state)

After REHAB24-6 integration:
- **YouTube cohort**: 10 subjects, 10 single-rep biomarker rows
- **REHAB24-6 cohort**: 9 subjects, 98 per-rep biomarker rows with correctness labels

Total: 19 subjects, 108 squat samples. The two cohorts are analysed separately in the dissertation (different recording conditions, different label availability) but compared for cross-cohort consistency.

---

## Documented failure modes (for dissertation methods chapter)

1. **Camera-view dependence**: in-the-wild footage predominantly oblique (32/91 oblique vs 15/91 sagittal in YouTube cohort)
2. **Visibility-vs-localization-accuracy gap**: MediaPipe visibility ≥0.5 doesn't guarantee correct placement (subjects 1679, 1863)
3. **Peak-flexion occlusion truncation**: subject 1682 — near-side leg landmarks occluded by far leg/bar at deep flexion
4. **Exercise-variant ambiguity**: subject 1774 — box-mat partial squat produces same biomarker shape as depth-restricted athlete
5. **Environmental interference**: subject 1683 (cat in frame), 1679 (dark gym/rack bars)
6. **Single-frame landmark spikes**: addressed by median-filter pre-pass before Savitzky-Golay smoothing
7. **Rep-segmentation on fragmented data**: algorithm unsuited to noisy YouTube footage; retained for cleanly-segmented datasets. REHAB24-6 bypassed this by using ground-truth boundaries from Segmentation.csv
8. **Pose-extraction gaps in lab footage**: even controlled recording shows occasional gaps (e.g. PM_022 rep 1 has 3-frame gap mid-descent), handled by NaN-aware smoothing

---

## Planned scope (committed)

**Exercises** (in order of priority):
1. Squat — **COMPLETE** (YouTube + REHAB24-6 cohorts)
2. Lunges — **COMPLETE** (REHAB24-6 cohort)
3. Vertical jump — **ACTIVE**
4. Drop jump — **ACTIVE**
5. Single-leg squat — **if time permits (see Scope decisions)**

### Scope decisions (locked 2026-06-22)

* **Timeline & Buffer**: There are approximately 10 weeks remaining until the September 1 submission. Since both primary exercise chapters (squats and lunges) and the pipeline learning curve are already complete, the remaining plan fits comfortably with buffer.
* **Single-leg squat** $\rightarrow$ Demoted to "if time permits."
  * *Rationale*: Lowest sagittal yield and highest pose-failure cost, with key faults being frontal-plane (which our sagittal-only pipeline cannot observe); the methodological failure-mode contributions are already successfully banked from the squat and lunge phases. (This is a signal decision, not a time decision.)
* **MM-Fit** $\rightarrow$ Scheduled AFTER the jump block, gated on a video-availability check.
  * *Rationale*: MM-Fit is multimodal; we must confirm it ships usable RGB video before committing (if it is pose/IMU only, it becomes a biomarker-reference cohort rather than a video-pipeline cohort). It enhances completed chapters and feeds the personalised-baseline demonstration, but does not block new chapters.
* **Demonstration components** $\rightarrow$ Committed to ALL FOUR in order: Personalised baseline $\rightarrow$ Temporal LSTM $\rightarrow$ Digital twin $\rightarrow$ Self-supervised.
  * *Rationale*: Self-supervised pretraining is strictly time-boxed to ~1 week with a null result pre-framed as acceptable ("method demonstrated; no fine-tuning gain expected at this data scale"); if pretraining is still being resolved on day 4, execution stops, the null result is documented, and the project moves on.

Basketball **deprioritised** — weak labelled-dataset coverage, methodological complexity. Moved to future work.

Push-ups, jumping jacks, skipping — added via MM-Fit if time permits; not primary scope.

---

## Datasets — current status

### Tier 1 — primary datasets
1. **REHAB24-6**: **DOWNLOADED AND INTEGRATED** (9 subjects, 98 squat reps). Source: https://zenodo.org/records/13305826
2. **MM-Fit**: not yet downloaded. Source: https://mmfit.github.io/. Multi-exercise: squats, lunges, push-ups, jumping jacks, 10 reps × 3 sets per subject
3. **Calisti et al. ACL** (figshare DOI `10.6084/m9.figshare.28890545.v1`): Mocap-only labelled reference cohort for the DROP-JUMP step (no RGB video; not a MediaPipe input). Not yet downloaded.
7. UCF101 lunges: 127 clips at 25 fps, 320x240 resolution, located at 1_raw_datasets/Dataset/Lunges Video/. Approximately 25 subjects with 3-5 single-rep clips per subject per UCF101 group convention. Integration deferred to future work; documented in phase5b_integration_summary.txt.


### Tier 2 — register/request when needed
4. **OpenCap**: https://simtk.org/projects/opencap — SimTK registration. RGB + marker GT
5. **Fitness-AQA**: request form at https://forms.gle/PbPTX1eVxGpa3QG88 — form-gated, submit early
6. **UI-PRMD**: https://webpages.uidaho.edu/ui-prmd/ — Vicon-tracked mocap/skeletal-only REFERENCE cohort for LUNGES (no RGB video; not a MediaPipe input). Used for kinematic range comparison.

**Licensing**: All non-commercial academic use. Each requires citation in methods chapter.

---

## Self-recording plan (parallel work)

**Realistic estimate**: 5–10 friends across 5 exercises. Reframed as **controlled validation cohort**, not primary cohort.

**Ethics approval**: obtained.

**Per-exercise perturbation patterns**:
- **Squat**: restricted depth, knee valgus, excessive forward trunk lean
- **Lunge**: bilateral asymmetry, trunk lean, restricted depth
- **Vertical jump**: bilateral landing asymmetry, restricted knee flexion at landing
- **Drop jump**: knee valgus at landing, restricted knee flexion at landing, asymmetric landing
- **Single-leg squat**: knee valgus, trunk drop, restricted depth

Recording protocol and consent form template drafted. Consent form requires supervisor/ethics office review before participant use.

---

## Pending action items

1. **Send supervisor a scoping note** confirming Track A scope is appropriate for A-tier targeting. Recommended text:
   > For my AE2 dissertation I'm building a sensorless markerless screening framework that extracts kinematic patterns from athletic exercise video and flags movement patterns associated with elevated injury risk per published clinical literature. Contributions will include cross-exercise integration, failure-mode documentation for in-the-wild pose, uncertainty-weighted biomarker aggregation, and counterfactual explanation of rule firings. Can you confirm this scope is appropriate for A-tier targeting?

2. **Begin friend recruitment** for recording sessions (independent of pipeline work; takes weeks of scheduling)

3. **Submit Fitness-AQA access form** (gated, lead time needed)

---

## Remaining-Steps Plan (locked 2026-06-22)

### Active Block: Jumps
1. **Vertical Jump**: Develop pose-extraction and knee flexion kinematic analysis pipeline.
2. **Drop Jump**: Develop pose-extraction and landing kinematic analysis pipeline (utilizing Calisti ACL as a mocap-only reference cohort).

### Demonstration Components (Committed Sequence)
1. **Personalised Baseline**: Demonstration of session-to-session progression tracking.
2. **Temporal LSTM / Sequence Model**: Classifying temporal sequences for biomarker validation.
3. **Digital Twin**: Continuous-update architecture design.
4. **Self-Supervised Pretraining**: Time-boxed to ~1 week. A null result is pre-framed as acceptable ("method demonstrated; no fine-tuning gain expected at this data scale"). If pretraining is still being resolved on day 4, execution stops, the null result is documented, and the project moves on.

### If time permits / deferred
* **Single-leg squat**: Demoted from active block (see Scope Decisions).
* **MM-Fit integration**: Evaluated after the Jumps block, gated on verifying usable RGB video availability.

---

## Documented limitations to address in dissertation writing

Running list of known limitations to fold into the dissertation's limitations chapter. Each entry records the limitation, the mitigation applied (if any), and suggested dissertation framing.

1. **REHAB24-6 lacks per-subject error labels.** The dataset annotates correctness as binary (correct/incorrect) but does not publish which specific error each subject was instructed to perform; the SISAP 2024 paper notes only that the physiotherapist suggested different mistakes per subject.
   - *Mitigation*: per-subject biomarker shift decomposition to infer which subjects' incorrect reps involved sagittal-detectable errors versus frontal-plane errors invisible to monocular sagittal pose.
   - *Framing*: acknowledge explicitly; describe the per-subject decomposition as partial mitigation; identify manual error-type annotation with inter-rater reliability as future work.

2. **Sagittal-only analysis cannot detect frontal-plane errors.** The pipeline as built measures sagittal-plane kinematics only (knee flexion, ROM, descent timing); frontal-plane errors (knee valgus, lateral trunk shift, hip drop) are biomechanically invisible to this configuration by design.
   - *Mitigation*: screening claims restricted to sagittal-plane patterns; frontal-plane analysis positioned as future work requiring re-downloaded REHAB24-6 cam17 videos or new frontal-camera self-recordings.
   - *Framing*: document the sagittal-only scope as a deliberate design choice rather than an oversight, with frontal-plane extension as natural future work.

3. **Small incorrect-rep sample size in REHAB24-6.** Only 26 of 98 sagittal reps are labelled incorrect, from 5 subjects rather than the full cohort, so findings are descriptive not inferential; subject 1 contributed 16 correct and only 1 incorrect rep, creating a per-subject correctness imbalance.
   - *Mitigation*: cluster-aware bootstrap CIs at subject level (not rep level) to respect within-subject clustering.
   - *Framing*: report effect sizes with appropriately conservative confidence bounds; make no population-level claims.

4. **YouTube cohort is biased toward clean movement quality.** Quality filtering (camera-view classification, pose-validity tiers) preferentially retains experienced lifters with good technique, so risk-pattern findings are limited by the cohort's lack of high-risk movers.
   - *Mitigation*: cross-cohort comparison with labelled REHAB24-6 and planned future integration of additional datasets plus self-recorded subjects under a deliberate-perturbation protocol.
   - *Framing*: explicitly characterise the YouTube cohort as a "clean technique cohort" useful for pipeline validation but not for population-level screening claims.

5. **No injury outcome labels in any dataset.** None of the integrated or planned datasets (YouTube, REHAB24-6, MM-Fit, UI-PRMD) include prospective injury outcomes, so the framework cannot validate whether flagged subjects subsequently became injured.
   - *Mitigation*: framing as screening (identification of patterns associated with elevated risk per literature) rather than prediction (forecasting individual injury outcomes).
   - *Framing*: this is the foundational Track A vs Track B scoping decision and must be maintained throughout; future work requires a longitudinal cohort study with clinical injury surveillance.

6. **No longitudinal multi-session data per subject.** All datasets capture single-session recordings, so personalised baseline learning, fatigue-drift analysis, and digital twin functionality (steps 7 and 12 of the 14-step vision) cannot be built.
   - *Mitigation*: single-session within-subject rep-to-rep variability (via the rep-segmentation pipeline) provides a partial repeatability proxy.
   - *Framing*: explicitly defer personalised baseline and digital twin to Track B future work, naming the data requirements that would enable them.

7. **Velocity biomarkers reported in degrees per frame, not degrees per second.** Inconsistent per-source frame-rate metadata across the aggregated datasets prevents reliable conversion to absolute-time units.
   - *Mitigation*: per-frame normalisation enables within-cohort and cross-cohort comparison but precludes direct comparison with absolute-time velocities reported in published biomechanics literature.
   - *Framing*: document as an explicit methodological choice in the methods chapter; note that REHAB24-6 specifically is 30 fps and could be converted if direct literature comparison is needed.

8. **Rep-segmentation algorithm unreliable on fragmented in-the-wild data.** The `scipy.signal.find_peaks`-based rep detection (prominence=20, distance=15) produces false-positive multi-rep classifications on noisy YouTube footage.
   - *Mitigation*: post-audit visual review reclassified all 10 YouTube subjects as single_rep; REHAB24-6 integration bypassed the algorithm by using ground-truth rep boundaries from Segmentation.csv.
   - *Framing*: document the algorithm's behaviour on both data types as a methodological finding about monocular pose limitations, and note it is retained for future application to cleanly-segmented multi-rep datasets.

---

## Working preferences (noted from past conversations)

- Verify every figure from actual code/data before stating it; do not introduce unverified numbers
- Use kinematic/screening language; never stress/load/overuse/prediction
- Maintain audit trail from raw frames through to final claims
- Prefer companion CSVs over modifying upstream metadata files (provenance discipline)
- Pre-write sanity checkpoints before any output writes
- Pose extraction defaults to left-side knee chain, falls back to right-side if left visibility < 0.5

---

*Document version: end of Phase 5A REHAB24-6 integration.*
