#!/usr/bin/env python3
"""
phase7_worked_example.py
========================
This script applies the approved cross-exercise transfer weights to a handful of
existing squat and lunge repetitions from the REHAB24-6 dataset.

It performs a screening characterisation of these repetitions by mapping the measured
biomarkers, their projection-uncertainty bounds, and their transfer weights.
It saves the outputs to 17_uncertainty_framework_outputs/worked_example.csv and
generates a figure worked_example_weights.png.
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
OUT_DIR = PROJECT_ROOT / "17_uncertainty_framework_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data Sources
SQUAT_CSV = PROJECT_ROOT / "14_rehab24_outputs" / "biomarkers_per_rep" / "rehab24_squat_per_rep_biomarkers.csv"
LUNGE_CSV = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"

# Transfer Weights and SDs (Projection-only component)
transfer_weights = {
    "start_flexion": 0.2263,
    "peak_flexion": 0.5715,
    "rom": 0.1530,
    "velocity": 0.0492
}

transfer_sds = {
    "start_flexion": np.sqrt(94.4880),  # 9.7205 deg
    "peak_flexion": np.sqrt(37.4132),   # 6.1166 deg
    "rom": np.sqrt(139.7047),          # 11.8197 deg
    "velocity": np.sqrt(434.6253)      # 20.8477 deg/s
}

def main():
    print("=========================================================")
    print("RUNNING PHASE 7 WORKED EXAMPLE: CHARACTERISATION PASS")
    print("=========================================================")
    
    # 1. Load Squat data and extract selected reps
    if not SQUAT_CSV.is_file():
        print(f"Error: Squat CSV not found at: {SQUAT_CSV}")
        sys.exit(1)
    df_squat = pd.read_csv(SQUAT_CSV)
    
    # Select PM_008 rep 2 (correct) and PM_008 rep 17 (incorrect)
    sq_rep1 = df_squat[(df_squat["video_id"] == "PM_008") & (df_squat["rep_number"] == 2)].iloc[0]
    sq_rep2 = df_squat[(df_squat["video_id"] == "PM_008") & (df_squat["rep_number"] == 17)].iloc[0]
    
    # 2. Load Lunge data and extract selected reps
    if not LUNGE_CSV.is_file():
        print(f"Error: Lunge CSV not found at: {LUNGE_CSV}")
        sys.exit(1)
    df_lunge = pd.read_csv(LUNGE_CSV)
    
    # Select PM_021 rep 2 (correct) and PM_021 rep 7 (incorrect)
    lg_rep1 = df_lunge[(df_lunge["video_id"] == "PM_021") & (df_lunge["rep_number"] == 2)].iloc[0]
    lg_rep2 = df_lunge[(df_lunge["video_id"] == "PM_021") & (df_lunge["rep_number"] == 7)].iloc[0]
    
    # Selected repetitions dictionary
    reps_data = [
        {
            "exercise": "Squat",
            "video_id": "PM_008",
            "rep_number": 2,
            "form": "Correct",
            "start_flexion": 180.0 - sq_rep1["peak_extension_deg"],
            "peak_flexion": sq_rep1["peak_flexion_deg"],
            "rom": sq_rep1["rom_deg"],
            # Convert degrees/frame to degrees/second (30 FPS video)
            "velocity": abs(sq_rep1["mean_descent_velocity_deg_per_frame"]) * 30.0
        },
        {
            "exercise": "Squat",
            "video_id": "PM_008",
            "rep_number": 17,
            "form": "Incorrect",
            "start_flexion": 180.0 - sq_rep2["peak_extension_deg"],
            "peak_flexion": sq_rep2["peak_flexion_deg"],
            "rom": sq_rep2["rom_deg"],
            "velocity": abs(sq_rep2["mean_descent_velocity_deg_per_frame"]) * 30.0
        },
        {
            "exercise": "Lunge",
            "video_id": "PM_021",
            "rep_number": 2,
            "form": "Correct",
            "start_flexion": 180.0 - lg_rep1["peak_extension_deg"],
            "peak_flexion": lg_rep1["peak_flexion_deg"],
            "rom": lg_rep1["rom_deg"],
            # Convert degrees/frame to degrees/second (30 FPS video)
            "velocity": abs(lg_rep1["mean_descent_velocity_deg_per_frame"]) * 30.0
        },
        {
            "exercise": "Lunge",
            "video_id": "PM_021",
            "rep_number": 7,
            "form": "Incorrect",
            "start_flexion": 180.0 - lg_rep2["peak_extension_deg"],
            "peak_flexion": lg_rep2["peak_flexion_deg"],
            "rom": lg_rep2["rom_deg"],
            "velocity": abs(lg_rep2["mean_descent_velocity_deg_per_frame"]) * 30.0
        }
    ]
    
    # Create worked example DataFrame
    df_worked = pd.DataFrame(reps_data)
    
    # Calculate confidence bounds for each biomarker (95% CI: +/- 1.96 * SD)
    for bio in ["start_flexion", "peak_flexion", "rom", "velocity"]:
        sd = transfer_sds[bio]
        df_worked[f"{bio}_ci_half"] = round(1.96 * sd, 4)
        df_worked[f"{bio}_weight"] = transfer_weights[bio]
        
    worked_csv_path = OUT_DIR / "worked_example.csv"
    df_worked.to_csv(worked_csv_path, index=False)
    print(f"Saved worked example CSV to: {worked_csv_path}")
    
    # 3. Print Worked Example Characterisation details
    print("\n--- Worked Example Repetitions Characterisation ---")
    for idx, rep in df_worked.iterrows():
        print(f"\n{rep['exercise']} Rep ({rep['video_id']} rep {rep['rep_number']}, Label: {rep['form']}):")
        print(f"  Start Flexion : {rep['start_flexion']:.2f}° (95% CI: ±{rep['start_flexion_ci_half']:.2f}°, Weight: {rep['start_flexion_weight']:.4f})")
        print(f"  Peak Flexion  : {rep['peak_flexion']:.2f}° (95% CI: ±{rep['peak_flexion_ci_half']:.2f}°, Weight: {rep['peak_flexion_weight']:.4f})")
        print(f"  ROM           : {rep['rom']:.2f}° (95% CI: ±{rep['rom_ci_half']:.2f}°, Weight: {rep['rom_weight']:.4f})")
        print(f"  Descent Vel   : {rep['velocity']:.2f}°/s (95% CI: ±{rep['velocity_ci_half']:.2f}°/s, Weight: {rep['velocity_weight']:.4f})")

    # 4. Generate Figure showing weighting and uncertainties in action
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    biomarkers = ["start_flexion", "peak_flexion", "rom", "velocity"]
    titles = [
        "Start Flexion (Weight: 22.63%)",
        "Peak Flexion / Depth (Weight: 57.15%)",
        "Range of Motion (Weight: 15.30%)",
        "Descent Velocity (Weight: 4.92%)"
    ]
    units = ["degrees", "degrees", "degrees", "degrees/second"]
    
    labels = [f"{r['exercise']}\n({r['form']})" for _, r in df_worked.iterrows()]
    x_positions = np.arange(len(df_worked))
    
    for idx, bio in enumerate(biomarkers):
        ax = axes[idx]
        vals = df_worked[bio].values
        ci_half = df_worked[f"{bio}_ci_half"].values
        
        # Color coding: squats in blue, lunges in green
        colors = ["royalblue", "navy", "mediumseagreen", "darkgreen"]
        
        bars = ax.bar(x_positions, vals, yerr=ci_half, capsize=8, color=colors, alpha=0.8, edgecolor="black", error_kw={"elinewidth": 2, "capthick": 1.5})
        
        ax.set_title(titles[idx], fontsize=12, fontweight="bold")
        ax.set_ylabel(f"Value ({units[idx]})")
        ax.set_xticks(x_positions)
        ax.set_xticklabels(labels)
        ax.grid(True, alpha=0.3, linestyle=":")
        
        # Label values on top of bars
        for bar, val in zip(bars, vals):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2.0, height / 2.0, f"{val:.1f}", ha="center", va="center", color="white", fontweight="bold", fontsize=10)
            
    plt.suptitle("Worked Example: Uncertainty Bounds (95% CI) and Weights in Action\n(Notice narrow bounds/high weight for Peak Flexion vs. wide bounds/low weight for Velocity)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    
    fig_path = OUT_DIR / "worked_example_weights.png"
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"\nSaved worked example weights figure to: {fig_path}")
    print("=========================================================")

if __name__ == "__main__":
    main()
