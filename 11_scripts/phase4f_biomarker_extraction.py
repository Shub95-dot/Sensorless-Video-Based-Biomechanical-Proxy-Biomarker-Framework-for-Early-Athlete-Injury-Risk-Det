import sys
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def nan_safe_min(series):
    vals = series.dropna()
    return float(vals.min()) if len(vals) > 0 else np.nan

def nan_safe_max(series):
    vals = series.dropna()
    return float(vals.max()) if len(vals) > 0 else np.nan

def nan_safe_mean(series):
    vals = series.dropna()
    return float(vals.mean()) if len(vals) > 0 else np.nan

def main():
    project_root = Path(".")
    inclusion_path = project_root / "3_metadata" / "squats_temporal_inclusion.csv"
    smoothing_summary_path = project_root / "4_pose_outputs" / "temporal" / "squats_smoothing_summary.csv"
    smoothed_dir = project_root / "4_pose_outputs" / "temporal" / "smoothed_trajectories"
    
    # Output destinations
    output_csv_path = project_root / "4_pose_outputs" / "temporal" / "squats_biomarkers.csv"
    output_txt_path = project_root / "4_pose_outputs" / "temporal" / "phase4f_biomarker_summary.txt"
    plots_dir = project_root / "6_visualizations" / "temporal" / "squats_biomarkers"

    # 1. Validate inputs exist
    if not inclusion_path.is_file():
        print(f"Error: Inclusion manifest not found at {inclusion_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
    if not smoothing_summary_path.is_file():
        print(f"Error: Smoothing summary not found at {smoothing_summary_path.as_posix()}", file=sys.stderr)
        sys.exit(1)

    # Load inclusion CSV and filter to non-excluded subjects
    inclusion_df = pd.read_csv(inclusion_path, sep=None, engine='python')
    included_df = inclusion_df[inclusion_df['inclusion_tier'] != 'excluded'].copy()
    
    # Load smoothing summary for spike rate and validity context
    smoothing_df = pd.read_csv(smoothing_summary_path, sep=None, engine='python')
    
    included_subjects = sorted(included_df['Subject_ID'].tolist())
    print(f"Processing biomarkers for {len(included_subjects)} subjects: {included_subjects}")

    # Verify smoothed trajectory CSV files exist
    for sub_id in included_subjects:
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        if not csv_path.is_file():
            print(f"Error: Smoothed trajectory file not found: {csv_path.as_posix()}", file=sys.stderr)
            sys.exit(1)

    biomarker_results = []
    phase_ok_count = 0
    phase_failed_count = 0
    peak_flexion_invalid_count = 0
    exercise_variant_partial_count = 0
    velocity_nan_subjects = []

    for idx, sub_id in enumerate(included_subjects, 1):
        # Load smoothed trajectory
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        df = pd.read_csv(csv_path, sep=None, engine='python')
        
        # Load meta information
        sub_meta = included_df[included_df['Subject_ID'] == sub_id].iloc[0]
        sub_smooth_meta = smoothing_df[smoothing_df['Subject_ID'] == sub_id].iloc[0]
        
        depth_truncated = bool(sub_meta['depth_truncated'])
        partial_depth_real = bool(sub_meta['partial_depth_real'])
        
        knee_angle_smoothed = df['knee_angle_smoothed']
        
        # Range-based biomarkers
        peak_flexion_deg = nan_safe_min(knee_angle_smoothed)
        peak_extension_deg = nan_safe_max(knee_angle_smoothed)
        rom_deg = peak_extension_deg - peak_flexion_deg if not (np.isnan(peak_flexion_deg) or np.isnan(peak_extension_deg)) else np.nan
        mean_smoothed_angle_deg = nan_safe_mean(knee_angle_smoothed)
        
        # Peak flexion frame (global minimum frame)
        if knee_angle_smoothed.notna().any():
            peak_flexion_frame = int(knee_angle_smoothed.idxmin())
            bottom_frame = peak_flexion_frame
        else:
            peak_flexion_frame = np.nan
            bottom_frame = np.nan
            
        # Phase-based and velocity biomarkers
        # Check for NaN gaps and phase identification failure criteria
        total_frames = len(df)
        nan_count = knee_angle_smoothed.isna().sum()
        pct_nan = (nan_count / total_frames) if total_frames > 0 else 1.0
        
        first_non_nan = knee_angle_smoothed.first_valid_index()
        last_non_nan = knee_angle_smoothed.last_valid_index()
        
        # Conditions for phase identification failure
        is_failed = False
        if pct_nan > 0.30:
            is_failed = True
        if bottom_frame is np.nan or first_non_nan is None or last_non_nan is None:
            is_failed = True
        elif bottom_frame == first_non_nan or bottom_frame == last_non_nan:
            is_failed = True
            
        if is_failed:
            phase_identification_status = 'failed'
            phase_failed_count += 1
            descent_frames = np.nan
            ascent_frames = np.nan
            tempo_ratio = np.nan
            total_rep_frames = np.nan
            
            peak_descent_velocity = np.nan
            peak_ascent_velocity = np.nan
            mean_descent_velocity = np.nan
            mean_ascent_velocity = np.nan
        else:
            phase_identification_status = 'ok'
            phase_ok_count += 1
            
            # Descent and ascent durations (in frame steps / transitions)
            descent_frames = int(bottom_frame - first_non_nan)
            ascent_frames = int(last_non_nan - bottom_frame)
            total_rep_frames = descent_frames + ascent_frames
            
            tempo_ratio = ascent_frames / descent_frames if descent_frames > 0 else np.nan
            
            # Velocity computation on consecutive non-NaN transitions
            # np.diff computes diff between consecutive frames.
            # We align indices to df index to separate descent/ascent phases
            delta_angle = pd.Series(np.diff(knee_angle_smoothed), index=df.index[:-1])
            
            # Descent transitions correspond to indices from first_non_nan to bottom_frame - 1
            descent_deltas = delta_angle.loc[first_non_nan : bottom_frame - 1]
            # Ascent transitions correspond to indices from bottom_frame to last_non_nan - 1
            ascent_deltas = delta_angle.loc[bottom_frame : last_non_nan - 1]
            
            # Compute velocities safely (skipping NaN-to-value or value-to-NaN transitions)
            peak_descent_velocity = nan_safe_min(descent_deltas)
            peak_ascent_velocity = nan_safe_max(ascent_deltas)
            mean_descent_velocity = nan_safe_mean(descent_deltas)
            mean_ascent_velocity = nan_safe_mean(ascent_deltas)
            
            # Check if velocity values are NaN due to lack of consecutive transitions
            if (np.isnan(peak_descent_velocity) or np.isnan(peak_ascent_velocity) or
                np.isnan(mean_descent_velocity) or np.isnan(mean_ascent_velocity)):
                velocity_nan_subjects.append(sub_id)
                
        # Smoothness biomarker
        # jerk_proxy_std is the standard deviation of the second derivative
        second_diff = np.diff(np.diff(knee_angle_smoothed))
        second_diff_clean = second_diff[~np.isnan(second_diff)]
        jerk_proxy_std = float(np.std(second_diff_clean, ddof=1)) if len(second_diff_clean) > 1 else np.nan
        
        # Apply caveats and flags from inclusion CSV
        peak_flexion_valid = not depth_truncated
        exercise_variant_partial = partial_depth_real
        
        if not peak_flexion_valid:
            peak_flexion_invalid_count += 1
        if exercise_variant_partial:
            exercise_variant_partial_count += 1
            
        # Round numeric biomarkers to 4 decimal places safely
        res_row = {
            'Subject_ID': sub_id,
            'inclusion_tier': sub_meta['inclusion_tier'],
            'total_frames': int(sub_smooth_meta['total_frames']),
            'valid_frames': int(sub_smooth_meta['valid_frames']),
            'spike_rate_pct': round(float(sub_smooth_meta['spike_rate_pct']), 4),
            'peak_flexion_deg': round(peak_flexion_deg, 4) if not np.isnan(peak_flexion_deg) else np.nan,
            'peak_extension_deg': round(peak_extension_deg, 4) if not np.isnan(peak_extension_deg) else np.nan,
            'rom_deg': round(rom_deg, 4) if not np.isnan(rom_deg) else np.nan,
            'peak_flexion_frame': int(peak_flexion_frame) if not np.isnan(peak_flexion_frame) else np.nan,
            'mean_smoothed_angle_deg': round(mean_smoothed_angle_deg, 4) if not np.isnan(mean_smoothed_angle_deg) else np.nan,
            'descent_frames': int(descent_frames) if not np.isnan(descent_frames) else np.nan,
            'ascent_frames': int(ascent_frames) if not np.isnan(ascent_frames) else np.nan,
            'tempo_ratio': round(tempo_ratio, 4) if not np.isnan(tempo_ratio) else np.nan,
            'total_rep_frames': int(total_rep_frames) if not np.isnan(total_rep_frames) else np.nan,
            'peak_descent_velocity_deg_per_frame': round(peak_descent_velocity, 4) if not np.isnan(peak_descent_velocity) else np.nan,
            'peak_ascent_velocity_deg_per_frame': round(peak_ascent_velocity, 4) if not np.isnan(peak_ascent_velocity) else np.nan,
            'mean_descent_velocity_deg_per_frame': round(mean_descent_velocity, 4) if not np.isnan(mean_descent_velocity) else np.nan,
            'mean_ascent_velocity_deg_per_frame': round(mean_ascent_velocity, 4) if not np.isnan(mean_ascent_velocity) else np.nan,
            'jerk_proxy_std': round(jerk_proxy_std, 4) if not np.isnan(jerk_proxy_std) else np.nan,
            'peak_flexion_valid': peak_flexion_valid,
            'exercise_variant_partial': exercise_variant_partial,
            'phase_identification_status': phase_identification_status,
            'depth_truncated': depth_truncated,
            'partial_depth_real': partial_depth_real
        }
        
        # Log per subject progress
        log_rom = f"{rom_deg:.4f}" if not np.isnan(rom_deg) else "NaN"
        log_peak = f"{peak_flexion_deg:.4f}" if not np.isnan(peak_flexion_deg) else "NaN"
        log_tempo = f"{tempo_ratio:.4f}" if not np.isnan(tempo_ratio) else "NaN"
        print(f"  [{idx}/{len(included_subjects)}] {sub_id}: ROM={log_rom}° peak={log_peak}° tempo={log_tempo}")
        
        biomarker_results.append(res_row)

    # 3. Pre-write sanity checkpoint
    print("\n--- Pre-write Sanity Checkpoint ---")
    print(f"Subjects processed             : {len(included_subjects)}    (expected: 11)")
    print(f"Phase identification ok        : {phase_ok_count}")
    print(f"Phase identification failed    : {phase_failed_count}")
    print(f"Peak flexion flagged invalid   : {peak_flexion_invalid_count}    (expected: 1)")
    print(f"Exercise variant partial       : {exercise_variant_partial_count}    (expected: 1)")
    print(f"Velocity-NaN subjects          : {len(velocity_nan_subjects)}    {velocity_nan_subjects}")
    
    # Check for unexpected counts and print warning if any
    warning_triggered = False
    if len(included_subjects) != 11:
        print("Warning: Processed subjects count is not 11!", file=sys.stderr)
        warning_triggered = True
    if peak_flexion_invalid_count != 1:
        print("Warning: Peak flexion flagged invalid count is not 1!", file=sys.stderr)
        warning_triggered = True
    if exercise_variant_partial_count != 1:
        print("Warning: Exercise variant partial count is not 1!", file=sys.stderr)
        warning_triggered = True
    if warning_triggered:
        print("Pre-write validation warnings triggered. Proceeding anyway...", file=sys.stderr)
    else:
        print("Pre-write validation checks completed successfully. Proceeding to write output files...")

    # Create output directories
    plots_dir.mkdir(parents=True, exist_ok=True)

    # 4. Generate per-subject annotated plots and save
    for res in biomarker_results:
        sub_id = res['Subject_ID']
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        df = pd.read_csv(csv_path, sep=None, engine='python')
        
        plt.figure(figsize=(10, 4))
        
        # Plot smoothed trajectory as red line
        plt.plot(df['frame_index'], df['knee_angle_smoothed'], color='red', linewidth=2.0, label='Smoothed knee angle')
        
        # Shade phases if phase detection succeeded
        if res['phase_identification_status'] == 'ok':
            bottom_frame = res['peak_flexion_frame']
            first_non_nan = int(df['knee_angle_smoothed'].first_valid_index())
            last_non_nan = int(df['knee_angle_smoothed'].last_valid_index())
            
            # Shade descent in light blue
            plt.axvspan(first_non_nan, bottom_frame, color='lightblue', alpha=0.3, label='Descent Phase')
            # Shade ascent in light green
            plt.axvspan(bottom_frame, last_non_nan, color='lightgreen', alpha=0.3, label='Ascent Phase')
            
            # Vertical dashed line at peak flexion frame
            plt.axvline(x=bottom_frame, color='black', linestyle='--', alpha=0.7)
            
            # Text label above peak flexion
            y_offset = (df['knee_angle_smoothed'].max() - df['knee_angle_smoothed'].min()) * 0.1
            y_pos = res['peak_flexion_deg'] + (y_offset if y_offset > 5 else 15)
            # Clip y_pos to reasonable range
            y_pos = min(max(y_pos, 10), 180)
            
            plt.text(bottom_frame, y_pos, f"Peak flexion: {res['peak_flexion_deg']:.2f}°", 
                     ha='center', va='bottom', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))
            
            title_tempo = f"{res['tempo_ratio']:.2f}"
            title_rom = f"{res['rom_deg']:.2f}°"
        else:
            title_tempo = "failed"
            title_rom = "NaN"
            
        plt.ylim(0, 200)
        plt.xlabel('frame_index')
        plt.ylabel('knee_angle_deg (degrees)')
        
        # Title: Subject {Subject_ID} — tier: {tier} — ROM: X° — Peak flexion: Y° — Tempo ratio: Z
        plt.title(f"Subject {sub_id} — tier: {res['inclusion_tier']} — ROM: {title_rom} — Peak flexion: {res['peak_flexion_deg']:.2f}° — Tempo ratio: {title_tempo}")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='upper right')
        
        plot_path = plots_dir / f"SQ_{sub_id}_biomarker_overlay.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()

    # 5. Write squats_biomarkers.csv
    biomarkers_df = pd.DataFrame(biomarker_results)
    
    # Force exact column order
    cols_order = [
        'Subject_ID', 'inclusion_tier', 'total_frames', 'valid_frames', 'spike_rate_pct',
        'peak_flexion_deg', 'peak_extension_deg', 'rom_deg', 'peak_flexion_frame', 'mean_smoothed_angle_deg',
        'descent_frames', 'ascent_frames', 'tempo_ratio', 'total_rep_frames',
        'peak_descent_velocity_deg_per_frame', 'peak_ascent_velocity_deg_per_frame',
        'mean_descent_velocity_deg_per_frame', 'mean_ascent_velocity_deg_per_frame',
        'jerk_proxy_std', 'peak_flexion_valid', 'exercise_variant_partial',
        'phase_identification_status', 'depth_truncated', 'partial_depth_real'
    ]
    biomarkers_df = biomarkers_df[cols_order]
    biomarkers_df.to_csv(output_csv_path, index=False)
    print(f"Saved squats biomarkers to {output_csv_path.as_posix()}")

    # 6. Write phase4f_biomarker_summary.txt
    failed_status_ids = [res['Subject_ID'] for res in biomarker_results if res['phase_identification_status'] == 'failed']
    invalid_flexion_ids = [res['Subject_ID'] for res in biomarker_results if not res['peak_flexion_valid']]
    partial_variant_ids = [res['Subject_ID'] for res in biomarker_results if res['exercise_variant_partial']]
    
    # Calculate cohort summary statistics for all numeric columns
    numeric_cols = [
        'peak_flexion_deg', 'peak_extension_deg', 'rom_deg', 'peak_flexion_frame', 'mean_smoothed_angle_deg',
        'descent_frames', 'ascent_frames', 'tempo_ratio', 'total_rep_frames',
        'peak_descent_velocity_deg_per_frame', 'peak_ascent_velocity_deg_per_frame',
        'mean_descent_velocity_deg_per_frame', 'mean_ascent_velocity_deg_per_frame',
        'jerk_proxy_std'
    ]
    
    summary_txt_content = f"""Phase 4F Biomarker Extraction Summary
======================================
Subjects processed: {len(included_subjects)}
Subjects with phase_identification_status = 'failed': {failed_status_ids}
Subjects with peak_flexion_valid = False: {invalid_flexion_ids} (expected: [1682])
Subjects with exercise_variant_partial = True: {partial_variant_ids} (expected: [1774])

Cohort Descriptive Summary Statistics:
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Note: cohort statistics computed on n=11 are descriptive only and do not support inferential claims given the small sample.

"""
    
    # Format a pretty markdown table of cohort stats
    summary_txt_content += f"{'Biomarker':<40} | {'min':>10} | {'max':>10} | {'mean':>10} | {'median':>10} | {'std':>10}\n"
    summary_txt_content += f"{'-'*40}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}\n"
    
    for col in numeric_cols:
        col_values = biomarkers_df[col].dropna()
        if len(col_values) > 0:
            c_min = col_values.min()
            c_max = col_values.max()
            c_mean = col_values.mean()
            c_median = col_values.median()
            c_std = col_values.std(ddof=1) if len(col_values) > 1 else 0.0
            
            summary_txt_content += f"{col:<40} | {c_min:>10.4f} | {c_max:>10.4f} | {c_mean:>10.4f} | {c_median:>10.4f} | {c_std:>10.4f}\n"
        else:
            summary_txt_content += f"{col:<40} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10}\n"

    output_txt_path.write_text(summary_txt_content, encoding='utf-8')
    print(f"Saved run summary text file to {output_txt_path.as_posix()}")

    # 7. Print final stdout summary
    print("\n--- Final stdout Summary ---")
    print(f"Biomarkers extracted for       : {len(included_subjects)} subjects")
    print(f"Phase identification ok        : {phase_ok_count}")
    print(f"Phase identification failed    : {phase_failed_count}")
    print(f"Biomarker extraction phase completed successfully.")

if __name__ == '__main__':
    main()
