import os
import cv2
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path("1_raw_datasets/OpenCap/LabValidation_withVideos")
OUT_DIR = Path("16_opencap_dropjump_outputs/metadata")
STILLS_DIR = Path("16_opencap_dropjump_outputs/cam_angle_check/manifest_check")

OUT_DIR.mkdir(parents=True, exist_ok=True)
STILLS_DIR.mkdir(parents=True, exist_ok=True)

SUBJECTS = ["subject2", "subject3", "subject4", "subject5", "subject7", "subject8", "subject10", "subject11"]

manifest_rows = []
warnings = []
stills_saved = []

print("=========================================================")
# Step 1: Process each subject
print("STEP 1 & 2 & 3: Processing subjects and resolving files...")
print("=========================================================")

for sub in SUBJECTS:
    sub_dir = BASE_DIR / sub
    video_session_dir = sub_dir / "VideoData" / "Session0"
    
    if not video_session_dir.exists():
        warnings.append(f"{sub}: VideoData/Session0 directory not found!")
        continue
        
    # Check cameras
    cams = [d for d in os.listdir(video_session_dir) if d.startswith("Cam")]
    
    # Selection of camera index
    if "Cam4" in cams:
        cam_used = "Cam4"
    else:
        cam_used = "Cam0"
        warnings.append(f"{sub}: Cam4 not found. Flipped to alternative: {cam_used}.")
        
    cam_dir = video_session_dir / cam_used
    
    # Glob DJ trials
    dj_trials = sorted([d for d in os.listdir(cam_dir) if d.startswith("DJ")])
    print(f"Processing {sub} using {cam_used} ({len(dj_trials)} trials found)...")
    
    still_extracted = False
    
    for trial in dj_trials:
        trial_dir = cam_dir / trial
        
        # Classification
        condition = "asymmetric" if "Asym" in trial else "symmetric"
        
        # Paths relative to project root
        video_relpath = (trial_dir / f"{trial}_syncdWithMocap.avi").as_posix()
        mocap_ik_relpath = (sub_dir / "OpenSimData" / "Mocap" / "IK" / f"{trial}.mot").as_posix()
        video_ik_relpath = (sub_dir / "OpenSimData" / "Video" / "OpenPose_highAccuracy" / "5-cameras" / "IK" / f"{trial}.mot").as_posix()
        marker_relpath = (sub_dir / "MarkerData" / "Mocap" / f"{trial}.trc").as_posix()
        force_relpath = (sub_dir / "ForceData" / f"{trial}_forces.mot").as_posix()
        
        # Verify existence
        video_present = Path(video_relpath).is_file()
        mocap_ik_present = Path(mocap_ik_relpath).is_file()
        video_ik_present = Path(video_ik_relpath).is_file()
        marker_present = Path(marker_relpath).is_file()
        force_present = Path(force_relpath).is_file()
        
        if not video_present:
            warnings.append(f"{sub}/{trial}: Synced video file not found at {video_relpath}")
        if not mocap_ik_present:
            warnings.append(f"{sub}/{trial}: Mocap IK file not found at {mocap_ik_relpath}")
        if not marker_present:
            warnings.append(f"{sub}/{trial}: Marker file not found at {marker_relpath}")
            
        manifest_rows.append({
            "subject_id": sub,
            "trial_id": trial,
            "condition": condition,
            "camera_used": cam_used,
            "video_path": video_relpath if video_present else "",
            "mocap_ik_path": mocap_ik_relpath if mocap_ik_present else "",
            "video_ik_path_secondary": video_ik_relpath if video_ik_present else "",
            "marker_path": marker_relpath if marker_present else "",
            "force_path": force_relpath if force_present else "",
            "synced_video_present": video_present,
            "mocap_ik_present": mocap_ik_present,
            "force_present": force_present
        })
        
        # Save still for manifest check (one per subject)
        if not still_extracted and video_present:
            cap = cv2.VideoCapture(video_relpath)
            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                target_frame = min(85, frame_count // 2)
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = cap.read()
                if ret:
                    still_out_path = STILLS_DIR / f"{sub}_{cam_used}_{trial}.png"
                    cv2.imwrite(str(still_out_path), frame)
                    stills_saved.append(still_out_path.as_posix())
                    still_extracted = True
                cap.release()

# Convert to DataFrame
df = pd.DataFrame(manifest_rows)
# Sort by subject_id and trial_id
df = df.sort_values(by=["subject_id", "trial_id"]).reset_index(drop=True)

# Step 4: Write manifest CSV
manifest_csv_path = OUT_DIR / "opencap_dropjump_manifest.csv"
df.to_csv(manifest_csv_path, index=False)

print("\n=========================================================")
print("STEP 4: Manifest CSV written successfully.")
print(f"Path: {manifest_csv_path.as_posix()}")
print("=========================================================")

# Step 5: Generate Markdown Report
print("\nSTEP 5: Generating report...")

total_subjects = len(df["subject_id"].unique())
total_trials = len(df)
sym_count = len(df[df["condition"] == "symmetric"])
asym_count = len(df[df["condition"] == "asymmetric"])

report_content = f"""# OpenCap Drop Jump Manifest Build Report

This report summarizes the creation of the OpenCap Drop Jump dataset manifest, including cohort coverage, camera assignments, resolved files, and validation stills.

---

## 1. Cohort Summary
*   **Total Video-Capable Subjects**: {total_subjects} (subject2, subject3, subject4, subject5, subject7, subject8, subject10, subject11).
    *   *Note: `subject6` was excluded from this cohort as the videos are private.*
*   **Total Drop Jump Trials**: {total_trials}
*   **Symmetric Trials**: {sym_count}
*   **Asymmetric Trials**: {asym_count}

### Per-Subject Trial Breakdown
"""

breakdown_df = df.groupby(["subject_id", "condition"]).size().unstack(fill_value=0)
table_lines = [
    "| Subject ID | Symmetric Trials | Asymmetric Trials |",
    "| :--- | :---: | :---: |"
]
for sub_id, row_data in breakdown_df.iterrows():
    table_lines.append(f"| {sub_id} | {row_data['symmetric']} | {row_data['asymmetric']} |")
report_content += "\n".join(table_lines)

report_content += "\n\n---\n\n## 2. Camera Selection & Verification\n"
report_content += "*   **Default Camera**: `Cam4` was selected as the primary sagittal view for all subjects where available.\n"

exceptions = df[df["camera_used"] != "Cam4"][["subject_id", "camera_used"]].drop_duplicates()
if not exceptions.empty:
    report_content += "*   **Exceptions**:\n"
    for _, row in exceptions.iterrows():
        report_content += f"    *   **{row['subject_id']}**: Only `{row['camera_used']}` was present on disk. It was used consistently for this subject.\n"
else:
    report_content += "*   **Exceptions**: None. All subjects used `Cam4`.\n"

report_content += "\n---\n\n## 3. Synced Videos & Mocap IK Verification\n"
missing_video = df[~df["synced_video_present"]]
missing_mocap = df[~df["mocap_ik_present"]]

if missing_video.empty:
    report_content += "*   **Synced Video Status**: All trials have their synchronized video (`_syncdWithMocap.avi`) present.\n"
else:
    report_content += f"*   **Synced Video Status**: Warning! Missing videos in {len(missing_video)} trials.\n"

if missing_mocap.empty:
    report_content += "*   **Mocap IK Status**: All trials have their corresponding ground-truth Mocap IK `.mot` files present.\n"
else:
    report_content += f"*   **Mocap IK Status**: Warning! Missing Mocap IK files in {len(missing_mocap)} trials.\n"

# Verify force files
missing_force = df[~df["force_present"]]
if missing_force.empty:
    report_content += "*   **Force Data Status**: All trials have their ground-truth ForceData `.mot` files present (ready for force-sync validation).\n"
else:
    report_content += f"*   **Force Data Status**: Warning! Missing ForceData in {len(missing_force)} trials.\n"

report_content += "\n---\n\n## 4. Verification Stills Saved\n"
report_content += "The following still frames have been extracted and saved to `16_opencap_dropjump_outputs/cam_angle_check/manifest_check/` to visually verify the sagittal profile view before processing:\n\n"
for path in stills_saved:
    filename = Path(path).name
    report_content += f"- **{filename}**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/{filename}](file:///{BASE_DIR.resolve().parent.parent.parent / '16_opencap_dropjump_outputs/cam_angle_check/manifest_check' / filename})\n"

report_md_path = OUT_DIR / "manifest_build_report.md"
with open(report_md_path, "w", encoding="utf-8") as f:
    f.write(report_content)

print("=========================================================")
print(f"Markdown report generated successfully at {report_md_path.as_posix()}")
print("=========================================================")

# Print warnings
if warnings:
    print("\nWarnings:")
    for w in warnings:
        print(f"  - {w}")
else:
    print("\nNo warnings generated. Everything is fully aligned!")
