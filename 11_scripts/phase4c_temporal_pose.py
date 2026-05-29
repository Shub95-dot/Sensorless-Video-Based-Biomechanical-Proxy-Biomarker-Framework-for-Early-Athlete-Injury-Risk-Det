import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import MediaPipe Tasks API
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

def main():
    project_root = Path(".")
    manifest_path = project_root / "3_metadata" / "squats_temporal_manifest.csv"
    model_path = project_root / "12_models" / "pose_landmarker_heavy.task"

    # 1. Validate inputs exist
    if not manifest_path.is_file():
        print(f"Error: squats_temporal_manifest.csv not found at {manifest_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
    if not model_path.is_file():
        print(f"Error: MediaPipe heavy pose model not found at {model_path.as_posix()}", file=sys.stderr)
        print("Please download it from:", file=sys.stderr)
        print("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task", file=sys.stderr)
        sys.exit(1)

    # 2. Load manifest
    manifest_df = pd.read_csv(manifest_path, sep=None, engine='python')
    print(f"Loaded {len(manifest_df)} rows from {manifest_path.name}")

    # 3. Initialize MediaPipe detector
    options = mp_vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(model_path)),
        running_mode=mp_vision.RunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5,
        output_segmentation_masks=False,
    )
    detector = mp_vision.PoseLandmarker.create_from_options(options)

    # We group frames by Subject_ID and process them in sorted order.
    # Within each subject, we iterate manifest rows in frame_index order.
    unique_subjects = sorted(list(manifest_df['Subject_ID'].unique()))
    print(f"Discovered {len(unique_subjects)} subjects to process.")

    # Dictionary to hold the extracted raw frame results for Pass 1, 2, and 3
    # key: File_ID or (Subject_ID, frame_index)
    frame_results = {}
    
    # We will track statistics for pre-write sanity checkpoint
    S = len(unique_subjects)
    F = len(manifest_df)

    landmark_ids = {
        'left_hip': 23, 'right_hip': 24,
        'left_knee': 25, 'right_knee': 26,
        'left_ankle': 27, 'right_ankle': 28
    }

    try:
        # ==================== PASS 1 ====================
        # Process every frame, extract BGR->RGB, run MediaPipe, check chain visibility
        print("\nStarting PASS 1: Landmark Extraction & Visibility Checking...")
        for sub_idx, sub_id in enumerate(unique_subjects):
            sub_df = manifest_df[manifest_df['Subject_ID'] == sub_id].sort_values(by='frame_index')
            total_sub_frames = len(sub_df)
            
            print(f"  [subject {sub_idx + 1}/{S}] {sub_id}: Processing {total_sub_frames} frames...")
            
            for _, row in sub_df.iterrows():
                f_idx = int(row['frame_index'])
                f_num = int(row['frame_number'])
                f_path_str = str(row['frame_path'])
                f_path = project_root / f_path_str

                # Initialize results dictionary for this frame
                res = {
                    'Subject_ID': sub_id,
                    'frame_index': f_idx,
                    'frame_number': f_num,
                    'frame_path': f_path_str,
                    'pose_detected': False,
                    'left_chain_complete': False,
                    'right_chain_complete': False,
                    'landmarks': {}
                }
                
                # Fill all landmarks with default 0.0 values
                for name in landmark_ids.keys():
                    res['landmarks'][name] = {'x': 0.0, 'y': 0.0, 'vis': 0.0}

                if not f_path.is_file():
                    # Frame path missing
                    res['pose_detected'] = False
                    res['status_reason'] = "file_not_found"
                    frame_results[(sub_id, f_idx)] = res
                    continue

                bgr_img = cv2.imread(str(f_path))
                if bgr_img is None:
                    # BGR read failed
                    res['pose_detected'] = False
                    res['status_reason'] = "failed_load"
                    frame_results[(sub_id, f_idx)] = res
                    continue

                # Convert to RGB and mp.Image
                rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)

                # Run detector
                detection_result = detector.detect(mp_image)

                if detection_result and detection_result.pose_landmarks:
                    res['pose_detected'] = True
                    # Get the first detected pose
                    pose_landmarks = detection_result.pose_landmarks[0]
                    
                    # Extract coordinates and visibility for the 6 landmarks of interest
                    for name, lid in landmark_ids.items():
                        if lid < len(pose_landmarks):
                            lm = pose_landmarks[lid]
                            res['landmarks'][name] = {
                                'x': lm.x,
                                'y': lm.y,
                                'vis': lm.visibility
                            }

                    # Determine chain visibility completeness (threshold >= 0.5)
                    left_ok = (res['landmarks']['left_hip']['vis'] >= 0.5 and
                               res['landmarks']['left_knee']['vis'] >= 0.5 and
                               res['landmarks']['left_ankle']['vis'] >= 0.5)
                    
                    right_ok = (res['landmarks']['right_hip']['vis'] >= 0.5 and
                                res['landmarks']['right_knee']['vis'] >= 0.5 and
                                res['landmarks']['right_ankle']['vis'] >= 0.5)

                    res['left_chain_complete'] = left_ok
                    res['right_chain_complete'] = right_ok
                    res['status_reason'] = "success"
                else:
                    res['pose_detected'] = False
                    res['status_reason'] = "no_detection"

                frame_results[(sub_id, f_idx)] = res

        # ==================== PASS 2 ====================
        # Per subject, decide visible_side from Pass 1 counts
        print("\nStarting PASS 2: Determining Sagittal Visible Leg Side...")
        subject_visible_sides = {}
        for sub_id in unique_subjects:
            sub_keys = [k for k in frame_results.keys() if k[0] == sub_id]
            total_sub_frames = len(sub_keys)
            
            left_complete_count = sum(1 for k in sub_keys if frame_results[k]['left_chain_complete'])
            right_complete_count = sum(1 for k in sub_keys if frame_results[k]['right_chain_complete'])
            
            # Visibility thresholds: must be higher count, and at least 30% of total frames
            threshold_count = 0.3 * total_sub_frames
            
            if left_complete_count > right_complete_count:
                visible_side = 'left'
            elif right_complete_count > left_complete_count:
                visible_side = 'right'
            else:
                visible_side = 'undetermined'

            # Secondary check: if the highest complete side is below 30% of total frames, mark undetermined
            highest_count = max(left_complete_count, right_complete_count)
            if highest_count < threshold_count:
                visible_side = 'undetermined'

            subject_visible_sides[sub_id] = {
                'visible_side': visible_side,
                'left_complete_count': left_complete_count,
                'right_complete_count': right_complete_count,
                'total_sub_frames': total_sub_frames
            }
            print(f"  Subject {sub_id}: left complete={left_complete_count}/{total_sub_frames}, right complete={right_complete_count}/{total_sub_frames} -> decided visible side: {visible_side}")

        # ==================== PASS 3 ====================
        # Compute knee angles for the determined side
        print("\nStarting PASS 3: Extracting Knee Angles...")
        final_rows = []
        C = 0
        FM = 0
        CI = 0
        NP = 0

        for sub_id in unique_subjects:
            side_dec = subject_visible_sides[sub_id]['visible_side']
            sub_keys = sorted([k for k in frame_results.keys() if k[0] == sub_id], key=lambda x: x[1])
            
            valid_angles_for_sub = 0

            for k in sub_keys:
                res = frame_results[k]
                res['visible_side'] = side_dec

                knee_angle_deg = np.nan
                angle_status = "chain_incomplete"

                if not res['pose_detected']:
                    angle_status = "no_pose_detected"
                    NP += 1
                elif side_dec == 'undetermined':
                    angle_status = "chain_incomplete"
                    CI += 1
                else:
                    # Determined side (left or right)
                    is_complete = res['left_chain_complete'] if side_dec == 'left' else res['right_chain_complete']
                    if not is_complete:
                        angle_status = "chain_incomplete"
                        CI += 1
                    else:
                        # Extract landmarks for visible side
                        hip = res['landmarks'][f"{side_dec}_hip"]
                        knee = res['landmarks'][f"{side_dec}_knee"]
                        ankle = res['landmarks'][f"{side_dec}_ankle"]

                        H = np.array([hip['x'], hip['y']])
                        K = np.array([knee['x'], knee['y']])
                        A = np.array([ankle['x'], ankle['y']])

                        v1 = H - K
                        v2 = A - K

                        norm1 = np.linalg.norm(v1)
                        norm2 = np.linalg.norm(v2)

                        if norm1 == 0.0 or norm2 == 0.0:
                            angle_status = "failed_math"
                            FM += 1
                        else:
                            dot_prod = np.dot(v1, v2)
                            cos_theta = dot_prod / (norm1 * norm2)
                            cos_theta_clipped = np.clip(cos_theta, -1.0, 1.0)
                            theta_rad = np.arccos(cos_theta_clipped)
                            theta_deg = float(np.degrees(theta_rad))
                            
                            knee_angle_deg = round(theta_deg, 4)
                            angle_status = "computed"
                            C += 1
                            valid_angles_for_sub += 1

                # Append per-frame result
                row_data = {
                    'Subject_ID': res['Subject_ID'],
                    'frame_index': res['frame_index'],
                    'frame_number': res['frame_number'],
                    'frame_path': res['frame_path'],
                    'pose_detected': res['pose_detected'],
                    'left_hip_x': res['landmarks']['left_hip']['x'],
                    'left_hip_y': res['landmarks']['left_hip']['y'],
                    'left_hip_visibility': res['landmarks']['left_hip']['vis'],
                    'left_knee_x': res['landmarks']['left_knee']['x'],
                    'left_knee_y': res['landmarks']['left_knee']['y'],
                    'left_knee_visibility': res['landmarks']['left_knee']['vis'],
                    'left_ankle_x': res['landmarks']['left_ankle']['x'],
                    'left_ankle_y': res['landmarks']['left_ankle']['y'],
                    'left_ankle_visibility': res['landmarks']['left_ankle']['vis'],
                    'right_hip_x': res['landmarks']['right_hip']['x'],
                    'right_hip_y': res['landmarks']['right_hip']['y'],
                    'right_hip_visibility': res['landmarks']['right_hip']['vis'],
                    'right_knee_x': res['landmarks']['right_knee']['x'],
                    'right_knee_y': res['landmarks']['right_knee']['y'],
                    'right_knee_visibility': res['landmarks']['right_knee']['vis'],
                    'right_ankle_x': res['landmarks']['right_ankle']['x'],
                    'right_ankle_y': res['landmarks']['right_ankle']['y'],
                    'right_ankle_visibility': res['landmarks']['right_ankle']['vis'],
                    'left_chain_complete': res['left_chain_complete'],
                    'right_chain_complete': res['right_chain_complete'],
                    'visible_side': side_dec,
                    'knee_angle_deg': knee_angle_deg,
                    'angle_status': angle_status
                }
                final_rows.append(row_data)

            # Log subject-level progress
            print(f"  [subject {unique_subjects.index(sub_id) + 1}/{S}] {sub_id}: processed {total_sub_frames} frames, valid {valid_angles_for_sub}")

    finally:
        # Close detector cleanly in finally
        detector.close()

    # Create DataFrames
    per_frame_df = pd.DataFrame(final_rows)

    # Count visible_side breakdown
    L = sum(1 for s in unique_subjects if subject_visible_sides[s]['visible_side'] == 'left')
    R = sum(1 for s in unique_subjects if subject_visible_sides[s]['visible_side'] == 'right')
    U = sum(1 for s in unique_subjects if subject_visible_sides[s]['visible_side'] == 'undetermined')

    # ==================== Step 7 — Pre-write sanity checkpoint ====================
    print()
    print("--- Pre-write Sanity Checkpoint ---")
    print(f"Subjects processed       : {S}")
    print(f"Total frames processed   : {F}  (expected: 1396)")
    print(f"Total computed angles    : {C}")
    print(f"Total failed_math        : {FM}")
    print(f"Total chain_incomplete   : {CI}")
    print(f"Total no_pose_detected   : {NP}")
    print(f"Sanity check             : {C} + {FM} + {CI} + {NP} should equal {F}")
    print(f"Visible_side breakdown   : {L} left, {R} right, {U} undetermined  ({L} + {R} + {U} should equal {S})")

    # Assertions
    sanity_failed = False
    if C + FM + CI + NP != F:
        print(f"Sanity Check FAILED: C({C}) + FM({FM}) + CI({CI}) + NP({NP}) != F({F})", file=sys.stderr)
        sanity_failed = True
    if L + R + U != S:
        print(f"Sanity Check FAILED: L({L}) + R({R}) + U({U}) != S({S})", file=sys.stderr)
        sanity_failed = True

    if sanity_failed:
        sys.exit("Error: Sanity checks failed. Aborting file creation.")
    
    print("Sanity checks passed successfully. Writing output files...")

    # Define paths
    outputs_dir = project_root / "4_pose_outputs" / "temporal"
    trajectories_dir = outputs_dir / "trajectories"
    plots_dir = project_root / "6_visualizations" / "temporal" / "squats"

    # Create directories if needed
    outputs_dir.mkdir(parents=True, exist_ok=True)
    trajectories_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    # Save per-frame CSV
    per_frame_csv_path = outputs_dir / "squats_temporal_per_frame.csv"
    per_frame_df.to_csv(per_frame_csv_path, index=False)
    print(f"Saved main per-frame CSV to {per_frame_csv_path.as_posix()}")

    # Process each subject for slim trajectories and plots
    summary_lines = []
    outlier_count = 0
    total_computed_vals = []

    for sub_id in unique_subjects:
        side_dec = subject_visible_sides[sub_id]['visible_side']
        sub_data = per_frame_df[per_frame_df['Subject_ID'] == sub_id].sort_values(by='frame_index')
        total_sub_frames = len(sub_data)
        
        computed_df = sub_data[sub_data['angle_status'] == 'computed']
        computed_cnt = len(computed_df)
        pct_valid = (computed_cnt / total_sub_frames) if total_sub_frames > 0 else 0.0
        
        # Determine usability flag
        if pct_valid >= 0.70:
            usability = 'ok'
        elif pct_valid >= 0.40:
            usability = 'marginal'
        else:
            usability = 'insufficient'

        # Pose_detected count for summary report
        pose_det_cnt = int(sub_data['pose_detected'].sum())

        # Collect summary line
        summary_lines.append(f"{sub_id} | {total_sub_frames} | {pose_det_cnt} | {side_dec} | {computed_cnt} | {pct_valid * 100:.2f}% | {usability}")

        if side_dec == 'undetermined':
            # Skip trajectory and plotting for undetermined subjects
            continue

        # Wrote SLIM trajectory CSV
        # columns: frame_index, frame_number, knee_angle_deg, angle_status, hip_x, hip_y, knee_x, knee_y, ankle_x, ankle_y
        slim_trajectory_rows = []
        for _, row in sub_data.iterrows():
            is_comp = row['angle_status'] == 'computed'
            slim_trajectory_rows.append({
                'frame_index': row['frame_index'],
                'frame_number': row['frame_number'],
                'knee_angle_deg': row['knee_angle_deg'],
                'angle_status': row['angle_status'],
                'hip_x': row[f"{side_dec}_hip_x"] if is_comp else np.nan,
                'hip_y': row[f"{side_dec}_hip_y"] if is_comp else np.nan,
                'knee_x': row[f"{side_dec}_knee_x"] if is_comp else np.nan,
                'knee_y': row[f"{side_dec}_knee_y"] if is_comp else np.nan,
                'ankle_x': row[f"{side_dec}_ankle_x"] if is_comp else np.nan,
                'ankle_y': row[f"{side_dec}_ankle_y"] if is_comp else np.nan
            })
        
        slim_df = pd.DataFrame(slim_trajectory_rows)
        slim_csv_path = trajectories_dir / f"SQ_{sub_id}_trajectory.csv"
        slim_df.to_csv(slim_csv_path, index=False)
        print(f"Saved trajectory CSV for Subject {sub_id} to {slim_csv_path.as_posix()}")

        # Outlier counts and computed list for statistics
        for deg in computed_df['knee_angle_deg'].dropna().tolist():
            total_computed_vals.append(deg)
            if deg < 40.0 or deg > 185.0:
                outlier_count += 1

        # Wrote Plot
        plt.figure(figsize=(10, 4))
        # Plot raw dots
        plt.scatter(sub_data['frame_index'], sub_data['knee_angle_deg'], color='red', s=10, label='Raw Angles', zorder=3)
        # Connect consecutive computed with a thin line (breaking over NaN)
        # In matplotlib, plotting a series containing np.nan naturally breaks the line!
        plt.plot(sub_data['frame_index'], sub_data['knee_angle_deg'], color='blue', linewidth=0.75, zorder=2)
        
        plt.ylim(0, 200)
        plt.xlabel('frame_index')
        plt.ylabel('knee_angle_deg (degrees)')
        plt.title(f"Subject {sub_id} — visible side: {side_dec} — {computed_cnt} valid / {total_sub_frames} total frames")
        plt.grid(True, linestyle=':', alpha=0.6)
        
        plot_path = plots_dir / f"SQ_{sub_id}_knee_angle.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"Saved trajectory plot for Subject {sub_id} to {plot_path.as_posix()}")

    # Save summary report
    summary_report_path = outputs_dir / "phase4c_temporal_pose_summary.txt"
    undetermined_subjects = [s for s in unique_subjects if subject_visible_sides[s]['visible_side'] == 'undetermined']
    insufficient_subjects = [s for s in unique_subjects if per_frame_df[per_frame_df['Subject_ID'] == s]['angle_status'].eq('computed').sum() / len(per_frame_df[per_frame_df['Subject_ID'] == s]) < 0.4]
    
    summary_report_content = f"""Phase 4C Temporal Pose Extraction Summary
=========================================
Total subjects processed           : {S}
Total frames processed             : {F}

Subject-level Trajectory Usability Table:
Subject_ID | total_frames | pose_detected | visible_side | computed_angles | pct_valid | usability
---------------------------------------------------------------------------------------------
"""
    for line in summary_lines:
        summary_report_content += line + "\n"

    summary_report_content += f"""
Aggregate Counts:
  Total computed angles            : {C}
  Total failed_math                : {FM}
  Total chain_incomplete           : {CI}
  Total no_pose_detected           : {NP}

Undetermined visible side subjects : {undetermined_subjects}
Insufficient usability subjects    : {insufficient_subjects}

MediaPipe Configuration Used:
  Model Variant                    : Heavy
  Running Mode                     : static IMAGE mode
  min_pose_detection_confidence    : 0.5
  min_pose_presence_confidence     : 0.5
  min_tracking_confidence          : 0.5
"""
    
    summary_report_path.write_text(summary_report_content, encoding='utf-8')
    print(f"Saved summary report to {summary_report_path.as_posix()}")

    # Print final summary to stdout
    mean_angle = np.mean(total_computed_vals) if total_computed_vals else 0.0
    frames_contributing = len(set(per_frame_df[per_frame_df['angle_status'] == 'computed']['Subject_ID']))
    pass_status = "Yes" if C >= 50 else "No"

    print()
    print(f"Computed knee angle rows           : {C}")
    print(f"Frames contributing >=1 angle      : {frames_contributing}")
    print(f"Mean knee angle (degrees)          : {mean_angle:.4f}")
    print(f"Possible outlier count             : {outlier_count}")
    print(f"Phase 4A passed                    : {pass_status}")

if __name__ == '__main__':
    main()
