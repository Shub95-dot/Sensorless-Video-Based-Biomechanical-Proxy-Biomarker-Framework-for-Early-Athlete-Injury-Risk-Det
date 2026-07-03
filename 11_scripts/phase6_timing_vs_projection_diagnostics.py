#!/usr/bin/env python3
"""
phase6_timing_vs_projection_diagnostics.py
==========================================
This script performs a new timing-vs-projection diagnostic analysis on all 48 trials
of the OpenCap drop-jump dataset.

It computes:
1. Per-trial residual lag (video knee-flexion peak time minus IK knee-flexion peak time).
2. Frame-matched vs. peak-matched error for the closer knee.
3. Static-peak error-vs-depth for both knees (96 points).
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd
import scipy.stats
import scipy.signal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / "1_raw_datasets" / "OpenCap" / "LabValidation_withVideos"
OUT_DIR = PROJECT_ROOT / "16_opencap_dropjump_outputs"
METADATA_DIR = OUT_DIR / "metadata"
FIGURES_DIR = OUT_DIR / "figures"
MODEL_PATH = PROJECT_ROOT / "12_models" / "pose_landmarker_heavy.task"

# Ensure directories exist
METADATA_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Import MediaPipe Tasks API
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def compute_knee_angle_3d(hip, knee, ankle):
    """Compute 2D angle between hip-knee and knee-ankle vectors in degrees."""
    v1 = np.array([hip[0] - knee[0], hip[1] - knee[1]])
    v2 = np.array([ankle[0] - knee[0], ankle[1] - knee[1]])
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

def smooth_trajectory(angles, median_window=5, sg_window=7, sg_polyorder=2):
    """2-stage NaN-aware smoothing filter (Median -> Savitzky-Golay)."""
    s = pd.Series(angles)
    median_filtered = s.rolling(window=median_window, center=True, min_periods=1).median()
    median_filtered = median_filtered.where(s.notna(), np.nan)
    
    if median_filtered.notna().any():
        gap_filled = median_filtered.interpolate(method='linear', limit_direction='both')
        smoothed = scipy.signal.savgol_filter(gap_filled.values, window_length=sg_window, polyorder=sg_polyorder)
        smoothed = pd.Series(smoothed, index=s.index).where(median_filtered.notna(), np.nan)
        return smoothed.values
    else:
        return np.full_like(angles, np.nan)

def parse_mot(filepath):
    """Parse OpenSim MOT motion/force file."""
    with open(filepath, 'r') as f:
        header_lines = []
        for line in f:
            header_lines.append(line)
            if 'endheader' in line:
                break
    skip_rows = len(header_lines)
    df = pd.read_csv(filepath, skiprows=skip_rows, sep='\t')
    df.columns = [c.strip() for c in df.columns]
    return df

def run_mediapipe_on_video(video_path, horizontal_flip=False):
    """Extract pose landmarks from video and compute knee flexion angles."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise IOError(f"Could not open video file {video_path}")
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize MediaPipe PoseLandmarker
    base_options = mp_python.BaseOptions(model_asset_path=str(MODEL_PATH))
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
    
    records = []
    f_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if horizontal_flip:
            frame = cv2.flip(frame, 1)
            
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = detector.detect(mp_image)
        
        frame_rec = {
            'frame_index': f_idx,
            'time': f_idx / fps,
            'l_knee_flexion': np.nan,
            'r_knee_flexion': np.nan,
            'l_hip_vis': 0.0,
            'l_knee_vis': 0.0,
            'l_ankle_vis': 0.0,
            'r_hip_vis': 0.0,
            'r_knee_vis': 0.0,
            'r_ankle_vis': 0.0,
        }
        
        if result.pose_landmarks and len(result.pose_landmarks) > 0:
            landmarks = result.pose_landmarks[0]
            
            lh = [landmarks[23].x, landmarks[23].y]
            lk = [landmarks[25].x, landmarks[25].y]
            la = [landmarks[27].x, landmarks[27].y]
            
            rh = [landmarks[24].x, landmarks[24].y]
            rk = [landmarks[26].x, landmarks[26].y]
            ra = [landmarks[28].x, landmarks[28].y]
            
            frame_rec['l_hip_vis'] = landmarks[23].visibility
            frame_rec['l_knee_vis'] = landmarks[25].visibility
            frame_rec['l_ankle_vis'] = landmarks[27].visibility
            frame_rec['r_hip_vis'] = landmarks[24].visibility
            frame_rec['r_knee_vis'] = landmarks[26].visibility
            frame_rec['r_ankle_vis'] = landmarks[28].visibility
            
            l_angle = compute_knee_angle_3d(lh, lk, la)
            r_angle = compute_knee_angle_3d(rh, rk, ra)
            
            if not np.isnan(l_angle):
                frame_rec['l_knee_flexion'] = 180.0 - l_angle
            if not np.isnan(r_angle):
                frame_rec['r_knee_flexion'] = 180.0 - r_angle
                
        records.append(frame_rec)
        f_idx += 1
        
    cap.release()
    detector.close()
    
    df_res = pd.DataFrame(records)
    df_res['l_knee_flexion_smooth'] = smooth_trajectory(df_res['l_knee_flexion'].values)
    df_res['r_knee_flexion_smooth'] = smooth_trajectory(df_res['r_knee_flexion'].values)
    return df_res, fps

# ---------------------------------------------------------------------------
# Main Diagnostics Loop
# ---------------------------------------------------------------------------

def run_diagnostics():
    manifest_path = METADATA_DIR / "opencap_dropjump_manifest.csv"
    if not manifest_path.exists():
        print(f"Error: Manifest file {manifest_path} not found.")
        sys.exit(1)
        
    manifest_df = pd.read_csv(manifest_path)
    total_trials = len(manifest_df)
    
    lag_records = []
    error_comparison_records = []
    static_peak_records = []
    
    print(f"Processing all {total_trials} trials...")
    
    for i, row in manifest_df.iterrows():
        sub = row["subject_id"]
        trial = row["trial_id"]
        cond = row["condition"]
        flip = row["horizontal_flip"]
        
        # Paths
        video_p = PROJECT_ROOT / row["video_path"]
        mocap_ik_p = PROJECT_ROOT / row["mocap_ik_path"]
        force_p = PROJECT_ROOT / row["force_path"]
        
        # Load Video
        df_video, video_fps = run_mediapipe_on_video(video_p, horizontal_flip=flip)
        video_time = df_video["time"].values
        
        # Load Mocap IK
        df_ik = parse_mot(mocap_ik_p)
        ik_time = df_ik["time"].values
        
        # Load Force data and find IC1 & TO1
        df_force = parse_mot(force_p)
        grf_time = df_force["time"].values
        grf_vertical = (df_force["R_ground_force_vy"] + df_force["L_ground_force_vy"]).values
        
        force_threshold = 20.0 # N
        on_ground = grf_vertical > force_threshold
        # Assume force hz is around 2000Hz (we dynamically find it to be safe)
        force_hz = 1.0 / np.mean(np.diff(grf_time))
        min_idx = int(0.1 * force_hz)
        grf_on = np.where(on_ground[min_idx:])[0] + min_idx
        
        if len(grf_on) == 0:
            print(f"Skipping {sub} {trial}: No GRF contact detected.")
            continue
        ic1_time = grf_time[grf_on[0]]
        
        off_ground_after_ic1 = np.where(grf_vertical[grf_on[0]:] < 10.0)[0] + grf_on[0]
        if len(off_ground_after_ic1) == 0:
            print(f"Skipping {sub} {trial}: No rebound takeoff detected.")
            continue
        to1_time = grf_time[off_ground_after_ic1[0]]
        
        # Detect Video IC1 Frame using Right Knee flexion as in original sync
        t_start = ic1_time - 0.25
        t_end = ic1_time + 0.25
        slice_df = df_video[(video_time >= t_start) & (video_time <= t_end)]
        min_flex_idx = slice_df["r_knee_flexion_smooth"].idxmin()
        ic1_video_time = df_video.loc[min_flex_idx, "time"]
        
        # Compute GRF-anchored lag
        grf_lag = ic1_video_time - ic1_time
        
        # Aligned video time axis
        video_time_aligned = video_time - grf_lag
        
        # Closer leg mapping
        closer_leg = "L" if sub == "subject8" else "R"
        v_col_closer = "l_knee_flexion_smooth" if closer_leg == "L" else "r_knee_flexion_smooth"
        v_col_far = "r_knee_flexion_smooth" if closer_leg == "L" else "l_knee_flexion_smooth"
        ik_col_closer = "knee_angle_l" if closer_leg == "L" else "knee_angle_r"
        ik_col_far = "knee_angle_r" if closer_leg == "L" else "knee_angle_l"
        
        # 1. PEAK TIME IDENTIFICATION (CLOSER LEG ONLY FOR RESIDUAL LAG)
        # Find Mocap Peak Flexion Time in the landing window [IC1, TO1]
        ik_mask = (ik_time >= ic1_time) & (ik_time <= to1_time)
        ik_closer_window = df_ik[ik_col_closer].values[ik_mask]
        ik_times_window = ik_time[ik_mask]
        
        if len(ik_closer_window) == 0:
            print(f"Skipping {sub} {trial}: No IK data in landing window.")
            continue
            
        t_ik_peak = ik_times_window[np.argmax(ik_closer_window)]
        ik_peak_val = np.max(ik_closer_window)
        
        # Find Video Peak Flexion Time in the landing window [IC1, TO1] (on aligned timeline)
        video_mask = (video_time_aligned >= ic1_time) & (video_time_aligned <= to1_time)
        video_closer_window = df_video[v_col_closer].values[video_mask]
        video_times_window_aligned = video_time_aligned[video_mask]
        
        if len(video_closer_window) == 0 or np.isnan(video_closer_window).all():
            print(f"Skipping {sub} {trial}: No Video data in landing window.")
            continue
            
        t_video_peak = video_times_window_aligned[np.nanargmax(video_closer_window)]
        video_peak_val = np.nanmax(video_closer_window)
        
        # Calculate residual lag
        residual_lag_s = t_video_peak - t_ik_peak
        residual_lag_frames = residual_lag_s * video_fps
        
        lag_records.append({
            "subject_id": sub,
            "trial_id": trial,
            "condition": cond,
            "closer_leg": closer_leg,
            "video_fps": video_fps,
            "t_video_peak": t_video_peak,
            "t_ik_peak": t_ik_peak,
            "residual_lag_s": residual_lag_s,
            "residual_lag_frames": residual_lag_frames
        })
        
        # 2. FRAME-MATCHED vs PEAK-MATCHED ERROR (CLOSER LEG)
        # (a) Frame-matched on GRF anchor (Evaluate video at the Mocap peak time)
        video_val_a = np.interp(t_ik_peak, video_time_aligned, df_video[v_col_closer].values)
        error_a = video_val_a - ik_peak_val
        
        # (b) Peak-matched (align peaks exactly)
        error_b = video_peak_val - ik_peak_val
        
        error_comparison_records.append({
            "subject_id": sub,
            "trial_id": trial,
            "condition": cond,
            "closer_leg": closer_leg,
            "ik_peak_val": ik_peak_val,
            "video_val_frame_matched": video_val_a,
            "video_val_peak_matched": video_peak_val,
            "error_frame_matched": error_a,
            "error_peak_matched": error_b
        })
        
        # 3. STATIC-PEAK ERROR-vs-DEPTH (BOTH KNEES -> 96 points)
        # Find peak for Left Knee
        ik_l_window = df_ik["knee_angle_l"].values[ik_mask]
        t_ik_peak_l = ik_times_window[np.argmax(ik_l_window)]
        ik_flex_l = np.max(ik_l_window)
        video_flex_l = np.interp(t_ik_peak_l, video_time_aligned, df_video["l_knee_flexion_smooth"].values)
        error_l = video_flex_l - ik_flex_l
        
        static_peak_records.append({
            "subject_id": sub,
            "trial_id": trial,
            "condition": cond,
            "knee": "L",
            "ik_peak_flexion": ik_flex_l,
            "video_flexion_at_peak": video_flex_l,
            "error": error_l
        })
        
        # Find peak for Right Knee
        ik_r_window = df_ik["knee_angle_r"].values[ik_mask]
        t_ik_peak_r = ik_times_window[np.argmax(ik_r_window)]
        ik_flex_r = np.max(ik_r_window)
        video_flex_r = np.interp(t_ik_peak_r, video_time_aligned, df_video["r_knee_flexion_smooth"].values)
        error_r = video_flex_r - ik_flex_r
        
        static_peak_records.append({
            "subject_id": sub,
            "trial_id": trial,
            "condition": cond,
            "knee": "R",
            "ik_peak_flexion": ik_flex_r,
            "video_flexion_at_peak": video_flex_r,
            "error": error_r
        })
        
        print(f"  Processed {sub} {trial}: Closer leg lag = {residual_lag_frames:.2f} frames. Error(a) = {error_a:.2f}°, Error(b) = {error_b:.2f}°")

    # ---------------------------------------------------------------------------
    # Analysis & Formatting Outputs
    # ---------------------------------------------------------------------------
    
    # 1. Process Residual Lags
    df_lag = pd.DataFrame(lag_records)
    lag_csv_path = METADATA_DIR / "residual_lag_per_trial.csv"
    df_lag.to_csv(lag_csv_path, index=False)
    print(f"\nSaved per-trial residual lag CSV to: {lag_csv_path}")
    
    lags = df_lag["residual_lag_frames"].values
    lag_min = np.min(lags)
    lag_max = np.max(lags)
    lag_mean = np.mean(lags)
    lag_sd = np.std(lags, ddof=1)
    
    print("\n=========================================================")
    print("1. PER-TRIAL RESIDUAL LAG DISTRIBUTION (frames)")
    print("=========================================================")
    print(f"Min  : {lag_min:.4f}")
    print(f"Max  : {lag_max:.4f}")
    print(f"Mean : {lag_mean:.4f}")
    print(f"SD   : {lag_sd:.4f}")
    
    # Plot lag histogram
    plt.figure(figsize=(8, 6))
    plt.hist(lags, bins=15, color="skyblue", edgecolor="black", alpha=0.7)
    plt.axvline(lag_mean, color="red", linestyle="dashed", linewidth=2, label=f"Mean: {lag_mean:.2f}")
    plt.xlabel("Residual Lag (frames)")
    plt.ylabel("Frequency")
    plt.title("Distribution of Per-Trial Residual Lag (Video Peak - Mocap Peak)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    histogram_path = FIGURES_DIR / "residual_lag_histogram.png"
    plt.savefig(histogram_path, dpi=300)
    plt.close()
    print(f"Saved residual lag histogram plot to: {histogram_path}")
    
    # 2. Process Frame-Matched vs. Peak-Matched Error
    df_err_comp = pd.DataFrame(error_comparison_records)
    
    err_a = df_err_comp["error_frame_matched"].values
    err_b = df_err_comp["error_peak_matched"].values
    
    mae_a = np.mean(np.abs(err_a))
    mae_b = np.mean(np.abs(err_b))
    
    rmse_a = np.sqrt(np.mean(err_a ** 2))
    rmse_b = np.sqrt(np.mean(err_b ** 2))
    
    bias_a = np.mean(err_a)
    bias_b = np.mean(err_b)
    
    sd_a = np.std(err_a, ddof=1)
    sd_b = np.std(err_b, ddof=1)
    
    print("\n=========================================================")
    print("2. FRAME-MATCHED vs PEAK-MATCHED ERROR COMPARISON")
    print("=========================================================")
    print(f"Metric              | Frame-Matched (a) | Peak-Matched (b)")
    print(f"--------------------|-------------------|------------------")
    print(f"Mean Abs Error (MAE)| {mae_a:<17.4f} | {mae_b:.4f}")
    print(f"RMSE                | {rmse_a:<17.4f} | {rmse_b:.4f}")
    print(f"Mean Bias           | {bias_a:<17.4f} | {bias_b:.4f}")
    print(f"SD of Error         | {sd_a:<17.4f} | {sd_b:.4f}")
    
    # 3. Process Static-Peak Error-vs-Depth
    df_static = pd.DataFrame(static_peak_records)
    
    # Drop rows where video flexion or error is NaN (if any occluded cases)
    df_static_clean = df_static.dropna(subset=["ik_peak_flexion", "video_flexion_at_peak", "error"]).copy()
    static_csv_path = METADATA_DIR / "static_peak_error.csv"
    df_static.to_csv(static_csv_path, index=False)
    print(f"\nSaved static peak error CSV to: {static_csv_path}")
    print(f"Total points pooled: {len(df_static)} (Cleaned non-NaN: {len(df_static_clean)})")
    
    ik_flex_vals = df_static_clean["ik_peak_flexion"].values
    err_vals = df_static_clean["error"].values
    
    r_val, p_val = scipy.stats.pearsonr(ik_flex_vals, err_vals)
    rho_val, p_rho = scipy.stats.spearmanr(ik_flex_vals, err_vals)
    
    # Check monotonicity
    # We can check if Spearman correlation is high and statistically significant.
    # Monotonicity can be described as monotonic if Spearman rho is close to 1 or -1 with p < 0.05.
    is_monotonic = "Yes" if (p_rho < 0.05 and abs(rho_val) > 0.8) else "No (or weak)"
    
    print("\n=========================================================")
    print("3. STATIC-PEAK ERROR-vs-DEPTH (96 points)")
    print("=========================================================")
    print(f"Pearson Correlation r  : {r_val:.4f} (p = {p_val:.4e})")
    print(f"Spearman Correlation rho: {rho_val:.4f} (p = {p_rho:.4e})")
    print(f"Strictly Monotonic     : {is_monotonic}")
    
    # Plot scatter plot
    plt.figure(figsize=(8, 6))
    plt.scatter(ik_flex_vals, err_vals, color="darkcyan", alpha=0.7, edgecolors="black", s=30, label="Static Peaks (96 points)")
    
    # Linear fit
    slope, intercept = np.polyfit(ik_flex_vals, err_vals, 1)
    x_range = np.linspace(np.min(ik_flex_vals), np.max(ik_flex_vals), 100)
    plt.plot(x_range, slope * x_range + intercept, "r--", linewidth=2, label=f"Linear Fit (slope={slope:.3f})")
    
    plt.xlabel("Mocap IK Peak Knee Flexion (degrees)")
    plt.ylabel("Static Peak Error: Video - IK (degrees)")
    plt.title("Static Peak Joint Angle Measurement Error vs. Flexion Depth")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    scatter_path = FIGURES_DIR / "static_peak_error_scatter.png"
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"Saved static peak error scatter plot to: {scatter_path}")
    print("\n=========================================================\n")

if __name__ == "__main__":
    run_diagnostics()
