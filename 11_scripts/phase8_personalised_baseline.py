#!/usr/bin/env python3
"""
phase8_personalised_baseline.py
===============================
This script executes Phase 8 Stage 3: Personalised Progression Tracking.
It builds a baseline from correct reps 1-2 for Squat Subject 8 and Lunge Subject 6,
gates subsequent test reps (3-5 correct, 6-10 incorrect) against the Phase 7 validated
projection noise floors, saves a worked example CSV, and plots the baseline tracking figure.
Points in the figure are color-coded by their own biomarker's gating status.
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_ROOT / "18_personalised_baseline_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data Sources
SQUAT_CSV = PROJECT_ROOT / "14_rehab24_outputs" / "biomarkers_per_rep" / "rehab24_squat_per_rep_biomarkers.csv"
LUNGE_CSV = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"

# Phase 7 Projection Noise Floors (95% CI = +/- 1.96 * SD_proj)
noise_floors = {
    "start_flexion": 1.96 * 9.7205,    # 19.0522 deg
    "peak_flexion": 1.96 * 6.1166,     # 11.9885 deg
    "rom": 1.96 * 11.8197,            # 23.1666 deg
    "velocity": 1.96 * 20.8477        # 40.8615 deg/s
}

def process_subject(df, sub_id, video_id, is_squat=True):
    # Filter subject data
    df_sub = df[(df["subject_id"] == sub_id) & (df["video_id"] == video_id)].copy()
    df_sub = df_sub.sort_values("rep_number")
    
    # Calculate biomarkers with consistent scaling/naming
    reps_list = []
    for _, row in df_sub.iterrows():
        rep_num = row["rep_number"]
        label = row["correctness_label"]
        
        start_flex = 180.0 - row["peak_extension_deg"]
        peak_flex = row["peak_flexion_deg"]
        rom = row["rom_deg"]
        # Convert deg/frame to deg/s (30 FPS video)
        vel = abs(row["mean_descent_velocity_deg_per_frame"]) * 30.0
        
        reps_list.append({
            "rep_number": rep_num,
            "correctness_label": label,
            "start_flexion": start_flex,
            "peak_flexion": peak_flex,
            "rom": rom,
            "velocity": vel
        })
        
    df_reps = pd.DataFrame(reps_list)
    
    # Baseline Block: first 2 correct reps (Reps 1 and 2)
    # We verify that reps 1 and 2 are indeed correct (label == 1)
    df_base = df_reps[df_reps["rep_number"].isin([1, 2])]
    if (df_base["correctness_label"] != 1).any():
        print(f"Warning: Baseline reps for Subject {sub_id} include non-correct reps!")
        
    # Calculate baseline mean
    base_mean = df_base[["start_flexion", "peak_flexion", "rom", "velocity"]].mean().to_dict()
    # Calculate baseline SD (descriptive only!)
    base_sd = df_base[["start_flexion", "peak_flexion", "rom", "velocity"]].std().to_dict()
    
    # Process test sequence (Reps 3-10)
    records = []
    for _, row in df_reps.iterrows():
        rep_num = int(row["rep_number"])
        label = int(row["correctness_label"])
        role = "Baseline" if rep_num in [1, 2] else ("Quiet-Test" if label == 1 else "Firing-Test")
        
        rep_record = {
            "subject_id": sub_id,
            "video_id": video_id,
            "exercise": "Squat" if is_squat else "Lunge",
            "rep_number": rep_num,
            "role": role,
            "correctness_label": label
        }
        
        for bio in ["start_flexion", "peak_flexion", "rom", "velocity"]:
            val = row[bio]
            mu = base_mean[bio]
            sd_desc = base_sd[bio] if not np.isnan(base_sd[bio]) else 0.0
            nf = noise_floors[bio]
            
            delta = abs(val - mu)
            flag = "DEVIATION DETECTED" if delta > nf else "WITHIN-NOISE"
            
            rep_record[f"{bio}_val"] = round(val, 4)
            rep_record[f"{bio}_base_mean"] = round(mu, 4)
            rep_record[f"{bio}_base_sd_desc"] = round(sd_desc, 4)
            rep_record[f"{bio}_noise_floor"] = round(nf, 4)
            rep_record[f"{bio}_delta"] = round(delta, 4)
            rep_record[f"{bio}_status"] = flag
            
        records.append(rep_record)
        
    return pd.DataFrame(records), base_mean, base_sd

def main():
    print("=========================================================")
    print("RUNNING PHASE 8 PERSONALISED BASELINE: STAGE 3 EXECUTION")
    print("=========================================================")
    
    # 1. Load datasets
    if not SQUAT_CSV.is_file():
        print(f"Error: Squat CSV not found at: {SQUAT_CSV}")
        sys.exit(1)
    df_squat_raw = pd.read_csv(SQUAT_CSV)
    
    if not LUNGE_CSV.is_file():
        print(f"Error: Lunge CSV not found at: {LUNGE_CSV}")
        sys.exit(1)
    df_lunge_raw = pd.read_csv(LUNGE_CSV)
    
    # 2. Process Squat Subject 8 (PM_113)
    df_sq_processed, sq_mean, sq_sd = process_subject(df_squat_raw, 8, "PM_113", is_squat=True)
    
    # 3. Process Lunge Subject 6 (PM_104)
    df_lg_processed, lg_mean, lg_sd = process_subject(df_lunge_raw, 6, "PM_104", is_squat=False)
    
    # 4. Combine and save worked example CSV
    df_combined = pd.concat([df_sq_processed, df_lg_processed], ignore_index=True)
    worked_csv_path = OUT_DIR / "worked_example_baseline.csv"
    df_combined.to_csv(worked_csv_path, index=False)
    print(f"Saved baseline tracking CSV to: {worked_csv_path}")
    
    # 5. Print out text results for review
    for ex in ["Squat", "Lunge"]:
        df_ex = df_combined[df_combined["exercise"] == ex]
        print(f"\n--- {ex} Progression Tracking (Subject {df_ex.iloc[0]['subject_id']}, {df_ex.iloc[0]['video_id']}) ---")
        for _, row in df_ex.iterrows():
            print(f"  Rep {row['rep_number']} ({row['role']}):")
            print(f"    Peak Flexion : {row['peak_flexion_val']:.2f}° (Delta: {row['peak_flexion_delta']:.2f}°, Gated Status: {row['peak_flexion_status']})")
            print(f"    Descent Vel  : {row['velocity_val']:.2f}°/s (Delta: {row['velocity_delta']:.2f}°/s, Gated Status: {row['velocity_status']})")
            
    # 6. Plotting baseline_tracking.png
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    
    # Squats Left, Lunges Right
    # Row 1: Peak Flexion (Depth), Row 2: Descent Velocity
    biomarkers = ["peak_flexion", "velocity"]
    titles = {
        "peak_flexion": "Peak Flexion (Depth)",
        "velocity": "Descent Velocity"
    }
    units = {
        "peak_flexion": "degrees",
        "velocity": "degrees / second"
    }
    
    x = np.arange(1, 11)
    
    for row_idx, bio in enumerate(biomarkers):
        nf = noise_floors[bio]
        
        # --- SQUAT (Subject 8, Left Column) ---
        ax_sq = axes[row_idx, 0]
        sq_sub = df_combined[(df_combined["exercise"] == "Squat")]
        vals_sq = sq_sub[f"{bio}_val"].values
        deltas_sq = sq_sub[f"{bio}_delta"].values
        mu_sq = sq_mean[bio]
        
        # Plot baseline line and shaded noise band
        ax_sq.axhline(mu_sq, color="darkgray", linestyle="--", linewidth=1.5, label="Baseline Mean")
        ax_sq.fill_between(x, mu_sq - nf, mu_sq + nf, color="darkgray", alpha=0.15, label=f"95% Noise Floor (±{nf:.2f})")
        
        # Plot the connection line
        ax_sq.plot(x, vals_sq, color="lightgray", linestyle="-", linewidth=1.5, zorder=1)
        
        # Plot individual points color-coded by their OWN biomarker status
        # We also want to accumulate labels for the legend
        legend_labels = {}
        for idx in range(10):
            val = vals_sq[idx]
            delta = deltas_sq[idx]
            rep_x = x[idx]
            
            if idx < 2:
                # Baseline
                lbl = "Baseline (Reps 1-2)"
                color = "dimgray"
                marker = "o"
            else:
                if delta > nf:
                    lbl = "Deviation Detected"
                    color = "crimson"
                    marker = "s"
                else:
                    lbl = "Within Noise Floor"
                    color = "mediumseagreen"
                    marker = "o"
            
            h = ax_sq.scatter(rep_x, val, color=color, marker=marker, s=80, edgecolors="black", zorder=3)
            if lbl not in legend_labels:
                legend_labels[lbl] = h
        
        # Formatting
        ax_sq.set_title(f"Squat Subject 8 - {titles[bio]}", fontsize=12, fontweight="bold")
        ax_sq.set_xlabel("Repetition Number (Pseudo-Time)")
        ax_sq.set_ylabel(f"Value ({units[bio]})")
        ax_sq.set_xticks(x)
        ax_sq.grid(True, alpha=0.3, linestyle=":")
        
        # Add labels to legend
        if row_idx == 0:
            handles = [ax_sq.get_lines()[0], ax_sq.collections[0]] + list(legend_labels.values())
            labels = ["Baseline Mean", f"95% Noise Floor (±{nf:.2f})"] + list(legend_labels.keys())
            ax_sq.legend(handles, labels, loc="lower left", fontsize=9)
            
        # Add specific annotations for descent velocity showing it doesn't independently fire
        if bio == "velocity":
            ax_sq.text(0.05, 0.05, "Velocity has wide floor (±40.86°/s);\nonly Rep 6 deviates.", 
                       transform=ax_sq.transAxes, fontsize=9.5, fontweight="bold",
                       bbox=dict(facecolor='white', alpha=0.9, edgecolor='crimson', boxstyle="round,pad=0.4"))
            
        # --- LUNGE (Subject 6, Right Column) ---
        ax_lg = axes[row_idx, 1]
        lg_sub = df_combined[(df_combined["exercise"] == "Lunge")]
        vals_lg = lg_sub[f"{bio}_val"].values
        deltas_lg = lg_sub[f"{bio}_delta"].values
        mu_lg = lg_mean[bio]
        
        # Plot baseline line and shaded noise band
        ax_lg.axhline(mu_lg, color="darkgray", linestyle="--", linewidth=1.5, label="Baseline Mean")
        ax_lg.fill_between(x, mu_lg - nf, mu_lg + nf, color="darkgray", alpha=0.15, label=f"95% Noise Floor (±{nf:.2f})")
        
        # Plot the connection line
        ax_lg.plot(x, vals_lg, color="lightgray", linestyle="-", linewidth=1.5, zorder=1)
        
        # Plot individual points color-coded by their OWN biomarker status
        legend_labels_lg = {}
        for idx in range(10):
            val = vals_lg[idx]
            delta = deltas_lg[idx]
            rep_x = x[idx]
            
            if idx < 2:
                # Baseline
                lbl = "Baseline (Reps 1-2)"
                color = "dimgray"
                marker = "o"
            else:
                if delta > nf:
                    lbl = "Deviation Detected"
                    color = "crimson"
                    marker = "s"
                else:
                    lbl = "Within Noise Floor"
                    color = "mediumseagreen"
                    marker = "o"
            
            h = ax_lg.scatter(rep_x, val, color=color, marker=marker, s=80, edgecolors="black", zorder=3)
            if lbl not in legend_labels_lg:
                legend_labels_lg[lbl] = h
        
        # Formatting
        ax_lg.set_title(f"Lunge Subject 6 - {titles[bio]}", fontsize=12, fontweight="bold")
        ax_lg.set_xlabel("Repetition Number (Pseudo-Time)")
        ax_lg.set_ylabel(f"Value ({units[bio]})")
        ax_lg.set_xticks(x)
        ax_lg.grid(True, alpha=0.3, linestyle=":")
        
        # Add labels to legend
        if row_idx == 0:
            handles = [ax_lg.get_lines()[0], ax_lg.collections[0]] + list(legend_labels_lg.values())
            labels = ["Baseline Mean", f"95% Noise Floor (±{nf:.2f})"] + list(legend_labels_lg.keys())
            ax_lg.legend(handles, labels, loc="lower left", fontsize=9)
            
        # Add specific annotations for descent velocity showing it doesn't independently fire
        if bio == "velocity":
            ax_lg.text(0.05, 0.05, "Velocity has wide floor (±40.86°/s);\nall test reps stay within-noise.", 
                       transform=ax_lg.transAxes, fontsize=9.5, fontweight="bold",
                       bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkgray', boxstyle="round,pad=0.4"))
            
    plt.suptitle("Personalised progression tracking: Baseline and Gated Deviation Detection\n(Quiet reps stay within measurement noise band; Firing reps exceed noise floor)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    
    fig_path = OUT_DIR / "baseline_tracking.png"
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"\nSaved baseline progression tracking plot to: {fig_path}")
    print("=========================================================")

if __name__ == "__main__":
    main()
