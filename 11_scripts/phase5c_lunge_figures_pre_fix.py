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

FILE_LUNGE_BIOMARKERS_PATH = BASE / "15_rehab24_lunge_outputs/biomarkers_per_rep/rehab24_lunge_per_rep_biomarkers.csv"
FILE_LUNGE_EFFECTS_PATH = BASE / "15_rehab24_lunge_outputs/metadata/phase5c_effect_sizes_ci.csv"
FILE_LUNGE_SHIFTS_PATH = BASE / "15_rehab24_lunge_outputs/metadata/phase5c_per_subject_shifts.csv"
FILE_SQUAT_EFFECTS_PATH = BASE / "14_rehab24_outputs/metadata/phase5b_effect_sizes_ci.csv"

FILE_C_CORRECT_PATH = BASE / "15_rehab24_lunge_outputs/smoothed_per_rep/PM_125_rep_14_smoothed.csv"
FILE_C_INCORRECT_PATH = BASE / "15_rehab24_lunge_outputs/smoothed_per_rep/PM_125_rep_16_smoothed.csv"

OUTDIR = BASE / "15_rehab24_lunge_outputs/figures_publication"

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
    cols_to_hash = [c for c in columns if c in df.columns]
    csv_bytes = df[cols_to_hash].to_csv(index=False).encode('utf-8')
    return hashlib.sha256(csv_bytes).hexdigest()

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

    # Load lunge files
    if not FILE_LUNGE_BIOMARKERS_PATH.is_file():
        raise FileNotFoundError(f"Missing lunge biomarkers file: {FILE_LUNGE_BIOMARKERS_PATH}")
    df_biomarkers = pd.read_csv(FILE_LUNGE_BIOMARKERS_PATH)
    print(f"Loaded Lunge Biomarkers: {FILE_LUNGE_BIOMARKERS_PATH.name} (shape: {df_biomarkers.shape})")

    if not FILE_LUNGE_EFFECTS_PATH.is_file():
        raise FileNotFoundError(f"Missing lunge effects file: {FILE_LUNGE_EFFECTS_PATH}")
    df_effects = pd.read_csv(FILE_LUNGE_EFFECTS_PATH)
    print(f"Loaded Lunge Effects: {FILE_LUNGE_EFFECTS_PATH.name} (shape: {df_effects.shape})")

    if not FILE_SQUAT_EFFECTS_PATH.is_file():
        raise FileNotFoundError(f"Missing squat effects file: {FILE_SQUAT_EFFECTS_PATH}")
    df_squat_effects = pd.read_csv(FILE_SQUAT_EFFECTS_PATH)
    print(f"Loaded Squat Effects: {FILE_SQUAT_EFFECTS_PATH.name} (shape: {df_squat_effects.shape})")

    # Confirm files C exist
    if not FILE_C_CORRECT_PATH.is_file():
        raise FileNotFoundError(f"Missing File C (correct): {FILE_C_CORRECT_PATH}")
    if not FILE_C_INCORRECT_PATH.is_file():
        raise FileNotFoundError(f"Missing File C (incorrect): {FILE_C_INCORRECT_PATH}")

    df_c_corr = pd.read_csv(FILE_C_CORRECT_PATH)
    df_c_incorr = pd.read_csv(FILE_C_INCORRECT_PATH)
    
    if "knee_angle_smoothed" not in df_c_corr.columns:
        raise ValueError("Column 'knee_angle_smoothed' missing from File C (correct)!")
    if "knee_angle_smoothed" not in df_c_incorr.columns:
        raise ValueError("Column 'knee_angle_smoothed' missing from File C (incorrect)!")
    print("Files C checks passed: files exist and contain 'knee_angle_smoothed'.")

    # Create df_usable (filtering phase_identification_status == 'ok')
    df_usable = df_biomarkers[df_biomarkers['phase_identification_status'] == 'ok'].copy()
    
    n_correct = int(df_effects['n_correct'].iloc[0])
    n_incorrect = int(df_effects['n_incorrect'].iloc[0])
    
    # Assert shape and label counts of analytical cohort
    assert len(df_usable) == n_correct + n_incorrect, f"Usable cohort size mismatch: {len(df_usable)} vs {n_correct + n_incorrect}"
    print(f"Descriptive counts verified: n = {n_correct} correct vs {n_incorrect} incorrect reps (total usable = {len(df_usable)}).")

    # Check for biomarker alignment between squat and lunge CSVs
    squat_bios = set(df_squat_effects['biomarker'])
    lunge_bios = set(df_effects['biomarker'])
    common_bios = squat_bios.intersection(lunge_bios)
    print(f"\nBiomarker name check:")
    print(f"  Squat biomarkers: {sorted(list(squat_bios))}")
    print(f"  Lunge biomarkers: {sorted(list(lunge_bios))}")
    print(f"  Common biomarkers: {sorted(list(common_bios))}")
    
    diff_squat = squat_bios - lunge_bios
    diff_lunge = lunge_bios - squat_bios
    if diff_squat or diff_lunge:
        print(f"  Warning: Biomarkers differ!")
        print(f"    Only in squat: {diff_squat}")
        print(f"    Only in lunge: {diff_lunge}")
    else:
        print("  All biomarker names are identical in both CSVs.")

    print("\nSTAGE 0 checks passed successfully. Proceeding to plotting.")

    # ========================================================================
    # STAGE 2 — FIGURE 1 (correct vs incorrect, with cluster CIs)
    # ========================================================================
    print("\nGenerating Figure 1...")
    
    # Filter and sort reliable/marginal biomarkers
    fig1_df = df_effects[df_effects['reliability_tier'].isin(['reliable', 'reliable_marginal'])].copy()
    fig1_df['abs_d'] = fig1_df['cohens_d'].abs()
    fig1_df_sorted = fig1_df.sort_values(by='abs_d', ascending=False).reset_index(drop=True)
    fig1_biomarkers_sorted = fig1_df_sorted['biomarker'].tolist()
    
    # Since we have 7 biomarkers, we will use a 2x4 layout (8 panels)
    fig1, axes = plt.subplots(2, 4, figsize=(14, 6.5))
    axes_flat = axes.flatten()

    units_dict = {
        'peak_flexion_deg': 'degrees (°)',
        'rom_deg': 'degrees (°)',
        'peak_descent_velocity_deg_per_frame': 'deg/frame',
        'mean_descent_velocity_deg_per_frame': 'deg/frame',
        'jerk_proxy_std': 'unitless',
        'peak_ascent_velocity_deg_per_frame': 'deg/frame',
        'mean_ascent_velocity_deg_per_frame': 'deg/frame',
        'peak_extension_deg': 'degrees (°)',
        'tempo_ratio': 'ratio'
    }

    B = 5000

    for idx, bio in enumerate(fig1_biomarkers_sorted):
        ax = axes_flat[idx]
        row = fig1_df_sorted[fig1_df_sorted['biomarker'] == bio].iloc[0]
        mean_c = row['mean_correct']
        mean_i = row['mean_incorrect']
        d_val = row['cohens_d']
        tier = row['reliability_tier']
        
        # Bootstrap CIs for means at runtime
        subjects_c = df_usable[df_usable['correctness_label'] == 1]['subject_id'].unique()
        correct_by_sub = {s: df_usable[(df_usable['subject_id'] == s) & (df_usable['correctness_label'] == 1)][bio].values for s in subjects_c}
        boot_means_c = []
        for _ in range(B):
            pick = rng.choice(subjects_c, size=len(subjects_c), replace=True)
            boot_means_c.append(np.concatenate([correct_by_sub[s] for s in pick]).mean())
        ci_c_low, ci_c_high = np.percentile(boot_means_c, [2.5, 97.5])
        
        subjects_i = df_usable[df_usable['correctness_label'] == 0]['subject_id'].unique()
        incorrect_by_sub = {s: df_usable[(df_usable['subject_id'] == s) & (df_usable['correctness_label'] == 0)][bio].values for s in subjects_i}
        boot_means_i = []
        for _ in range(B):
            pick = rng.choice(subjects_i, size=len(subjects_i), replace=True)
            boot_means_i.append(np.concatenate([incorrect_by_sub[s] for s in pick]).mean())
        ci_i_low, ci_i_high = np.percentile(boot_means_i, [2.5, 97.5])

        # Plot bars
        ax.bar(0, mean_c, color=color_correct, width=0.5, label='Correct' if idx == 0 else "")
        ax.bar(1, mean_i, color=color_incorrect, width=0.5, label='Incorrect' if idx == 0 else "")
        
        # Plot asymmetric error bars
        yerr_c = [[mean_c - ci_c_low], [ci_c_high - mean_c]]
        yerr_i = [[mean_i - ci_i_low], [ci_i_high - mean_i]]
        
        ax.errorbar(0, mean_c, yerr=yerr_c, fmt='none', ecolor='black', capsize=5, elinewidth=1.2)
        ax.errorbar(1, mean_i, yerr=yerr_i, fmt='none', ecolor='black', capsize=5, elinewidth=1.2)
        
        # Subplot details
        title_suffix = ""
        if tier == "reliable_marginal":
            title_suffix = " (marginal)"
        ax.set_title(f"{bio}{title_suffix}\n(d = {d_val:+.2f})", fontsize=10)
        ax.set_ylabel(units_dict.get(bio, 'unitless'), fontsize=9)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Correct', 'Incorrect'])
        
        # Sample size annotation
        ax.text(0.5, 0.05, f"n={n_correct} vs {n_incorrect}", transform=ax.transAxes, ha='center', fontsize=8, color='gray')

    # Legend in Panel 8
    ax_leg = axes_flat[7]
    ax_leg.axis('off')
    ax_leg.bar(0, 0, color=color_correct, label=f"Correct (n={n_correct})")
    ax_leg.bar(0, 0, color=color_incorrect, label=f"Incorrect (n={n_incorrect})")
    ax_leg.errorbar([0], [0], yerr=[0], fmt='none', ecolor='black', capsize=5, elinewidth=1.2, label="subject-clustered 95% CI")
    ax_leg.legend(loc='center', frameon=False, fontsize=9)
    ax_leg.text(0.5, 0.2, "Note: Kinematic form discrimination biomarkers\nordered by descending effect size |d|.",
                ha='center', va='center', transform=ax_leg.transAxes, fontsize=9, style='italic')

    fig1.suptitle("REHAB24-6 lunge form discrimination: correct vs incorrect (working leg)", fontsize=12, y=0.98)
    fig1.tight_layout()
    
    # Save PNG and SVG
    fig1_png = OUTDIR / "fig_L1_correct_vs_incorrect.png"
    fig1_svg = OUTDIR / "fig_L1_correct_vs_incorrect.svg"
    plt.savefig(fig1_png, dpi=300)
    plt.savefig(fig1_svg)
    plt.close()
    print("Figure L1 generated.")

    # ========================================================================
    # STAGE 3 — FIGURE 2 (effect-size forest plot)
    # ========================================================================
    print("\nGenerating Figure 2...")
    plt.figure(figsize=(7, 6))
    
    # Sort all 9 by absolute cohens_d descending
    df_effects['abs_d'] = df_effects['cohens_d'].abs()
    df_effects_sorted = df_effects.sort_values(by='abs_d', ascending=False).reset_index(drop=True)
    num_bios = len(df_effects_sorted)
    
    for i, row in enumerate(reversed(df_effects_sorted.to_dict('records'))):
        y_pos = i
        d_val = row['cohens_d']
        ci_low = row['ci_lower']
        ci_high = row['ci_upper']
        bio_name = row['biomarker']
        excludes_zero = row['ci_excludes_zero']
        
        # Determine color: saturated if CI excludes 0, grey if CI crosses 0
        color = cmap(0.35) if excludes_zero else '#888888'
        
        # Plot point and horizontal error bar
        plt.errorbar(d_val, y_pos, xerr=[[d_val - ci_low], [ci_high - d_val]],
                     fmt='o', color=color, ecolor=color, capsize=4, elinewidth=1.5, markersize=6)
        
        # Annotate d value beside point
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
        plt.text(val, num_bios - 0.3, f"{val:+.1f}\n({label})",
                 ha='center', va='bottom', fontsize=8, color='gray', alpha=0.8)

    # Set y-ticks
    labels_sorted = [row['biomarker'] for row in reversed(df_effects_sorted.to_dict('records'))]
    plt.yticks(range(num_bios), labels_sorted, fontsize=9)
    plt.ylim(-0.5, num_bios - 0.2)
    plt.xlim(-3.5, 4.0)
    
    plt.xlabel("Cohen's d (correct − incorrect), subject-clustered 95% CI", fontsize=9)
    plt.title(f"Lunge biomarker form-discrimination effect sizes (n = {n_correct} correct vs {n_incorrect} incorrect)", fontsize=10, pad=15)
    
    # Add caption note
    plt.text(-3.4, -0.8, "* grey markers indicate confidence intervals crossing zero (p >= 0.05 equivalent)", fontsize=8, style='italic', color='gray')

    fig2_png = OUTDIR / "fig_L2_effect_sizes.png"
    fig2_svg = OUTDIR / "fig_L2_effect_sizes.svg"
    plt.savefig(fig2_png, dpi=300)
    plt.savefig(fig2_svg)
    plt.close()
    print("Figure L2 generated.")

    # ========================================================================
    # STAGE 4 — FIGURE 3 (cross-exercise comparison: squat vs lunge)
    # ========================================================================
    print("\nGenerating Figure 3...")
    
    # Define grouped panels: left panel (7 biomarkers) and right panel (2 ascent velocity biomarkers)
    left_bios_ordered = [
        "peak_flexion_deg",
        "rom_deg",
        "mean_descent_velocity_deg_per_frame",
        "peak_descent_velocity_deg_per_frame",
        "jerk_proxy_std",
        "peak_extension_deg",
        "tempo_ratio"
    ]
    right_bios_ordered = [
        "peak_ascent_velocity_deg_per_frame",
        "mean_ascent_velocity_deg_per_frame"
    ]
    
    fig3, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6.5), gridspec_kw={'width_ratios': [5, 2]})
    
    color_squat_reg = cmap(0.75) # light green
    color_lunge_reg = cmap(0.25) # dark blue-purple
    
    # Draw guides and horizontal axes on both
    for ax in [ax1, ax2]:
        ax.axvline(0, color='black', linestyle='-', linewidth=1.0)
        ax.set_xlim(-3.5, 4.0)
        for val, label in guides:
            ax.axvline(val, color='gray', linestyle=':', alpha=0.3, linewidth=0.8)
            
    # Plot left panel (Shared & Null Biomarkers)
    num_left = len(left_bios_ordered)
    for i, bio in enumerate(reversed(left_bios_ordered)):
        y_pos = i
        
        # Squat data
        row_s = df_squat_effects[df_squat_effects['biomarker'] == bio].iloc[0]
        d_s = row_s['cohens_d']
        ci_l_s = row_s['ci_lower']
        ci_h_s = row_s['ci_upper']
        excl_s = row_s['ci_excludes_zero']
        color_s = color_squat_reg if excl_s else '#888888'
        
        ax1.errorbar(d_s, y_pos + 0.15, xerr=[[d_s - ci_l_s], [ci_h_s - d_s]],
                     fmt='o', color=color_s, ecolor=color_s, capsize=4, elinewidth=1.5, markersize=6)
                     
        # Lunge data
        row_l = df_effects[df_effects['biomarker'] == bio].iloc[0]
        d_l = row_l['cohens_d']
        ci_l_l = row_l['ci_lower']
        ci_h_l = row_l['ci_upper']
        excl_l = row_l['ci_excludes_zero']
        color_l = color_lunge_reg if excl_l else '#888888'
        
        ax1.errorbar(d_l, y_pos - 0.15, xerr=[[d_l - ci_l_l], [ci_h_l - d_l]],
                     fmt='o', color=color_l, ecolor=color_l, capsize=4, elinewidth=1.5, markersize=6)

    # Plot labels along the top of guides for ax1
    for val, label in guides:
        ax1.text(val, num_left - 0.3, f"{val:+.1f}\n({label})",
                 ha='center', va='bottom', fontsize=8, color='gray', alpha=0.8)
                 
    ax1.set_yticks(range(num_left))
    ax1.set_yticklabels(reversed(left_bios_ordered), fontsize=9)
    ax1.set_ylim(-0.5, num_left - 0.2)
    ax1.set_xlabel("Cohen's d (correct − incorrect), 95% CI", fontsize=9)
    ax1.set_title("Shared Signature & General Kinematics", fontsize=10)
    
    # Plot right panel (Ascent velocity biomarkers)
    num_right = len(right_bios_ordered)
    for i, bio in enumerate(reversed(right_bios_ordered)):
        y_pos = i
        
        # Squat data
        row_s = df_squat_effects[df_squat_effects['biomarker'] == bio].iloc[0]
        d_s = row_s['cohens_d']
        ci_l_s = row_s['ci_lower']
        ci_h_s = row_s['ci_upper']
        excl_s = row_s['ci_excludes_zero']
        color_s = color_squat_reg if excl_s else '#888888'
        
        ax2.errorbar(d_s, y_pos + 0.15, xerr=[[d_s - ci_l_s], [ci_h_s - d_s]],
                     fmt='o', color=color_s, ecolor=color_s, capsize=4, elinewidth=1.5, markersize=6)
                     
        # Lunge data
        row_l = df_effects[df_effects['biomarker'] == bio].iloc[0]
        d_l = row_l['cohens_d']
        ci_l_l = row_l['ci_lower']
        ci_h_l = row_l['ci_upper']
        excl_l = row_l['ci_excludes_zero']
        color_l = color_lunge_reg if excl_l else '#888888'
        
        ax2.errorbar(d_l, y_pos - 0.15, xerr=[[d_l - ci_l_l], [ci_h_l - d_l]],
                     fmt='o', color=color_l, ecolor=color_l, capsize=4, elinewidth=1.5, markersize=6)

    # Plot labels along the top of guides for ax2
    for val, label in guides:
        ax2.text(val, num_right - 0.3, f"{val:+.1f}\n({label})",
                 ha='center', va='bottom', fontsize=8, color='gray', alpha=0.8)
                 
    ax2.set_yticks(range(num_right))
    ax2.set_yticklabels(reversed(right_bios_ordered), fontsize=9)
    ax2.set_ylim(-0.5, num_right - 0.2)
    ax2.set_xlabel("Cohen's d (correct − incorrect), 95% CI", fontsize=9)
    ax2.set_title("Ascent Phase Divergence", fontsize=10)
    
    # Custom Legend
    import matplotlib.lines as mlines
    squat_line = mlines.Line2D([], [], color=color_squat_reg, marker='o', linestyle='none',
                               markersize=6, label='Squat (n = 72 vs 26)')
    lunge_line = mlines.Line2D([], [], color=color_lunge_reg, marker='o', linestyle='none',
                               markersize=6, label='Lunge (n = 25 vs 36)')
    ns_line = mlines.Line2D([], [], color='#888888', marker='o', linestyle='none',
                             markersize=6, label='CI crosses zero (p >= 0.05 equivalent)')
    ax1.legend(handles=[squat_line, lunge_line, ns_line], loc='upper left', fontsize=8, frameon=True)
    
    fig3.suptitle("Cross-exercise form-discrimination signature: squat vs lunge (REHAB24-6)", fontsize=12, y=0.98)
    fig3.tight_layout()
    
    fig3_png = OUTDIR / "fig_L3_cross_exercise_distributions.png"
    fig3_svg = OUTDIR / "fig_L3_cross_exercise_distributions.svg"
    plt.savefig(fig3_png, dpi=300)
    plt.savefig(fig3_svg)
    plt.close()
    print("Figure L3 generated.")

    # ========================================================================
    # STAGE 5 — FIGURE 4 (representative trajectories)
    # ========================================================================
    print("\nGenerating Figure 4...")
    
    plt.figure(figsize=(7, 5))
    
    x_corr = df_c_corr['frame_index_in_rep'].values if 'frame_index_in_rep' in df_c_corr.columns else np.arange(len(df_c_corr))
    y_corr = df_c_corr['knee_angle_smoothed'].values
    
    x_incorr = df_c_incorr['frame_index_in_rep'].values if 'frame_index_in_rep' in df_c_incorr.columns else np.arange(len(df_c_incorr))
    y_incorr = df_c_incorr['knee_angle_smoothed'].values
    
    # Plot curves
    plt.plot(x_corr, y_corr, color=color_correct, linewidth=2, label="Correct (rep 14)")
    plt.plot(x_incorr, y_incorr, color=color_incorrect, linewidth=2, linestyle='--', label="Incorrect (rep 16)")
    
    # Find deepest points (peak flexion)
    idx_min_corr = np.argmin(y_corr)
    peak_corr = y_corr[idx_min_corr]
    frame_min_corr = x_corr[idx_min_corr]
    
    idx_min_incorr = np.argmin(y_incorr)
    peak_incorr = y_incorr[idx_min_incorr]
    frame_min_incorr = x_incorr[idx_min_incorr]
    
    # Print peak values
    print(f"Correct rep peak flexion: {peak_corr:.2f}° (expected: ~99.87°)")
    print(f"Incorrect rep peak flexion: {peak_incorr:.2f}° (expected: ~57.04°)")
    
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
    plt.title("Representative lunge trajectories: correct (rep 14) vs incorrect (rep 16), subject 7", fontsize=10)
    
    # Read stats dynamically for rep 14 and 16 from df_biomarkers
    rep14_stats = df_biomarkers[(df_biomarkers['subject_id'] == 7) & (df_biomarkers['rep_number'] == 14)].iloc[0]
    rep16_stats = df_biomarkers[(df_biomarkers['subject_id'] == 7) & (df_biomarkers['rep_number'] == 16)].iloc[0]
    
    leg_labels = [
        f"Correct (rep 14): peak {rep14_stats['peak_flexion_deg']:.2f}°, ROM {rep14_stats['rom_deg']:.2f}°, tempo {rep14_stats['tempo_ratio']:.2f}",
        f"Incorrect (rep 16): peak {rep16_stats['peak_flexion_deg']:.2f}°, ROM {rep16_stats['rom_deg']:.2f}°, tempo {rep16_stats['tempo_ratio']:.2f}"
    ]
    plt.legend(leg_labels, loc='upper right', fontsize=9)
    
    fig4_png = OUTDIR / "fig_L4_representative_trajectories.png"
    fig4_svg = OUTDIR / "fig_L4_representative_trajectories.svg"
    plt.savefig(fig4_png, dpi=300)
    plt.savefig(fig4_svg)
    plt.close()
    print("Figure L4 generated.")

    # ========================================================================
    # STAGE 6 — PROVENANCE CSV
    # ========================================================================
    print("\n========================================================================")
    print("STAGE 6 — PROVENANCE CSV")
    print("========================================================================")

    # Compute hashes of full source files
    sha_lunge_biomarkers = compute_full_file_hash(FILE_LUNGE_BIOMARKERS_PATH)
    sha_lunge_effects = compute_full_file_hash(FILE_LUNGE_EFFECTS_PATH)
    sha_squat_effects = compute_full_file_hash(FILE_SQUAT_EFFECTS_PATH)
    sha_c_corr = compute_full_file_hash(FILE_C_CORRECT_PATH)
    sha_c_incorr = compute_full_file_hash(FILE_C_INCORRECT_PATH)

    # Column definitions for hashing
    cols_fig1 = ["subject_id", "correctness_label", "peak_flexion_deg", "rom_deg", 
                 "peak_descent_velocity_deg_per_frame", "mean_descent_velocity_deg_per_frame", 
                 "jerk_proxy_std", "peak_ascent_velocity_deg_per_frame", "mean_ascent_velocity_deg_per_frame"]
    cols_fig2 = ["biomarker", "cohens_d", "ci_lower", "ci_upper", "ci_excludes_zero", "reliability_tier"]
    cols_fig3_lunge = ["biomarker", "cohens_d", "ci_lower", "ci_upper", "ci_excludes_zero"]
    cols_fig3_squat = ["biomarker", "cohens_d", "ci_lower", "ci_upper", "ci_excludes_zero"]
    cols_fig4_corr = ["frame_index_in_rep", "knee_angle_smoothed"]
    cols_fig4_incorr = ["frame_index_in_rep", "knee_angle_smoothed"]

    generated_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    provenance_data = [
        {
            'figure_id': 'fig_L1',
            'source_role': 'rehab_per_rep',
            'source_relpath': FILE_LUNGE_BIOMARKERS_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_biomarkers),
            'n_cols': df_biomarkers.shape[1],
            'columns_used': "|".join(cols_fig1),
            'sha256_used_columns': compute_used_columns_hash(df_biomarkers, cols_fig1),
            'sha256_full_file': sha_lunge_biomarkers,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig_L2',
            'source_role': 'lunge_effect_sizes',
            'source_relpath': FILE_LUNGE_EFFECTS_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_effects),
            'n_cols': df_effects.shape[1],
            'columns_used': "|".join(cols_fig2),
            'sha256_used_columns': compute_used_columns_hash(df_effects, cols_fig2),
            'sha256_full_file': sha_lunge_effects,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig_L3',
            'source_role': 'lunge_effect_sizes',
            'source_relpath': FILE_LUNGE_EFFECTS_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_effects),
            'n_cols': df_effects.shape[1],
            'columns_used': "|".join(cols_fig3_lunge),
            'sha256_used_columns': compute_used_columns_hash(df_effects, cols_fig3_lunge),
            'sha256_full_file': sha_lunge_effects,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig_L3',
            'source_role': 'squat_effect_sizes',
            'source_relpath': FILE_SQUAT_EFFECTS_PATH.relative_to(BASE).as_posix(),
            'n_rows': len(df_squat_effects),
            'n_cols': df_squat_effects.shape[1],
            'columns_used': "|".join(cols_fig3_squat),
            'sha256_used_columns': compute_used_columns_hash(df_squat_effects, cols_fig3_squat),
            'sha256_full_file': sha_squat_effects,
            'generated_utc': generated_utc
        },
        {
            'figure_id': 'fig_L4',
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
            'figure_id': 'fig_L4',
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
        "fig_L1_correct_vs_incorrect.png", "fig_L1_correct_vs_incorrect.svg",
        "fig_L2_effect_sizes.png", "fig_L2_effect_sizes.svg",
        "fig_L3_cross_exercise_distributions.png", "fig_L3_cross_exercise_distributions.svg",
        "fig_L4_representative_trajectories.png", "fig_L4_representative_trajectories.svg",
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
    
    peak_flex_row = df_effects[df_effects['biomarker'] == 'peak_flexion_deg'].iloc[0]
    largest_row = df_effects_sorted.iloc[0]
    print(f"fig_L1   | fig_L1_correct_vs_incorrect.[png|svg]                   | {FILE_LUNGE_BIOMARKERS_PATH.name:<35} | peak_flexion d = {peak_flex_row['cohens_d']:+.4f}")
    print(f"fig_L2   | fig_L2_effect_sizes.[png|svg]                           | {FILE_LUNGE_EFFECTS_PATH.name:<35} | largest d = {largest_row['cohens_d']:+.4f} ({largest_row['biomarker']})")
    print(f"fig_L3   | fig_L3_cross_exercise_distributions.[png|svg]           | {FILE_LUNGE_EFFECTS_PATH.name} & {FILE_SQUAT_EFFECTS_PATH.name} | Peak flexion d: Squat = {df_squat_effects[df_squat_effects['biomarker'] == 'peak_flexion_deg'].iloc[0]['cohens_d']:.4f}, Lunge = {peak_flex_row['cohens_d']:.4f}")
    print(f"fig_L4   | fig_L4_representative_trajectories.[png|svg]            | {FILE_C_CORRECT_PATH.name} & {FILE_C_INCORRECT_PATH.name:<30} | peak flexion correct vs incorrect: {peak_corr:.2f}° vs {peak_incorr:.2f}°")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nCRITICAL PIPELINE ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
