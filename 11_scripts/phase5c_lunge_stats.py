#!/usr/bin/env python3
"""
phase5c_lunge_stats.py
======================
Phase 5C — REHAB24-6 Lunge form-discrimination stats.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Define paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BIOMARKERS_PATH = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"
OUT_EFFECT_SIZES = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "metadata" / "phase5c_effect_sizes_ci.csv"
OUT_SUBJ_SHIFTS = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "metadata" / "phase5c_per_subject_shifts.csv"

def cohens_d(correct_vals, incorrect_vals):
    n1 = len(correct_vals)
    n2 = len(incorrect_vals)
    if n1 <= 1 or n2 <= 1:
        return 0.0
    v1 = np.var(correct_vals, ddof=1)
    v2 = np.var(incorrect_vals, ddof=1)
    sp = np.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    if sp == 0:
        return 0.0
    return (np.mean(correct_vals) - np.mean(incorrect_vals)) / sp

def main():
    print("=== Phase 5C — REHAB24-6 Lunge Statistics Script Started ===")
    
    if not BIOMARKERS_PATH.is_file():
        print(f"ERROR: Biomarkers file not found at: {BIOMARKERS_PATH}")
        sys.exit(1)
        
    df_raw = pd.read_csv(BIOMARKERS_PATH)
    total_reps = len(df_raw)
    
    # Exclude failed reps
    df_failed = df_raw[df_raw['phase_identification_status'] == 'failed']
    df_usable = df_raw[df_raw['phase_identification_status'] == 'ok'].copy()
    
    # 1. Cohort Construction Counts
    print("\n--- Cohort Construction Counts ---")
    print(f"Total reps in file                          : {total_reps}")
    print("Reps excluded (failed) broken down by subject:")
    failed_counts = df_failed.groupby('subject_id').size()
    for sub, count in failed_counts.items():
        print(f"  Subject {sub:<2}: {count} reps")
    if len(failed_counts) == 0:
        print("  None")
    print(f"Total reps excluded                         : {len(df_failed)}")
    print(f"Usable reps remaining                       : {len(df_usable)}")
    
    usable_by_correctness = df_usable.groupby('correctness_label').size()
    n_correct_usable = usable_by_correctness.get(1, 0)
    n_incorrect_usable = usable_by_correctness.get(0, 0)
    print(f"Usable reps (correct, correctness=1)        : {n_correct_usable}")
    print(f"Usable reps (incorrect, correctness=0)      : {n_incorrect_usable}")
    
    print("\nUsable reps by subject_id x correctness:")
    c_table = pd.crosstab(df_usable['subject_id'], df_usable['correctness_label'])
    c_table.columns = ['Incorrect (0)', 'Correct (1)']
    print(c_table.to_string())
    
    # Identify subjects that contributed only one class
    subjects_all = sorted(df_usable['subject_id'].unique())
    single_class_subjects = []
    both_class_subjects = []
    for s in subjects_all:
        sub_reps = df_usable[df_usable['subject_id'] == s]
        corr_unique = sub_reps['correctness_label'].unique()
        if len(corr_unique) < 2:
            single_class_subjects.append((s, corr_unique[0]))
        else:
            both_class_subjects.append(s)
            
    print("\nSubjects contributing only ONE class (usable reps):")
    if single_class_subjects:
        for s, label in single_class_subjects:
            label_str = "correct only" if label == 1 else "incorrect only"
            print(f"  Subject {s} (contributed {label_str})")
    else:
        print("  None")
        
    # 2. Compute Effect Sizes & Bootstrap CIs
    biomarkers = [
        "peak_flexion_deg", "peak_extension_deg", "rom_deg",
        "peak_descent_velocity_deg_per_frame", "mean_descent_velocity_deg_per_frame",
        "peak_ascent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame",
        "tempo_ratio", "jerk_proxy_std"
    ]
    
    B = 5000
    rng = np.random.default_rng(42)
    results = []
    
    for bio in biomarkers:
        # Pre-group data by subject for bootstrapping speed
        correct_by_sub = {s: df_usable[(df_usable['subject_id'] == s) & (df_usable['correctness_label'] == 1)][bio].values for s in subjects_all}
        incorrect_by_sub = {s: df_usable[(df_usable['subject_id'] == s) & (df_usable['correctness_label'] == 0)][bio].values for s in subjects_all}
        
        cv_all = df_usable[df_usable['correctness_label'] == 1][bio].values
        iv_all = df_usable[df_usable['correctness_label'] == 0][bio].values
        
        mean_correct = np.mean(cv_all) if len(cv_all) > 0 else np.nan
        sd_correct = np.std(cv_all, ddof=1) if len(cv_all) > 1 else np.nan
        
        mean_incorrect = np.mean(iv_all) if len(iv_all) > 0 else np.nan
        sd_incorrect = np.std(iv_all, ddof=1) if len(iv_all) > 1 else np.nan
        
        d_val = cohens_d(cv_all, iv_all)
        
        boot_ds = []
        for _ in range(B):
            pick = rng.choice(subjects_all, size=len(subjects_all), replace=True)
            cv_boot = np.concatenate([correct_by_sub[s] for s in pick])
            iv_boot = np.concatenate([incorrect_by_sub[s] for s in pick])
            if len(cv_boot) > 1 and len(iv_boot) > 1:
                boot_ds.append(cohens_d(cv_boot, iv_boot))
                
        if boot_ds:
            ci_low, ci_high = np.percentile(boot_ds, [2.5, 97.5])
            excludes_zero = (ci_low > 0) or (ci_high < 0)
        else:
            ci_low, ci_high, excludes_zero = np.nan, np.nan, False
            
        results.append({
            "biomarker": bio,
            "n_correct": len(cv_all),
            "n_incorrect": len(iv_all),
            "mean_correct": round(float(mean_correct), 4),
            "sd_correct": round(float(sd_correct), 4),
            "mean_incorrect": round(float(mean_incorrect), 4),
            "sd_incorrect": round(float(sd_incorrect), 4),
            "cohens_d": round(float(d_val), 4),
            "ci_lower": round(float(ci_low), 4) if not np.isnan(ci_low) else np.nan,
            "ci_upper": round(float(ci_high), 4) if not np.isnan(ci_high) else np.nan,
            "ci_excludes_zero": bool(excludes_zero)
        })
        
    res_df = pd.DataFrame(results)
    
    # Sort by descending |cohens_d|
    res_df['abs_d'] = res_df['cohens_d'].abs()
    res_df = res_df.sort_values(by='abs_d', ascending=False).drop(columns=['abs_d']).reset_index(drop=True)
    
    # Save Output CSV
    OUT_EFFECT_SIZES.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(OUT_EFFECT_SIZES, index=False)
    
    print("\n--- Full Effect-Size Table (sorted by |d|) ---")
    cols_to_print = ["biomarker", "cohens_d", "ci_lower", "ci_upper", "ci_excludes_zero"]
    print(res_df[cols_to_print].to_string(index=False))
    
    # 3. Explicit Ascent-Velocity Callout
    print("\n--- Ascent-Velocity Callout ---")
    for val_type in ["peak_ascent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame"]:
        row = res_df[res_df['biomarker'] == val_type].iloc[0]
        ex_zero_str = "excludes zero (reliable)" if row['ci_excludes_zero'] else "crosses zero (not reliable)"
        print(f"  {val_type}: d={row['cohens_d']:.4f}, CI [{row['ci_lower']:.4f}, {row['ci_upper']:.4f}] - {ex_zero_str}")
        
    # 4. Per-Subject Shift Table
    significant_biomarkers = [
        "peak_flexion_deg", "rom_deg", "peak_descent_velocity_deg_per_frame",
        "mean_descent_velocity_deg_per_frame", "jerk_proxy_std"
    ]
    
    shifts = []
    for s in both_class_subjects:
        sub_df = df_usable[df_usable['subject_id'] == s]
        corr_reps = sub_df[sub_df['correctness_label'] == 1]
        incorr_reps = sub_df[sub_df['correctness_label'] == 0]
        
        n_correct = len(corr_reps)
        n_incorrect = len(incorr_reps)
        
        sub_shifts = {
            "subject_id": s,
            "n_correct": n_correct,
            "n_incorrect": n_incorrect
        }
        
        for bio in significant_biomarkers:
            mean_corr = corr_reps[bio].mean()
            mean_incorr = incorr_reps[bio].mean()
            # shift = incorrect - correct
            sub_shifts[f"shift_{bio}"] = round(float(mean_incorr - mean_corr), 4)
            
        shifts.append(sub_shifts)
        
    shifts_df = pd.DataFrame(shifts)
    if not shifts_df.empty:
        # Sort by peak_flexion shift
        shifts_df = shifts_df.sort_values(by="shift_peak_flexion_deg", ascending=True).reset_index(drop=True)
        # Save CSV
        shifts_df.to_csv(OUT_SUBJ_SHIFTS, index=False)
        print("\n--- Per-Subject Shift Table (sorted by peak_flexion shift) ---")
        print(shifts_df.to_string(index=False))
    else:
        print("\n--- Per-Subject Shift Table ---")
        print("  No subjects contributed both correct and incorrect usable reps.")
        
    # 5. One-line-per-biomarker Plain Summary
    print("\n--- Plain Summaries (incorrect vs correct contrast) ---")
    # incorrect - correct shift direction
    for bio in biomarkers:
        row = res_df[res_df['biomarker'] == bio].iloc[0]
        # Calculate overall incorrect - correct delta
        overall_corr_mean = df_usable[df_usable['correctness_label'] == 1][bio].mean()
        overall_incorr_mean = df_usable[df_usable['correctness_label'] == 0][bio].mean()
        delta = overall_incorr_mean - overall_corr_mean
        direction = "higher" if delta > 0 else "lower"
        rel_str = "reliable" if row['ci_excludes_zero'] else "crosses zero"
        print(f"  {bio}: incorrect {direction} by {abs(delta):.4f}, d={row['cohens_d']:.4f}, CI [{row['ci_lower']:.4f}, {row['ci_upper']:.4f}], {rel_str}")
        
    print("\n=== Phase 5C Statistics Complete ===")

if __name__ == "__main__":
    main()
