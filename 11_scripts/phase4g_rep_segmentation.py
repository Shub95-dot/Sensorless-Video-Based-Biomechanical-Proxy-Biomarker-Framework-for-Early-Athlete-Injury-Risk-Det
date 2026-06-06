import sys
from pathlib import Path
import pandas as pd
import numpy as np
import scipy
from scipy.signal import find_peaks
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
    inclusion_csv_path = project_root / "3_metadata" / "squats_temporal_inclusion.csv"
    smoothed_dir = project_root / "4_pose_outputs" / "temporal" / "smoothed_trajectories"
    
    # Outputs
    per_rep_csv_path = project_root / "4_pose_outputs" / "temporal" / "squats_per_rep_biomarkers.csv"
    rep_summary_csv_path = project_root / "4_pose_outputs" / "temporal" / "squats_rep_summary.csv"
    plots_dir = project_root / "6_visualizations" / "temporal" / "squats_rep_segmentation"
    summary_txt_path = project_root / "4_pose_outputs" / "temporal" / "phase4g_rep_segmentation_summary.txt"

    # 1. Load inclusion CSV and filter to non-excluded subjects
    if not inclusion_csv_path.is_file():
        print(f"Error: Inclusion manifest not found at {inclusion_csv_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
        
    inclusion_df = pd.read_csv(inclusion_csv_path, sep=None, engine='python')
    included_df = inclusion_df[inclusion_df['inclusion_tier'] != 'excluded'].copy()
    included_subjects = sorted(included_df['Subject_ID'].tolist())
    
    if len(included_subjects) != 10:
        print(f"Warning: Expected 10 subjects but found {len(included_subjects)}!", file=sys.stderr)
    else:
        print(f"Loaded 10 included subjects from inclusion manifest: {included_subjects}")

    # Check smoothed trajectory files exist
    for sub_id in included_subjects:
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        if not csv_path.is_file():
            print(f"Error: Smoothed trajectory file not found: {csv_path.as_posix()}", file=sys.stderr)
            sys.exit(1)

    # State variables for processing
    rep_biomarkers_rows = []
    subject_summary_rows = []
    
    single_rep_count = 0
    multi_rep_count = 0
    no_clean_rep_count = 0
    total_reps_detected = 0
    subject_1863_classification = 'unknown'
    multi_rep_subjects_list = []
    
    print("\nStarting repetition segmentation and biomarker extraction...")
    for idx, sub_id in enumerate(included_subjects, 1):
        csv_path = smoothed_dir / f"SQ_{sub_id}_smoothed.csv"
        df = pd.read_csv(csv_path, sep=None, engine='python')
        sub_row = included_df[included_df['Subject_ID'] == sub_id].iloc[0]
        inclusion_tier = sub_row['inclusion_tier']
        
        knee_angle_smoothed = df['knee_angle_smoothed']
        
        # Step 1 & 2 — Rep detection using scipy.signal.find_peaks:
        # Fill NaN values in knee_angle_smoothed with maximum observed value (to avoid false peaks)
        max_observed_val = knee_angle_smoothed.max()
        filled_signal = knee_angle_smoothed.fillna(max_observed_val)
        inverted_signal = -filled_signal
        
        # Detect candidate bottoms using prominence = 20, distance = 15
        peaks, _ = find_peaks(inverted_signal, prominence=20, distance=15)
        
        # Filter out peaks that fall within original NaN regions
        valid_peaks = sorted([int(p) for p in peaks if not np.isnan(knee_angle_smoothed.iloc[p])])
        rep_count = len(valid_peaks)
        
        # Step 3 — Classify subject
        if rep_count == 0:
            rep_classification = 'no_clean_rep'
            no_clean_rep_count += 1
        elif rep_count == 1:
            rep_classification = 'single_rep'
            single_rep_count += 1
        else:
            rep_classification = 'multi_rep'
            multi_rep_count += 1
            multi_rep_subjects_list.append((sub_id, rep_count))
            
        if sub_id == 1863:
            subject_1863_classification = rep_classification
            
        total_reps_detected += rep_count
        
        first_non_nan = knee_angle_smoothed.first_valid_index()
        last_non_nan = knee_angle_smoothed.last_valid_index()
        
        # Log subject-level status (peak_flexion_cv will be added later)
        # We will compute reps first, then compute repeatability statistics
        subject_reps = []
        
        # Step 4 — For each detected rep, compute per-rep biomarkers
        for i in range(rep_count):
            rep_bottom_frame = valid_peaks[i]
            
            # Determine start frame
            if i == 0:
                rep_start_frame = first_non_nan
            else:
                rep_start_frame = int((valid_peaks[i-1] + valid_peaks[i]) // 2) + 1
                
            # Determine end frame
            if i == rep_count - 1:
                rep_end_frame = last_non_nan
            else:
                rep_end_frame = int((valid_peaks[i] + valid_peaks[i+1]) // 2)
                
            # Slice rep trajectory
            rep_slice = knee_angle_smoothed.loc[rep_start_frame : rep_end_frame]
            
            # Compute range-based biomarkers
            rep_peak_flexion_deg = nan_safe_min(rep_slice)
            rep_peak_extension_deg = nan_safe_max(rep_slice)
            rep_rom_deg = rep_peak_extension_deg - rep_peak_flexion_deg if not (np.isnan(rep_peak_flexion_deg) or np.isnan(rep_peak_extension_deg)) else np.nan
            
            # Compute phase durations
            rep_descent_frames = int(rep_bottom_frame - rep_start_frame)
            rep_ascent_frames = int(rep_end_frame - rep_bottom_frame)
            rep_total_frames = rep_descent_frames + rep_ascent_frames
            rep_tempo_ratio = rep_ascent_frames / rep_descent_frames if rep_descent_frames > 0 else np.nan
            
            # Compute velocities
            delta_angle = pd.Series(np.diff(knee_angle_smoothed), index=df.index[:-1])
            descent_deltas = delta_angle.loc[rep_start_frame : rep_bottom_frame - 1]
            ascent_deltas = delta_angle.loc[rep_bottom_frame : rep_end_frame - 1]
            
            rep_peak_descent_velocity = nan_safe_min(descent_deltas)
            rep_peak_ascent_velocity = nan_safe_max(ascent_deltas)
            rep_mean_descent_velocity = nan_safe_mean(descent_deltas)
            rep_mean_ascent_velocity = nan_safe_mean(ascent_deltas)
            
            rep_data = {
                'Subject_ID': sub_id,
                'inclusion_tier': inclusion_tier,
                'rep_index': i,
                'rep_count_for_subject': rep_count,
                'rep_bottom_frame': rep_bottom_frame,
                'rep_start_frame': rep_start_frame,
                'rep_end_frame': rep_end_frame,
                'rep_peak_flexion_deg': round(rep_peak_flexion_deg, 4) if not np.isnan(rep_peak_flexion_deg) else np.nan,
                'rep_peak_extension_deg': round(rep_peak_extension_deg, 4) if not np.isnan(rep_peak_extension_deg) else np.nan,
                'rep_rom_deg': round(rep_rom_deg, 4) if not np.isnan(rep_rom_deg) else np.nan,
                'rep_descent_frames': int(rep_descent_frames),
                'rep_ascent_frames': int(rep_ascent_frames),
                'rep_tempo_ratio': round(rep_tempo_ratio, 4) if not np.isnan(rep_tempo_ratio) else np.nan,
                'rep_total_frames': int(rep_total_frames),
                'rep_peak_descent_velocity_deg_per_frame': round(rep_peak_descent_velocity, 4) if not np.isnan(rep_peak_descent_velocity) else np.nan,
                'rep_peak_ascent_velocity_deg_per_frame': round(rep_peak_ascent_velocity, 4) if not np.isnan(rep_peak_ascent_velocity) else np.nan,
                'rep_mean_descent_velocity_deg_per_frame': round(rep_mean_descent_velocity, 4) if not np.isnan(rep_mean_descent_velocity) else np.nan,
                'rep_mean_ascent_velocity_deg_per_frame': round(rep_mean_ascent_velocity, 4) if not np.isnan(rep_mean_ascent_velocity) else np.nan
            }
            subject_reps.append(rep_data)
            rep_biomarkers_rows.append(rep_data)

        # Step 5 — Compute within-subject repeatability statistics
        if rep_count >= 2:
            peak_flexions = [r['rep_peak_flexion_deg'] for r in subject_reps if not np.isnan(r['rep_peak_flexion_deg'])]
            roms = [r['rep_rom_deg'] for r in subject_reps if not np.isnan(r['rep_rom_deg'])]
            tempo_ratios = [r['rep_tempo_ratio'] for r in subject_reps if not np.isnan(r['rep_tempo_ratio'])]
            
            # Flexion stats
            pf_mean = np.mean(peak_flexions) if peak_flexions else np.nan
            pf_std = np.std(peak_flexions, ddof=1) if len(peak_flexions) > 1 else np.nan
            pf_cv = pf_std / np.abs(pf_mean) if not (np.isnan(pf_mean) or np.isnan(pf_std) or pf_mean == 0) else np.nan
            
            # ROM stats
            rom_mean = np.mean(roms) if roms else np.nan
            rom_std = np.std(roms, ddof=1) if len(roms) > 1 else np.nan
            rom_cv = rom_std / np.abs(rom_mean) if not (np.isnan(rom_mean) or np.isnan(rom_std) or rom_mean == 0) else np.nan
            
            # Tempo ratio stats
            tr_mean = np.mean(tempo_ratios) if tempo_ratios else np.nan
            tr_std = np.std(tempo_ratios, ddof=1) if len(tempo_ratios) > 1 else np.nan
            tr_cv = tr_std / np.abs(tr_mean) if not (np.isnan(tr_mean) or np.isnan(tr_std) or tr_mean == 0) else np.nan
            
            log_cv_val = f"{pf_cv:.4f}" if not np.isnan(pf_cv) else "NaN"
        else:
            # Single rep or 0 reps
            pf_mean = subject_reps[0]['rep_peak_flexion_deg'] if rep_count == 1 else np.nan
            pf_std = np.nan
            pf_cv = np.nan
            
            rom_mean = subject_reps[0]['rep_rom_deg'] if rep_count == 1 else np.nan
            rom_std = np.nan
            rom_cv = np.nan
            
            tr_mean = subject_reps[0]['rep_tempo_ratio'] if rep_count == 1 else np.nan
            tr_std = np.nan
            tr_cv = np.nan
            
            log_cv_val = "NaN"
            
        print(f"  [{idx}/{len(included_subjects)}] {sub_id}: {rep_classification} with {rep_count} reps; peak_flexion_cv = {log_cv_val}")
        
        subject_summary_rows.append({
            'Subject_ID': sub_id,
            'inclusion_tier': inclusion_tier,
            'rep_classification': rep_classification,
            'rep_count': rep_count,
            'peak_flexion_cv': round(pf_cv, 4) if not np.isnan(pf_cv) else np.nan,
            'rom_cv': round(rom_cv, 4) if not np.isnan(rom_cv) else np.nan,
            'tempo_ratio_cv': round(tr_cv, 4) if not np.isnan(tr_cv) else np.nan,
            'peak_flexion_mean': round(pf_mean, 4) if not np.isnan(pf_mean) else np.nan,
            'peak_flexion_std': round(pf_std, 4) if not np.isnan(pf_std) else np.nan,
            'rom_mean': round(rom_mean, 4) if not np.isnan(rom_mean) else np.nan,
            'rom_std': round(rom_std, 4) if not np.isnan(rom_std) else np.nan,
            'tempo_ratio_mean': round(tr_mean, 4) if not np.isnan(tr_mean) else np.nan,
            'tempo_ratio_std': round(tr_std, 4) if not np.isnan(tr_std) else np.nan
        })

        # Step 4e — Write rep-segmentation overlay plot
        plots_dir.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(12, 4))
        
        # Plot smoothed knee angle trajectory as red line
        plt.plot(df['frame_index'], knee_angle_smoothed, color='red', linewidth=2.0, label='Smoothed trajectory')
        
        # Shade background per rep alternating between light blue and light yellow
        colors = ['lightblue', 'lightyellow']
        for r_idx, r in enumerate(subject_reps):
            # Alternating colors
            c = colors[r_idx % 2]
            plt.axvspan(r['rep_start_frame'], r['rep_end_frame'], color=c, alpha=0.3, label=f"Rep {r_idx} Window" if r_idx < 2 else None)
            
            # Vertical dashed line at detected bottom frame
            plt.axvline(x=r['rep_bottom_frame'], color='black', linestyle='--', alpha=0.7)
            
            # Label the bottom frame
            # Compute a position offset for text label
            y_val = knee_angle_smoothed.iloc[r['rep_bottom_frame']]
            plt.text(r['rep_bottom_frame'], y_val + 10, f"Rep {r_idx}: {y_val:.1f}°",
                     ha='center', va='bottom', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='gray'))
            
        plt.ylim(0, 200)
        plt.xlabel('frame_index')
        plt.ylabel('knee_angle_deg (degrees)')
        
        # Title: Subject {Subject_ID} — tier: {tier} — rep classification: {single_rep/multi_rep} — N reps detected
        plt.title(f"Subject {sub_id} — tier: {inclusion_tier} — rep classification: {rep_classification} — {rep_count} reps detected")
        plt.grid(True, linestyle=':', alpha=0.6)
        
        # Unique legend handles
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        plot_path = plots_dir / f"SQ_{sub_id}_rep_segmentation.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()

    # Pre-write sanity checkpoint
    print("\n--- Pre-write Sanity Checkpoint ---")
    print(f"Subjects processed                   : {len(included_subjects)}    (expected: 10)")
    print(f"Single-rep subjects                  : {single_rep_count}")
    print(f"Multi-rep subjects                   : {multi_rep_count}")
    print(f"No-clean-rep subjects                : {no_clean_rep_count}  (expected: 0; flag if >0)")
    print(f"Total reps detected across cohort    : {total_reps_detected}")
    print(f"Subject 1863 rep classification      : {subject_1863_classification}    (expected: multi_rep based on visual review)")
    
    if no_clean_rep_count > 0:
        ncr_ids = [r['Subject_ID'] for r in subject_summary_rows if r['rep_count'] == 0]
        print(f"Warning: No clean reps detected for subjects: {ncr_ids}", file=sys.stderr)
        
    print("Sanity checks completed. Writing output files...")
    
    # Save per-rep biomarkers CSV
    per_rep_df = pd.DataFrame(rep_biomarkers_rows)
    per_rep_df.to_csv(per_rep_csv_path, index=False)
    print(f"Saved per-rep biomarkers CSV to {per_rep_csv_path.as_posix()}")
    
    # Save subject-level rep summary CSV
    rep_summary_df = pd.DataFrame(subject_summary_rows)
    rep_summary_df.to_csv(rep_summary_csv_path, index=False)
    print(f"Saved subject-level rep summary CSV to {rep_summary_csv_path.as_posix()}")
    
    # Write run summary text file
    mean_reps = total_reps_detected / len(included_subjects) if len(included_subjects) > 0 else 0.0
    
    # Subjects with peak_flexion_cv > 0.10 flagged
    flagged_cv_subjects = []
    for r in subject_summary_rows:
        if r['rep_count'] >= 2 and not np.isnan(r['peak_flexion_cv']) and r['peak_flexion_cv'] > 0.10:
            flagged_cv_subjects.append(f"Subject {r['Subject_ID']} (CV: {r['peak_flexion_cv']:.4f})")
            
    summary_txt_content = f"""Phase 4G Rep Segmentation and Within-Subject Repeatability Summary
=============================================================
Subjects processed: {len(included_subjects)}
Rep classifications:
- single_rep: {single_rep_count}
- multi_rep: {multi_rep_count}
- no_clean_rep: {no_clean_rep_count}

Multi-rep subjects:
"""
    if multi_rep_subjects_list:
        for sub_id, cnt in multi_rep_subjects_list:
            summary_txt_content += f"- Subject {sub_id}: {cnt} reps\n"
    else:
        summary_txt_content += "- None\n"
        
    summary_txt_content += f"""
Total reps detected across cohort: {total_reps_detected}
Mean rep_count per subject: {mean_reps:.2f}

Subjects with peak_flexion_cv > 0.10 (flagged for dissertation as exhibiting notable depth variability):
"""
    if flagged_cv_subjects:
        for fs in flagged_cv_subjects:
            summary_txt_content += f"- {fs}\n"
    else:
        summary_txt_content += "- None (no multi-rep subject had depth CV > 0.10)\n"
        
    summary_txt_path.write_text(summary_txt_content, encoding='utf-8')
    print(f"Saved run summary text report to {summary_txt_path.as_posix()}")
    
    # Final summary to stdout
    print("\n--- Final Summary ---")
    print(f"Total reps detected across cohort    : {total_reps_detected}")
    print(f"Single-rep subjects                  : {single_rep_count}")
    print(f"Multi-rep subjects                   : {multi_rep_count}")
    print("Rep segmentation and repeatability analysis completed successfully.")

if __name__ == '__main__':
    main()
