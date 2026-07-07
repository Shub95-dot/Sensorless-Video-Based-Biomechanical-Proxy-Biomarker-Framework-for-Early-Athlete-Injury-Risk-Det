# Phase 12 — Temporal Sequence Model Feasibility Check

This report evaluates the feasibility of modeling the within-repetition knee-flexion trajectory (frame-by-frame shape) to determine if trajectory shape carries form-screening signal beyond simple endpoint biomarkers (such as peak flexion and ROM).

---

## Check 1 — Trajectory Availability

*   **Location and Form:** Per-repetition frame-by-frame knee flexion trajectories are cleanly available as CSV files:
    *   **Squat:** [14_rehab24_outputs/smoothed_per_rep/](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/14_rehab24_outputs/smoothed_per_rep) (`PM_XXX_rep_YY_smoothed.csv`)
    *   **Lunge:** [15_rehab24_lunge_outputs/smoothed_per_rep/](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/15_rehab24_lunge_outputs/smoothed_per_rep) (`PM_XXX_rep_YY_smoothed.csv`)
    *   **Primary Column:** `knee_angle_smoothed` (included angle convention, in degrees).
*   **Segmentation:** Repetitions are already segmented using phase detection (descent start to ascent terminal extension). There are no mid-rep gaps; however, sequence lengths vary dynamically based on movement speed.
*   **Sequence Length Distribution (Frames at 30 fps):**
    *   **Squat (98 reps):** Min = 65 frames, Max = 155 frames, Mean = 100.3 frames, Median = 95 frames, Std = 21.2 frames.
    *   **Lunge (88 reps on disk):** Min = 41 frames, Max = 166 frames, Mean = 102.4 frames, Median = 102 frames, Std = 28.0 frames.
    *   *Modeling Implication:* Input sequences must be padded/masked or normalized/interpolated to a fixed length (e.g., 100 points) to be ingested by standard temporal architectures.
*   **Missing or Corrupt Trajectories:**
    *   **Squat:** All 98 repetitions are fully processed with valid, complete trajectory data.
    *   **Lunge:** Out of 88 repetitions on disk, **27 repetitions** failed phase-identification quality filtering (all reps of Subject 8/PM_112, and 12 of 13 reps of Subject 5/PM_042) and are excluded from the usable analytical cohort. Only the **61 usable repetitions** (status = `ok`) have reliable segmentations and corresponding biomarker targets.

---

## Check 2 — Data Volume for Honest Evaluation

The data volume is extremely small for deep learning sequence models, which severely limits the viability of standard train/test splitting:

### Squat Cohort
*   **Total Usable Reps:** 98
*   **Total Subjects:** 9
*   **Reps per Subject Split (Correct / Incorrect):**
    *   Subject 1 (PM_008): 17 reps (16 Correct / 1 Incorrect)
    *   Subject 2 (PM_022): 10 reps (10 Correct / 0 Incorrect)
    *   Subject 3 (PM_029): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 4 (PM_038): 10 reps (10 Correct / 0 Incorrect)
    *   Subject 5 (PM_043): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 6 (PM_105): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 7 (PM_126): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 8 (PM_113): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 9 (PM_118): 11 reps (11 Correct / 0 Incorrect)
    *   *Total Split:* 72 Correct / 26 Incorrect (73.5% / 26.5%)

### Lunge Cohort
*   **Total Usable Reps:** 61
*   **Total Usable Subjects:** 7 (Subject 8 has 0 usable reps; Subject 5 has only 1 usable rep)
*   **Reps per Subject Split (Correct / Incorrect):**
    *   Subject 2 (PM_021): 9 reps (4 Correct / 5 Incorrect)
    *   Subject 3 (PM_028): 10 reps (0 Correct / 10 Incorrect)
    *   Subject 4 (PM_037): 9 reps (5 Correct / 4 Incorrect)
    *   Subject 5 (PM_042): 1 rep (0 Correct / 1 Incorrect)
    *   Subject 6 (PM_104): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 7 (PM_125): 10 reps (5 Correct / 5 Incorrect)
    *   Subject 9 (PM_117a): 12 reps (6 Correct / 6 Incorrect)
    *   *Total Split:* 25 Correct / 36 Incorrect (41.0% / 59.0%)

> [!IMPORTANT]
> **Subject-Level Train/Test Split Viability:**
> A subject-level split is highly constrained. Leave-One-Subject-Out (LOSO) cross-validation is the only honest way to prevent the model from memorizing subject identities. However, because several subjects have only one label class (e.g., S2, S4, S9 in squats have 0 incorrect reps; S3 in lunges has 0 correct reps), validation folds will contain highly skewed or single-class distributions, complicating standard performance metrics like AUC-ROC.

---

## Check 3 — Label for the Task

*   **Label Availability:** Target labels (`correctness_label` where 1 = correct, 0 = incorrect) are fully populated in the per-rep biomarker files:
    *   Squat: [rehab24_squat_per_rep_biomarkers.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/14_rehab24_outputs/biomarkers_per_rep/rehab24_squat_per_rep_biomarkers.csv)
    *   Lunge: [rehab24_lunge_per_rep_biomarkers.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/15_rehab24_lunge_outputs/biomarkers_per_rep/rehab24_lunge_per_rep_biomarkers.csv)
*   **Balance:** Squat labels are moderately imbalanced (73.5% correct), while lunge labels are reasonably balanced (59.0% incorrect).
*   **Framing:** The task evaluates whether temporal shape features predict `correctness_label` (identifying movement deviations) rather than claiming any predictive utility for clinical outcomes.

---

## Check 4 — Tool Appropriateness

### Overfitting Risk Assessment
Given the small sample sizes ($N=98$ squat reps across 9 subjects; $N=61$ lunge reps across 7 subjects), **a full LSTM is highly inappropriate and carries an extreme risk of overfitting**. An LSTM has thousands of trainable parameters. Rather than learning generalized geometric patterns (such as descent asymmetry or ascent deceleration), the network will easily memorize the raw angle ranges or calibration offsets unique to individual subjects (e.g., memorizing that a baseline knee angle of $\approx 170^\circ$ corresponds to Subject 1).

### Recommended Alternatives
If the objective is to honestly demonstrate whether *trajectory shape* carries diagnostic signal beyond simple endpoints, we recommend the following lighter alternatives:

1.  **Trajectory Shape Feature Extraction + Shallow Classifier (Highly Recommended):**
    *   *Approach:* Downsample/interpolate all trajectories to a fixed grid (e.g., 50 or 100 points) or compute explicit shape features (e.g., descent slope, ascent slope, descent-ascent ratio, peak-to-mean ratio, curvature/jerk dynamics).
    *   *Model:* Train a simple regularized classifier (e.g., Ridge Logistic Regression or a small Random Forest) on these shape features.
    *   *Benefit:* Restricts model capacity, permits explicit feature importance auditing, and dramatically reduces overfitting risk.
2.  **Dynamic Time Warping (DTW) with k-NN:**
    *   *Approach:* Compute DTW alignment distances between rep shapes directly without training network parameters.
    *   *Model:* 1-Nearest Neighbor classifier based on DTW distance.
    *   *Benefit:* Zero-parameter training; directly evaluates shape similarity.
3.  **Ultra-Light 1D-CNN:**
    *   *Approach:* If a neural network is required, use a tiny 1D-CNN (e.g., 1–2 convolutional layers, kernel size 5, global average pooling, high dropout $>50\%$).
    *   *Benefit:* Far fewer parameters than an LSTM; translation-invariant features focus on local shape changes rather than absolute values.
