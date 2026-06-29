import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Configure paths
PROJECT_ROOT = Path(".").resolve()
sys.path.append(str(PROJECT_ROOT / "16_opencap_dropjump_outputs" / "metadata"))
from stage0_processor import run_mediapipe_on_video, parse_mot, parse_trc

def run_diagnostic():
    print("=========================================================")
    print("RUNNING BIOMECHANICAL DIAGNOSTIC: 15-DEG DISAGREEMENT")
    print("=========================================================")
    
    # We use subject2 DJ1 as the sample trial
    sub = "subject2"
    trial = "DJ1"
    
    # 1. Load video and extract knee angles
    video_path = PROJECT_ROOT / "1_raw_datasets" / "OpenCap" / "LabValidation_withVideos" / sub / "VideoData" / "Session0" / "Cam4" / trial / f"{trial}_syncdWithMocap.avi"
    print(f"Loading Synced Video: {video_path}")
    df_video, video_fps = run_mediapipe_on_video(video_path, horizontal_flip=False)
    
    # 2. Load OpenSim MOT (IK coordinates)
    ik_path = PROJECT_ROOT / "1_raw_datasets" / "OpenCap" / "LabValidation_withVideos" / sub / "OpenSimData" / "Mocap" / "IK" / f"{trial}.mot"
    print(f"Loading Mocap IK: {ik_path}")
    df_ik, ik_header = parse_mot(ik_path)
    
    # 3. Load TRC (Marker positions)
    trc_path = PROJECT_ROOT / "1_raw_datasets" / "OpenCap" / "LabValidation_withVideos" / sub / "MarkerData" / "Mocap" / f"{trial}.trc"
    print(f"Loading Mocap TRC: {trc_path}")
    df_trc = parse_trc(trc_path)
    
    # 4. Load Forces to get Force IC1
    force_path = PROJECT_ROOT / "1_raw_datasets" / "OpenCap" / "LabValidation_withVideos" / sub / "ForceData" / f"{trial}_forces.mot"
    df_force, _ = parse_mot(force_path)
    grf_time = df_force["time"].values
    grf_vertical = (df_force["R_ground_force_vy"] + df_force["L_ground_force_vy"]).values
    
    # Detect Force IC1
    force_threshold = 20.0
    on_ground = grf_vertical > force_threshold
    min_idx = int(0.1 * 2000.0) # assume 2000Hz
    grf_on = np.where(on_ground[min_idx:])[0] + min_idx
    ic1_force_time = grf_time[grf_on[0]]
    print(f"Force IC1 Time: {ic1_force_time:.4f} s")
    
    # Detect Video IC1 Frame (minimum flexion before absorption phase)
    # Search window around force IC1 (+/- 0.2s)
    video_time = df_video["time"].values
    t_start, t_end = ic1_force_time - 0.2, ic1_force_time + 0.2
    slice_df = df_video[(video_time >= t_start) & (video_time <= t_end)]
    
    # We use Right Knee (Cam4 is right side view)
    min_flex_idx = slice_df["r_knee_flexion_smooth"].idxmin()
    ic1_video_time = df_video.loc[min_flex_idx, "time"]
    ic1_video_frame = df_video.loc[min_flex_idx, "frame_index"]
    print(f"Video IC1 Frame: {ic1_video_frame} at {ic1_video_time:.4f} s")
    
    # Compare Lags:
    grf_anchored_lag = ic1_video_time - ic1_force_time
    grf_anchored_lag_frames = round(grf_anchored_lag * video_fps)
    print(f"GRF-anchored Lag: {grf_anchored_lag*1000:.2f} ms ({grf_anchored_lag_frames} frames)")
    
    # 5. Compute knee angle two ways from Mocap:
    # (a) OpenSim knee_angle from .mot
    ik_time = df_ik["time"].values
    ik_opensim_r = df_ik["knee_angle_r"].values
    
    # (b) 3-point hip-knee-ankle angle from .trc markers
    # Using R_HJC, r_knee, r_ankle
    trc_time = df_trc["Time"].values
    
    # Align TRC and IK coordinates (both at 100Hz on same time axis)
    # Hip Joint Center R_HJC
    h_x, h_y, h_z = df_trc["R_HJC_X"].values, df_trc["R_HJC_Y"].values, df_trc["R_HJC_Z"].values
    # Knee r_knee
    k_x, k_y, k_z = df_trc["r_knee_X"].values, df_trc["r_knee_Y"].values, df_trc["r_knee_Z"].values
    # Ankle r_ankle
    a_x, a_y, a_z = df_trc["r_ankle_X"].values, df_trc["r_ankle_Y"].values, df_trc["r_ankle_Z"].values
    
    # Vectors
    v_k_h = np.column_stack((h_x - k_x, h_y - k_y, h_z - k_z))
    v_k_a = np.column_stack((a_x - k_x, a_y - k_y, a_z - k_z))
    
    # 3D angles
    dot_prod = np.sum(v_k_h * v_k_a, axis=1)
    norm_h = np.linalg.norm(v_k_h, axis=1)
    norm_a = np.linalg.norm(v_k_a, axis=1)
    cos_theta = dot_prod / (norm_h * norm_a)
    theta_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
    theta_deg = np.degrees(theta_rad)
    trc_3pt_r = 180.0 - theta_deg # convert to flexion definition
    
    # Interpolate Video and Marker angles to Mocap IK time using GRF-anchored lag:
    v_time_grf = video_time - grf_anchored_lag
    v_flex_grf = np.interp(ik_time, v_time_grf, df_video["r_knee_flexion_smooth"].values, left=np.nan, right=np.nan)
    
    # Interpolate 3-point marker angle (originally at trc_time) onto ik_time
    trc_3pt_r_aligned = np.interp(ik_time, trc_time, trc_3pt_r)
    
    # Compute RMSEs:
    # Video vs OpenSim (a)
    rmse_opensim = np.sqrt(np.nanmean((v_flex_grf - ik_opensim_r) ** 2))
    # Video vs 3-Point TRC (b)
    rmse_trc = np.sqrt(np.nanmean((v_flex_grf - trc_3pt_r_aligned) ** 2))
    
    print("\n--- Diagnostic Results ---")
    print(f"RMSE (Video vs. (a) OpenSim joint angle)  : {rmse_opensim:.4f} degrees")
    print(f"RMSE (Video vs. (b) 3-Point Marker angle) : {rmse_trc:.4f} degrees")
    
    # Offset difference between OpenSim joint angle and 3-marker angle:
    mean_offset_a_b = np.nanmean(trc_3pt_r_aligned - ik_opensim_r)
    print(f"Mean offset between 3-Point Marker and OpenSim joint angle: {mean_offset_a_b:.4f} degrees")
    
    # 6. Plot Knee Angles Comparison
    plt.figure(figsize=(10, 6))
    plt.plot(ik_time, v_flex_grf, 'g-', linewidth=2.5, label="Video Flexion Angle (GRF-Lag Shifted)")
    plt.plot(ik_time, ik_opensim_r, 'b-', linewidth=2, label="IK definition (a) - OpenSim knee_angle")
    plt.plot(ik_time, trc_3pt_r_aligned, 'r--', linewidth=2, label="Marker definition (b) - 3-Point Included Angle")
    
    plt.axvline(x=ic1_force_time, color='gray', linestyle=':', label='IC1 Contact')
    plt.xlabel("Time (seconds)")
    plt.ylabel("Knee Flexion Angle (degrees)")
    plt.title(f"Diagnostic: Knee Angle Definitions Comparison ({sub} {trial})")
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plot1_path = PROJECT_ROOT / "16_opencap_dropjump_outputs" / "stage0" / "diagnostic_angles_comparison.png"
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    print(f"Plot saved: {plot1_path}")
    
    # 7. Plot Error vs. Flexion Magnitude
    # Let's compute errors:
    error_opensim = v_flex_grf - ik_opensim_r
    error_trc = v_flex_grf - trc_3pt_r_aligned
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left Panel: Video vs. OpenSim
    ax1.scatter(ik_opensim_r, error_opensim, color='blue', alpha=0.6, s=15)
    # Fit line
    valid_mask_a = ~np.isnan(ik_opensim_r) & ~np.isnan(error_opensim)
    slope_a, intercept_a = np.polyfit(ik_opensim_r[valid_mask_a], error_opensim[valid_mask_a], 1)
    x_range_a = np.linspace(np.nanmin(ik_opensim_r), np.nanmax(ik_opensim_r), 100)
    ax1.plot(x_range_a, slope_a * x_range_a + intercept_a, 'k--', label=f"Fit: slope={slope_a:.3f}")
    ax1.set_xlabel("OpenSim knee_angle (degrees)")
    ax1.set_ylabel("Error: Video - OpenSim (degrees)")
    ax1.set_title("Video Error vs. OpenSim Flexion Depth")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Right Panel: Video vs. 3-Point Marker
    ax2.scatter(trc_3pt_r_aligned, error_trc, color='red', alpha=0.6, s=15)
    valid_mask_b = ~np.isnan(trc_3pt_r_aligned) & ~np.isnan(error_trc)
    slope_b, intercept_b = np.polyfit(trc_3pt_r_aligned[valid_mask_b], error_trc[valid_mask_b], 1)
    x_range_b = np.linspace(np.nanmin(trc_3pt_r_aligned), np.nanmax(trc_3pt_r_aligned), 100)
    ax2.plot(x_range_b, slope_b * x_range_b + intercept_b, 'k--', label=f"Fit: slope={slope_b:.3f}")
    ax2.set_xlabel("3-Point Marker angle (degrees)")
    ax2.set_ylabel("Error: Video - 3-Point (degrees)")
    ax2.set_title("Video Error vs. 3-Point Flexion Depth")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(f"Diagnostic Error Patterns ({sub} {trial})")
    plt.tight_layout()
    plot2_path = PROJECT_ROOT / "16_opencap_dropjump_outputs" / "stage0" / "diagnostic_error_patterns.png"
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    print(f"Plot saved: {plot2_path}")
    
    print("\n--- Error Pattern Interpretation ---")
    print(f"OpenSim Error Slope: {slope_a:.4f} (if close to 0, error is flat offset)")
    print(f"3-Point Error Slope: {slope_b:.4f} (if close to 0, error is flat offset)")
    
    if abs(slope_b) > 0.15:
        print("Interpretation: FORESHORTENING detected (error increases with flexion depth).")
    else:
        print("Interpretation: DEFINITION MISMATCH detected (error is a flat geometric offset).")
        
    print("\n=========================================================")

if __name__ == "__main__":
    run_diagnostic()
