# OpenCap Dataset Structure Map & Drop-Jump Cohort Inventory

This document maps the directory structure, camera perspectives, trial naming, and asset paths for the **OpenCap Lab Validation dataset** (`1_raw_datasets/OpenCap/LabValidation_withVideos/`). This mapping serves as the blueprint for building the vertical/drop-jump analysis manifest.

---

## 1. Subjects Inventory
A visual scan of the `LabValidation_withVideos/` directory reveals **9 subject folders** in total. The subject numbering is non-contiguous:
- **Folders**: `subject2`, `subject3`, `subject4`, `subject5`, `subject6`, `subject7`, `subject8`, `subject10`, `subject11`
- **Total Subjects Count**: 9 subjects

*Note: `subject1` and `subject9` are not present in this dataset.*

---

## 2. Sessions and Trial Allocation
Each subject folder contains a `VideoData` folder, which organizes recordings into discrete sessions (typically `Session0` and `Session1`). For our sample subjects, the activities are partitioned as follows:

### Subject 2:
- **`Session0`**: Calibration, squat, and jump tasks.
  - *Trials under Session0*: `static1` (calibration), `squats1`, `squatsAsym1`, `STS1` (Sit-to-Stand), `STSweakLegs1`, `DJ1`, `DJ2`, `DJ3` (symmetric Drop Jumps), `DJAsym1`, `DJAsym4`, `DJAsym5` (asymmetric Drop Jumps).
- **`Session1`**: Gait tasks.
  - *Trials under Session1*: `walking1`, `walking2`, `walking3`, `walkingTS1`, `walkingTS2`, `walkingTS4`.
- **Drop-Jump Allocation**: All Drop-Jump trials (symmetric and asymmetric) live **exclusively in `Session0`**.

### Subject 3:
- **`Session0`**: Calibration, squat, and jump tasks.
  - *Trials under Session0*: `static1`, `squats1`, `squatsAsym1`, `STS1`, `STSweakLegs1`, `DJ1`, `DJ2`, `DJ4` (symmetric), `DJAsym1`, `DJAsym2`, `DJAsym4` (asymmetric).
- **`Session1`**: Gait tasks.
  - *Trials under Session1*: `walking1`, `walking2`, `walking3`, `walkingTS2`, `walkingTS3`, `walkingTS4`.
- **Drop-Jump Allocation**: All Drop-Jump trials live **exclusively in `Session0`**.

---

## 3. Camera Layout & Perspectives
Under `VideoData/Session0/`, five camera folders (`Cam0` through `Cam4`) exist. Stills extracted from `subject2/VideoData/Session0/CamN/DJ1/DJ1_syncdWithMocap.avi` at frame 85 reveal the following camera layout and orientations:

| Camera Index | Layout Position & Perspective | Yaw Angle (OpenCV space) | Biomechanical Utility |
| :---: | :--- | :---: | :--- |
| **`Cam2`** | **Central Frontal View**: The camera is positioned directly in front of the jump box, looking straight at the subject. | $8.3^\circ$ | **Frontal-plane analysis** (knee valgus/varus, lateral trunk displacement). |
| **`Cam1`** | **Right-Frontal View**: Positioned to the subject's left (right side of camera scene), looking obliquely at the front-left. | $39.8^\circ$ | Oblique perspective. |
| **`Cam0`** | **Far Right-Frontal/Side View**: Positioned further to the subject's left, capturing a steep oblique view. | $68.8^\circ$ | Steep oblique perspective. |
| **`Cam3`** | **Left-Frontal View**: Positioned to the subject's right (left side of camera scene), looking obliquely at the front-right. | $-34.9^\circ$ | Oblique perspective. |
| **`Cam4`** | **Sagittal/Side View**: Positioned to the subject's right, capturing a near-pure side profile of the subject. | $-62.0^\circ$ | **Sagittal-plane analysis** (knee flexion depth, hip/ankle sagittal angles). |

---

## 4. Trial Naming Conventions
The trial folder names for Drop Jumps vary across subjects, showing that we cannot assume a fixed set of suffixes (like `DJ1/2/3`).

For a single camera folder (`Cam0`), the exact drop-jump folders per subject are:
- **`subject2`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ3`
  - *Asymmetric*: `DJAsym1`, `DJAsym4`, `DJAsym5`
- **`subject3`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ4`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym4`
- **`subject4`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ3`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym3`
- **`subject5`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ3`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym3`
- **`subject7`**:
  - *Symmetric*: `DJ2`, `DJ3`, `DJ4`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym3`
- **`subject8`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ3`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym3`
- **`subject10`**:
  - *Symmetric*: `DJ1`, `DJ2`, `DJ3`
  - *Asymmetric*: `DJAsym1`, `DJAsym2`, `DJAsym3`
- **`subject11`**:
  - *Symmetric*: `DJ1`, `DJ4`, `DJ5`
  - *Asymmetric*: `DJAsym3`, `DJAsym4`, `DJAsym5`

**Asset Verification**: Every checked trial folder contains both the raw `{trial}.avi` and the synchronized `{trial}_syncdWithMocap.avi` video files.

---

## 5. Per-Trial Assets Resolution
To construct the validation manifest, the video-to-mocap pipeline requires matching the video recording to its corresponding motion capture and OpenSim inverse kinematics files. For the representative trial **`subject2` / `DJ1`**, the paths are fully resolved as follows:

*   **Synced Video (Cam4 - Sagittal)**:
    `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/VideoData/Session0/Cam4/DJ1/DJ1_syncdWithMocap.avi`
*   **IK Motion File (`.mot`)**:
    *   *Mocap IK*: `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/OpenSimData/Mocap/IK/DJ1.mot`
    *   *Video IK (5-cam high accuracy)*: `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/OpenSimData/Video/OpenPose_highAccuracy/5-cameras/IK/DJ1.mot`
*   **MarkerData File (`.trc`)**:
    `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/MarkerData/Mocap/DJ1.trc`
*   **Force Plate Data**: **Yes, exists**. Located at:
    `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/ForceData/DJ1_forces.mot`
*   **Electromyography (EMG) Data**: **Yes, exists**. Located at:
    `1_raw_datasets/OpenCap/LabValidation_withVideos/subject2/EMGData/DJ1_EMG.sto`

This confirms that the video $\leftrightarrow$ IK $\leftrightarrow$ marker triple can be resolved unambiguously per trial.

---

## 6. Analytical Cohort Count & Anomaly Flagging

### Cohort Anomaly Flag: `subject6`
- **Exclusion**: `subject6` contains a `VideoData` folder, but it only contains a `README.txt` stating: *"This participant chose not to share their videos publicly."*
- **Status**: The folder completely lacks camera/session video files. While mocap `.trc` markers and OpenSim `.mot` IK coordinates exist under `subject6/MarkerData` and `subject6/OpenSimData`, `subject6` **must be excluded** from the main video-based screening cohort.

### Real Analytical Cohort Size (Video-Capable)
Excluding `subject6`, the remaining **8 subjects** each contribute exactly 3 symmetric and 3 asymmetric Drop Jump trials:

$$\text{Cohort Size} = 8 \text{ subjects} \times 6 \text{ trials/subject} = 48 \text{ trials}$$

*   **Symmetric DJ Trials**: 24 trials (3 per subject across 8 subjects)
*   **Asymmetric DJ Trials**: 24 trials (3 per subject across 8 subjects)
*   **Total Cohort Size**: **48 trials**
