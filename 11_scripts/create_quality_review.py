#!/usr/bin/env python3
"""
create_quality_review.py
========================
Phase 2B — Manual Quality Review Subset Creator

Reads dataset_metadata.csv, filters for squats, and creates a smaller
review CSV (squat_quality_review.csv) with ~100 files sampled across
as many unique subjects as possible.

This script does NOT modify the original dataset_metadata.csv.

Author  : Dissertation Project
Created : 2026-05-26
"""

import csv
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_CSV = PROJECT_ROOT / "3_metadata" / "dataset_metadata.csv"
OUTPUT_CSV = PROJECT_ROOT / "3_metadata" / "squat_quality_review.csv"

TARGET_EXERCISE = "squats"
MAX_REVIEW_ROWS = 100

REVIEW_INSTRUCTION = (
    "Manually inspect this file. "
    "Mark Quality as good/moderate/bad and Selected as yes/no."
)

# Output columns (original + Review_Instruction)
OUTPUT_COLUMNS = [
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
    "Review_Instruction",
]

# Reproducible sampling
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Validate input
    if not METADATA_CSV.exists():
        print(f"[ERROR] Metadata CSV not found: {METADATA_CSV}")
        sys.exit(1)

    # Read all squat rows
    all_squats = []
    with open(METADATA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Exercise"] == TARGET_EXERCISE:
                all_squats.append(row)

    total_squat_rows = len(all_squats)
    if total_squat_rows == 0:
        print("[WARNING] No squat rows found in dataset_metadata.csv.")
        print("          Cannot create review file.")
        sys.exit(0)

    # Group by Subject_ID
    subjects = defaultdict(list)
    for row in all_squats:
        subjects[row["Subject_ID"]].append(row)

    num_subjects = len(subjects)
    subject_ids = sorted(subjects.keys())

    # -----------------------------------------------------------------------
    # Sampling strategy:
    #   - Spread across as many subjects as possible
    #   - If subjects <= MAX_REVIEW_ROWS, sample multiple frames per subject
    #   - If subjects > MAX_REVIEW_ROWS, pick 1 frame from 100 random subjects
    #   - Always include videos if any exist
    # -----------------------------------------------------------------------

    random.seed(RANDOM_SEED)
    selected_rows = []

    # Step 1: Collect any video files first (they are rare and valuable)
    video_rows = [r for r in all_squats if r["File_Type"] == "video"]
    for vr in video_rows:
        selected_rows.append(vr)

    video_count = len(selected_rows)
    remaining_budget = MAX_REVIEW_ROWS - video_count

    # Step 2: Sample image frames across subjects
    if num_subjects <= remaining_budget:
        # We can include at least 1 frame from every subject
        frames_per_subject = max(1, remaining_budget // num_subjects)
        for sid in subject_ids:
            image_frames = [r for r in subjects[sid] if r["File_Type"] == "image"]
            if not image_frames:
                continue
            # Sample a spread of frames (early, middle, late in sequence)
            if len(image_frames) <= frames_per_subject:
                sampled = image_frames
            else:
                # Deterministic spread: pick evenly spaced frames
                step = len(image_frames) / frames_per_subject
                indices = [int(i * step) for i in range(frames_per_subject)]
                sampled = [image_frames[i] for i in indices]
            selected_rows.extend(sampled)
    else:
        # More subjects than budget: pick 1 frame from random subjects
        chosen_subjects = random.sample(subject_ids, remaining_budget)
        for sid in chosen_subjects:
            image_frames = [r for r in subjects[sid] if r["File_Type"] == "image"]
            if image_frames:
                # Pick a middle frame for best representation
                mid_idx = len(image_frames) // 2
                selected_rows.append(image_frames[mid_idx])

    # Trim to exactly MAX_REVIEW_ROWS if overshot
    if len(selected_rows) > MAX_REVIEW_ROWS:
        selected_rows = selected_rows[:MAX_REVIEW_ROWS]

    # Deduplicate by File_Path (safety check)
    seen_paths = set()
    deduped = []
    for row in selected_rows:
        if row["File_Path"] not in seen_paths:
            seen_paths.add(row["File_Path"])
            deduped.append(row)
    selected_rows = deduped

    # Add Review_Instruction column
    for row in selected_rows:
        row["Review_Instruction"] = REVIEW_INSTRUCTION

    # -----------------------------------------------------------------------
    # Write output CSV
    # -----------------------------------------------------------------------
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(selected_rows)

    # -----------------------------------------------------------------------
    # Compute summary stats
    # -----------------------------------------------------------------------
    review_subjects = set(r["Subject_ID"] for r in selected_rows)
    review_ftypes = defaultdict(int)
    for r in selected_rows:
        review_ftypes[r["File_Type"]] += 1

    # Print summary
    print("\n" + "=" * 60)
    print("  PHASE 2B -- QUALITY REVIEW SUBSET SUMMARY")
    print("=" * 60)
    print(f"\n  Total squat rows in dataset_metadata.csv : {total_squat_rows}")
    print(f"  Rows selected for squat_quality_review.csv: {len(selected_rows)}")
    print(f"  Unique Subject_IDs included              : {len(review_subjects)}")

    print("\n  Count by File_Type:")
    for ft in ["video", "image"]:
        count = review_ftypes.get(ft, 0)
        if count > 0:
            print(f"    {ft:15s} : {count}")

    csv_rel = OUTPUT_CSV.relative_to(PROJECT_ROOT).as_posix()
    print(f"\n  Review CSV path     : {csv_rel}")
    print(f"  Instructions path   : 3_metadata/quality_review_instructions.md")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
