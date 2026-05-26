#!/usr/bin/env python3
"""
create_metadata.py
==================
Phase 2 Dataset Preparation — Metadata Generation Script

Sensorless Video-Based Computational Biomechanics System
for Athlete Injury-Risk Detection

This script scans the 1_raw_datasets/Dataset/ directory for exercise
folders, normalizes their names to core Phase 2 categories, extracts
file-level metadata from videos and images, and produces a clean CSV
at 3_metadata/dataset_metadata.csv.

Core exercises indexed in this version:
    squats, lunges, long_jump, basketball

Author  : Dissertation Project
Created : 2026-05-26
"""

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# PROJECT_ROOT is the workspace root (parent of 11_scripts/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_DIR = PROJECT_ROOT / "1_raw_datasets" / "Dataset"
METADATA_DIR = PROJECT_ROOT / "3_metadata"
OUTPUT_CSV = METADATA_DIR / "dataset_metadata.csv"

DATASET_SOURCE = "Dataset"

# Core exercises to index in Phase 2 (normalized names)
CORE_EXERCISES = ["squats", "lunges", "long_jump", "basketball"]

# File-ID prefix mapping
EXERCISE_PREFIX = {
    "squats": "SQ",
    "lunges": "LU",
    "long_jump": "LJ",
    "basketball": "BB",
}

# ---------------------------------------------------------------------------
# Exercise name normalization
# ---------------------------------------------------------------------------
# Maps lowercased folder names to their normalized exercise category.
# Only folders that map to a CORE_EXERCISES value will be indexed.

EXERCISE_NORMALIZATION = {
    # Squats variations
    "squat": "squats",
    "squats": "squats",
    "squats frames": "squats",
    "squats_frames": "squats",
    "weighted squat": "squats",
    "weighted_squat": "squats",
    "squats with weights": "squats",
    "squats_with_weights": "squats",
    "squat with weights": "squats",

    # Lunges variations
    "lunge": "lunges",
    "lunges": "lunges",
    "lunges video": "lunges",
    "lunges_video": "lunges",

    # Long Jump variations
    "long jump": "long_jump",
    "long_jump": "long_jump",
    "longjump": "long_jump",
    "long-jump": "long_jump",
    "high jump": "long_jump",
    "high_jump": "long_jump",
    "highjump": "long_jump",
    "high-jump": "long_jump",

    # Basketball variations
    "basketball": "basketball",
    "basket ball": "basketball",
    "basket_ball": "basketball",
    "basketball frames": "basketball",
    "basketball_frames": "basketball",
    "basketball videos": "basketball",
    "basketball_videos": "basketball",
}

# Supported file extensions
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}
ALL_EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS

# CSV column order
CSV_COLUMNS = [
    "File_ID",
    "Subject_ID",
    "Exercise",
    "Dataset_Source",
    "File_Type",
    "File_Path",
    "FPS",
    "Resolution",
    "Duration_sec",
    "Frame_Count",
    "Camera_View",
    "Quality",
    "Selected",
    "Pose_Status",
    "Notes",
]

# ---------------------------------------------------------------------------
# Dependency helpers
# ---------------------------------------------------------------------------

def _import_cv2():
    """Lazily import OpenCV; return None if unavailable."""
    try:
        import cv2
        return cv2
    except ImportError:
        print("[WARNING] opencv-python (cv2) is not installed.")
        print("          Video metadata (FPS, Resolution, Duration, Frame_Count) will be left blank.")
        print("          Install with: pip install opencv-python")
        return None


def _import_pil():
    """Lazily import Pillow; return None if unavailable."""
    try:
        from PIL import Image
        return Image
    except ImportError:
        print("[WARNING] Pillow (PIL) is not installed.")
        print("          Image resolution will be left blank.")
        print("          Install with: pip install Pillow")
        return None

# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_video_metadata(filepath: Path, cv2_module):
    """
    Extract FPS, Resolution, Duration_sec, and Frame_Count from a video file
    using OpenCV.

    Returns a dict with keys: FPS, Resolution, Duration_sec, Frame_Count.
    Returns partial/empty values on failure or if cv2 is unavailable.
    """
    result = {"FPS": "", "Resolution": "", "Duration_sec": "", "Frame_Count": ""}

    if cv2_module is None:
        return result

    cap = None
    try:
        cap = cv2_module.VideoCapture(str(filepath))
        if not cap.isOpened():
            print(f"  [WARNING] Cannot open video: {filepath.name}")
            return result

        fps = cap.get(cv2_module.CAP_PROP_FPS)
        width = int(cap.get(cv2_module.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2_module.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2_module.CAP_PROP_FRAME_COUNT))

        duration = round(frame_count / fps, 3) if fps and fps > 0 else ""

        result["FPS"] = round(fps, 2) if fps else ""
        result["Resolution"] = f"{width}x{height}" if width and height else ""
        result["Duration_sec"] = duration
        result["Frame_Count"] = frame_count if frame_count > 0 else ""

    except Exception as exc:
        print(f"  [WARNING] Error reading video {filepath.name}: {exc}")
    finally:
        if cap is not None:
            cap.release()

    return result


def extract_image_metadata(filepath: Path, pil_module):
    """
    Extract Resolution from an image file using Pillow.

    Frame_Count is always 1 for images.
    FPS and Duration_sec are left empty.

    Returns a dict with keys: FPS, Resolution, Duration_sec, Frame_Count.
    """
    result = {"FPS": "", "Resolution": "", "Duration_sec": "", "Frame_Count": 1}

    if pil_module is None:
        return result

    try:
        with pil_module.open(filepath) as img:
            width, height = img.size
            result["Resolution"] = f"{width}x{height}"
    except Exception as exc:
        print(f"  [WARNING] Error reading image {filepath.name}: {exc}")

    return result

# ---------------------------------------------------------------------------
# Subject ID inference
# ---------------------------------------------------------------------------

def infer_subject_id(filepath: Path, exercise_dir: Path):
    """
    Infer the Subject_ID from the folder structure.

    Expected layout:
        1_raw_datasets/Dataset/<exercise_folder>/<Subject_ID>/.../<file>

    If the file sits directly inside the exercise folder (no subject
    subfolder), Subject_ID defaults to 'unknown'.
    """
    try:
        rel = filepath.relative_to(exercise_dir)
        parts = rel.parts  # e.g. ('1659', '000001.jpg') or ('video.avi',)
        if len(parts) > 1:
            return parts[0]  # first subfolder = Subject_ID
        return "unknown"
    except ValueError:
        return "unknown"

# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def build_metadata():
    """Scan, extract, and write metadata CSV. Returns summary statistics."""

    # Lazy imports
    cv2_module = _import_cv2()
    pil_module = _import_pil()
    dep_warnings = []
    if cv2_module is None:
        dep_warnings.append("opencv-python (cv2) not installed — video metadata will be blank")
    if pil_module is None:
        dep_warnings.append("Pillow (PIL) not installed — image resolution will be blank")

    # Ensure output directory exists
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # Tracking counters
    rows = []
    seen_paths = set()  # duplicate protection
    exercise_counts = defaultdict(int)
    filetype_counts = defaultdict(int)
    subject_counts = defaultdict(int)
    skipped_folders = []
    unreadable_files = []
    # Sequence counters keyed by (exercise, subject_id)
    sequence_counters = defaultdict(int)

    # Validate source directory
    if not DATASET_DIR.exists():
        print(f"[ERROR] Dataset directory not found: {DATASET_DIR}")
        print("        Expected: 1_raw_datasets/Dataset/")
        sys.exit(1)

    # Discover all top-level subfolders in the dataset directory
    all_subfolders = sorted([
        d for d in DATASET_DIR.iterdir() if d.is_dir()
    ], key=lambda d: d.name.lower())

    for exercise_dir in all_subfolders:
        folder_name = exercise_dir.name
        normalized_key = folder_name.lower()

        # Attempt to normalize the folder name to a core exercise
        normalized_exercise = EXERCISE_NORMALIZATION.get(normalized_key)

        if normalized_exercise is None or normalized_exercise not in CORE_EXERCISES:
            skipped_folders.append(folder_name)
            continue

        exercise = normalized_exercise
        prefix = EXERCISE_PREFIX[exercise]

        print(f"  Scanning: {folder_name} -> {exercise}")

        # Recursively walk the exercise directory
        for root, _dirs, files in os.walk(exercise_dir):
            root_path = Path(root)
            for fname in sorted(files):
                fpath = root_path / fname
                ext = fpath.suffix.lower()

                if ext not in ALL_EXTENSIONS:
                    continue  # skip non-media files silently

                # Duplicate protection (by absolute resolved path)
                resolved = fpath.resolve()
                if resolved in seen_paths:
                    continue
                seen_paths.add(resolved)

                # Determine file type
                if ext in VIDEO_EXTENSIONS:
                    file_type = "video"
                else:
                    file_type = "image"

                # Infer subject ID
                subject_id = infer_subject_id(fpath, exercise_dir)

                # Generate File_ID:  PREFIX_SubjectID_SEQ
                seq_key = (exercise, subject_id)
                sequence_counters[seq_key] += 1
                seq_num = sequence_counters[seq_key]
                file_id = f"{prefix}_{subject_id}_{seq_num:03d}"

                # Relative path from project root (forward slashes)
                try:
                    rel_path = fpath.relative_to(PROJECT_ROOT).as_posix()
                except ValueError:
                    rel_path = str(fpath).replace("\\", "/")

                # Extract metadata
                try:
                    if file_type == "video":
                        meta = extract_video_metadata(fpath, cv2_module)
                    else:
                        meta = extract_image_metadata(fpath, pil_module)
                except Exception as exc:
                    print(f"  [WARNING] Skipping unreadable file {fpath.name}: {exc}")
                    unreadable_files.append(rel_path)
                    continue

                row = {
                    "File_ID": file_id,
                    "Subject_ID": subject_id,
                    "Exercise": exercise,
                    "Dataset_Source": DATASET_SOURCE,
                    "File_Type": file_type,
                    "File_Path": rel_path,
                    "FPS": meta["FPS"],
                    "Resolution": meta["Resolution"],
                    "Duration_sec": meta["Duration_sec"],
                    "Frame_Count": meta["Frame_Count"],
                    "Camera_View": "unknown",
                    "Quality": "unchecked",
                    "Selected": "yes",
                    "Pose_Status": "not_started",
                    "Notes": "",
                }

                rows.append(row)
                exercise_counts[exercise] += 1
                filetype_counts[file_type] += 1
                subject_counts[f"{exercise}/{subject_id}"] += 1

    # -----------------------------------------------------------------------
    # Write CSV
    # -----------------------------------------------------------------------
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    # -----------------------------------------------------------------------
    # Print summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("  PHASE 2 — METADATA GENERATION SUMMARY")
    print("=" * 70)

    csv_rel = OUTPUT_CSV.relative_to(PROJECT_ROOT).as_posix()
    print(f"\n  1. CSV path          : {csv_rel}")
    print(f"  2. Total files indexed: {len(rows)}")

    # Count per exercise
    print("\n  3. Count per exercise:")
    if exercise_counts:
        for ex in CORE_EXERCISES:
            count = exercise_counts.get(ex, 0)
            print(f"       {ex:15s} : {count}")
    else:
        print("       (no files found)")

    # Count by file type
    print("\n  4. Count by file type:")
    if filetype_counts:
        for ft in ["video", "image"]:
            count = filetype_counts.get(ft, 0)
            if count > 0:
                print(f"       {ft:15s} : {count}")
    else:
        print("       (no files found)")

    # Count per subject (sorted, show unique subject count per exercise)
    print("\n  5. Count per subject (unique subjects per exercise):")
    if subject_counts:
        # Group by exercise
        exercise_subjects = defaultdict(dict)
        for key, count in sorted(subject_counts.items()):
            ex, subj = key.split("/", 1)
            exercise_subjects[ex][subj] = count

        for ex in CORE_EXERCISES:
            subjects = exercise_subjects.get(ex, {})
            if subjects:
                print(f"       {ex}: {len(subjects)} subjects, {sum(subjects.values())} total files")
            else:
                print(f"       {ex}: 0 subjects")
    else:
        print("       (no subjects found)")

    # Skipped folders
    print("\n  6. Skipped folders (not in core exercises):")
    if skipped_folders:
        for sf in skipped_folders:
            print(f"       - {sf}")
    else:
        print("       (none)")

    # Unreadable files
    print("\n  7. Unreadable files:")
    if unreadable_files:
        for uf in unreadable_files:
            print(f"       - {uf}")
    else:
        print("       (none)")

    # Dependency warnings
    print("\n  8. Dependency warnings:")
    if dep_warnings:
        for dw in dep_warnings:
            print(f"       - {dw}")
    else:
        print("       (none — all dependencies available)")

    # First 5 rows
    print("\n  9. First 5 metadata rows:")
    if rows:
        # Print header
        print(f"       {'File_ID':<20s} {'Subject_ID':<12s} {'Exercise':<12s} {'File_Type':<8s} {'Resolution':<12s} {'File_Path'}")
        print(f"       {'—'*20} {'—'*12} {'—'*12} {'—'*8} {'—'*12} {'—'*40}")
        for r in rows[:5]:
            res = r['Resolution'] if r['Resolution'] else '—'
            # Truncate path for display
            fpath_display = r['File_Path']
            if len(fpath_display) > 55:
                fpath_display = "..." + fpath_display[-52:]
            print(f"       {r['File_ID']:<20s} {r['Subject_ID']:<12s} {r['Exercise']:<12s} {r['File_Type']:<8s} {res:<12s} {fpath_display}")
    else:
        print("       (no rows)")

    # Confirm relative paths
    print("\n  10. File_Path format:")
    if rows:
        all_relative = all(not r["File_Path"].startswith(("C:", "c:", "/", "\\")) for r in rows)
        if all_relative:
            print("       [OK] All File_Path values are relative paths (forward slashes)")
        else:
            print("       [!!] WARNING: Some File_Path values appear to be absolute paths")
    else:
        print("       (no rows to verify)")

    print("\n" + "=" * 70 + "\n")

    return {
        "total": len(rows),
        "exercise_counts": dict(exercise_counts),
        "filetype_counts": dict(filetype_counts),
        "subject_counts": dict(subject_counts),
        "skipped_folders": skipped_folders,
        "unreadable_files": unreadable_files,
        "dep_warnings": dep_warnings,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Scanning     : {DATASET_DIR}")
    print(f"Output CSV   : {OUTPUT_CSV}")
    print()
    build_metadata()
