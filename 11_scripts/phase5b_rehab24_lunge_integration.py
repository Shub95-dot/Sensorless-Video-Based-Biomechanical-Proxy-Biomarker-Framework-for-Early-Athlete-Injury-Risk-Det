#!/usr/bin/env python3
"""
phase5b_rehab24_lunge_integration.py
====================================
Phase 5B — REHAB24-6 Lunge Integration (Sagittal Lunge Cohort)

Applies the pipeline methodology to REHAB24-6's lunge recordings (exercise_id = 5)
using the dataset's ground-truth rep boundaries.

Author  : Dissertation Project
Date    : 2026-06-16
"""

import os
import sys
import warnings
from pathlib import Path
import pandas as pd
import numpy as np
import cv2
import scipy
import scipy.signal
import scipy.ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ---------------------------------------------------------------------------
# Helper functions for calculations
# ---------------------------------------------------------------------------

def compute_knee_angle(hip, knee, ankle):
    """Compute unsigned 2D knee angle in degrees using arccos of normalized vectors."""
    H = np.array([hip.x, hip.y])
    K = np.array([knee.x, knee.y])
    A = np.array([ankle.x, ankle.y])

    v1 = H - K
    v2 = A - K

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0.0 or norm2 == 0.0:
        return np.nan

    dot_prod = np.dot(v1, v2)
    cos_theta = dot_prod / (norm1 * norm2)
    cos_theta_clipped = np.clip(cos_theta, -1.0, 1.0)
    theta_rad = np.arccos(cos_theta_clipped)
    theta_deg = float(np.degrees(theta_rad))
    return round(theta_deg, 4)

def nan_safe_min(series):
    vals = series.dropna()
    return float(vals.min()) if len(vals) > 0 else np.nan

def nan_safe_max(series):
    vals = series.dropna()
    return float(vals.max()) if len(vals) > 0 else np.nan

def nan_safe_mean(series):
    vals = series.dropna()
    return float(vals.mean()) if len(vals) > 0 else np.nan

# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def main():
    print("=== Phase 5B — REHAB24-6 Lunge Integration Script Started ===")
    project_root = Path(__file__).resolve().parent.parent
    
    # Define relative input paths
    seg_csv_path = project_root / "1_raw_datasets" / "Rehab 26 dataset" / "REHAB24-6 integration" / "Segmentation.csv"
    seg_txt_path = project_root / "1_raw_datasets" / "Rehab 26 dataset" / "REHAB24-6 integration" / "Segmentation.txt"
    video_dir = project_root / "1_raw_datasets" / "Rehab 26 dataset" / "REHAB24-6 integration" / "Lunges"
    model_path = project_root / "12_models" / "pose_landmarker_heavy.task"

    # Define output paths
    out_dir = project_root / "15_rehab24_lunge_outputs"
    metadata_dir = out_dir / "metadata"
    pose_dir = out_dir / "pose_per_video"
    smoothed_dir = out_dir / "smoothed_per_rep"
    biomarkers_dir = out_dir / "biomarkers_per_rep"
    vis_dir = out_dir / "visualizations"

    # Ensure output directories exist
    metadata_dir.mkdir(parents=True, exist_ok=True)
    pose_dir.mkdir(parents=True, exist_ok=True)
    smoothed_dir.mkdir(parents=True, exist_ok=True)
    biomarkers_dir.mkdir(parents=True, exist_ok=True)
    vis_dir.mkdir(parents=True, exist_ok=True)

    # 1. Stage 0 verification gate — resolve paths, verify videos, inspect schema, confirm correctness encoding, orientation filter, and working-leg mapping. STOP on any failure.
    if not seg_csv_path.is_file():
        sys.exit(f"ERROR: Segmentation.csv not found at: {seg_csv_path}")
    if not seg_txt_path.is_file():
        sys.exit(f"ERROR: Segmentation.txt not found at: {seg_txt_path}")
    if not model_path.is_file():
        sys.exit(f"ERROR: MediaPipe task file not found at: {model_path}")
    if not video_dir.is_dir():
        sys.exit(f"ERROR: Video directory not found at: {video_dir}")

    # 2. Build the sagittal lunge manifest (Stage 1)
    print("Loading Segmentation.csv and building sagittal lunge manifest...")
    df_raw = pd.read_csv(seg_csv_path, sep=';')
    
    # Filter for lunges (exercise_id == 5), cam17 orientation 'front' (so cam18 is side/sagittal), and mocap_erroneous == 0
    df_filtered = df_raw[
        (df_raw['exercise_id'] == 5) &
        (df_raw['cam17_orientation'] == 'front') &
        (df_raw['mocap_erroneous'] == 0)
    ].copy()

    if len(df_filtered) == 0:
        sys.exit("ERROR: No lunge records found matching criteria in Segmentation.csv")

    # Derived columns
    df_filtered['video_filename'] = df_filtered['video_id'].apply(lambda x: f"{x}-Camera18-30fps-transposed.mp4")
    df_filtered['subject_id'] = df_filtered['person_id'].astype(int)
    df_filtered['rep_number'] = df_filtered['repetition_number'].astype(int)
    df_filtered['start_frame'] = df_filtered['first_frame'].astype(int)
    df_filtered['end_frame'] = df_filtered['last_frame'].astype(int)
    df_filtered['correctness_label'] = df_filtered['correctness'].astype(int)

    # Map working_leg based on exercise_subtype
    # 'front leg left' -> 'left', 'front leg right' -> 'right'
    def map_working_leg(subtype):
        if subtype == 'front leg left':
            return 'left'
        elif subtype == 'front leg right':
            return 'right'
        else:
            raise ValueError(f"Unknown exercise subtype: {subtype}")

    df_filtered['working_leg'] = df_filtered['exercise_subtype'].apply(map_working_leg)

    # Sort manifest by subject_id then rep_number
    df_filtered = df_filtered.sort_values(by=['subject_id', 'rep_number']).reset_index(drop=True)

    # Columns as requested
    manifest_cols = [
        'subject_id', 'video_id', 'video_filename', 'rep_number', 'start_frame', 'end_frame',
        'correctness_label', 'working_leg', 'exercise_subtype', 'lights_on', 'extra_person_in_cam18', 'mocap_erroneous'
    ]
    df_manifest = df_filtered[manifest_cols].copy()

    # Count unique subjects and videos in filtered dataset
    unique_subjects = df_manifest['subject_id'].unique()
    unique_videos = df_manifest['video_id'].unique()
    
    # Check videos found on disk
    videos_on_disk = []
    for vid in unique_videos:
        vid_file = video_dir / f"{vid}-Camera18-30fps-transposed.mp4"
        if vid_file.is_file():
            videos_on_disk.append(vid_file)
    V_count = len(videos_on_disk)

    N_expected = 88
    N_actual = len(df_manifest)
    C_actual = (df_manifest['correctness_label'] == 1).sum()
    I_actual = (df_manifest['correctness_label'] == 0).sum()

    # Perform mismatches checking and issue warnings per mismatch
    warnings_list = []
    if N_actual != N_expected:
        warnings_list.append(f"WARNING: Expected {N_expected} manifest rows, but got {N_actual}!")
    if len(unique_subjects) != 8:
        warnings_list.append(f"WARNING: Expected 8 unique subjects, but got {len(unique_subjects)}!")
    if len(unique_videos) != 9:
        warnings_list.append(f"WARNING: Expected 9 unique videos, but got {len(unique_videos)}!")
    if V_count < 9:
        missing_videos = set(unique_videos) - {v.name.split('-')[0] for v in videos_on_disk}
        print(f"ERROR: Missing video files for subjects: {missing_videos}", file=sys.stderr)
        sys.exit("Execution stopped due to missing video files.")
    if C_actual != 39:
        warnings_list.append(f"WARNING: Expected 39 correct reps, but got {C_actual}!")
    if I_actual != 49:
        warnings_list.append(f"WARNING: Expected 49 incorrect reps, but got {I_actual}!")

    for warn in warnings_list:
        print(warn, file=sys.stderr)

    # Save manifest (Stage 1)
    manifest_csv_path = metadata_dir / "rehab24_lunge_sagittal_manifest.csv"
    df_manifest.to_csv(manifest_csv_path, index=False)
    print(f"Manifest saved to: {manifest_csv_path.as_posix()}")

    # 3. Pre-write Sanity Checkpoint
    print("\n=== Phase 5B REHAB24-6 Lunge Integration — Sanity Checkpoint ===")
    print(f"Sagittal lunge manifest rows                    : {N_actual}      (expected: 88)")
    print(f"Unique subjects                                 : {len(unique_subjects)}      (expected: 8)")
    print(f"Unique videos                                   : {len(unique_videos)}      (expected: 9)")
    print(f"Videos found on disk                            : {V_count}      (expected: 9)")
    print(f"Reps with correctness=1 (correct form)          : {C_actual}      (expected: 39)")
    print(f"Reps with correctness=0 (incorrect form)        : {I_actual}      (expected: 49)")
    print("==========================================================")

    # 4. MediaPipe Pose Extraction per Video (Stage 2)
    # Load MediaPipe PoseLandmarker
    base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )
    detector = mp_vision.PoseLandmarker.create_from_options(options)

    # Dictionary to hold pose data per video: video_id -> list of frame data dicts
    video_poses = {}

    try:
        # Sort videos in ascending order of subject_id
        video_info_list = df_manifest[['subject_id', 'video_id', 'video_filename']].drop_duplicates().sort_values(by='subject_id').values
        
        for v_idx, (sub_id, vid_id, vid_filename) in enumerate(video_info_list, 1):
            vid_path = video_dir / vid_filename
            print(f"Opening video: {vid_filename}")
            cap = cv2.VideoCapture(str(vid_path))
            if not cap.isOpened():
                sys.exit(f"ERROR: Could not open video file: {vid_path}")
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"[video {v_idx}/9] {vid_id}: extracting pose from {total_frames} frames")
            
            frame_records = []
            f_idx = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Run landmarker
                result = detector.detect(mp_image)
                
                left_knee_angle = np.nan
                right_knee_angle = np.nan
                
                left_hip_vis = left_knee_vis = left_ankle_vis = 0.0
                right_hip_vis = right_knee_vis = right_ankle_vis = 0.0
                
                left_angle_status = 'no_pose_detected'
                right_angle_status = 'no_pose_detected'
                
                if result.pose_landmarks and len(result.pose_landmarks) > 0:
                    landmarks = result.pose_landmarks[0]
                    
                    # Left limb visibilities (23, 25, 27)
                    left_hip_vis = round(landmarks[23].visibility, 4)
                    left_knee_vis = round(landmarks[25].visibility, 4)
                    left_ankle_vis = round(landmarks[27].visibility, 4)
                    
                    # Right limb visibilities (24, 26, 28)
                    right_hip_vis = round(landmarks[24].visibility, 4)
                    right_knee_vis = round(landmarks[26].visibility, 4)
                    right_ankle_vis = round(landmarks[28].visibility, 4)
                    
                    left_complete = (left_hip_vis >= 0.5 and left_knee_vis >= 0.5 and left_ankle_vis >= 0.5)
                    right_complete = (right_hip_vis >= 0.5 and right_knee_vis >= 0.5 and right_ankle_vis >= 0.5)
                    
                    if left_complete:
                        left_angle_status = 'valid'
                        left_knee_angle = compute_knee_angle(landmarks[23], landmarks[25], landmarks[27])
                    else:
                        left_angle_status = 'chain_incomplete'
                        
                    if right_complete:
                        right_angle_status = 'valid'
                        right_knee_angle = compute_knee_angle(landmarks[24], landmarks[26], landmarks[28])
                    else:
                        right_angle_status = 'chain_incomplete'
                
                frame_records.append({
                    'frame_index': f_idx,
                    'left_knee_angle_deg': left_knee_angle,
                    'right_knee_angle_deg': right_knee_angle,
                    'left_hip_visibility': left_hip_vis,
                    'left_knee_visibility': left_knee_vis,
                    'left_ankle_visibility': left_ankle_vis,
                    'right_hip_visibility': right_hip_vis,
                    'right_knee_visibility': right_knee_vis,
                    'right_ankle_visibility': right_ankle_vis,
                    'left_angle_status': left_angle_status,
                    'right_angle_status': right_angle_status
                })
                f_idx += 1
            
            cap.release()
            
            # Store in poses dict
            video_poses[vid_id] = pd.DataFrame(frame_records)
            
            # Save per-video pose CSV
            pose_csv = pose_dir / f"{vid_id}_pose_full.csv"
            video_poses[vid_id].to_csv(pose_csv, index=False)
            print(f"  Saved pose extraction to {pose_csv.name}")
            
    finally:
        detector.close()
        print("MediaPipe Pose Landmarker closed cleanly.")

    # 5. Trajectory Slicing, Smoothing, and Biomarker Extraction (Stages 3-4)
    rep_smoothed_dfs = {}
    rep_biomarkers = []
    rep_processing_log = []
    
    P_count = 0
    F_count = 0
    
    print("\nProcessing repetitions...")
    for idx, row in df_manifest.iterrows():
        sub_id = int(row['subject_id'])
        vid_id = row['video_id']
        rep_num = int(row['rep_number'])
        start_f = int(row['start_frame'])
        end_f = int(row['end_frame'])
        correctness = int(row['correctness_label'])
        subtype = row['exercise_subtype']
        working_leg = row['working_leg']
        
        # Load corresponding video pose df
        df_pose = video_poses[vid_id]
        
        # Slice raw trajectory
        df_rep = df_pose[(df_pose['frame_index'] >= start_f) & (df_pose['frame_index'] <= end_f)].copy()
        
        # Reset index and add frame_index_in_rep
        df_rep = df_rep.reset_index(drop=True)
        df_rep['frame_index_in_rep'] = df_rep.index
        df_rep['frame_index_global'] = df_rep['frame_index']
        
        # Select working-leg trajectory column (no fallback)
        if working_leg == 'left':
            col_name = 'left_knee_angle_deg'
            status_col = 'left_angle_status'
        else:
            col_name = 'right_knee_angle_deg'
            status_col = 'right_angle_status'
            
        df_rep['knee_angle_deg'] = df_rep[col_name]
        df_rep['angle_status'] = df_rep[status_col]
        
        # 2-stage smoothing
        MEDIAN_WINDOW = 5
        SG_WINDOW = 7
        SG_POLYORDER = 2
        
        # Stage 1: Median filter (NaN-aware)
        knee_angle_median = df_rep['knee_angle_deg'].rolling(window=MEDIAN_WINDOW, center=True, min_periods=1).median()
        knee_angle_median = knee_angle_median.where(df_rep['knee_angle_deg'].notna(), np.nan)
        
        # Stage 2: Savitzky-Golay (NaN-aware)
        if knee_angle_median.notna().any():
            gap_filled = knee_angle_median.interpolate(method='linear', limit_direction='both')
            smoothed_array = scipy.signal.savgol_filter(gap_filled.values, window_length=SG_WINDOW, polyorder=SG_POLYORDER)
            knee_angle_smoothed = pd.Series(smoothed_array, index=df_rep.index).where(knee_angle_median.notna(), np.nan)
        else:
            knee_angle_smoothed = pd.Series(np.nan, index=df_rep.index)
            
        # Round angles to 4 decimal places
        df_rep['knee_angle_median'] = knee_angle_median.round(4)
        df_rep['knee_angle_smoothed'] = knee_angle_smoothed.round(4)
        
        # Clean up column order for smoothed CSV
        df_smoothed_out = df_rep[[
            'frame_index_global', 'frame_index_in_rep', 'knee_angle_deg', 
            'knee_angle_median', 'knee_angle_smoothed', 'angle_status'
        ]].copy()
        
        # Save per-rep smoothed CSV
        smoothed_csv = smoothed_dir / f"{vid_id}_rep_{rep_num:02d}_smoothed.csv"
        df_smoothed_out.to_csv(smoothed_csv, index=False)
        rep_smoothed_dfs[(vid_id, rep_num)] = df_smoothed_out
        
        # Biomarker calculations (Stage 4)
        total_rep_frames = len(df_rep)
        nan_count = knee_angle_smoothed.isna().sum()
        pct_nan = nan_count / total_rep_frames if total_rep_frames > 0 else 1.0
        
        peak_flexion_deg = nan_safe_min(knee_angle_smoothed)
        peak_extension_deg = nan_safe_max(knee_angle_smoothed)
        rom_deg = peak_extension_deg - peak_flexion_deg if not (np.isnan(peak_flexion_deg) or np.isnan(peak_extension_deg)) else np.nan
        
        if knee_angle_smoothed.notna().any():
            bottom_frame_idx = knee_angle_smoothed.idxmin()
            peak_flexion_frame_in_rep = int(df_rep.loc[bottom_frame_idx, 'frame_index_in_rep'])
        else:
            bottom_frame_idx = np.nan
            peak_flexion_frame_in_rep = np.nan
            
        first_non_nan_idx = knee_angle_smoothed.first_valid_index()
        last_non_nan_idx = knee_angle_smoothed.last_valid_index()
        
        is_failed = False
        if pct_nan > 0.30:
            is_failed = True
        if np.isnan(peak_flexion_frame_in_rep) or first_non_nan_idx is None or last_non_nan_idx is None:
            is_failed = True
        else:
            first_non_nan = int(df_rep.loc[first_non_nan_idx, 'frame_index_in_rep'])
            last_non_nan = int(df_rep.loc[last_non_nan_idx, 'frame_index_in_rep'])
            if peak_flexion_frame_in_rep == first_non_nan or peak_flexion_frame_in_rep == last_non_nan:
                is_failed = True
                
        if is_failed:
            phase_status = 'failed'
            F_count += 1
            descent_frames = np.nan
            ascent_frames = np.nan
            tempo_ratio = np.nan
            total_rep_frames_calc = np.nan
            
            peak_descent_vel = np.nan
            peak_ascent_vel = np.nan
            mean_descent_vel = np.nan
            mean_ascent_vel = np.nan
        else:
            phase_status = 'ok'
            P_count += 1
            descent_frames = int(peak_flexion_frame_in_rep - first_non_nan)
            ascent_frames = int(last_non_nan - peak_flexion_frame_in_rep)
            total_rep_frames_calc = descent_frames + ascent_frames
            tempo_ratio = ascent_frames / descent_frames if descent_frames > 0 else np.nan
            
            delta_angle = pd.Series(np.diff(knee_angle_smoothed), index=df_rep.index[:-1])
            descent_deltas = delta_angle.loc[first_non_nan_idx : bottom_frame_idx - 1]
            ascent_deltas = delta_angle.loc[bottom_frame_idx : last_non_nan_idx - 1]
            
            peak_descent_vel = nan_safe_min(descent_deltas)
            peak_ascent_vel = nan_safe_max(ascent_deltas)
            mean_descent_vel = nan_safe_mean(descent_deltas)
            mean_ascent_vel = nan_safe_mean(ascent_deltas)
            
        second_diff = np.diff(np.diff(knee_angle_smoothed))
        second_diff_clean = second_diff[~np.isnan(second_diff)]
        jerk_proxy_std = float(np.std(second_diff_clean, ddof=1)) if len(second_diff_clean) > 1 else np.nan
        
        # Spike rate pct calculation
        diff_median = np.abs(df_rep['knee_angle_deg'] - knee_angle_median)
        spike_count = np.sum(diff_median > 15.0)
        valid_frames_count = df_rep['knee_angle_deg'].notna().sum()
        spike_rate_pct = (spike_count / valid_frames_count * 100.0) if valid_frames_count > 0 else 0.0
        
        # Rounded values to 4 decimal places
        res_row = {
            'subject_id': sub_id,
            'video_id': vid_id,
            'rep_number': rep_num,
            'correctness_label': correctness,
            'exercise_subtype': subtype,
            'total_frames_in_rep': int(total_rep_frames),
            'valid_frames_in_rep': int(valid_frames_count),
            'spike_rate_pct': round(spike_rate_pct, 4),
            'peak_flexion_deg': round(peak_flexion_deg, 4) if not np.isnan(peak_flexion_deg) else np.nan,
            'peak_extension_deg': round(peak_extension_deg, 4) if not np.isnan(peak_extension_deg) else np.nan,
            'rom_deg': round(rom_deg, 4) if not np.isnan(rom_deg) else np.nan,
            'peak_flexion_frame_in_rep': int(peak_flexion_frame_in_rep) if not np.isnan(peak_flexion_frame_in_rep) else np.nan,
            'descent_frames': int(descent_frames) if not np.isnan(descent_frames) else np.nan,
            'ascent_frames': int(ascent_frames) if not np.isnan(ascent_frames) else np.nan,
            'tempo_ratio': round(tempo_ratio, 4) if not np.isnan(tempo_ratio) else np.nan,
            'total_rep_frames': int(total_rep_frames_calc) if not np.isnan(total_rep_frames_calc) else np.nan,
            'peak_descent_velocity_deg_per_frame': round(peak_descent_vel, 4) if not np.isnan(peak_descent_vel) else np.nan,
            'peak_ascent_velocity_deg_per_frame': round(peak_ascent_vel, 4) if not np.isnan(peak_ascent_vel) else np.nan,
            'mean_descent_velocity_deg_per_frame': round(mean_descent_vel, 4) if not np.isnan(mean_descent_vel) else np.nan,
            'mean_ascent_velocity_deg_per_frame': round(mean_ascent_vel, 4) if not np.isnan(mean_ascent_vel) else np.nan,
            'jerk_proxy_std': round(jerk_proxy_std, 4) if not np.isnan(jerk_proxy_std) else np.nan,
            'phase_identification_status': phase_status,
            'visible_side_used': working_leg # direct map
        }
        
        rep_biomarkers.append(res_row)
        
        # Log progress per rep (Stages 3-6)
        log_rom = f"{rom_deg:.4f}" if not np.isnan(rom_deg) else "NaN"
        log_peak = f"{peak_flexion_deg:.4f}" if not np.isnan(peak_flexion_deg) else "NaN"
        log_tempo = f"{tempo_ratio:.4f}" if not np.isnan(tempo_ratio) else "NaN"
        working_leg_short = 'L' if working_leg == 'left' else 'R'
        print(f"  [rep {idx+1}/{N_actual}] {vid_id} rep {rep_num} (working_leg={working_leg_short}): ROM={log_rom}° peak={log_peak}° tempo={log_tempo} correctness={correctness}")
        
        # Generate visual overlay plot (Stage 6)
        # 12x4 inches overlay plot
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Plot smoothed curve
        ax.plot(df_smoothed_out['frame_index_in_rep'], df_smoothed_out['knee_angle_smoothed'], color='red', linewidth=2.0, label='Smoothed knee angle')
        
        if phase_status == 'ok':
            peak_f_frame = int(peak_flexion_frame_in_rep)
            first_non_nan = int(first_non_nan_idx)
            last_non_nan = int(last_non_nan_idx)
            
            # Shade descent blue
            ax.axvspan(first_non_nan, peak_f_frame, color='lightblue', alpha=0.3, label='Descent Phase')
            # Shade ascent green
            ax.axvspan(peak_f_frame, last_non_nan, color='lightgreen', alpha=0.3, label='Ascent Phase')
            # Vertical dashed line at peak
            ax.axvline(x=peak_f_frame, color='black', linestyle='--', alpha=0.7)
            
            # Text label above peak flexion
            y_min = df_smoothed_out['knee_angle_smoothed'].min()
            y_max = df_smoothed_out['knee_angle_smoothed'].max()
            y_offset = (y_max - y_min) * 0.1 if not np.isnan(y_max - y_min) else 15
            y_pos = peak_flexion_deg + (y_offset if y_offset > 5 else 15)
            y_pos = min(max(y_pos, 10), 180)
            
            ax.text(peak_f_frame, y_pos, f"Peak flexion: {peak_flexion_deg:.2f}°", 
                    ha='center', va='bottom', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='gray'))
            
            title_rom = f"{rom_deg:.2f}°"
            title_tempo = f"{tempo_ratio:.2f}"
        else:
            title_rom = "NaN"
            title_tempo = "failed"
            
        ax.set_ylim(0, 200)
        ax.set_xlabel('Frame index in rep')
        ax.set_ylabel('Knee angle (degrees)')
        correctness_str = 'correct' if correctness == 1 else 'incorrect'
        ax.set_title(f"{vid_id} (Subject {sub_id}) - Rep {rep_num} | ROM: {title_rom} | Peak: {peak_flexion_deg:.2f}° | Tempo: {title_tempo} | correctness: {correctness_str} | working_leg: {working_leg_short}")
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper right')
        
        plot_path = vis_dir / f"{vid_id}_rep_{rep_num:02d}_overlay.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        
        # Record processing log row
        rep_processing_log.append({
            'subject_id': sub_id,
            'video_id': vid_id,
            'rep_number': rep_num,
            'status': 'success',
            'error_message': '',
            'total_frames': total_rep_frames,
            'valid_frames': valid_frames_count,
            'phase_identification_status': phase_status
        })

    # Save combined biomarkers CSV (Stage 5)
    df_biomarkers = pd.DataFrame(rep_biomarkers)
    # Ensure columns order is exactly as requested
    biomarker_cols = [
        'subject_id', 'video_id', 'rep_number', 'correctness_label', 'exercise_subtype',
        'total_frames_in_rep', 'valid_frames_in_rep', 'spike_rate_pct',
        'peak_flexion_deg', 'peak_extension_deg', 'rom_deg', 'peak_flexion_frame_in_rep',
        'descent_frames', 'ascent_frames', 'tempo_ratio', 'total_rep_frames',
        'peak_descent_velocity_deg_per_frame', 'peak_ascent_velocity_deg_per_frame',
        'mean_descent_velocity_deg_per_frame', 'mean_ascent_velocity_deg_per_frame',
        'jerk_proxy_std', 'phase_identification_status', 'visible_side_used'
    ]
    df_biomarkers = df_biomarkers[biomarker_cols]
    biomarkers_csv_path = biomarkers_dir / "rehab24_lunge_per_rep_biomarkers.csv"
    df_biomarkers.to_csv(biomarkers_csv_path, index=False)
    print(f"\nCombined biomarkers saved to: {biomarkers_csv_path.as_posix()}")

    # Save per-rep processing status log (Stage 5)
    df_proc_log = pd.DataFrame(rep_processing_log)
    proc_log_cols = [
        'subject_id', 'video_id', 'rep_number', 'status', 'error_message',
        'total_frames', 'valid_frames', 'phase_identification_status'
    ]
    df_proc_log = df_proc_log[proc_log_cols]
    proc_log_csv_path = metadata_dir / "rehab24_lunge_processing_log.csv"
    df_proc_log.to_csv(proc_log_csv_path, index=False)
    print(f"Processing log saved to: {proc_log_csv_path.as_posix()}")

    # 7. Write run summary (Stage 7)
    print("Compiling run summary...")
    
    # Reps with phase_identification_status = 'failed'
    failed_reps_list = df_biomarkers[df_biomarkers['phase_identification_status'] == 'failed']
    failed_reps_tuples = [(row['video_id'], row['rep_number']) for _, row in failed_reps_list.iterrows()]
    
    # Per-subject rep counts broken down by correctness
    sub_counts = []
    for sub in sorted(df_biomarkers['subject_id'].unique()):
        sub_df = df_biomarkers[df_biomarkers['subject_id'] == sub]
        total_sub_reps = len(sub_df)
        correct_sub_reps = (sub_df['correctness_label'] == 1).sum()
        incorrect_sub_reps = (sub_df['correctness_label'] == 0).sum()
        sub_counts.append((sub, total_sub_reps, correct_sub_reps, incorrect_sub_reps))
        
    # Cohort biomarker summary statistics across successfully-processed reps
    df_ok = df_biomarkers[df_biomarkers['phase_identification_status'] == 'ok']
    
    biomarkers_to_summary = ['peak_flexion_deg', 'rom_deg', 'tempo_ratio', 'jerk_proxy_std']
    summary_stats = {}
    for col in biomarkers_to_summary:
        col_vals = df_ok[col].dropna()
        if len(col_vals) > 0:
            summary_stats[col] = {
                'min': col_vals.min(),
                'max': col_vals.max(),
                'mean': col_vals.mean(),
                'median': col_vals.median(),
                'std': col_vals.std(ddof=1) if len(col_vals) > 1 else 0.0
            }
        else:
            summary_stats[col] = {'min': np.nan, 'max': np.nan, 'mean': np.nan, 'median': np.nan, 'std': np.nan}

    # Correct-vs-incorrect biomarker comparison
    biomarkers_all = [
        'peak_flexion_deg', 'peak_extension_deg', 'rom_deg', 'descent_frames', 'ascent_frames',
        'tempo_ratio', 'total_rep_frames', 'peak_descent_velocity_deg_per_frame',
        'peak_ascent_velocity_deg_per_frame', 'mean_descent_velocity_deg_per_frame',
        'mean_ascent_velocity_deg_per_frame', 'jerk_proxy_std'
    ]
    comparison_stats = {}
    
    df_correct = df_ok[df_ok['correctness_label'] == 1]
    df_incorrect = df_ok[df_ok['correctness_label'] == 0]
    
    for col in biomarkers_all:
        corr_vals = df_correct[col].dropna()
        incorr_vals = df_incorrect[col].dropna()
        
        c_mean = corr_vals.mean() if len(corr_vals) > 0 else np.nan
        c_std = corr_vals.std(ddof=1) if len(corr_vals) > 1 else 0.0
        
        i_mean = incorr_vals.mean() if len(incorr_vals) > 0 else np.nan
        i_std = incorr_vals.std(ddof=1) if len(incorr_vals) > 1 else 0.0
        
        comparison_stats[col] = {
            'correct_mean': c_mean, 'correct_std': c_std,
            'incorrect_mean': i_mean, 'incorrect_std': i_std
        }

    # Subjects flagged with mean spike_rate > 5%
    flagged_subjects = []
    for sub in sorted(df_biomarkers['subject_id'].unique()):
        sub_df = df_biomarkers[df_biomarkers['subject_id'] == sub]
        sub_mean_spike = sub_df['spike_rate_pct'].mean()
        if sub_mean_spike > 5.0:
            flagged_subjects.append((sub, sub_mean_spike))

    # Compile the summary text
    summary_txt = f"""Phase 5B REHAB24-6 Lunge Integration Summary
======================================
Total reps in manifest: {N_actual} (expected: 88)
Reps successfully processed: {P_count}
Reps with phase_identification_status = 'failed': {F_count}

Failed Reps List (video_id, rep_number):
---------------------------------------
"""
    if failed_reps_tuples:
        for t in failed_reps_tuples:
            summary_txt += f"- {t[0]} rep {t[1]}\n"
    else:
        summary_txt += "- None\n"
        
    summary_txt += """
Per-Subject Rep Counts (broken down by correctness):
---------------------------------------------------
  subject_id | total reps | correct | incorrect
"""
    for sub, tot, corr, incorr in sub_counts:
        summary_txt += f"  {sub:<10} | {tot:<10} | {corr:<7} | {incorr:<9}\n"
        
    summary_txt += """
Cohort Biomarker Summary Statistics (across successfully-processed reps):
-----------------------------------------------------------------------
"""
    summary_txt += f"{'Biomarker':<25} | {'min':>10} | {'max':>10} | {'mean':>10} | {'median':>10} | {'std':>10}\n"
    summary_txt += f"{'-'*25}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}-|-{'-'*10}\n"
    for col in biomarkers_to_summary:
        s = summary_stats[col]
        summary_txt += f"{col:<25} | {s['min']:>10.4f} | {s['max']:>10.4f} | {s['mean']:>10.4f} | {s['median']:>10.4f} | {s['std']:>10.4f}\n"

    summary_txt += """
Correct-vs-Incorrect Biomarker Comparison (mean ± std per group):
--------------------------------------------------------------
"""
    summary_txt += f"{'Biomarker':<40} | {'Correct (n=' + str(len(df_correct)) + ')':<22} | {'Incorrect (n=' + str(len(df_incorrect)) + ')':<22}\n"
    summary_txt += f"{'-'*40}-|-{'-'*22}-|-{'-'*22}\n"
    for col in biomarkers_all:
        c = comparison_stats[col]
        c_str = f"{c['correct_mean']:>9.4f} ± {c['correct_std']:<8.4f}" if not np.isnan(c['correct_mean']) else "N/A"
        i_str = f"{c['incorrect_mean']:>9.4f} ± {c['incorrect_std']:<8.4f}" if not np.isnan(c['incorrect_mean']) else "N/A"
        summary_txt += f"{col:<40} | {c_str:<22} | {i_str:<22}\n"

    summary_txt += """
Subjects flagged with mean spike_rate > 5%:
------------------------------------------
"""
    if flagged_subjects:
        for sub, mean_spike in flagged_subjects:
            summary_txt += f"- Subject {sub}: mean spike rate = {mean_spike:.4f}%\n"
    else:
        summary_txt += "- None\n"

    # Save summary report
    summary_txt_path = metadata_dir / "phase5b_integration_summary.txt"
    summary_txt_path.write_text(summary_txt, encoding='utf-8')
    print(f"Summary report written to: {summary_txt_path.as_posix()}")

    # 8. Print final stdout summary
    print("\n=== Final stdout Summary ===")
    print(f"Total reps in manifest         : {N_actual}")
    print(f"Reps processed successfully    : {P_count}")
    print(f"Reps failed                    : {F_count}")
    print(f"Phase 5B completed successfully.")
    print("============================\n")

if __name__ == '__main__':
    main()
