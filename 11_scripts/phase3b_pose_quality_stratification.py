import sys
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    # 1. Load pose data
    project_root = Path(".")
    raw_pose_path = project_root / "4_pose_outputs" / "raw_pose" / "squats_pose_raw.csv"
    frame_status_path = project_root / "4_pose_outputs" / "raw_pose" / "squats_pose_frame_status.csv"

    # Validate that input CSVs exist before processing
    if not raw_pose_path.is_file():
        print(f"Error: Missing input file {raw_pose_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
    if not frame_status_path.is_file():
        print(f"Error: Missing input file {frame_status_path.as_posix()}", file=sys.stderr)
        sys.exit(1)

    # Load with pd.read_csv(..., sep=None, engine='python')
    raw_df = pd.read_csv(raw_pose_path, sep=None, engine='python')
    print(f"Loaded {len(raw_df)} rows from {raw_pose_path.name}")
    
    status_df = pd.read_csv(frame_status_path, sep=None, engine='python')
    print(f"Loaded {len(status_df)} rows from {frame_status_path.name}")

    # Build raw pose lookup mapping: File_ID -> landmark_id -> visibility
    raw_lookup = {}
    for _, row in raw_df.iterrows():
        fid = str(row['File_ID'])
        lid = int(row['landmark_id'])
        vis = float(row['visibility'])
        if fid not in raw_lookup:
            raw_lookup[fid] = {}
        raw_lookup[fid][lid] = vis

    # Process all frames from status_df
    records = []
    low_vis_counts = {
        'left_hip': 0,
        'right_hip': 0,
        'left_knee': 0,
        'right_knee': 0,
        'left_ankle': 0,
        'right_ankle': 0
    }

    landmark_mapping = [
        (23, 'left_hip'),
        (24, 'right_hip'),
        (25, 'left_knee'),
        (26, 'right_knee'),
        (27, 'left_ankle'),
        (28, 'right_ankle')
    ]

    for _, row in status_df.iterrows():
        fid = str(row['File_ID'])
        sub_id = int(row['Subject_ID'])
        exc = str(row['Exercise'])
        
        # Handle pose_detected defensively
        pd_val = row['pose_detected']
        if isinstance(pd_val, str):
            pose_detected = pd_val.strip().lower() == 'true'
        else:
            pose_detected = bool(pd_val)

        # Retrieve visibility for the six landmarks of interest
        vis_dict = {}
        if pose_detected and fid in raw_lookup:
            for lid, _ in landmark_mapping:
                vis_dict[lid] = raw_lookup[fid].get(lid, 0.0)
        else:
            pose_detected = False
            for lid, _ in landmark_mapping:
                vis_dict[lid] = 0.0

        # Visibility status (threshold >= 0.5)
        left_hip_ok = vis_dict[23] >= 0.5
        right_hip_ok = vis_dict[24] >= 0.5
        left_knee_ok = vis_dict[25] >= 0.5
        right_knee_ok = vis_dict[26] >= 0.5
        left_ankle_ok = vis_dict[27] >= 0.5
        right_ankle_ok = vis_dict[28] >= 0.5

        left_chain_complete = left_hip_ok and left_knee_ok and left_ankle_ok
        right_chain_complete = right_hip_ok and right_knee_ok and right_ankle_ok
        bilateral_lower_body_complete = left_chain_complete and right_chain_complete
        partial_unilateral_usable = left_chain_complete or right_chain_complete

        # Assign each frame to one analysis tier
        if not pose_detected:
            tier = "Rejected_Tier"
        elif bilateral_lower_body_complete:
            tier = "Gold_Tier"
        elif partial_unilateral_usable:
            tier = "Unilateral_Tier"
        else:
            tier = "Rejected_Tier"

        # Count and list low-visibility landmarks
        num_low_vis = 0
        low_vis_names = []
        for lid, name in landmark_mapping:
            if vis_dict[lid] < 0.5:
                num_low_vis += 1
                low_vis_counts[name] += 1
                if pose_detected:
                    low_vis_names.append(name)

        low_vis_str = ";".join(low_vis_names) if pose_detected else ""

        records.append({
            'File_ID': fid,
            'Subject_ID': sub_id,
            'Exercise': exc,
            'pose_detected': pose_detected,
            'left_chain_complete': left_chain_complete,
            'right_chain_complete': right_chain_complete,
            'bilateral_lower_body_complete': bilateral_lower_body_complete,
            'partial_unilateral_usable': partial_unilateral_usable,
            'analysis_tier': tier,
            'num_low_visibility_lower_body_landmarks': num_low_vis,
            'low_visibility_landmarks': low_vis_str
        })

    # Prepare DataFrame
    output_df = pd.DataFrame(records)

    # Cast data types explicitly before writing
    output_df['File_ID'] = output_df['File_ID'].astype(str)
    output_df['Subject_ID'] = output_df['Subject_ID'].astype(int)
    output_df['Exercise'] = output_df['Exercise'].astype(str)
    output_df['pose_detected'] = output_df['pose_detected'].astype(bool)
    output_df['left_chain_complete'] = output_df['left_chain_complete'].astype(bool)
    output_df['right_chain_complete'] = output_df['right_chain_complete'].astype(bool)
    output_df['bilateral_lower_body_complete'] = output_df['bilateral_lower_body_complete'].astype(bool)
    output_df['partial_unilateral_usable'] = output_df['partial_unilateral_usable'].astype(bool)
    output_df['analysis_tier'] = output_df['analysis_tier'].astype(str)
    output_df['num_low_visibility_lower_body_landmarks'] = output_df['num_low_visibility_lower_body_landmarks'].astype(int)
    output_df['low_visibility_landmarks'] = output_df['low_visibility_landmarks'].astype(str)

    # 7. Pre-write sanity checkpoint
    N = len(output_df)
    X = int((output_df['analysis_tier'] == 'Gold_Tier').sum())
    Y = int((output_df['analysis_tier'] == 'Unilateral_Tier').sum())
    Z = int((output_df['analysis_tier'] == 'Rejected_Tier').sum())

    print()
    print(f"Total frames analysed     : {N}")
    print(f"Gold_Tier count           : {X}")
    print(f"Unilateral_Tier count     : {Y}")
    print(f"Rejected_Tier count       : {Z}")
    print(f"Sanity check              : {X} + {Y} + {Z} should equal {N}")
    
    if X + Y + Z != N:
        print("Error: Sanity check FAILED! The sum of the tiers does not equal the total frames.", file=sys.stderr)
        sys.exit(1)
    
    print("Sanity check passed. Proceeding to save output files...")

    # 8. Save output CSV
    # Ensure correct column order
    cols_order = [
        'File_ID',
        'Subject_ID',
        'Exercise',
        'pose_detected',
        'left_chain_complete',
        'right_chain_complete',
        'bilateral_lower_body_complete',
        'partial_unilateral_usable',
        'analysis_tier',
        'num_low_visibility_lower_body_landmarks',
        'low_visibility_landmarks'
    ]
    output_df = output_df[cols_order]
    
    output_csv_path = project_root / "4_pose_outputs" / "raw_pose" / "squats_pose_quality_tiers.csv"
    output_df.to_csv(output_csv_path, index=False)
    print(f"Saved tiers CSV to {output_csv_path.as_posix()}")

    # 9. Create summary report
    pose_detected_count = int(output_df['pose_detected'].sum())
    pose_detected_pct = (pose_detected_count / N) * 100
    
    gold_pct = (X / N) * 100
    unilateral_pct = (Y / N) * 100
    rejected_pct = (Z / N) * 100

    missing_0 = int((output_df['num_low_visibility_lower_body_landmarks'] == 0).sum())
    missing_1 = int((output_df['num_low_visibility_lower_body_landmarks'] == 1).sum())
    missing_2 = int((output_df['num_low_visibility_lower_body_landmarks'] == 2).sum())
    missing_3_or_more = int((output_df['num_low_visibility_lower_body_landmarks'] >= 3).sum())

    # Median and max within the Unilateral_Tier subset only
    unilateral_subset = output_df[output_df['analysis_tier'] == 'Unilateral_Tier']
    if not unilateral_subset.empty:
        unilateral_median = float(unilateral_subset['num_low_visibility_lower_body_landmarks'].median())
        unilateral_max = int(unilateral_subset['num_low_visibility_lower_body_landmarks'].max())
    else:
        unilateral_median = 0.0
        unilateral_max = 0

    summary_content = f"""Pose Quality Stratification Run Summary
=======================================
Total frames analysed: {N}

Tiers Breakdown:
  Gold_Tier       : {X} ({gold_pct:.2f}%)
  Unilateral_Tier : {Y} ({unilateral_pct:.2f}%)
  Rejected_Tier   : {Z} ({rejected_pct:.2f}%)

Pose Detection:
  Detected: {pose_detected_count} ({pose_detected_pct:.2f}%)
  Not Detected: {N - pose_detected_count} ({100 - pose_detected_pct:.2f}%)

Low-Visibility Landmarks Count distribution:
  Missing 0 landmarks: {missing_0}
  Missing 1 landmark : {missing_1}
  Missing 2 landmarks: {missing_2}
  Missing 3 or more landmarks: {missing_3_or_more}

Unilateral_Tier Diagnostic Metrics:
  Median low-visibility lower-body landmarks: {unilateral_median:.1f}
  Max low-visibility lower-body landmarks: {unilateral_max}

Per-Landmark Low-Visibility Occurrences (out of {N} frames):
  left_hip    : {low_vis_counts['left_hip']}
  right_hip   : {low_vis_counts['right_hip']}
  left_knee   : {low_vis_counts['left_knee']}
  right_knee  : {low_vis_counts['right_knee']}
  left_ankle  : {low_vis_counts['left_ankle']}
  right_ankle : {low_vis_counts['right_ankle']}
"""
    
    summary_path = project_root / "4_pose_outputs" / "phase3b_pose_quality_stratification_summary.txt"
    summary_path.write_text(summary_content, encoding='utf-8')
    print(f"Saved run summary to {summary_path.as_posix()}")

    # 10. Create methods note
    methods_content = f"""# Pose Quality Stratification Methods Note

Pose quality was stratified into three analysis tiers. Gold Tier frames contained complete bilateral hip-knee-ankle chains and were considered suitable for bilateral lower-body biomechanical analysis. Unilateral Tier frames contained at least one complete hip-knee-ankle chain and were considered suitable for visible-side single-limb analysis. Rejected Tier frames lacked a complete unilateral lower-body chain or had no pose detection and were excluded from Phase 4 biomechanical feature extraction.

## Caveat
MediaPipe's `visibility` attribute is a model-internal confidence score, not a ground-truth measure of anatomical landmark accuracy. Therefore, high visibility does not guarantee perfect landmark localisation.
"""
    
    methods_path = project_root / "4_pose_outputs" / "phase3b_methods_note.md"
    methods_path.write_text(methods_content, encoding='utf-8')
    print(f"Saved methods note to {methods_path.as_posix()}")

    # 11. Print final summary to stdout
    proceed_status = "Yes" if (X + Y) >= 30 else "No"
    print()
    print(f"Total frames        : {N}")
    print(f"Gold_Tier           : {X}")
    print(f"Unilateral_Tier     : {Y}")
    print(f"Rejected_Tier       : {Z}")
    print(f"Phase 4 can proceed : {proceed_status}")

if __name__ == '__main__':
    main()
