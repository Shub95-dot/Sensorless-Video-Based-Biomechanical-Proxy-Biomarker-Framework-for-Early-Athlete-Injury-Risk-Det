# Metadata — README

## Purpose

The file `dataset_metadata.csv` is the central index for all media files selected for Phase 2 of this dissertation project. It catalogues every video and image frame in the raw dataset that belongs to a core exercise category, providing a single source of truth for downstream processes such as pose estimation, biomarker extraction, and machine-learning pipelines.

This metadata file is generated automatically by `11_scripts/create_metadata.py`.

> **Important:** Metadata creation does **not** perform pose estimation or ML training. It only indexes and describes files.

---

## Current Source Folder

```
1_raw_datasets/Dataset/
```

---

## Folder Interpretation

The script infers metadata from the folder hierarchy:

```
1_raw_datasets/Dataset/<exercise_folder>/<subject_folder>/<files>
```

| Path Level | Inference |
|---|---|
| Exercise folder (e.g., `Squats Frames`) | Normalized to `Exercise` (e.g., `squats`) |
| Subject folder (e.g., `1659`) | Used as `Subject_ID` |
| Files directly in exercise folder (no subject subfolder) | `Subject_ID = unknown` |

### Exercise Name Normalization

Raw folder names are normalized to canonical exercise names:

| Raw Folder Name | Normalized Exercise |
|---|---|
| `Squats Frames`, `squat`, `squats`, `weighted squat`, etc. | `squats` |
| `Lunges Video`, `lunge`, `lunges` | `lunges` |
| `long jump`, `long_jump`, `high jump`, `high_jump`, etc. | `long_jump` |
| `basketball`, `basket ball`, `basket_ball` | `basketball` |

Folders that do not match any normalization rule are **skipped** (not indexed) and reported in the execution summary.

---

## Current Scope — Core Phase 2 Exercises

This metadata file currently focuses on **core Phase 2 exercises only**:

| Exercise | File-ID Prefix |
|---|---|
| squats | `SQ` |
| lunges | `LU` |
| long_jump | `LJ` |
| basketball | `BB` |

Other exercise folders are intentionally excluded from this first metadata version. They can be added in future phases by updating the `CORE_EXERCISES` list and `EXERCISE_NORMALIZATION` mapping in the script.

---

## Column Definitions

| Column | Description |
|---|---|
| `File_ID` | Unique identifier for each file. Format: `{PREFIX}_{Subject_ID}_{SEQ:03d}` (e.g., `SQ_1659_001`). |
| `Subject_ID` | Identifier for the individual/subject, inferred from the subfolder directly inside the exercise folder. Defaults to `unknown` if not inferable. |
| `Exercise` | Normalized exercise category (e.g., `squats`, `lunges`, `long_jump`, `basketball`). |
| `Dataset_Source` | Origin dataset or collection name (e.g., `Dataset`). |
| `File_Type` | Either `video` or `image`. |
| `File_Path` | Relative path from the project root to the file (forward-slash separated). |
| `FPS` | Frames per second (videos only). Empty for images. |
| `Resolution` | Width×Height in pixels (e.g., `1920x1080`). |
| `Duration_sec` | Duration in seconds (videos only). Empty for images. |
| `Frame_Count` | Total number of frames. Always `1` for images. |
| `Camera_View` | The camera perspective used during recording. |
| `Quality` | Subjective quality assessment of the file. |
| `Selected` | Whether this file is selected for processing (`yes` / `no`). |
| `Pose_Status` | Current status of pose estimation for this file. |
| `Notes` | Free-text field for any additional annotations. |

---

## Quality Labels

| Label | Meaning |
|---|---|
| `good` | Full body visible, clear motion, minimal blur — suitable for pose extraction. |
| `moderate` | Partially usable — minor blur or occlusion present. |
| `bad` | Unusable — body cut off, heavy blur, major occlusion. |
| `unchecked` | Not yet manually reviewed. This is the default for all newly indexed files. |

> **Important:** For the **first pose extraction experiment**, use only files where:
> - `Exercise = squats`
> - `Quality = good`
> - `Selected = yes`

---

## Camera View Labels

| Label | Meaning |
|---|---|
| `front` | Camera facing the subject from the front. |
| `side` | Camera positioned to the side (sagittal plane). |
| `diagonal` | Camera at an oblique angle between front and side. |
| `unknown` | Camera angle has not been determined. This is the default. |

---

## Pose Status Labels

| Status | Meaning |
|---|---|
| `not_started` | Pose estimation has not been attempted. Default for all new entries. |
| `success` | Pose estimation completed successfully. |
| `failed` | Pose estimation was attempted but failed. |

---

## How to Regenerate

To regenerate the metadata CSV, run the following from the project root:

```bash
python 11_scripts/create_metadata.py
```

This will overwrite the existing `dataset_metadata.csv` with a fresh scan.

### Dependencies

```bash
pip install opencv-python Pillow
```

- **OpenCV** (`cv2`) is used to extract video metadata (FPS, resolution, duration, frame count). If unavailable, videos are still indexed but these fields are left blank.
- **Pillow** (`PIL`) is used to extract image resolution. If unavailable, images are still indexed but resolution is left blank.

---

## Next Steps

1. **Review quality** — Open `dataset_metadata.csv` and manually set `Quality` for each file.
2. **Set camera views** — Update `Camera_View` where applicable.
3. **Filter for pose estimation** — Use only rows where `Exercise = squats`, `Quality = good`, and `Selected = yes`.
4. **Proceed to Phase 3** — Run pose estimation on the filtered subset.
