import os
import numpy as np
import pandas as pd

# Define paths
BASE_DIR = r"c:/Users/shiro/OneDrive/Desktop/Python files/BIOMECHANICAL ANALYSIS OF INJURY"
BIOMARKERS_PATH = os.path.join(BASE_DIR, "14_rehab24_outputs", "biomarkers_per_rep", "rehab24_squat_per_rep_biomarkers.csv")
OUT_EFFECT_SIZES = os.path.join(BASE_DIR, "14_rehab24_outputs", "metadata", "phase5b_effect_sizes_ci.csv")
OUT_SUBJ_SHIFTS = os.path.join(BASE_DIR, "14_rehab24_outputs", "metadata", "phase5b_per_subject_shifts.csv")

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

def run_task1(df):
    biomarkers = [
        "peak_flexion_deg",
        "peak_extension_deg",
        "rom_deg",
        "peak_descent_velocity_deg_per_frame",
        "mean_descent_velocity_deg_per_frame",
        "peak_ascent_velocity_deg_per_frame",
        "mean_ascent_velocity_deg_per_frame",
        "tempo_ratio",
        "jerk_proxy_std"
    ]
    
    subjects_all = df['subject_id'].unique()
    B = 5000
    rng = np.random.default_rng(42)
    
    results = []
    
    for bio in biomarkers:
        # Pre-group data by subject for bootstrapping speed
        correct_by_sub = {s: df[(df['subject_id'] == s) & (df['correctness_label'] == 1)][bio].values for s in subjects_all}
        incorrect_by_sub = {s: df[(df['subject_id'] == s) & (df['correctness_label'] == 0)][bio].values for s in subjects_all}
        
        cv_all = df[df['correctness_label'] == 1][bio].values
        iv_all = df[df['correctness_label'] == 0][bio].values
        d_val = cohens_d(cv_all, iv_all)
        
        boot_ds = []
        for _ in range(B):
            pick = rng.choice(subjects_all, size=len(subjects_all), replace=True)
            cv_boot = np.concatenate([correct_by_sub[s] for s in pick])
            iv_boot = np.concatenate([incorrect_by_sub[s] for s in pick])
            if len(cv_boot) > 1 and len(iv_boot) > 1:
                boot_ds.append(cohens_d(cv_boot, iv_boot))
                
        ci_low, ci_high = np.percentile(boot_ds, [2.5, 97.5])
        excludes_zero = (ci_low > 0) or (ci_high < 0)
        
        results.append({
            "biomarker": bio,
            "cohens_d": d_val,
            "ci_lower": ci_low,
            "ci_upper": ci_high,
            "ci_excludes_zero": bool(excludes_zero)
        })
        
    res_df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(OUT_EFFECT_SIZES), exist_ok=True)
    res_df.to_csv(OUT_EFFECT_SIZES, index=False)
    print("TASK 1 RESULT (phase5b_effect_sizes_ci.csv):")
    print(res_df.to_string(index=False))
    print("\n" + "="*80 + "\n")
    return res_df

def run_task2(df):
    # Subjects contributing BOTH correct and incorrect reps
    target_subjects = [1, 3, 5, 6, 7, 8]
    significant_biomarkers = [
        "peak_flexion_deg",
        "rom_deg",
        "peak_descent_velocity_deg_per_frame",
        "mean_descent_velocity_deg_per_frame",
        "jerk_proxy_std"
    ]
    
    shifts = []
    
    for s in target_subjects:
        sub_df = df[df['subject_id'] == s]
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
            sub_shifts[f"shift_{bio}"] = mean_incorr - mean_corr
            
        shifts.append(sub_shifts)
        
    shifts_df = pd.DataFrame(shifts)
    # Sort by peak_flexion shift (shift_peak_flexion_deg)
    shifts_df = shifts_df.sort_values(by="shift_peak_flexion_deg", ascending=True)
    
    os.makedirs(os.path.dirname(OUT_SUBJ_SHIFTS), exist_ok=True)
    shifts_df.to_csv(OUT_SUBJ_SHIFTS, index=False)
    print("TASK 2 RESULT (phase5b_per_subject_shifts.csv):")
    print(shifts_df.to_string(index=False))
    print("\n" + "="*80 + "\n")
    return shifts_df

def main():
    if not os.path.exists(BIOMARKERS_PATH):
        raise FileNotFoundError(f"Biomarkers file not found at: {BIOMARKERS_PATH}")
        
    df = pd.read_csv(BIOMARKERS_PATH)
    print(f"Loaded {len(df)} rows from {BIOMARKERS_PATH}")
    print("\n" + "="*80 + "\n")
    
    run_task1(df)
    run_task2(df)

if __name__ == "__main__":
    main()
