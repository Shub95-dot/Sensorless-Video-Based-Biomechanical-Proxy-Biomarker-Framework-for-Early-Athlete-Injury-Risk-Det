#!/usr/bin/env python3
"""
phase10_rule_screening.py
=========================
Implements Step 10: Rule-Based Screening Layer.
It loads biomarkers, filters for Squat Subject 8 (PM_113) and Lunge Subject 6 (PM_104),
builds individual baselines from reps 1-2, applies personalised-deviation screening rules
grounded in the validated Phase 7 noise floors, outputs the screening flags, reasons,
and margins, and saves the worked example to 20_screening_outputs/worked_example_screening.csv.
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "20_screening_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data Sources
SQUAT_CSV = PROJECT_ROOT / "14_rehab24_outputs" / "biomarkers_per_rep" / "rehab24_squat_per_rep_biomarkers.csv"
LUNGE_CSV = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"

# Phase 7 Noise Floors (95% CI)
noise_floors = {
    "peak_flexion": 11.9885,    # deg
    "rom": 23.1666,             # deg
    "velocity": 40.8615         # deg/s
}

def apply_screening(df, sub_id, video_id, is_squat=True):
    df_sub = df[(df["subject_id"] == sub_id) & (df["video_id"] == video_id)].copy()
    df_sub = df_sub.sort_values("rep_number")
    
    exercise_name = "Squat" if is_squat else "Lunge"
    print(f"\n--- Running Step 10 Screening for {exercise_name} Subject {sub_id} ({video_id}) ---")
    
    # Pre-calculate biomarkers
    reps_list = []
    for _, row in df_sub.iterrows():
        rep_num = int(row["rep_number"])
        label = int(row["correctness_label"])
        
        peak_flex = row["peak_flexion_deg"]
        rom = row["rom_deg"]
        # Convert descent velocity from deg/frame to deg/s (30 fps)
        vel = abs(row["mean_descent_velocity_deg_per_frame"]) * 30.0
        
        reps_list.append({
            "rep_number": rep_num,
            "correctness_label": label,
            "peak_flexion": peak_flex,
            "rom": rom,
            "velocity": vel
        })
    df_reps = pd.DataFrame(reps_list)
    
    # Baseline is built from correct reps 1 and 2
    df_base = df_reps[df_reps["rep_number"].isin([1, 2])]
    baseline_means = df_base[["peak_flexion", "rom", "velocity"]].mean().to_dict()
    
    records = []
    
    for _, row in df_reps.iterrows():
        rep_num = int(row["rep_number"])
        label = int(row["correctness_label"])
        
        val_peak = row["peak_flexion"]
        val_rom = row["rom"]
        val_velocity = row["velocity"]
        
        # Thresholds
        t_depth = baseline_means["peak_flexion"] - noise_floors["peak_flexion"]
        t_rom = baseline_means["rom"] + noise_floors["rom"]
        t_velocity = baseline_means["velocity"] + noise_floors["velocity"]
        
        fired_rules = []
        
        # Rule 1: Excess Knee Flexion Depth (EXCESS_DEPTH)
        if val_peak < t_depth:
            fired_rules.append("EXCESS_DEPTH")
            margin_depth = t_depth - val_peak
        else:
            margin_depth = 0.0
            
        # Rule 2: Uncontrolled Descent Speed (EXCESS_VELOCITY)
        if val_velocity > t_velocity:
            fired_rules.append("EXCESS_VELOCITY")
            margin_velocity = val_velocity - t_velocity
        else:
            margin_velocity = 0.0
            
        # Rule 3: Excess Knee Excursion (EXCESS_ROM)
        if val_rom > t_rom:
            fired_rules.append("EXCESS_ROM")
            margin_rom = val_rom - t_rom
        else:
            margin_rom = 0.0
            
        flag = "SCREENING_POSITIVE" if len(fired_rules) > 0 else "NOT_FLAGGED"
        
        rec = {
            "subject_id": sub_id,
            "video_id": video_id,
            "exercise": exercise_name,
            "rep_number": rep_num,
            "correctness_label": label,
            "screening_flag": flag,
            "fired_rules": ";".join(fired_rules) if fired_rules else "None",
            "peak_flexion_val": round(val_peak, 4),
            "peak_flexion_base": round(baseline_means["peak_flexion"], 4),
            "peak_flexion_threshold": round(t_depth, 4),
            "peak_flexion_margin": round(margin_depth, 4),
            "rom_val": round(val_rom, 4),
            "rom_base": round(baseline_means["rom"], 4),
            "rom_threshold": round(t_rom, 4),
            "rom_margin": round(margin_rom, 4),
            "velocity_val": round(val_velocity, 4),
            "velocity_base": round(baseline_means["velocity"], 4),
            "velocity_threshold": round(t_velocity, 4),
            "velocity_margin": round(margin_velocity, 4)
        }
        records.append(rec)
        
        print(f"  Rep {rep_num} (label={label}): Flag={flag}, Fired={fired_rules}")
        if fired_rules:
            print(f"    Margins -> Depth: {margin_depth:.2f}°, ROM: {margin_rom:.2f}°, Velocity: {margin_velocity:.2f}°/s")
            
    return pd.DataFrame(records)

def main():
    print("=========================================================")
    print("RUNNING PHASE 10 RULE-BASED SCREENING LAYER BUILD")
    print("=========================================================")
    
    # 1. Load data
    df_squat_raw = pd.read_csv(SQUAT_CSV)
    df_lunge_raw = pd.read_csv(LUNGE_CSV)
    
    # 2. Run screening
    df_sq_screened = apply_screening(df_squat_raw, 8, "PM_113", is_squat=True)
    df_lg_screened = apply_screening(df_lunge_raw, 6, "PM_104", is_squat=False)
    
    # 3. Save combined worked example screening CSV
    df_combined = pd.concat([df_sq_screened, df_lg_screened], ignore_index=True)
    worked_csv_path = OUT_DIR / "worked_example_screening.csv"
    df_combined.to_csv(worked_csv_path, index=False)
    
    print(f"\nSaved rule-based screening outputs to: {worked_csv_path}")
    print("=========================================================")

if __name__ == "__main__":
    main()
