import sys
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    # 1. Load pose raw and tier CSVs
    project_root = Path(".")
    raw_pose_path = project_root / "4_pose_outputs" / "raw_pose" / "squats_pose_raw.csv"
    tiers_path = project_root / "4_pose_outputs" / "raw_pose" / "squats_pose_quality_tiers.csv"

    # Validate that input CSVs exist before processing
    if not raw_pose_path.is_file():
        print(f"Error: Missing input file {raw_pose_path.as_posix()}", file=sys.stderr)
        sys.exit(1)
    if not tiers_path.is_file():
        print(f"Error: Missing input file {tiers_path.as_posix()}", file=sys.stderr)
        sys.exit(1)

    # Load with pd.read_csv(..., sep=None, engine='python')
    raw_df = pd.read_csv(raw_pose_path, sep=None, engine='python')
    print(f"Loaded {len(raw_df)} rows from {raw_pose_path.name}")
    
    tiers_df = pd.read_csv(tiers_path, sep=None, engine='python')
    print(f"Loaded {len(tiers_df)} rows from {tiers_path.name}")

    # Build raw landmark coordinates and visibility lookup: File_ID -> landmark_id -> (x, y, visibility)
    raw_lookup = {}
    for _, row in raw_df.iterrows():
        fid = str(row['File_ID'])
        lid = int(row['landmark_id'])
        x = float(row['x'])
        y = float(row['y'])
        vis = float(row['visibility'])
        if fid not in raw_lookup:
            raw_lookup[fid] = {}
        raw_lookup[fid][lid] = {
            'x': x,
            'y': y,
            'vis': vis
        }

    # Prepare records for main and diagnostics CSVs
    main_records = []
    diag_records = []

    # Count variables for sanity checkpoints
    C = 0
    C_left = 0
    C_right = 0
    S_lv = 0
    S_rt = 0
    S_fm = 0
    O = 0

    # Landmark mapping per side
    sides_config = {
        'left': {
            'hip': 23, 'knee': 25, 'ankle': 27,
            'names': ['left_hip', 'left_knee', 'left_ankle']
        },
        'right': {
            'hip': 24, 'knee': 26, 'ankle': 28,
            'names': ['right_hip', 'right_knee', 'right_ankle']
        }
    }

    # Process each frame in the quality tiers CSV
    for _, row in tiers_df.iterrows():
        fid = str(row['File_ID'])
        sub_id = int(row['Subject_ID'])
        exc = str(row['Exercise'])
        tier = str(row['analysis_tier'])

        # For Rejected_Tier, skip computation entirely and log as skipped_rejected_tier
        if tier == 'Rejected_Tier':
            for side in ['left', 'right']:
                diag_records.append({
                    'File_ID': fid,
                    'Subject_ID': sub_id,
                    'Exercise': exc,
                    'analysis_tier': tier,
                    'side': side,
                    'angle_status': 'skipped_rejected_tier',
                    'reason': 'skipped_rejected_tier'
                })
                S_rt += 1
            continue

        # For Gold_Tier and Unilateral_Tier
        for side, cfg in sides_config.items():
            hip_id = cfg['hip']
            knee_id = cfg['knee']
            ankle_id = cfg['ankle']
            hip_name, knee_name, ankle_name = cfg['names']

            # Check if coordinates are present for this File_ID in raw pose
            has_landmarks = (fid in raw_lookup and 
                             hip_id in raw_lookup[fid] and 
                             knee_id in raw_lookup[fid] and 
                             ankle_id in raw_lookup[fid])

            if has_landmarks:
                h_data = raw_lookup[fid][hip_id]
                k_data = raw_lookup[fid][knee_id]
                a_data = raw_lookup[fid][ankle_id]

                h_x, h_y, h_vis = h_data['x'], h_data['y'], h_data['vis']
                k_x, k_y, k_vis = k_data['x'], k_data['y'], k_data['vis']
                a_x, a_y, a_vis = a_data['x'], a_data['y'], a_data['vis']
            else:
                h_x = h_y = h_vis = 0.0
                k_x = k_y = k_vis = 0.0
                a_x = a_y = a_vis = 0.0

            # Visibility threshold: visibility >= 0.5
            low_vis_landmarks = []
            if h_vis < 0.5:
                low_vis_landmarks.append(hip_name)
            if k_vis < 0.5:
                low_vis_landmarks.append(knee_name)
            if a_vis < 0.5:
                low_vis_landmarks.append(ankle_name)

            if len(low_vis_landmarks) > 0:
                reason = "low_visibility: " + ";".join(low_vis_landmarks)
                diag_records.append({
                    'File_ID': fid,
                    'Subject_ID': sub_id,
                    'Exercise': exc,
                    'analysis_tier': tier,
                    'side': side,
                    'angle_status': 'skipped_low_visibility',
                    'reason': reason
                })
                S_lv += 1
            else:
                # Math extraction
                # Coordinates
                H = np.array([h_x, h_y])
                K = np.array([k_x, k_y])
                A = np.array([a_x, a_y])

                v1 = H - K
                v2 = A - K

                norm1 = np.linalg.norm(v1)
                norm2 = np.linalg.norm(v2)

                if norm1 == 0.0 or norm2 == 0.0:
                    # Degenerate geometry
                    main_records.append({
                        'File_ID': fid,
                        'Subject_ID': sub_id,
                        'Exercise': exc,
                        'analysis_tier': tier,
                        'side': side,
                        'hip_x': h_x,
                        'hip_y': h_y,
                        'knee_x': k_x,
                        'knee_y': k_y,
                        'ankle_x': a_x,
                        'ankle_y': a_y,
                        'hip_visibility': h_vis,
                        'knee_visibility': k_vis,
                        'ankle_visibility': a_vis,
                        'knee_angle_deg': np.nan,
                        'angle_status': 'failed_math'
                    })
                    diag_records.append({
                        'File_ID': fid,
                        'Subject_ID': sub_id,
                        'Exercise': exc,
                        'analysis_tier': tier,
                        'side': side,
                        'angle_status': 'failed_math',
                        'reason': 'degenerate_landmark_geometry'
                    })
                    S_fm += 1
                else:
                    dot_prod = np.dot(v1, v2)
                    cos_theta = dot_prod / (norm1 * norm2)
                    cos_theta_clipped = np.clip(cos_theta, -1.0, 1.0)
                    theta_rad = np.arccos(cos_theta_clipped)
                    theta_deg = float(np.degrees(theta_rad))
                    theta_deg_rounded = round(theta_deg, 4)

                    # Outlier classification: plausible range is 40 <= angle <= 185
                    is_outlier = (theta_deg_rounded < 40.0 or theta_deg_rounded > 185.0)

                    main_records.append({
                        'File_ID': fid,
                        'Subject_ID': sub_id,
                        'Exercise': exc,
                        'analysis_tier': tier,
                        'side': side,
                        'hip_x': h_x,
                        'hip_y': h_y,
                        'knee_x': k_x,
                        'knee_y': k_y,
                        'ankle_x': a_x,
                        'ankle_y': a_y,
                        'hip_visibility': h_vis,
                        'knee_visibility': k_vis,
                        'ankle_visibility': a_vis,
                        'knee_angle_deg': theta_deg_rounded,
                        'angle_status': 'computed'
                    })

                    C += 1
                    if side == 'left':
                        C_left += 1
                    else:
                        C_right += 1

                    if is_outlier:
                        reason = f"below_40_deg ({theta_deg_rounded:.2f}°)" if theta_deg_rounded < 40.0 else f"above_185_deg ({theta_deg_rounded:.2f}°)"
                        diag_records.append({
                            'File_ID': fid,
                            'Subject_ID': sub_id,
                            'Exercise': exc,
                            'analysis_tier': tier,
                            'side': side,
                            'angle_status': 'possible_outlier',
                            'reason': reason
                        })
                        O += 1

    # Convert lists to DataFrames
    main_df = pd.DataFrame(main_records)
    diag_df = pd.DataFrame(diag_records)

    # 7. Pre-write sanity checkpoint
    N = len(tiers_df)
    G = int((tiers_df['analysis_tier'] == 'Gold_Tier').sum())
    U = int((tiers_df['analysis_tier'] == 'Unilateral_Tier').sum())
    R = int((tiers_df['analysis_tier'] == 'Rejected_Tier').sum())
    S = S_lv + S_rt + S_fm

    print()
    print(f"Total frames in tier CSV     : {N}")
    print(f"  Gold_Tier                  : {G}")
    print(f"  Unilateral_Tier            : {U}")
    print(f"  Rejected_Tier              : {R}")
    print(f"Computed angle rows          : {C}")
    print(f"  left side                  : {C_left}")
    print(f"  right side                 : {C_right}")
    print(f"Skipped rows                 : {S}")
    print(f"  low_visibility             : {S_lv}")
    print(f"  rejected_tier              : {S_rt}")
    print(f"  failed_math                : {S_fm}")
    print(f"Possible outliers            : {O}")

    # Check assertions strictly
    sanity_failed = False
    if G + U + R != N:
        print(f"Sanity Check FAILED: Gold_Tier({G}) + Unilateral_Tier({U}) + Rejected_Tier({R}) != Total({N})", file=sys.stderr)
        sanity_failed = True
    if C + S_lv + S_rt + S_fm != 2 * N:
        print(f"Sanity Check FAILED: Computed({C}) + low_vis({S_lv}) + rejected({S_rt}) + failed_math({S_fm}) != 2 * Total({2 * N})", file=sys.stderr)
        sanity_failed = True
    if C_left + C_right != C:
        print(f"Sanity Check FAILED: C_left({C_left}) + C_right({C_right}) != Computed({C})", file=sys.stderr)
        sanity_failed = True

    if sanity_failed:
        sys.exit("Error: Sanity checks failed. Aborting file creation.")
    
    print("Sanity checks passed successfully. Writing output files...")

    # Define paths
    output_dir = project_root / "5_biomarkers" / "knee_angle"
    output_dir.mkdir(parents=True, exist_ok=True)

    main_csv_path = output_dir / "squats_knee_angle.csv"
    diag_csv_path = output_dir / "squats_knee_angle_diagnostics.csv"
    summary_path = output_dir / "phase4a_knee_angle_summary.txt"
    methods_path = output_dir / "phase4a_methods_note.md"

    # Save Main CSV with defensive typing
    if not main_df.empty:
        main_df['File_ID'] = main_df['File_ID'].astype(str)
        main_df['Subject_ID'] = main_df['Subject_ID'].astype(int)
        main_df['Exercise'] = main_df['Exercise'].astype(str)
        main_df['analysis_tier'] = main_df['analysis_tier'].astype(str)
        main_df['side'] = main_df['side'].astype(str)
        main_df['hip_x'] = main_df['hip_x'].astype(float)
        main_df['hip_y'] = main_df['hip_y'].astype(float)
        main_df['knee_x'] = main_df['knee_x'].astype(float)
        main_df['knee_y'] = main_df['knee_y'].astype(float)
        main_df['ankle_x'] = main_df['ankle_x'].astype(float)
        main_df['ankle_y'] = main_df['ankle_y'].astype(float)
        main_df['hip_visibility'] = main_df['hip_visibility'].astype(float)
        main_df['knee_visibility'] = main_df['knee_visibility'].astype(float)
        main_df['ankle_visibility'] = main_df['ankle_visibility'].astype(float)
        main_df['knee_angle_deg'] = main_df['knee_angle_deg'].astype(float)
        main_df['angle_status'] = main_df['angle_status'].astype(str)

        # Force exact column order
        main_cols = [
            'File_ID', 'Subject_ID', 'Exercise', 'analysis_tier', 'side',
            'hip_x', 'hip_y', 'knee_x', 'knee_y', 'ankle_x', 'ankle_y',
            'hip_visibility', 'knee_visibility', 'ankle_visibility',
            'knee_angle_deg', 'angle_status'
        ]
        main_df = main_df[main_cols]
    main_df.to_csv(main_csv_path, index=False)
    print(f"Saved main CSV to {main_csv_path.as_posix()}")

    # Save Diagnostics CSV with exact column order
    if not diag_df.empty:
        diag_df['File_ID'] = diag_df['File_ID'].astype(str)
        diag_df['Subject_ID'] = diag_df['Subject_ID'].astype(int)
        diag_df['Exercise'] = diag_df['Exercise'].astype(str)
        diag_df['analysis_tier'] = diag_df['analysis_tier'].astype(str)
        diag_df['side'] = diag_df['side'].astype(str)
        diag_df['angle_status'] = diag_df['angle_status'].astype(str)
        diag_df['reason'] = diag_df['reason'].astype(str)

        diag_cols = [
            'File_ID', 'Subject_ID', 'Exercise', 'analysis_tier',
            'side', 'angle_status', 'reason'
        ]
        diag_df = diag_df[diag_cols]
    diag_df.to_csv(diag_csv_path, index=False)
    print(f"Saved diagnostics CSV to {diag_csv_path.as_posix()}")

    # Calculate statistics for computed angles
    computed_angles = main_df[main_df['angle_status'] == 'computed']['knee_angle_deg'].tolist()
    if computed_angles:
        angle_min = min(computed_angles)
        angle_max = max(computed_angles)
        angle_mean = np.mean(computed_angles)
        angle_median = np.median(computed_angles)
        angle_std = np.std(computed_angles, ddof=1) if len(computed_angles) > 1 else 0.0
    else:
        angle_min = angle_max = angle_mean = angle_median = angle_std = 0.0

    # Save Summary Report
    summary_content = f"""Phase 4A Knee Angle Extraction Summary
======================================
Total frames in quality tier file   : {N}
  Gold_Tier                         : {G}
  Unilateral_Tier                   : {U}
  Rejected_Tier                     : {R}

Computed knee angle rows            : {C}
  Left knee angles computed         : {C_left}
  Right knee angles computed        : {C_right}

Skipped rows breakdown:
  skipped_low_visibility            : {S_lv}
  skipped_rejected_tier             : {S_rt}
  failed_math                       : {S_fm}

Knee Angle Statistics (Computed only):
  Min angle                         : {angle_min:.4f}°
  Max angle                         : {angle_max:.4f}°
  Mean angle                        : {angle_mean:.4f}°
  Median angle                      : {angle_median:.4f}°
  Standard Deviation                : {angle_std:.4f}°

Outliers classification:
  Plausible range                   : 40° to 185°
  Possible outlier count            : {O}
"""
    summary_path.write_text(summary_content, encoding='utf-8')
    print(f"Saved summary report to {summary_path.as_posix()}")

    # Save Methods Note
    methods_content = """# Phase 4A Knee Angle Extraction Methods Note

Knee angle was computed using 2D **normalized** MediaPipe hip-knee-ankle coordinates. This is an apparent **2D inter-segmental knee angle** derived from the sagittal-plane projection visible in each frame. It is **not** a clinical 3D knee flexion-extension measure. It is **not** knee valgus. 

The angle is computed as an **unsigned inter-segmental angle** (via `arccos` of the normalized dot product) and is therefore invariant to MediaPipe's image-space y-axis orientation. 

- **Gold_Tier** frames support bilateral knee angle computation.
- **Unilateral_Tier** frames support visible-side knee angle computation.
- **Rejected_Tier** frames were excluded from calculation.

## Plausible Range and Outlier Policy
Plausible range used for outlier flagging was 40°–185° (rationale: standing extension approaches ~180°, deep squat flexion rarely below ~40°; values outside this range likely reflect landmark localisation error rather than true anatomy). Outlier flags are informational, not rejections — outlier rows remain in the main CSV with `angle_status = computed`.
"""
    methods_path.write_text(methods_content, encoding='utf-8')
    print(f"Saved methods note to {methods_path.as_posix()}")

    # Print final stdout summary
    frames_contributing = len(set(main_df[main_df['angle_status'] == 'computed']['File_ID']))
    pass_status = "Yes" if C >= 50 else "No"
    
    print()
    print(f"Computed knee angle rows           : {C}")
    print(f"Frames contributing >=1 angle      : {frames_contributing}")
    print(f"Mean knee angle (degrees)          : {angle_mean:.4f}")
    print(f"Possible outlier count             : {O}")
    print(f"Phase 4A passed                    : {pass_status}")

if __name__ == '__main__':
    main()
