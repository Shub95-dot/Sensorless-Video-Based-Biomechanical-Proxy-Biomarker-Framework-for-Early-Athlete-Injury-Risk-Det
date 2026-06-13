import os
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Define BASE and paths using pathlib
BASE = Path(r"c:/Users/shiro/OneDrive/Desktop/Python files/BIOMECHANICAL ANALYSIS OF INJURY")

FILE_A_PATH = BASE / "14_rehab24_outputs/biomarkers_per_rep/rehab24_squat_per_rep_biomarkers.csv"
FILE_B_PATH = BASE / "4_pose_outputs/temporal/squats_biomarkers.csv"
FILE_C_CORRECT_PATH = BASE / "14_rehab24_outputs/smoothed_per_rep/PM_008_rep_02_smoothed.csv"
FILE_C_INCORRECT_PATH = BASE / "14_rehab24_outputs/smoothed_per_rep/PM_008_rep_17_smoothed.csv"
OUTDIR = BASE / "14_rehab24_outputs/figures_publication"

# Helper for SHA256 of full file
def compute_full_file_hash(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

# Helper for SHA256 of columns used
def compute_used_columns_hash(df, columns):
    csv_bytes = df[columns].to_csv(index=False).encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()

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
    # Setup global style
    try:
        font_path = fm.findfont("Arial", fallback_to_default=False)
        if "Arial" not in font_path:
            print("Warning: Arial font not found. Using default sans-serif font.")
    except Exception as e:
        print(f"Warning checking Arial font: {e}")

    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['Arial']
    matplotlib.rcParams['font.size'] = 11
    matplotlib.rcParams['axes.titlesize'] = 10
    matplotlib.rcParams['axes.labelsize'] = 9
    matplotlib.rcParams['xtick.labelsize'] = 9
    matplotlib.rcParams['ytick.labelsize'] = 9
    matplotlib.rcParams['legend.fontsize'] = 9
    matplotlib.rcParams['axes.spines.top'] = False
    matplotlib.rcParams['axes.spines.right'] = False
    matplotlib.rcParams['axes.grid'] = True
    matplotlib.rcParams['grid.alpha'] = 0.25
    matplotlib.rcParams['axes.axisbelow'] = True
    matplotlib.rcParams['savefig.dpi'] = 300
    matplotlib.rcParams['savefig.bbox'] = 'tight'

    # Color palette
    cmap = plt.get_cmap('viridis')
    color_correct = cmap(0.70)
    color_incorrect = cmap(0.15)

    # Deterministic RNG
    rng = np.random.default_rng(42)

    # Create output directory
    OUTDIR.mkdir(parents=True, exist_ok=True)

    print("========================================================================")
    print("STAGE 0 — Load + PRE-WRITE SANITY CHECKPOINT")
    print("========================================================================")

    # 1. Load file A
    if not FILE_A_PATH.is_file():
        raise FileNotFoundError(f"Missing File A: {FILE_A_PATH}")
    df_a = pd.read_csv(FILE_A_PATH)
    print(f"Loaded File A: {FILE_A_PATH.name} (shape: {df_a.shape})")
    
    expected_cols_a = [
        "subject_id", "video_id", "rep_number", "correctness_label",
        "peak_flexion_deg", "peak_extension_deg", "rom_deg", "tempo_ratio",
        "peak_descent_velocity_deg_per_frame", "peak_ascent_velocity_deg_per_frame",
        "mean_descent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame",
        "jerk_proxy_std"
    ]
    for col in expected_cols_a:
        if col not in df_a.columns:
            raise ValueError(f"Expected column '{col}' missing from File A!")

    # Assert shape and label counts
    assert len(df_a) == 98, f"Expected exactly 98 rows in File A, found {len(df_a)}"
    correct_count = (df_a['correctness_label'] == 1).sum()
    incorrect_count = (df_a['correctness_label'] == 0).sum()
    assert correct_count == 72, f"Expected 72 correct reps, found {correct_count}"
    assert incorrect_count == 26, f"Expected 26 incorrect reps, found {incorrect_count}"
    print(f"File A checks passed: 98 rows (72 correct, 26 incorrect).")

    # 2. Load file B
    if not FILE_B_PATH.is_file():
        raise FileNotFoundError(f"Missing File B: {FILE_B_PATH}")
    df_b = pd.read_csv(FILE_B_PATH)
    print(f"Loaded File B: {FILE_B_PATH.name} (shape: {df_b.shape})")

    assert len(df_b) == 10, f"Expected exactly 10 rows in File B, found {len(df_b)}"
    
    expected_cols_b = ["peak_flexion_deg", "rom_deg", "jerk_proxy_std"]
    for col in expected_cols_b:
        if col not in df_b.columns:
            print("File B column list:", list(df_b.columns))
            raise ValueError(f"Expected column '{col}' missing from File B!")
    print(f"File B checks passed: 10 rows, all expected biomarker columns resolved.")

    # 3. Confirm files C exist
    if not FILE_C_CORRECT_PATH.is_file():
        raise FileNotFoundError(f"Missing File C (correct): {FILE_C_CORRECT_PATH}")
    if not FILE_C_INCORRECT_PATH.is_file():
        raise FileNotFoundError(f"Missing File C (incorrect): {FILE_C_INCORRECT_PATH}")

    df_c_corr = pd.read_csv(FILE_C_CORRECT_PATH)
    df_c_incorr = pd.read_csv(FILE_C_INCORRECT_PATH)
    
    if "knee_angle_smoothed" not in df_c_corr.columns:
        print("File C correct column list:", list(df_c_corr.columns))
        raise ValueError("Column 'knee_angle_smoothed' missing from File C (correct)!")
    if "knee_angle_smoothed" not in df_c_incorr.columns:
        print("File C incorrect column list:", list(df_c_incorr.columns))
        raise ValueError("Column 'knee_angle_smoothed' missing from File C (incorrect)!")
    print("Files C checks passed: files exist and contain 'knee_angle_smoothed'.")

    # 4. Compute and print initial Cohen's d values
    fig1_biomarkers = [
        "peak_flexion_deg", "rom_deg",
        "peak_descent_velocity_deg_per_frame", "mean_descent_velocity_deg_per_frame",
        "jerk_proxy_std"
    ]
    print("\nInitial Cohen's d check:")
    for bio in fig1_biomarkers:
        correct_vals = df_a[df_a['correctness_label'] == 1][bio].values
        incorrect_vals = df_a[df_a['correctness_label'] == 0][bio].values
        d_val = cohens_d(correct_vals, incorrect_vals)
        mean_c = np.mean(correct_vals)
        mean_i = np.mean(incorrect_vals)
        print(f"  {bio:<40} : correct {mean_c:.2f} / incorrect {mean_i:.2f} / d {d_val:+.2f}")
    
    # Assert peak_flexion correct-mean is ~60.85 (±0.1)
    peak_flex_correct_mean = np.mean(df_a[df_a['correctness_label'] == 1]['peak_flexion_deg'])
    assert abs(peak_flex_correct_mean - 60.85) <= 0.1, f"Expected peak_flexion_deg correct-mean to be ~60.85, found {peak_flex_correct_mean:.4f}"
    print("\nSTAGE 0 checks passed successfully. Proceeding to plotting.")

    # ========================================================================
    # STAGE 1 — Effect sizes + ordering
    # ========================================================================
    print("\n========================================================================")
    print("STAGE 1 — Effect sizes + ordering")
    print("========================================================================")

    # Compute d for Fig 1 biomarkers and sort by |d| descending
    fig1_d_values = {}
    for bio in fig1_biomarkers:
        cv = df_a[df_a['correctness_label'] == 1][bio].values
        iv = df_a[df_a['correctness_label'] == 0][bio].values
        fig1_d_values[bio] = cohens_d(cv, iv)
    fig1_biomarkers_sorted = sorted(fig1_biomarkers, key=lambda x: abs(fig1_d_values[x]), reverse=True)
    print("Sorted Fig 1 biomarkers by |d|:")
    for bio in fig1_biomarkers_sorted:
        print(f"  {bio}: d = {fig1_d_values[bio]:.4f}")

    # Figure 2 biomarkers (all 9 numeric biomarkers)
    fig2_biomarkers = fig1_biomarkers + [
        "peak_ascent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame",
        "peak_extension_deg", "tempo_ratio"
    ]
    
    # Run cluster bootstrap for Cohen's d on all 9 biomarkers
    # Subjects = all 9 unique subject_ids in file A
    subjects_all = df_a['subject_id'].unique()
    B = 5000
    fig2_results = []

    for bio in fig2_biomarkers:
        # Pre-group data by subject for bootstrapping speed
        correct_by_sub = {s: df_a[(df_a['subject_id'] == s) & (df_a['correctness_label'] == 1)][bio].values for s in subjects_all}
        incorrect_by_sub = {s: df_a[(df_a['subject_id'] == s) & (df_a['correctness_label'] == 0)][bio].values for s in subjects_all}
        
        cv_all = df_a[df_a['correctness_label'] == 1][bio].values
        iv_all = df_a[df_a['correctness_label'] == 0][bio].values
        d_val = cohens_d(cv_all, iv_all)
        
        boot_ds = []
        for _ in range(B):
            pick = rng.choice(subjects_all, size=len(subjects_all), replace=True)
            cv_boot = np.concatenate([correct_by_sub[s] for s in pick])
            iv_boot = np.concatenate([incorrect_by_sub[s] for s in pick])
            if len(cv_boot) > 1 and len(iv_boot) > 1:
                boot_ds.append(cohens_d(cv_boot, iv_boot))
                
        ci_low, ci_high = np.percentile(boot_ds, [2.5, 97.5])
        fig2_results.append({
            'biomarker': bio,
            'd': d_val,
            'ci_low': ci_low,
            'ci_high': ci_high
        })

    # Sort Fig 2 biomarkers by |d| descending
    fig2_results_sorted = sorted(fig2_results, key=lambda x: abs(x['d']), reverse=True)
    print("\nSorted Fig 2 biomarkers by |d| with 95% CIs:")
    for res in fig2_results_sorted:
        print(f"  {res['biomarker']}: d = {res['d']:.4f} [95% CI: {res['ci_low']:.4f}, {res['ci_high']:.4f}]")

    # ========================================================================
    # STAGE 2 — FIGURE 1 (correct vs incorrect, with cluster CIs)
    # ========================================================================
    print("\nGenerating Figure 1...")
    fig1, axes = plt.subplots(2, 3, figsize=(11, 6.5))
    axes_flat = axes.flatten()

    units_dict = {
        'peak_flexion_deg': 'degrees (°)',
        'rom_deg': 'degrees (°)',
        'peak_descent_velocity_deg_per_frame': 'deg/frame',
        'mean_descent_velocity_deg_per_frame': 'deg/frame',
        'jerk_proxy_std': 'unitless'
    }

    # For each biomarker in Fig 1
    for idx, bio in enumerate(fig1_biomarkers_sorted):
        ax = axes_flat[idx]
        
        correct_vals = df_a[df_a['correctness_label'] == 1][bio].values
        incorrect_vals = df_a[df_a['correctness_label'] == 0][bio].values
        
        mean_c = np.mean(correct_vals)
        mean_i = np.mean(incorrect_vals)
        
        # Bootstrap CIs for means
        # Correct group bootstrap
        subjects_c = df_a[df_a['correctness_label'] == 1]['subject_id'].unique()
        correct_by_sub = {s: df_a[(df_a['subject_id'] == s) & (df_a['correctness_label'] == 1)][bio].values for s in subjects_c}
        boot_means_c = []
        for _ in range(B):
            pick = rng.choice(subjects_c, size=len(subjects_c), replace=True)
            boot_means_c.append(np.concatenate([correct_by_sub[s] for s in pick]).mean())
        ci_c_low, ci_c_high = np.percentile(boot_means_c, [2.5, 97.5])
        
        # Incorrect group bootstrap
        subjects_i = df_a[df_a['correctness_label'] == 0]['subject_id'].unique()
        incorrect_by_sub = {s: df_a[(df_a['subject_id'] == s) & (df_a['correctness_label'] == 0)][bio].values for s in subjects_i}
        boot_means_i = []
        for _ in range(B):
            pick = rng.choice(subjects_i, size=len(subjects_i), replace=True)
            boot_means_i.append(np.concatenate([incorrect_by_sub[s] for s in pick]).mean())
        ci_i_low, ci_i_high = np.percentile(boot_means_i, [2.5, 97.5])

        # Plot bars
        ax.bar(0, mean_c, color=color_correct, width=0.5, label='Correct' if idx == 0 else "")
        ax.bar(1, mean_i, color=color_incorrect, width=0.5, label='Incorrect' if idx == 0 else "")
        
        # Plot asymmetric error bars
        # yerr format: [[lower_error], [upper_error]]
        yerr_c = [[mean_c - ci_c_low], [ci_c_high - mean_c]]
        yerr_i = [[mean_i - ci_i_low], [ci_i_high - mean_i]]
        
        ax.errorbar(0, mean_c, yerr=yerr_c, fmt='none', ecolor='black', capsize=5, elinewidth=1.2)
        ax.errorbar(1, mean_i, yerr=yerr_i, fmt='none', ecolor='black', capsize=5, elinewidth=1.2)
        
        # Subplot details
        d_val = fig1_d_values[bio]
        ax.set_title(f"{bio}\n(d = {d_val:+.2f})", fontsize=10)
        ax.set_ylabel(units_dict[bio], fontsize=9)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Correct', 'Incorrect'])
        
        # Sample size annotation
        ax.text(0.5, 0.05, "n=72 vs 26", transform=ax.transAxes, ha='center', fontsize=8, color='gray')

    # Legend in Panel 6
    ax_leg = axes_flat[5]
    ax_leg.axis('off')
    ax_leg.bar(0, 0, color=color_correct, label="Correct (n=72)")
    ax_leg.bar(0, 0, color=color_incorrect, label="Incorrect (n=26)")
    ax_leg.errorbar([0], [0], yerr=[0], fmt='none', ecolor='black', capsize=5, elinewidth=1.2, label="subject-clustered 95% CI")
    ax_leg.legend(loc='center', frameon=False, fontsize=9)
    ax_leg.text(0.5, 0.2, "Note: Kinematic form discrimination biomarkers\nordered by descending effect size |d|.",
                ha='center', va='center', transform=ax_leg.transAxes, fontsize=9, style='italic')

    fig1.suptitle("REHAB24-6 squat form discrimination: correct vs incorrect reps", fontsize=12, y=0.98)
    fig1.tight_layout()
    
    # Save PNG and SVG
    fig1_png = OUTDIR / "fig1_correct_vs_incorrect.png"
    fig1_svg = OUTDIR / "fig1_correct_vs_incorrect.svg"
    plt.savefig(fig1_png, dpi=300)
    plt.savefig(fig1_svg)
    plt.close()
    print("Figure 1 generated.")

    # ========================================================================
    # STAGE 3 — FIGURE 2 (effect-size forest plot)
    # ========================================================================
    print("\nGenerating Figure 2...")
    plt.figure(figsize=(7, 6))
    
    # We will plot from bottom to top so that largest effect size is at the top
    # The sorted list has largest |d| at index 0. To put it at the top, we reverse the plotting index
    num_bios = len(fig2_results_sorted)
    
    for i, res in enumerate(reversed(fig2_results_sorted)):
        y_pos = i
        d_val = res['d']
        ci_low = res['ci_low']
        ci_high = res['ci_high']
        bio_name = res['biomarker']
        
        # Determine color: saturated if CI excludes 0, grey if CI crosses 0
        excludes_zero = (ci_low > 0) or (ci_high < 0)
        color = cmap(0.35) if excludes_zero else '#888888'
        
        # Plot point and horizontal error bar
        plt.errorbar(d_val, y_pos, xerr=[[d_val - ci_low], [ci_high - d_val]],
                     fmt='o', color=color, ecolor=color, capsize=4, elinewidth=1.5, markersize=6)
        
        # Annotate d value beside point
        # Adjust text placement depending on sign of d
        if d_val >= 0:
            text_x = ci_high + 0.08
            ha = 'left'
        else:
            text_x = ci_low - 0.08
            ha = 'right'
        plt.text(text_x, y_pos, f"{d_val:+.2f}", va='center', ha=ha, fontsize=8, color=color, fontweight='bold' if excludes_zero else 'normal')

    # Reference lines
    plt.axvline(0, color='black', linestyle='-', linewidth=1.0)
    
    # Guides at 0.2, 0.5, 0.8
    guides = [(-0.8, "large"), (-0.5, "medium"), (-0.2, "small"),
              (0.2, "small"), (0.5, "medium"), (0.8, "large")]
    for val, label in guides:
        plt.axvline(val, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)
        # Add tiny label along the top
        plt.text(val, num_bios - 0.3, f"{val:+.1f}\n({label})",
                 ha='center', va='bottom', fontsize=8, color='gray', alpha=0.8)

    # Set y-ticks
    labels_sorted = [res['biomarker'] for res in reversed(fig2_results_sorted)]
    plt.yticks(range(num_bios), labels_sorted, fontsize=9)
    plt.ylim(-0.5, num_bios - 0.2)
    plt.xlim(-2.5, 2.5)
    
    plt.xlabel("Cohen's d (correct − incorrect), subject-clustered 95% CI", fontsize=9)
    plt.title("Biomarker form discrimination effect sizes (n = 72 correct vs 26 incorrect)", fontsize=10, pad=15)
    
    # Add caption note
    plt.text(-2.4, -0.8, "* grey markers indicate confidence intervals crossing zero (p >= 0.05 equivalent)", fontsize=8, style='italic', color='gray')

    fig2_png = OUTDIR / "fig2_effect_sizes.png"
    fig2_svg = OUTDIR / "fig2_effect_sizes.svg"
    plt.savefig(fig2_png, dpi=300)
    plt.savefig(fig2_svg)
    plt.close()
    print("Figure 2 generated.")

    # ========================================================================
    # STAGE 4 — FIGURE 3 (cross-cohort distributions)
    # ========================================================================
    print("\nGenerating Figure 3...")
    # 1x3 panel layout for the three biomarkers
    fig3, axes = plt.subplots(1, 3, figsize=(11, 5))
    
    fig3_biomarkers = ["peak_flexion_deg", "rom_deg", "jerk_proxy_std"]
    titles_dict = {
        'peak_flexion_deg': 'Peak flexion (degrees)',
        'rom_deg': 'Range of motion (degrees)',
        'jerk_proxy_std': 'Jerk proxy (unitless)'
    }

    for idx, bio in enumerate(fig3_biomarkers):
        ax = axes[idx]
        
        # Data
        data_rehab = df_a[bio].dropna().values
        data_youtube = df_b[bio].dropna().values
        
        # Plot box plots
        bp = ax.boxplot([data_rehab, data_youtube], positions=[1, 2], widths=0.4,
                        patch_artist=True, showmeans=True,
                        meanprops=dict(marker='o', markerfacecolor='white', markeredgecolor='black', markersize=5))
        
        # Color boxes
        bp['boxes'][0].set_facecolor(color_correct)
        bp['boxes'][0].set_alpha(0.6)
        bp['boxes'][1].set_facecolor(color_incorrect)
        bp['boxes'][1].set_alpha(0.6)
        
        # Jittered individual points
        # Use rng for jitter
        jitter_rehab = rng.uniform(-0.1, 0.1, size=len(data_rehab))
        jitter_youtube = rng.uniform(-0.1, 0.1, size=len(data_youtube))
        
        ax.scatter(np.ones_like(data_rehab) + jitter_rehab, data_rehab, color=color_correct, alpha=0.4, s=12, label='REHAB24-6' if idx==0 else "")
        ax.scatter(np.ones(len(data_youtube))*2 + jitter_youtube, data_youtube, color=color_incorrect, alpha=0.5, s=20, label='YouTube' if idx==0 else "")
        
        ax.set_title(titles_dict[bio], fontsize=10)
        ax.set_xticks([1, 2])
        ax.set_xticklabels(['REHAB24-6\n(n = 98 reps)', 'YouTube\n(n = 10 subs)'], fontsize=9)
        ax.grid(True, alpha=0.25)

    fig3.suptitle("Cross-cohort kinematic distributions", fontsize=11, y=0.98)
    fig3.legend(loc='upper right', bbox_to_anchor=(0.98, 0.94), fontsize=9)
    
    # Subtitle / caption
    fig3.text(0.5, -0.05, "REHAB24-6 = per-repetition (n = 98 reps); YouTube = per-subject (n = 10 subjects).",
              ha='center', fontsize=9, style='italic')
    
    fig3.tight_layout()
    
    fig3_png = OUTDIR / "fig3_cross_cohort_distributions.png"
    fig3_svg = OUTDIR / "fig3_cross_cohort_distributions.svg"
    plt.savefig(fig3_png, dpi=300)
    plt.savefig(fig3_svg)
    plt.close()
    print("Figure 3 generated.")

    # ========================================================================
    # STAGE 5 — FIGURE 4 (representative trajectories)
    # ========================================================================
    print("\nGenerating Figure 4...")
    
    plt.figure(figsize=(7, 5))
    
    # Resolve frame index for correct trajectory
    # Correct rep: PM_008 rep 02
    x_corr = df_c_corr['frame_index_in_rep'].values if 'frame_index_in_rep' in df_c_corr.columns else np.arange(len(df_c_corr))
    y_corr = df_c_corr['knee_angle_smoothed'].values
    
    # Incorrect rep: PM_008 rep 17
    x_incorr = df_c_incorr['frame_index_in_rep'].values if 'frame_index_in_rep' in df_c_incorr.columns else np.arange(len(df_c_incorr))
    y_incorr = df_c_incorr['knee_angle_smoothed'].values
    
    # Plot curves
    plt.plot(x_corr, y_corr, color=color_correct, linewidth=2, label="Correct (rep 02)")
    plt.plot(x_incorr, y_incorr, color=color_incorrect, linewidth=2, linestyle='--', label="Incorrect (rep 17)")
    
    # Find deepest points (peak flexion)
    idx_min_corr = np.argmin(y_corr)
    peak_corr = y_corr[idx_min_corr]
    frame_min_corr = x_corr[idx_min_corr]
    
    idx_min_incorr = np.argmin(y_incorr)
    peak_incorr = y_incorr[idx_min_incorr]
    frame_min_incorr = x_incorr[idx_min_incorr]
    
    # Cross-check peak flexion values
    print(f"Correct rep peak flexion: {peak_corr:.2f}° (expected: ~62.16°)")
    print(f"Incorrect rep peak flexion: {peak_incorr:.2f}° (expected: ~50.03°)")
    
    if abs(peak_corr - 62.16) > 0.5:
        print(f"Warning: Correct rep peak flexion {peak_corr:.2f}° differs from expected 62.16° by more than 0.5°!")
    if abs(peak_incorr - 50.03) > 0.5:
        print(f"Warning: Incorrect rep peak flexion {peak_incorr:.2f}° differs from expected 50.03° by more than 0.5°!")
        
    # Mark deepest points
    plt.scatter(frame_min_corr, peak_corr, color=color_correct, marker='o', s=40, zorder=5)
    plt.scatter(frame_min_incorr, peak_incorr, color=color_incorrect, marker='o', s=40, zorder=5)
    
    # Annotate peak flexion text
    plt.annotate(f"peak flexion = {peak_corr:.2f}°", xy=(frame_min_corr, peak_corr),
                 xytext=(frame_min_corr, peak_corr + 15), ha='center', va='bottom',
                 arrowprops=dict(arrowstyle="->", color=color_correct, lw=1.0))
                 
    plt.annotate(f"peak flexion = {peak_incorr:.2f}°", xy=(frame_min_incorr, peak_incorr),
                 xytext=(frame_min_incorr, peak_incorr - 20), ha='center', va='top',
                 arrowprops=dict(arrowstyle="->", color=color_incorrect, lw=1.0))

    plt.xlabel("Frame index", fontsize=9)
    plt.ylabel("Knee flexion angle (degrees)", fontsize=9)
    plt.title("Representative knee-angle trajectories: correct vs incorrect squat form\n(subject PM_008)", fontsize=10)
    
    # Custom Legend
    # correct (rep 02):   peak 62.16°, ROM 117°, tempo 1.00
    # incorrect (rep 17): peak 50.03°, ROM 127.73°, tempo 1.65
    leg_labels = [
        f"Correct (rep 02): peak {peak_corr:.2f}°, ROM 117.02°, tempo 1.00",
        f"Incorrect (rep 17): peak {peak_incorr:.2f}°, ROM 127.73°, tempo 1.65"
    ]
    plt.legend(leg_labels, loc='upper right', fontsize=9)
    
    fig4_png = OUTDIR / "fig4_representative_trajectories.png"
    fig4_svg = OUTDIR / "fig4_representative_trajectories.svg"
    plt.savefig(fig4_png, dpi=300)
    plt.savefig(fig4_svg)
    plt.close()
    print("Figure 4 generated.")

    # ========================================================================
    # STAGE 6 — PROVENANCE CSV
    # ========================================================================
    print("\n========================================================================")
    print("STAGE 6 — PROVENANCE CSV")
    print("========================================================================")

    # Compute hashes of full source files
    sha_a = compute_full_file_hash(FILE_A_PATH)
    sha_b = compute_full_file_hash(FILE_B_PATH)
    sha_c_corr = compute_full_file_hash(FILE_C_CORRECT_PATH)
    sha_c_incorr = compute_full_file_hash(FILE_C_INCORRECT_PATH)

    # Columns definitions for hashing
    cols_fig1 = ["subject_id", "correctness_label", "peak_flexion_deg", "rom_deg", "peak_descent_velocity_deg_per_frame", "mean_descent_velocity_deg_per_frame", "jerk_proxy_std"]
    cols_fig2 = ["subject_id", "correctness_label", "peak_flexion_deg", "rom_deg", "peak_descent_velocity_deg_per_frame", "mean_descent_velocity_deg_per_frame", "jerk_proxy_std", "peak_ascent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame", "peak_extension_deg", "tempo_ratio"]
    cols_fig3_a = ["peak_flexion_deg", "rom_deg", "jerk_proxy_std"]
    cols_fig3_b = ["peak_flexion_deg", "rom_deg", "jerk_proxy_std"]
    cols_fig4_corr = ["frame_index_in_rep", "knee_angle_smoothed"]
    cols_fig4_incorr = ["frame_index_in_rep", "knee_angle_smoothed"]

    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    provenance_data = [
        {
            'figure_id': 'fig1',
            'source_role': 'rehab_per_rep',
            'source_relpath': FILE_A_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_a),
            'n_cols': df_a.shape[1],
            'columns_used': "|".join(cols_fig1),
            'sha256_used_columns': compute_used_columns_hash(df_a, cols_fig1),
            'sha256_full_file': sha_a,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig2',
            'source_role': 'rehab_per_rep',
            'source_relpath': FILE_A_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_a),
            'n_cols': df_a.shape[1],
            'columns_used': "|".join(cols_fig2),
            'sha256_used_columns': compute_used_columns_hash(df_a, cols_fig2),
            'sha256_full_file': sha_a,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig3',
            'source_role': 'rehab_per_rep',
            'source_relpath': FILE_A_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_a),
            'n_cols': df_a.shape[1],
            'columns_used': "|".join(cols_fig3_a),
            'sha256_used_columns': compute_used_columns_hash(df_a, cols_fig3_a),
            'sha256_full_file': sha_a,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig3',
            'source_role': 'youtube_per_subject',
            'source_relpath': FILE_B_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_b),
            'n_cols': df_b.shape[1],
            'columns_used': "|".join(cols_fig3_b),
            'sha256_used_columns': compute_used_columns_hash(df_b, cols_fig3_b),
            'sha256_full_file': sha_b,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig4',
            'source_role': 'trajectory_correct',
            'source_relpath': FILE_C_CORRECT_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_c_corr),
            'n_cols': df_c_corr.shape[1],
            'columns_used': "|".join(cols_fig4_corr),
            'sha256_used_columns': compute_used_columns_hash(df_c_corr, cols_fig4_corr),
            'sha256_full_file': sha_c_corr,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig4',
            'source_role': 'trajectory_incorrect',
            'source_relpath': FILE_C_INCORRECT_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_c_incorr),
            'n_cols': df_c_incorr.shape[1],
            'columns_used': "|".join(cols_fig4_incorr),
            'sha256_used_columns': compute_used_columns_hash(df_c_incorr, cols_fig4_incorr),
            'sha256_full_file': sha_c_incorr,
            'generated_utc': generated_utc
        }
    ]

    prov_df = pd.DataFrame(provenance_data)
    prov_csv_path = OUTDIR / "figure_data_provenance.csv"
    prov_df.to_csv(prov_csv_path, index=False)
    print(f"Generated figure data provenance CSV at: {prov_csv_path.name}")

    # ========================================================================
    # STAGE 7 — FINAL VERIFICATION
    # ========================================================================
    print("\n========================================================================")
    print("STAGE 7 — FINAL VERIFICATION")
    print("========================================================================")

    expected_files = [
        "fig1_correct_vs_incorrect.png", "fig1_correct_vs_incorrect.svg",
        "fig2_effect_sizes.png", "fig2_effect_sizes.svg",
        "fig3_cross_cohort_distributions.png", "fig3_cross_cohort_distributions.svg",
        "fig4_representative_trajectories.png", "fig4_representative_trajectories.svg",
        "figure_data_provenance.csv"
    ]

    missing_files = []
    for f in expected_files:
        p = OUTDIR / f
        if not p.is_file():
            missing_files.append(f)

    if missing_files:
        raise FileNotFoundError(f"Verification FAILED: The following files are missing in OUTDIR: {missing_files}")

    print("Verification PASSED: All 8 image files and the provenance CSV exist in OUTDIR.")
    print("\nSummary of Generated Figures and Key Stats:")
    print(f"{'Figure':<8} | {'Output Files':<55} | {'Source Files':<35} | {'Key Stat'}")
    print("-" * 125)
    
    # print stat details
    print(f"fig1     | fig1_correct_vs_incorrect.[png|svg]                     | {FILE_A_PATH.name:<35} | peak_flexion d = {fig1_d_values['peak_flexion_deg']:+.2f}")
    print(f"fig2     | fig2_effect_sizes.[png|svg]                             | {FILE_A_PATH.name:<35} | largest d = {fig2_results_sorted[0]['d']:+.2f} ({fig2_results_sorted[0]['biomarker']})")
    print(f"fig3     | fig3_cross_cohort_distributions.[png|svg]               | {FILE_A_PATH.name} & B | Rehab mean peak flexion: {np.mean(df_a['peak_flexion_deg']):.2f}°")
    print(f"fig4     | fig4_representative_trajectories.[png|svg]               | {FILE_C_CORRECT_PATH.name} & {FILE_C_INCORRECT_PATH.name:<30} | peak flexion correct vs incorrect: {peak_corr:.2f}° vs {peak_incorr:.2f}°")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nCRITICAL PIPELINE ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
