import sys
from pathlib import Path
import pandas as pd
import numpy as np
import scipy
import scipy.signal  # Used for savgol_filter. Scipy version: 1.17.1
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    project_root = Path(".")
    inclusion_path = project_root / "3_metadata" / "squats_temporal_inclusion.csv"
    trajectories_dir = project_root / "4_pose_outputs" / "temporal" / "trajectories"
    
    # Output directories
    smoothed_dir = project_root / "4_pose_outputs" / "temporal" / "smoothed_trajectories"
    visualizations_dir = project_root / "6_visualizations" / "temporal" / "squats_smoothed"
    summary_csv_path = project_root / "4_pose_outputs" / "temporal" / "squats_smoothing_summary.csv"
    summary_txt_path = project_root / "4_pose_outputs" / "temporal" / "phase4e_smoothing_summary.txt"

    # 1. Validate inputs exist
    if not inclusion_path.is_file():
        print(f"Error: Inclusion manifest not found at {inclusion_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Load inclusion CSV and filter to non-excluded subjects
    inclusion_df = pd.read_csv(inclusion_path, sep=None, engine='python')
    included_df = inclusion_df[inclusion_df['inclusion_tier'] != 'excluded'].copy()
    excluded_df = inclusion_df[inclusion_df['inclusion_tier'] == 'excluded'].copy()
    
    included_subjects = sorted(included_df['Subject_ID'].tolist())
    excluded_subjects = sorted(excluded_df['Subject_ID'].tolist())
    
    print(f"Loaded {len(inclusion_df)} total subjects from {inclusion_path.name}")
    print(f"Included subjects (to process): {len(included_subjects)} -> {included_subjects}")
    print(f"Excluded subjects (not processed): {len(excluded_subjects)} -> {excluded_subjects}")

    # Validate that all 11 trajectory files exist
    for sub_id in included_subjects:
        traj_path = trajectories_dir / f"SQ_{sub_id}_trajectory.csv"
        if not traj_path.is_file():
            print(f"Error: Required trajectory file not found: {traj_path.as_posix()}", file=sys.stderr)
            sys.exit(1)
            
    # Process subjects in ascending Subject_ID order
    processed_data = {}
    cohort_total_raw_frames = 0
    cohort_total_nan_frames = 0
    cohort_total_rows = 0
    
    # Constants
    MEDIAN_WINDOW = 5
    SG_WINDOW = 7
    SG_POLYORDER = 2
    
    print("\nProcessing subjects and running trajectory smoothing pipeline...")
    for idx, sub_id in enumerate(included_subjects, 1):
        traj_path = trajectories_dir / f"SQ_{sub_id}_trajectory.csv"
        sub_row = included_df[included_df['Subject_ID'] == sub_id].iloc[0]
        
        # Load trajectory
        df = pd.read_csv(traj_path, sep=None, engine='python')
        total_sub_frames = len(df)
        
        # Stage 1 — Median filter for spike removal:
        # Apply a centered 1D median filter with window size = 5.
        # Treat NaN values as gaps: do NOT interpolate before filtering.
        # We use pandas rolling median with center=True, min_periods=1 (skips NaNs in window),
        # then re-mask to force NaNs where the original raw angle was NaN.
        knee_angle_median = df['knee_angle_deg'].rolling(window=MEDIAN_WINDOW, center=True, min_periods=1).median()
        knee_angle_median = knee_angle_median.where(df['knee_angle_deg'].notna(), np.nan)
        
        # Stage 2 — Savitzky-Golay smoothing for curve fitting:
        # Apply a Savitzky-Golay filter with window length = 7, polynomial order = 2.
        # Again, NaN-aware: where median-filtered value is NaN, the output is NaN.
        # To handle gaps without generating edge artifacts or crashing on short valid segments,
        # we temporarily gap-fill the median-filtered series using linear interpolation to allow
        # scipy's savgol_filter to run on the entire sequence, then re-apply the NaNs to the final output.
        if knee_angle_median.notna().any():
            gap_filled = knee_angle_median.interpolate(method='linear', limit_direction='both')
            # Run savgol_filter (Scipy version: 1.17.1)
            smoothed_array = scipy.signal.savgol_filter(gap_filled.values, window_length=SG_WINDOW, polyorder=SG_POLYORDER)
            knee_angle_smoothed = pd.Series(smoothed_array, index=df.index).where(knee_angle_median.notna(), np.nan)
        else:
            # If all values are NaN, smoothed is also all NaN
            knee_angle_smoothed = pd.Series(np.nan, index=df.index)
            
        # Round angle columns to 4 decimal places
        knee_angle_deg_rounded = df['knee_angle_deg'].round(4)
        knee_angle_median_rounded = knee_angle_median.round(4)
        knee_angle_smoothed_rounded = knee_angle_smoothed.round(4)
        
        # Spike diagnostic
        # Count how often the raw signal differed from the median-filtered signal by > 15 degrees
        diff = np.abs(df['knee_angle_deg'] - knee_angle_median)
        spike_count = np.sum(diff > 15.0)
        valid_frames = df['knee_angle_deg'].notna().sum()
        nan_frames = df['knee_angle_deg'].isna().sum()
        
        spike_rate = spike_count / valid_frames if valid_frames > 0 else 0.0
        spike_rate_pct = spike_rate * 100
        
        # Accumulate cohort statistics
        cohort_total_raw_frames += valid_frames
        cohort_total_nan_frames += nan_frames
        cohort_total_rows += total_sub_frames
        
        # Log per subject progress
        print(f"  [{idx}/{len(included_subjects)}] {sub_id}: raw {total_sub_frames} frames, valid {valid_frames}, spike rate {spike_rate_pct:.2f}%")
        
        # Store processed results
        processed_data[sub_id] = {
            'df_out': pd.DataFrame({
                'frame_index': df['frame_index'],
                'frame_number': df['frame_number'],
                'knee_angle_deg': knee_angle_deg_rounded,
                'knee_angle_median': knee_angle_median_rounded,
                'knee_angle_smoothed': knee_angle_smoothed_rounded,
                'angle_status': df['angle_status']
            }),
            'inclusion_tier': sub_row['inclusion_tier'],
            'total_frames': total_sub_frames,
            'valid_frames': valid_frames,
            'pct_valid': round((valid_frames / total_sub_frames) * 100, 2) if total_sub_frames > 0 else 0.0,
            'spike_rate_pct': round(spike_rate_pct, 2),
            'depth_truncated': sub_row['depth_truncated'],
            'partial_depth_real': sub_row['partial_depth_real']
        }

    # 4. Pre-write sanity checkpoint
    print("\n--- Pre-write Sanity Checkpoint ---")
    print(f"Subjects to process              : {len(included_subjects)}  (expected: 11)")
    print(f"Excluded (not processed)         : {len(excluded_subjects)}  (expected: 4)")
    print(f"Total raw frames across cohort   : {cohort_total_raw_frames}")
    print(f"Total NaN frames (no angle)      : {cohort_total_nan_frames}")
    print(f"Sanity check                     : {cohort_total_raw_frames} + {cohort_total_nan_frames} = {cohort_total_raw_frames + cohort_total_nan_frames}")
    print(f"Expected total frames            : {cohort_total_rows}")
    
    # Assert counts match
    if cohort_total_raw_frames + cohort_total_nan_frames != cohort_total_rows:
        print("\nSanity Check FAILED: R + NaN_count does not equal total_frames_in_phase4c_trajectories!", file=sys.stderr)
        sys.exit(1)
        
    print("Sanity checks passed successfully. Writing output files...")
    
    # Create output directories
    smoothed_dir.mkdir(parents=True, exist_ok=True)
    visualizations_dir.mkdir(parents=True, exist_ok=True)
    
    # List for squats_smoothing_summary.csv
    summary_rows = []
    
    # 5. Write per-subject smoothed CSVs and plots
    for sub_id in included_subjects:
        res = processed_data[sub_id]
        
        # Save smoothed trajectory CSV
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        res['df_out'].to_csv(csv_path, index=False)
        
        # Save comparison plot
        # One figure per subject, ~10x4 inches
        plt.figure(figsize=(10, 4))
        df_plot = res['df_out']
        
        # Raw knee angle: small grey dots, alpha 0.5, no connecting line
        plt.plot(df_plot['frame_index'], df_plot['knee_angle_deg'], 'o', color='grey', alpha=0.5, markersize=3, label='Raw')
        # Median-filtered: blue line, thin
        plt.plot(df_plot['frame_index'], df_plot['knee_angle_median'], color='blue', linewidth=1.0, label='Median-filtered')
        # Smoothed: red line, slightly thicker
        plt.plot(df_plot['frame_index'], df_plot['knee_angle_smoothed'], color='red', linewidth=2.0, label='Smoothed')
        
        plt.ylim(0, 200)
        plt.xlabel('frame_index')
        plt.ylabel('knee_angle_deg (degrees)')
        
        # Title: Subject {Subject_ID} — tier: {tier} — spike rate: {X}%
        plt.title(f"Subject {sub_id} — tier: {res['inclusion_tier']} — spike rate: {res['spike_rate_pct']:.2f}%")
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend(loc='upper right')
        
        plot_path = visualizations_dir / f"SQ_{sub_id}_raw_vs_smoothed.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Collect for squats_smoothing_summary.csv
        summary_rows.append({
            'Subject_ID': sub_id,
            'inclusion_tier': res['inclusion_tier'],
            'total_frames': res['total_frames'],
            'valid_frames': res['valid_frames'],
            'pct_valid': res['pct_valid'],
            'spike_rate_pct': res['spike_rate_pct'],
            'median_window': MEDIAN_WINDOW,
            'sg_window': SG_WINDOW,
            'sg_polyorder': SG_POLYORDER,
            'depth_truncated': res['depth_truncated'],
            'partial_depth_real': res['partial_depth_real']
        })
        
    # 6. Write squats_smoothing_summary.csv
    summary_df = pd.DataFrame(summary_rows)
    # Ensure correct columns order
    cols_order = [
        'Subject_ID', 'inclusion_tier', 'total_frames', 'valid_frames', 'pct_valid',
        'spike_rate_pct', 'median_window', 'sg_window', 'sg_polyorder',
        'depth_truncated', 'partial_depth_real'
    ]
    summary_df = summary_df[cols_order]
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"Saved subject smoothing summary to {summary_csv_path.as_posix()}")
    
    # 7. Write phase4e_smoothing_summary.txt
    # Calculate cohort spike rate statistics
    spike_rates = [res['spike_rate_pct'] for res in processed_data.values()]
    mean_spike_rate = np.mean(spike_rates)
    median_spike_rate = np.median(spike_rates)
    
    # Sorted descending per-subject spike rate
    sorted_subjects_by_spike = sorted(
        [(sub_id, res['spike_rate_pct']) for sub_id, res in processed_data.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Subjects with spike rate > 5% flagged
    flagged_subjects = [f"Subject {sub_id} ({rate:.2f}%)" for sub_id, rate in sorted_subjects_by_spike if rate > 5.0]
    
    summary_txt_content = f"""Phase 4E Trajectory Smoothing Summary
=====================================
Subjects processed: {len(included_subjects)}
Excluded subjects (not processed): {len(excluded_subjects)} ({', '.join(map(str, excluded_subjects))})
Median filter: window {MEDIAN_WINDOW}
Savitzky-Golay: window {SG_WINDOW}, polyorder {SG_POLYORDER}

Scipy version used: {scipy.__version__}

Per-subject spike rate (sorted descending — high spike rate flags the noisiest subjects):
--------------------------------------------------------------------------------------
"""
    for sub_id, rate in sorted_subjects_by_spike:
        summary_txt_content += f"Subject {sub_id:<4} | spike_rate_pct: {rate:>6.2f}%\n"
        
    summary_txt_content += f"""
Cohort spike rate statistics:
- Mean spike rate: {mean_spike_rate:.2f}%
- Median spike rate: {median_spike_rate:.2f}%

Subjects with spike rate > 5% (flagged for dissertation's quality discussion):
"""
    if flagged_subjects:
        for fs in flagged_subjects:
            summary_txt_content += f"- {fs}\n"
    else:
        summary_txt_content += "- None\n"
        
    # Write summary text file
    summary_txt_path.write_text(summary_txt_content, encoding='utf-8')
    print(f"Saved run summary text file to {summary_txt_path.as_posix()}")
    
    # 8. Print final stdout summary
    print("\n--- Final Run Summary ---")
    print(f"Subjects processed           : {len(included_subjects)}")
    print(f"Mean cohort spike rate       : {mean_spike_rate:.2f}%")
    print(f"Median cohort spike rate     : {median_spike_rate:.2f}%")
    print(f"Flagged subjects (>5% spike) : {len(flagged_subjects)}")
    print("Trajectory smoothing completed successfully.")

if __name__ == '__main__':
    main()
