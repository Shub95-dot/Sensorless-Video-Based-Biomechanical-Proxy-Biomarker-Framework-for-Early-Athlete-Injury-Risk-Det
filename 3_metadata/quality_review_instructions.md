# Quality Review Instructions — Squats

## Purpose

This document explains how to manually review squat files listed in `squat_quality_review.csv` and mark them for the first pose extraction experiment.

The review CSV contains a sampled subset of squat frames from `dataset_metadata.csv`. Your task is to visually inspect each file and assign a **Quality** label and a **Selected** flag.

---

## How to Review

1. Open `3_metadata/squat_quality_review.csv` in a spreadsheet editor (Excel, Google Sheets, LibreOffice Calc).
2. For each row, open the file at the path in `File_Path` (relative to the project root).
3. Visually inspect the image or video.
4. Update the `Quality` column based on the criteria below.
5. Update the `Selected` column based on the quality decision.
6. Save the CSV when finished.

---

## Quality Labels

### Quality = good

Assign `good` if **all** of the following are true:

- Full body is visible in the frame
- **Hip, knee, and ankle joints** are clearly visible
- Only a **single athlete/person** is clearly visible
- **Minimal blur** — the frame is sharp
- The squat position or movement is **clearly recognizable**
- Lower-body joints are **not occluded** by equipment, clothing, or other objects

### Quality = moderate

Assign `moderate` if:

- Body is **mostly visible** but not fully
- There is **minor blur** or slight motion artifacts
- There is **slight occlusion** of one or two joints
- The file is **still possibly usable** for pose estimation, but with reduced confidence

### Quality = bad

Assign `bad` if **any** of the following are true:

- The body is **cut off** at critical joints (hip, knee, or ankle not visible)
- Hip, knee, or ankle joints are **hidden** behind objects or out of frame
- There is **heavy blur** making joint positions indistinguishable
- **Multiple people** are present and confuse which person is the subject
- The movement is **not a clear squat** (wrong exercise, transition frame, etc.)

---

## Selection Rule

| Quality | Selected |
|---|---|
| `good` | `yes` |
| `moderate` | `no` |
| `bad` | `no` |

> **For the first pose extraction experiment**, set `Selected = yes` **only** for files marked `Quality = good`.
> Files with `moderate` or `bad` quality should be set to `Selected = no` during this initial test phase.

---

## First Pose Extraction Experiment Target

After completing your review of `squat_quality_review.csv`:

> **Manually choose approximately 30 good squat files** from the review CSV.

These 30 files will form the initial test batch for:
- Pose estimation pipeline validation
- Verifying keypoint extraction accuracy
- Debugging joint angle calculations (knee angle, hip angle, ankle angle)
- Testing knee valgus approximation logic

You do **not** need to mark all 100 rows as `good`. The goal is to find **~30 high-quality, diverse samples** across different subjects.

---

## After Review

Once you have completed the quality review:

1. Save `squat_quality_review.csv` with your updated `Quality` and `Selected` columns.
2. The next step will be to update the main `dataset_metadata.csv` with your quality decisions.
3. Then proceed to Phase 3: pose estimation on the filtered subset (`Quality = good`, `Selected = yes`).

---

## Notes

- Do **not** modify the original `dataset_metadata.csv` during this review step.
- Do **not** move, rename, or delete any dataset files.
- Do **not** start pose estimation until the quality review is complete and approved.
- This review focuses on **squats only** for the first experiment.
