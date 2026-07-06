#!/usr/bin/env python3
"""
phase9_digital_twin.py
======================
This script implements Phase 9 Stage 2: Digital Twin Continuous Update.
It builds a baseline from reps 1-2, incrementally updates the reference on correct reps
3-5 (within noise floor), and locks the reference while flagging deviations on incorrect
reps 6-10 (outside noise floor). It prints measurement-based exclusion messages, saves the
log to worked_example_twin.csv, and plots the twin's reference evolution in twin_tracking.png.
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
OUT_DIR = PROJECT_ROOT / "19_digital_twin_outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Data Sources
SQUAT_CSV = PROJECT_ROOT / "14_rehab24_outputs" / "biomarkers_per_rep" / "rehab24_squat_per_rep_biomarkers.csv"
LUNGE_CSV = PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep" / "rehab24_lunge_per_rep_biomarkers.csv"

# Phase 7 Projection Noise Floors
noise_floors = {
    "start_flexion": 1.96 * 9.7205,    # 19.0522 deg
    "peak_flexion": 1.96 * 6.1166,     # 11.9885 deg
    "rom": 1.96 * 11.8197,            # 23.1666 deg
    "velocity": 1.96 * 20.8477        # 40.8615 deg/s
}

def simulate_twin(df, sub_id, video_id, is_squat=True):
    # Filter subject data
    df_sub = df[(df["subject_id"] == sub_id) & (df["video_id"] == video_id)].copy()
    df_sub = df_sub.sort_values("rep_number")
    
    exercise_name = "Squat" if is_squat else "Lunge"
    print(f"\n--- Digital Twin Simulation for {exercise_name} Subject {sub_id} ({video_id}) ---")
    
    # Pre-calculate biomarkers
    reps_list = []
    for _, row in df_sub.iterrows():
        rep_num = int(row["rep_number"])
        label = int(row["correctness_label"])
        
        start_flex = 180.0 - row["peak_extension_deg"]
        peak_flex = row["peak_flexion_deg"]
        rom = row["rom_deg"]
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
    
    # Initialize twin state (reps 1-2)
    # We compute baseline mean from Reps 1 and 2
    df_base = df_reps[df_reps["rep_number"].isin([1, 2])]
    active_ref = df_base[["start_flexion", "peak_flexion", "rom", "velocity"]].mean().to_dict()
    running_counts = {bio: 2 for bio in active_ref}
    
    # For descriptive purposes, keep descriptive SD of baseline
    base_sd = df_base[["start_flexion", "peak_flexion", "rom", "velocity"]].std().to_dict()
    
    records = []
    
    # Log initial state for Reps 1 and 2
    for idx, row in df_reps.iterrows():
        rep_num = int(row["rep_number"])
        label = int(row["correctness_label"])
        
        if rep_num in [1, 2]:
            # Baseline reps are just logged under the initial state
            rec = {
                "subject_id": sub_id,
                "video_id": video_id,
                "exercise": exercise_name,
                "rep_number": rep_num,
                "role": "Baseline",
                "correctness_label": label
            }
            for bio in ["start_flexion", "peak_flexion", "rom", "velocity"]:
                val = row[bio]
                rec[f"{bio}_val"] = round(val, 4)
                rec[f"{bio}_ref_before"] = round(active_ref[bio], 4)
                rec[f"{bio}_ref_after"] = round(active_ref[bio], 4)
                rec[f"{bio}_delta"] = 0.0
                rec[f"{bio}_status"] = "WITHIN-NOISE"
                rec[f"{bio}_exclusion_msg"] = ""
            records.append(rec)
            
        else:
            # Test Reps 3-10
            role = "Quiet-Test" if label == 1 else "Firing-Test"
            rec = {
                "subject_id": sub_id,
                "video_id": video_id,
                "exercise": exercise_name,
                "rep_number": rep_num,
                "role": role,
                "correctness_label": label
            }
            
            # We process each biomarker independently
            for bio in ["start_flexion", "peak_flexion", "rom", "velocity"]:
                val = row[bio]
                ref_before = active_ref[bio]
                nf = noise_floors[bio]
                
                delta = abs(val - ref_before)
                flag = "DEVIATION DETECTED" if delta > nf else "WITHIN-NOISE"
                
                exclusion_msg = ""
                # Update Twin State Reference
                if flag == "WITHIN-NOISE":
                    # Update running mean
                    n_old = running_counts[bio]
                    ref_after = (n_old * ref_before + val) / (n_old + 1)
                    running_counts[bio] = n_old + 1
                    active_ref[bio] = ref_after
                else:
                    # Keep old reference (exclusion)
                    ref_after = ref_before
                    # Display the Measurement-Based Exclusion Message
                    bio_name_clean = bio.replace("_", " ")
                    exclusion_msg = (
                        f"Rep {rep_num} deviated from your baseline beyond validated measurement uncertainty "
                        f"(on biomarker {bio_name_clean}). The twin does not update the reference from this rep, "
                        f"because from a single observation it cannot distinguish a transient fluctuation from a "
                        f"genuine sustained change — that distinction would require the deviation to persist across "
                        f"multiple sessions."
                    )
                    print(f"  [EXCLUSION INFO] {exclusion_msg}")
                
                rec[f"{bio}_val"] = round(val, 4)
                rec[f"{bio}_ref_before"] = round(ref_before, 4)
                rec[f"{bio}_ref_after"] = round(ref_after, 4)
                rec[f"{bio}_delta"] = round(delta, 4)
                rec[f"{bio}_status"] = flag
                rec[f"{bio}_exclusion_msg"] = exclusion_msg
                
            records.append(rec)
            
    return pd.DataFrame(records)

def main():
    # 1. Load data
    df_squat_raw = pd.read_csv(SQUAT_CSV)
    df_lunge_raw = pd.read_csv(LUNGE_CSV)
    
    # 2. Run Digital Twin simulation
    df_sq = simulate_twin(df_squat_raw, 8, "PM_113", is_squat=True)
    df_lg = simulate_twin(df_lunge_raw, 6, "PM_104", is_squat=False)
    
    # 3. Combine and save CSV
    df_combined = pd.concat([df_sq, df_lg], ignore_index=True)
    worked_csv_path = OUT_DIR / "worked_example_twin.csv"
    df_combined.to_csv(worked_csv_path, index=False)
    print(f"\nSaved twin progression tracking CSV to: {worked_csv_path}")
    
    # 4. Generate Plot twin_tracking.png
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    
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
        sq_sub = df_combined[df_combined["exercise"] == "Squat"]
        vals_sq = sq_sub[f"{bio}_val"].values
        refs_sq = sq_sub[f"{bio}_ref_before"].values  # Reference used for gating each rep
        deltas_sq = sq_sub[f"{bio}_delta"].values
        
        # Plot active reference mean at each step as a step-wise line
        ax_sq.step(x, refs_sq, where="mid", color="dimgray", linestyle="--", linewidth=1.5, label="Active Reference")
        
        # Plot shaded noise floor band centered on the active reference at each step
        ax_sq.fill_between(x, refs_sq - nf, refs_sq + nf, step="mid", color="darkgray", alpha=0.15, label=f"Gated Noise Floor (±{nf:.2f})")
        
        # Plot connection line for measured values
        ax_sq.plot(x, vals_sq, color="lightgray", linestyle="-", linewidth=1.5, zorder=1)
        
        # Plot points color-coded by their individual gating status
        legend_labels = {}
        for idx in range(10):
            val = vals_sq[idx]
            delta = deltas_sq[idx]
            rep_x = x[idx]
            
            if idx < 2:
                lbl = "Baseline (Reps 1-2)"
                color = "dimgray"
                marker = "o"
            else:
                if delta > nf:
                    lbl = "Deviation Detected (Excluded)"
                    color = "crimson"
                    marker = "s"
                else:
                    lbl = "Within Noise Floor (Absorbed)"
                    color = "mediumseagreen"
                    marker = "o"
            
            h = ax_sq.scatter(rep_x, val, color=color, marker=marker, s=80, edgecolors="black", zorder=3)
            if lbl not in legend_labels:
                legend_labels[lbl] = h
                
        ax_sq.set_title(f"Squat Subject 8 - {titles[bio]}", fontsize=12, fontweight="bold")
        ax_sq.set_xlabel("Repetition Number (Pseudo-Time)")
        ax_sq.set_ylabel(f"Value ({units[bio]})")
        ax_sq.set_xticks(x)
        ax_sq.grid(True, alpha=0.3, linestyle=":")
        
        if row_idx == 0:
            handles = [ax_sq.get_lines()[0], ax_sq.collections[0]] + list(legend_labels.values())
            labels = ["Active Reference", f"Gated Noise Floor (±{nf:.2f})"] + list(legend_labels.keys())
            ax_sq.legend(handles, labels, loc="lower left", fontsize=9)
            
        if bio == "velocity":
            ax_sq.text(0.05, 0.05, "Velocity has wide floor (±40.86°/s);\nreference remains stable.", 
                       transform=ax_sq.transAxes, fontsize=9.5, fontweight="bold",
                       bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkgray', boxstyle="round,pad=0.4"))
            
        # --- LUNGE (Subject 6, Right Column) ---
        ax_lg = axes[row_idx, 1]
        lg_sub = df_combined[df_combined["exercise"] == "Lunge"]
        vals_lg = lg_sub[f"{bio}_val"].values
        refs_lg = lg_sub[f"{bio}_ref_before"].values
        deltas_lg = lg_sub[f"{bio}_delta"].values
        
        # Plot active reference mean at each step as a step-wise line
        ax_lg.step(x, refs_lg, where="mid", color="dimgray", linestyle="--", linewidth=1.5, label="Active Reference")
        
        # Plot shaded noise floor band centered on the active reference
        ax_lg.fill_between(x, refs_lg - nf, refs_lg + nf, step="mid", color="darkgray", alpha=0.15, label=f"Gated Noise Floor (±{nf:.2f})")
        
        # Plot connection line for measured values
        ax_lg.plot(x, vals_lg, color="lightgray", linestyle="-", linewidth=1.5, zorder=1)
        
        # Plot points color-coded by their individual gating status
        legend_labels_lg = {}
        for idx in range(10):
            val = vals_lg[idx]
            delta = deltas_lg[idx]
            rep_x = x[idx]
            
            if idx < 2:
                lbl = "Baseline (Reps 1-2)"
                color = "dimgray"
                marker = "o"
            else:
                if delta > nf:
                    lbl = "Deviation Detected (Excluded)"
                    color = "crimson"
                    marker = "s"
                else:
                    lbl = "Within Noise Floor (Absorbed)"
                    color = "mediumseagreen"
                    marker = "o"
            
            h = ax_lg.scatter(rep_x, val, color=color, marker=marker, s=80, edgecolors="black", zorder=3)
            if lbl not in legend_labels_lg:
                legend_labels_lg[lbl] = h
                
        ax_lg.set_title(f"Lunge Subject 6 - {titles[bio]}", fontsize=12, fontweight="bold")
        ax_lg.set_xlabel("Repetition Number (Pseudo-Time)")
        ax_lg.set_ylabel(f"Value ({units[bio]})")
        ax_lg.set_xticks(x)
        ax_lg.grid(True, alpha=0.3, linestyle=":")
        
        if row_idx == 0:
            handles = [ax_lg.get_lines()[0], ax_lg.collections[0]] + list(legend_labels_lg.values())
            labels = ["Active Reference", f"Gated Noise Floor (±{nf:.2f})"] + list(legend_labels_lg.keys())
            ax_lg.legend(handles, labels, loc="lower left", fontsize=9)
            
        if bio == "velocity":
            ax_lg.text(0.05, 0.05, "Velocity has wide floor (±40.86°/s);\nall test reps stay within-noise.", 
                       transform=ax_lg.transAxes, fontsize=9.5, fontweight="bold",
                       bbox=dict(facecolor='white', alpha=0.9, edgecolor='darkgray', boxstyle="round,pad=0.4"))
            
    plt.suptitle("Continuous Digital Twin Progression: Reference Evolution & Noise-Gated updates\n(Baseline updates on absorbed correct reps 3-5; locked/flat when incorrect reps 6-10 are excluded)", fontsize=14, fontweight="bold")
    plt.tight_layout()
    
    fig_path = OUT_DIR / "twin_tracking.png"
    plt.savefig(fig_path, dpi=300)
    plt.close()
    print(f"\nSaved digital twin progression tracking plot to: {fig_path}")
    print("=========================================================")

if __name__ == "__main__":
    main()
