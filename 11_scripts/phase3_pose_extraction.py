#!/usr/bin/env python3
"""
phase3_pose_extraction.py
=========================
Phase 3 — Pose Extraction Test (Squats) — REVISED v2

Uses MediaPipe Tasks API (PoseLandmarker) with the Heavy model.
Performs manual skeleton drawing using cv2.line and cv2.circle.
Extracts 33 landmarks and writes exact csv outputs.

Author  : Dissertation Project
Created : 2026-05-26
"""

import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ---------------------------------------------------------------------------
# Paths and Configs
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_CSV = PROJECT_ROOT / "3_metadata" / "squat_quality_review.csv"
MODEL_PATH = PROJECT_ROOT / "12_models" / "pose_landmarker_heavy.task"

RAW_POSE_CSV = PROJECT_ROOT / "4_pose_outputs" / "raw_pose" / "squats_pose_raw.csv"
FRAME_STATUS_CSV = PROJECT_ROOT / "4_pose_outputs" / "raw_pose" / "squats_pose_frame_status.csv"
OVERLAY_DIR = PROJECT_ROOT / "6_visualizations" / "skeleton_overlays" / "squats"
POST_POSE_CSV = PROJECT_ROOT / "3_metadata" / "squat_quality_review_post_pose.csv"
SUMMARY_TXT = PROJECT_ROOT / "4_pose_outputs" / "phase3_summary.txt"

# BlazePose Landmark Names Reference (0-32)
LANDMARK_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index"
]

# Lower body landmarks to check for completeness
LOWER_BODY_LANDMARKS = {
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle"
}

# BlazePose skeleton connections
POSE_CONNECTIONS = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Left arm
    (11, 13), (13, 15),
    (15, 17), (15, 19), (15, 21), (17, 19),
    # Right arm
    (12, 14), (14, 16),
    (16, 18), (16, 20), (16, 22), (18, 20),
    # Left leg
    (23, 25), (25, 27),
    (27, 29), (29, 31), (27, 31),
    # Right leg
    (24, 26), (26, 28),
    (28, 30), (30, 32), (28, 32),
]

def main():
    print("Executing Phase 3 -- Pose Extraction Test (Squats)")

    # 1. Environment validation
    if not MODEL_PATH.exists():
        print(f"ERROR: Model file not found at: {MODEL_PATH}")
        print("Please download the Heavy variant model file from:")
        print("https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task")
        sys.exit(1)

    if not INPUT_CSV.exists():
        print(f"ERROR: Input CSV not found at: {INPUT_CSV}")
        sys.exit(1)

    # Auto-detect separator and read input CSV
    print(f"Loading input metadata from: {INPUT_CSV}")
    try:
        df_input = pd.read_csv(INPUT_CSV, sep=None, engine='python')
    except Exception as e:
        print(f"ERROR reading CSV: {e}")
        sys.exit(1)

    # Validate required columns
    required_cols = ["File_ID", "Exercise", "Quality", "Selected", "File_Path", "Subject_ID"]
    for col in required_cols:
        if col not in df_input.columns:
            print(f"ERROR: Input CSV is missing required column: {col}")
            sys.exit(1)

    # Defensive filtering
    df_input['__clean_exercise'] = df_input['Exercise'].astype(str).str.strip().str.lower()
    df_input['__clean_quality'] = df_input['Quality'].astype(str).str.strip().str.lower()
    df_input['__clean_selected'] = df_input['Selected'].astype(str).str.strip().str.lower()

    filtered_df = df_input[
        (df_input['__clean_exercise'] == 'squats') &
        (df_input['__clean_quality'] == 'good') &
        (df_input['__clean_selected'] == 'yes')
    ].copy()

    # Drop the temporary clean columns from the dataframe
    df_input.drop(columns=['__clean_exercise', '__clean_quality', '__clean_selected'], inplace=True, errors='ignore')
    filtered_df.drop(columns=['__clean_exercise', '__clean_quality', '__clean_selected'], inplace=True, errors='ignore')

    N = len(filtered_df)

    # 3. Mandatory checkpoint before pose extraction
    print(f"Filtered rows: {N}")
    print("Expected: ~100")
    print("Proceed? (await user confirmation)")
    
    # We will use python's input() for confirmation.
    if len(sys.argv) > 1 and sys.argv[1] in ["--yes", "-y"]:
        print("Automatically proceeding due to command-line flag...")
    else:
        try:
            user_response = input().strip().lower()
            if user_response not in ["y", "yes", "proceed", ""]:
                print("Execution aborted by user.")
                sys.exit(0)
        except EOFError:
            print("No interactive terminal detected. Continuing...")

    print("Starting Pose Extraction...")

    # Ensure output directories exist
    RAW_POSE_CSV.parent.mkdir(parents=True, exist_ok=True)
    OVERLAY_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize MediaPipe Tasks API detector
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

    # Data collection structures
    raw_pose_rows = []
    frame_status_rows = []
    
    # Map from File_ID to status_reason for post-pose quality CSV
    status_reason_map = {}

    failed_ids = []
    incomplete_ids = []
    low_visibility_counts = {name: 0 for name in LOWER_BODY_LANDMARKS.values()}

    pose_detected_count = 0
    lower_body_complete_count = 0
    no_detection_count = 0
    failed_load_count = 0
    file_not_found_count = 0

    try:
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            file_id = row['File_ID']
            subject_id = row['Subject_ID']
            exercise = row['Exercise']
            file_path_str = row['File_Path']

            # Resolve path relative to project root (handling back/forward slashes)
            normalized_path_str = file_path_str.replace("/", "\\") if sys.platform.startswith('win') else file_path_str.replace("\\", "/")
            file_path = PROJECT_ROOT / normalized_path_str

            print(f"[{idx+1}/{N}] {file_id} -> ", end="", flush=True)

            # Check if file exists
            if not file_path.exists():
                status_reason = "file_not_found"
                file_not_found_count += 1
                failed_ids.append(file_id)
                status_reason_map[file_id] = status_reason
                print(status_reason)
                
                frame_status_rows.append({
                    "File_ID": file_id,
                    "Subject_ID": subject_id,
                    "Exercise": exercise,
                    "File_Path": file_path_str,
                    "pose_detected": False,
                    "lower_body_complete": False,
                    "status_reason": status_reason,
                    "low_visibility_landmarks": ""
                })
                continue

            # Load image with cv2
            img_bgr = cv2.imread(str(file_path))
            if img_bgr is None:
                status_reason = "failed_load"
                failed_load_count += 1
                failed_ids.append(file_id)
                status_reason_map[file_id] = status_reason
                print(status_reason)

                frame_status_rows.append({
                    "File_ID": file_id,
                    "Subject_ID": subject_id,
                    "Exercise": exercise,
                    "File_Path": file_path_str,
                    "pose_detected": False,
                    "lower_body_complete": False,
                    "status_reason": status_reason,
                    "low_visibility_landmarks": ""
                })
                continue

            h, w = img_bgr.shape[:2]

            # Convert BGR to RGB for Tasks API
            rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            
            # Detect
            result = detector.detect(mp_image)

            # Detection check
            if not result.pose_landmarks or len(result.pose_landmarks) == 0:
                status_reason = "no_detection"
                no_detection_count += 1
                failed_ids.append(file_id)
                status_reason_map[file_id] = status_reason
                print(status_reason)

                frame_status_rows.append({
                    "File_ID": file_id,
                    "Subject_ID": subject_id,
                    "Exercise": exercise,
                    "File_Path": file_path_str,
                    "pose_detected": False,
                    "lower_body_complete": False,
                    "status_reason": status_reason,
                    "low_visibility_landmarks": ""
                })
                continue

            # Pose detected!
            pose_detected_count += 1
            pose_landmarks = result.pose_landmarks[0]

            # Check lower-body completeness and log visibility sanity warnings
            low_vis_list = []
            for lm_idx, lm_name in LOWER_BODY_LANDMARKS.items():
                lm = pose_landmarks[lm_idx]
                if not (0.0 <= lm.visibility <= 1.0):
                    print(f"\n[SANITY WARNING] {file_id} landmark '{lm_name}' visibility ({lm.visibility}) out of [0, 1] bounds!")
                if lm.visibility < 0.5:
                    low_vis_list.append(lm_name)
                    low_visibility_counts[lm_name] += 1

            lower_body_complete = (len(low_vis_list) == 0)
            low_visibility_str = ";".join(low_vis_list)

            if lower_body_complete:
                status_reason = "success"
                lower_body_complete_count += 1
            else:
                status_reason = "success_lower_body_incomplete"
                incomplete_ids.append(file_id)

            status_reason_map[file_id] = status_reason
            print(status_reason)

            # Store in squats_pose_raw.csv rows
            for lm_id, lm in enumerate(pose_landmarks):
                lm_name = LANDMARK_NAMES[lm_id]
                x = lm.x
                y = lm.y
                z = lm.z
                vis = lm.visibility
                x_px = int(round(x * w))
                y_px = int(round(y * h))

                # Sanity checking coordinates
                if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
                    # We print a silent trace or handle it safely, since person can be out of frame
                    pass
                if not (0 <= x_px <= w) or not (0 <= y_px <= h):
                    # Out of bounds check
                    pass

                raw_pose_rows.append({
                    "File_ID": file_id,
                    "Subject_ID": subject_id,
                    "Exercise": exercise,
                    "image_width": w,
                    "image_height": h,
                    "landmark_id": lm_id,
                    "landmark_name": lm_name,
                    "x": x,
                    "y": y,
                    "z": z,
                    "x_px": x_px,
                    "y_px": y_px,
                    "visibility": vis
                })

            # Store frame status
            frame_status_rows.append({
                "File_ID": file_id,
                "Subject_ID": subject_id,
                "Exercise": exercise,
                "File_Path": file_path_str,
                "pose_detected": True,
                "lower_body_complete": lower_body_complete,
                "status_reason": status_reason,
                "low_visibility_landmarks": low_visibility_str
            })

            # Manual skeleton drawing
            overlay = img_bgr.copy()

            # For each connection (a, b): skip if either endpoint has visibility < 0.5
            for a, b in POSE_CONNECTIONS:
                lm_a = pose_landmarks[a]
                lm_b = pose_landmarks[b]
                if lm_a.visibility >= 0.5 and lm_b.visibility >= 0.5:
                    pt_a = (int(lm_a.x * w), int(lm_a.y * h))
                    pt_b = (int(lm_b.x * w), int(lm_b.y * h))
                    cv2.line(overlay, pt_a, pt_b, color=(0, 255, 0), thickness=2) # green

            # For each landmark with visibility >= 0.5: draw red dot
            for lm in pose_landmarks:
                if lm.visibility >= 0.5:
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    cv2.circle(overlay, (px, py), 3, (0, 0, 255), -1) # red

            # Save overlay image
            overlay_path = OVERLAY_DIR / f"{file_id}.jpg"
            cv2.imwrite(str(overlay_path), overlay)

    finally:
        detector.close()
        print("Pose detector closed cleanly.")

    # 4. Write all five output files
    
    # Output 1: raw pose CSV
    df_raw_pose = pd.DataFrame(raw_pose_rows)
    raw_pose_cols = [
        "File_ID", "Subject_ID", "Exercise", "image_width", "image_height",
        "landmark_id", "landmark_name", "x", "y", "z", "x_px", "y_px", "visibility"
    ]
    if not df_raw_pose.empty:
        df_raw_pose = df_raw_pose[raw_pose_cols]
    else:
        df_raw_pose = pd.DataFrame(columns=raw_pose_cols)
    df_raw_pose.to_csv(RAW_POSE_CSV, index=False)
    print(f"Saved raw pose CSV: {RAW_POSE_CSV}")

    # Output 2: frame status CSV
    df_frame_status = pd.DataFrame(frame_status_rows)
    status_cols = [
        "File_ID", "Subject_ID", "Exercise", "File_Path",
        "pose_detected", "lower_body_complete", "status_reason", "low_visibility_landmarks"
    ]
    if not df_frame_status.empty:
        df_frame_status = df_frame_status[status_cols]
    else:
        df_frame_status = pd.DataFrame(columns=status_cols)
    df_frame_status.to_csv(FRAME_STATUS_CSV, index=False)
    print(f"Saved frame status CSV: {FRAME_STATUS_CSV}")

    # Output 3: copy of input CSV with Pose_Status populated
    df_post_pose = df_input.copy()
    if 'Pose_Status' not in df_post_pose.columns:
        df_post_pose['Pose_Status'] = "not_started"
    df_post_pose['Pose_Status'] = df_post_pose.apply(
        lambda r: status_reason_map.get(r['File_ID'], r.get('Pose_Status', 'not_started')), axis=1
    )
    df_post_pose.to_csv(POST_POSE_CSV, index=False)
    print(f"Saved post-pose metadata CSV: {POST_POSE_CSV}")

    # Compute rates
    det_rate = (pose_detected_count / N * 100) if N > 0 else 0
    comp_rate = (lower_body_complete_count / N * 100) if N > 0 else 0

    # Output 4: summary text file
    summary_lines = [
        "============================================================",
        "  PHASE 3 -- POSE EXTRACTION SUMMARY (SQUATS)",
        "============================================================",
        "",
        f"  Total curated frames processed: {N}",
        f"  Pose detected                 : {pose_detected_count}",
        f"  Lower body complete           : {lower_body_complete_count}",
        f"  No detection                  : {no_detection_count}",
        f"  Failed load                   : {failed_load_count}",
        f"  File not found                : {file_not_found_count}",
        "",
        f"  Detection rate                : {det_rate:.1f}%",
        f"  Lower-body completeness rate  : {comp_rate:.1f}%",
        "",
        f"  MediaPipe Config:",
        "    Model variant: Heavy (pose_landmarker_heavy.task)",
        "    min_pose_detection_confidence: 0.5",
        "    min_pose_presence_confidence : 0.5",
        "    min_tracking_confidence      : 0.5",
        "    running_mode                 : IMAGE",
        "",
        f"  Failed File_IDs (no_detection/failed_load/file_not_found) ({len(failed_ids)}):"
    ]
    for fid in failed_ids:
        summary_lines.append(f"    - {fid} ({status_reason_map.get(fid)})")
    
    summary_lines.append("")
    summary_lines.append(f"  Lower-body incomplete File_IDs ({len(incomplete_ids)}):")
    for fid in incomplete_ids:
        summary_lines.append(f"    - {fid}")

    summary_lines.append("")
    summary_lines.append("  Most common low-visibility landmarks:")
    sorted_low_vis = sorted(low_visibility_counts.items(), key=lambda item: item[1], reverse=True)
    for lm_name, count in sorted_low_vis:
        summary_lines.append(f"    - {lm_name}: {count} times ({count / N * 100:.1f}%)")

    summary_text = "\n".join(summary_lines)
    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write(summary_text)
    print(f"Saved summary report: {SUMMARY_TXT}")

    # Output 5: Visual skeleton overlays are already written to OVERLAY_DIR

    # Print final summary to terminal
    print("\n--- RUN RESULTS SUMMARY ---")
    print(summary_text)

if __name__ == "__main__":
    main()
