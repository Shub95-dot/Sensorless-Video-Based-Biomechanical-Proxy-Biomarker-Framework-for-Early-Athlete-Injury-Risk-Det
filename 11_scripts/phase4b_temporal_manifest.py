import sys
import re
from pathlib import Path
import pandas as pd
import numpy as np

def main():
    project_root = Path(".")
    metadata_dir = project_root / "3_metadata"
    review_path = metadata_dir / "squat_quality_review.csv"
    post_pose_path = metadata_dir / "squat_quality_review_post_pose.csv"

    # Step 1 — Load camera-view source
    source_file = None
    df = None
    
    # Try squat_quality_review.csv first
    if review_path.is_file():
        try:
            temp_df = pd.read_csv(review_path, sep=None, engine='python')
            print(f"Loaded {len(temp_df)} rows from {review_path.name}")
            # Validate columns
            if 'Camera_View' in temp_df.columns:
                temp_df['Camera_View_norm'] = temp_df['Camera_View'].astype(str).str.strip().str.lower()
                sagittal_count = (temp_df['Camera_View_norm'] == 'sagittal').sum()
                if sagittal_count > 0:
                    source_file = review_path
                    df = temp_df
        except Exception as e:
            print(f"Warning: Could not process {review_path.name} due to {e}")

    # Failover to squat_quality_review_post_pose.csv if N = 0
    if source_file is None and post_pose_path.is_file():
        try:
            temp_df = pd.read_csv(post_pose_path, sep=None, engine='python')
            print(f"Loaded {len(temp_df)} rows from {post_pose_path.name}")
            if 'Camera_View' in temp_df.columns:
                temp_df['Camera_View_norm'] = temp_df['Camera_View'].astype(str).str.strip().str.lower()
                sagittal_count = (temp_df['Camera_View_norm'] == 'sagittal').sum()
                if sagittal_count > 0:
                    print(f"Failover successful: Using {post_pose_path.name} as camera-view source (found {sagittal_count} sagittal subjects).")
                    source_file = post_pose_path
                    df = temp_df
        except Exception as e:
            print(f"Warning: Could not process {post_pose_path.name} due to {e}")

    if df is None:
        print("Error: Could not locate a valid camera-view source file with 'Camera_View' column.", file=sys.stderr)
        sys.exit(1)

    # Validate or derive Subject_ID
    if 'Subject_ID' not in df.columns:
        if 'File_ID' in df.columns:
            # Derive Subject_ID from File_ID pattern: SQ_{Subject_ID}_{SEQ}
            def derive_subject(fid):
                match = re.search(r'SQ_(\d+)_\d+', str(fid))
                return int(match.group(1)) if match else np.nan
            df['Subject_ID'] = df['File_ID'].apply(derive_subject)
        else:
            print("Error: Metadata file must contain Subject_ID or File_ID column.", file=sys.stderr)
            sys.exit(1)

    # Filter for normalized Camera_View == "sagittal"
    sagittal_df = df[df['Camera_View_norm'] == 'sagittal'].copy()
    N = len(sagittal_df)

    if N == 0:
        print("Error: Found 0 sagittal subjects.", file=sys.stderr)
        # Stop and report the available Camera_View values
        if 'Camera_View' in df.columns:
            print("Available Camera_View values in source file:")
            print(df['Camera_View'].value_counts())
        sys.exit(1)

    # Create a unique sorted list of sagittal Subject_IDs
    sagittal_subject_ids = sorted(list(sagittal_df['Subject_ID'].dropna().unique().astype(int)))
    print()
    print(f"Found {len(sagittal_subject_ids)} sagittal subjects:")
    print(sagittal_subject_ids)

    # Step 2 — Locate raw frames parent folder
    primary_parent = project_root / "1_raw_datasets" / "Dataset" / "Squats Frames"
    resolved_parent = None

    if primary_parent.is_dir() and any(primary_parent.glob("*")):
        resolved_parent = primary_parent
    else:
        # Fallbacks
        fallbacks = [
            project_root / "1_raw_datasets" / "Dataset" / "squats",
            project_root / "1_raw_datasets" / "Dataset" / "Squats",
        ]
        for fb in fallbacks:
            if fb.is_dir():
                resolved_parent = fb
                break
        
        if resolved_parent is None:
            # Search for direct subfolders starting with "squat"
            dataset_dir = project_root / "1_raw_datasets" / "Dataset"
            if dataset_dir.is_dir():
                for sub in dataset_dir.iterdir():
                    if sub.is_dir() and sub.name.lower().startswith("squat"):
                        resolved_parent = sub
                        break

    if resolved_parent is None:
        print("Error: Could not resolve raw frames parent folder containing subject folders.", file=sys.stderr)
        sys.exit(1)

    print(f"Resolved raw frames parent path: {resolved_parent.as_posix()}")

    # Step 3 — Discover and numerically sort frames per subject
    manifest_rows = []
    subject_summary_rows = []
    folder_missing_subjects = []
    unparseable_filenames = []
    per_subject_counts = {}

    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

    for sub_id in sagittal_subject_ids:
        subject_dir = resolved_parent / str(sub_id)
        if not subject_dir.is_dir():
            print(f"Warning: Subject folder missing for ID {sub_id} at {subject_dir.as_posix()}")
            folder_missing_subjects.append(sub_id)
            subject_summary_rows.append({
                'Subject_ID': sub_id,
                'Camera_View': 'sagittal',
                'Analysis_Group': 'primary_sagittal_knee_angle',
                'num_frames': 0,
                'first_frame_number': '',
                'last_frame_number': '',
                'has_temporal_sequence': 'no'
            })
            continue

        # List all image files
        image_files = []
        for file in subject_dir.iterdir():
            if file.is_file() and file.suffix.lower() in valid_extensions:
                image_files.append(file)

        subject_frames = []
        for file in image_files:
            stem = file.stem
            # Extract the LAST run of digits from the stem
            digit_runs = re.findall(r'\d+', stem)
            if digit_runs:
                frame_num = int(digit_runs[-1])
            else:
                frame_num = None
                unparseable_filenames.append(file.name)
                print(f"Warning: Unparseable frame name '{file.name}' in subject {sub_id}")

            subject_frames.append((frame_num, file.name, file))

        # Sort frames: numeric frame_number ascending, unparseable (None) sorted at the end
        # We sort using a tuple: (is_none, frame_num_value, filename)
        def get_sort_key(item):
            f_num, f_name, _ = item
            is_none = f_num is None
            val = f_num if not is_none else 0
            return (is_none, val, f_name)

        subject_frames.sort(key=get_sort_key)

        # Assign frame_index and append to manifest
        num_frames = len(subject_frames)
        per_subject_counts[sub_id] = num_frames
        
        first_frame_num = ""
        last_frame_num = ""

        if num_frames > 0:
            if subject_frames[0][0] is not None:
                first_frame_num = int(subject_frames[0][0])
            if subject_frames[-1][0] is not None:
                last_frame_num = int(subject_frames[-1][0])

        for idx, (f_num, f_name, f_path) in enumerate(subject_frames):
            # frame_path relative to project root with forward slashes
            rel_path = f_path.relative_to(project_root).as_posix()
            
            manifest_rows.append({
                'Subject_ID': sub_id,
                'Camera_View': 'sagittal',
                'Analysis_Group': 'primary_sagittal_knee_angle',
                'frame_index': idx,
                'frame_number': '' if f_num is None else f_num,
                'frame_filename': f_name,
                'frame_path': rel_path
            })

        # Append to subject summary
        has_temporal = 'yes' if num_frames >= 30 else 'no'
        subject_summary_rows.append({
            'Subject_ID': sub_id,
            'Camera_View': 'sagittal',
            'Analysis_Group': 'primary_sagittal_knee_angle',
            'num_frames': num_frames,
            'first_frame_number': first_frame_num,
            'last_frame_number': last_frame_num,
            'has_temporal_sequence': has_temporal
        })

    # Step 4 — Write manifest
    manifest_df = pd.DataFrame(manifest_rows)
    # Ensure exact column order and correct grouping/sorting
    if not manifest_df.empty:
        manifest_df['Subject_ID'] = manifest_df['Subject_ID'].astype(int)
        manifest_df['frame_index'] = manifest_df['frame_index'].astype(int)
        
        # Sort and group
        manifest_df = manifest_df.sort_values(by=['Subject_ID', 'frame_index'])
        manifest_cols = [
            'Subject_ID', 'Camera_View', 'Analysis_Group', 
            'frame_index', 'frame_number', 'frame_filename', 'frame_path'
        ]
        manifest_df = manifest_df[manifest_cols]
    
    manifest_csv_path = metadata_dir / "squats_temporal_manifest.csv"
    manifest_df.to_csv(manifest_csv_path, index=False)
    print(f"Saved temporal manifest to {manifest_csv_path.as_posix()}")

    # Step 5 — Verification sample (first 3 sagittal subjects)
    print()
    print("--- Verification Sample (First 3 sagittal subjects) ---")
    active_subjects_with_frames = [sub_id for sub_id in sagittal_subject_ids if sub_id not in folder_missing_subjects]
    first_3_subjects = active_subjects_with_frames[:3]

    for sub_id in first_3_subjects:
        sub_manifest = manifest_df[manifest_df['Subject_ID'] == sub_id]
        total_frames = len(sub_manifest)
        print(f"\nSubject_ID: {sub_id}")
        print(f"Total frames found: {total_frames}")
        
        print("First 5 frames:")
        for _, row in sub_manifest.head(5).iterrows():
            print(f"  frame_index: {row['frame_index']}, frame_number: {row['frame_number']}, frame_filename: {row['frame_filename']}")
            
        print("Last 5 frames:")
        for _, row in sub_manifest.tail(5).iterrows():
            print(f"  frame_index: {row['frame_index']}, frame_number: {row['frame_number']}, frame_filename: {row['frame_filename']}")

    # Step 6 — Write subject summary
    subject_summary_df = pd.DataFrame(subject_summary_rows)
    if not subject_summary_df.empty:
        subject_summary_df['Subject_ID'] = subject_summary_df['Subject_ID'].astype(int)
        subject_summary_df['num_frames'] = subject_summary_df['num_frames'].astype(int)
        subject_summary_df = subject_summary_df.sort_values(by='Subject_ID')
        
        summary_cols = [
            'Subject_ID', 'Camera_View', 'Analysis_Group', 
            'num_frames', 'first_frame_number', 'last_frame_number', 'has_temporal_sequence'
        ]
        subject_summary_df = subject_summary_df[summary_cols]
        
    subject_summary_csv_path = metadata_dir / "squats_temporal_subject_summary.csv"
    subject_summary_df.to_csv(subject_summary_csv_path, index=False)
    print(f"Saved temporal subject summary to {subject_summary_csv_path.as_posix()}")

    # Step 7 — Write summary report
    num_with_folders = len(sagittal_subject_ids) - len(folder_missing_subjects)
    total_frames_manifest = len(manifest_df)
    
    frame_counts = list(per_subject_counts.values())
    if frame_counts:
        min_frames = min(frame_counts)
        max_frames = max(frame_counts)
        mean_frames = np.mean(frame_counts)
        median_frames = np.median(frame_counts)
    else:
        min_frames = max_frames = mean_frames = median_frames = 0.0

    summary_report_content = f"""Squats Temporal Manifest Run Summary
======================================
Camera-view source file used       : {source_file.relative_to(project_root).as_posix()}
Resolved raw frames parent folder  : {resolved_parent.relative_to(project_root).as_posix()}
Number of sagittal subjects found  : {len(sagittal_subject_ids)}
List of sagittal Subject_IDs       : {sagittal_subject_ids}
Number of subjects with folders    : {num_with_folders}
Total frames across subjects       : {total_frames_manifest}

Per-Subject Frame Counts:
"""
    for sub_id in sagittal_subject_ids:
        cnt = per_subject_counts.get(sub_id, 0)
        summary_report_content += f"  Subject {sub_id}: {cnt} frames\n"

    summary_report_content += f"""
Frame Count Statistics:
  Min frames per subject           : {min_frames}
  Max frames per subject           : {max_frames}
  Mean frames per subject          : {mean_frames:.2f}
  Median frames per subject        : {median_frames:.1f}

Folder-missing subjects            : {folder_missing_subjects}
Unparseable filenames              : {unparseable_filenames}
"""

    summary_report_path = metadata_dir / "squats_temporal_manifest_summary.txt"
    summary_report_path.write_text(summary_report_content, encoding='utf-8')
    print(f"Saved summary report to {summary_report_path.as_posix()}")

    # Step 8 — Print final summary
    print()
    print(f"Sagittal subjects        : {len(sagittal_subject_ids)}")
    print(f"Subjects with folders    : {num_with_folders}")
    print(f"Total frames in manifest : {total_frames_manifest}")
    print(f"Mean frames per subject  : {mean_frames:.2f}")
    print(f"Unparseable filenames    : {len(unparseable_filenames)}")
    print(f"Folder-missing subjects  : {len(folder_missing_subjects)}")
    print()
    print("VERIFY the first-5/last-5 sample above before proceeding to temporal pose extraction.")

if __name__ == '__main__':
    main()
