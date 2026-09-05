"""
pipeline_wrapper.py
===================
Wraps the existing kinematic screening pipeline for single-video processing.

Replicates the exact algorithms from:
  - phase5a_rehab24_integration.py (pose extraction, smoothing, biomarkers)
  - phase10_rule_screening.py (rule-based screening)
  - phase11_counterfactual_xai.py (counterfactual explanations + MKI)

Does NOT modify or import the original scripts.
"""

import tempfile
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import ctypes
import ctypes.util
import sys

import cv2
import numpy as np
import pandas as pd
import scipy.signal

# ---------------------------------------------------------------------------
# Monkey-patch for MediaPipe Tasks + Python 3.14 on Windows
# MediaPipe's load_raw_library() calls `_shared_lib.free.argtypes = ...`
# but libmediapipe.dll doesn't export `free` (it's in ucrtbase.dll).
# Python 3.14 changed ctypes CDLL attribute resolution behaviour.
# Fix: pre-load the DLL and inject `free` from ucrtbase BEFORE MediaPipe
# tries to access it.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        _mcb = __import__(
            "mediapipe.tasks.python.core.mediapipe_c_bindings",
            fromlist=["mediapipe_c_bindings"],
        )
        # Pre-load the DLL if not yet loaded
        if _mcb._shared_lib is None:
            from importlib import resources as _imp_res
            _lib_ctx = _imp_res.files("mediapipe.tasks.c")
            _abs_path = str(_lib_ctx / "libmediapipe.dll")
            _mcb._shared_lib = ctypes.CDLL(_abs_path)

        # Inject free() from ucrtbase.dll via attribute assignment
        try:
            _mcb._shared_lib.free
        except AttributeError:
            _ucrt = ctypes.CDLL("ucrtbase.dll")
            _mcb._shared_lib.free = _ucrt.free
            _mcb._shared_lib.free.argtypes = [ctypes.c_void_p]
            _mcb._shared_lib.free.restype = None
    except Exception:
        pass

import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

from constants import (
    NOISE_FLOORS,
    TRANSFER_WEIGHTS,
    MEDIAPIPE_CONFIG,
    MEDIAN_WINDOW,
    SG_WINDOW,
    SG_POLYORDER,
    ASSUMED_FPS,
    POSE_CONNECTIONS,
    LOWER_BODY_LANDMARKS,
    BORDERLINE_FRACTION,
)

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "12_models" / "pose_landmarker_heavy.task"
SQUAT_BIOMARKERS_CSV = (
    PROJECT_ROOT / "14_rehab24_outputs" / "biomarkers_per_rep"
    / "rehab24_squat_per_rep_biomarkers.csv"
)
LUNGE_BIOMARKERS_CSV = (
    PROJECT_ROOT / "15_rehab24_lunge_outputs" / "biomarkers_per_rep"
    / "rehab24_lunge_per_rep_biomarkers.csv"
)


# ---------------------------------------------------------------------------
# Data classes for structured results
# ---------------------------------------------------------------------------
@dataclass
class PoseFrame:
    """Pose data for a single frame."""
    frame_index: int
    knee_angle_deg: float
    visible_side_used: str
    angle_status: str
    landmarks: Optional[list] = None  # raw landmark list for overlay
    image_width: int = 0
    image_height: int = 0


@dataclass
class BiomarkerResult:
    """Extracted biomarkers for the video."""
    peak_flexion_deg: float = np.nan
    peak_extension_deg: float = np.nan
    rom_deg: float = np.nan
    start_flexion_deg: float = np.nan
    mean_descent_velocity_deg_per_frame: float = np.nan
    mean_ascent_velocity_deg_per_frame: float = np.nan
    peak_descent_velocity_deg_per_frame: float = np.nan
    peak_ascent_velocity_deg_per_frame: float = np.nan
    jerk_proxy_std: float = np.nan
    descent_frames: int = 0
    ascent_frames: int = 0
    total_rep_frames: int = 0
    phase_status: str = "unknown"
    total_frames: int = 0
    valid_frames: int = 0


@dataclass
class ScreeningResult:
    """Screening decision for the video."""
    flag: str = "NOT_FLAGGED"          # NOT_FLAGGED or SCREENING_POSITIVE
    fired_rules: list = field(default_factory=list)
    # Margins
    peak_flexion_margin: float = 0.0
    rom_margin: float = 0.0
    velocity_margin: float = 0.0
    # Baseline values used
    baseline_peak_flexion: float = np.nan
    baseline_rom: float = np.nan
    baseline_velocity: float = np.nan
    # Thresholds
    threshold_depth: float = np.nan
    threshold_rom: float = np.nan
    threshold_velocity: float = np.nan
    # Measured values
    val_peak_flexion: float = np.nan
    val_rom: float = np.nan
    val_velocity: float = np.nan
    # Source of baseline
    baseline_source: str = "cohort_median"


@dataclass
class XAIResult:
    """Counterfactual XAI explanation."""
    explanations: list = field(default_factory=list)
    mki_text: str = ""


@dataclass
class PipelineResult:
    """Complete pipeline output."""
    success: bool = False
    error_message: str = ""
    pose_frames: list = field(default_factory=list)
    biomarkers: Optional[BiomarkerResult] = None
    screening: Optional[ScreeningResult] = None
    xai: Optional[XAIResult] = None
    overlay_frame: Optional[np.ndarray] = None      # BGR image with pose overlay
    representative_frame_index: int = 0
    smoothed_angles: Optional[pd.Series] = None


# ---------------------------------------------------------------------------
# Helper functions (exact replicas from phase5a)
# ---------------------------------------------------------------------------
def compute_knee_angle(hip, knee, ankle):
    """Compute unsigned 2D knee angle in degrees using arccos of normalised vectors.
    Identical to phase5a_rehab24_integration.py compute_knee_angle()."""
    H = np.array([hip.x, hip.y])
    K = np.array([knee.x, knee.y])
    A = np.array([ankle.x, ankle.y])

    v1 = H - K
    v2 = A - K

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0.0 or norm2 == 0.0:
        return np.nan

    dot_prod = np.dot(v1, v2)
    cos_theta = dot_prod / (norm1 * norm2)
    cos_theta_clipped = np.clip(cos_theta, -1.0, 1.0)
    theta_rad = np.arccos(cos_theta_clipped)
    theta_deg = float(np.degrees(theta_rad))
    return round(theta_deg, 4)


def nan_safe_min(series):
    vals = series.dropna()
    return float(vals.min()) if len(vals) > 0 else np.nan


def nan_safe_max(series):
    vals = series.dropna()
    return float(vals.max()) if len(vals) > 0 else np.nan


def nan_safe_mean(series):
    vals = series.dropna()
    return float(vals.mean()) if len(vals) > 0 else np.nan


# ---------------------------------------------------------------------------
# Stage 1: Pose Extraction
# ---------------------------------------------------------------------------
def extract_poses(video_path: str, progress_callback=None) -> list:
    """Extract MediaPipe poses from every frame of a video.
    Returns list of PoseFrame objects."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"MediaPipe model not found at {MODEL_PATH}. "
            "Please ensure pose_landmarker_heavy.task is in 12_models/."
        )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        cap.release()
        raise ValueError("Video contains zero frames.")

    if total_frames < 10:
        cap.release()
        raise ValueError(
            f"Video too short ({total_frames} frames). "
            "Need at least 10 frames for meaningful analysis."
        )

    # Initialise MediaPipe
    base_options = mp_python.BaseOptions(model_asset_path=str(MODEL_PATH))
    options = mp_vision.PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=mp_vision.RunningMode.IMAGE,
        num_poses=MEDIAPIPE_CONFIG["num_poses"],
        min_pose_detection_confidence=MEDIAPIPE_CONFIG["min_pose_detection_confidence"],
        min_pose_presence_confidence=MEDIAPIPE_CONFIG["min_pose_presence_confidence"],
        min_tracking_confidence=MEDIAPIPE_CONFIG["min_tracking_confidence"],
        output_segmentation_masks=False,
    )
    detector = mp_vision.PoseLandmarker.create_from_options(options)

    pose_frames = []
    f_idx = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            h, w = frame.shape[:2]
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            result = detector.detect(mp_image)

            knee_angle_deg = np.nan
            visible_side_used = "none"
            angle_status = "no_pose_detected"
            landmarks_list = None

            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = result.pose_landmarks[0]
                landmarks_list = landmarks

                # Left limb visibilities
                left_hip_vis = landmarks[23].visibility
                left_knee_vis = landmarks[25].visibility
                left_ankle_vis = landmarks[27].visibility

                # Right limb visibilities
                right_hip_vis = landmarks[24].visibility
                right_knee_vis = landmarks[26].visibility
                right_ankle_vis = landmarks[28].visibility

                left_complete = (
                    left_hip_vis >= 0.5
                    and left_knee_vis >= 0.5
                    and left_ankle_vis >= 0.5
                )
                right_complete = (
                    right_hip_vis >= 0.5
                    and right_knee_vis >= 0.5
                    and right_ankle_vis >= 0.5
                )

                if left_complete:
                    visible_side_used = "left"
                    angle_status = "valid"
                    knee_angle_deg = compute_knee_angle(
                        landmarks[23], landmarks[25], landmarks[27]
                    )
                elif right_complete:
                    visible_side_used = "right"
                    angle_status = "valid"
                    knee_angle_deg = compute_knee_angle(
                        landmarks[24], landmarks[26], landmarks[28]
                    )
                else:
                    angle_status = "chain_incomplete"

            pose_frames.append(PoseFrame(
                frame_index=f_idx,
                knee_angle_deg=knee_angle_deg,
                visible_side_used=visible_side_used,
                angle_status=angle_status,
                landmarks=landmarks_list,
                image_width=w,
                image_height=h,
            ))

            f_idx += 1
            if progress_callback and total_frames > 0:
                progress_callback(f_idx / total_frames)

    finally:
        detector.close()
        cap.release()

    # Validate: need some valid frames
    valid_count = sum(1 for pf in pose_frames if pf.angle_status == "valid")
    if valid_count == 0:
        raise ValueError(
            "No pose detected in any frame. Please ensure the video shows "
            "a person performing the exercise with visible lower body."
        )

    if valid_count < 5:
        raise ValueError(
            f"Only {valid_count} frames had valid pose detection. "
            "Need at least 5 valid frames for reliable analysis."
        )

    return pose_frames


# ---------------------------------------------------------------------------
# Stage 2: Smoothing
# ---------------------------------------------------------------------------
def smooth_trajectory(pose_frames: list) -> pd.Series:
    """Apply 2-stage smoothing (median → Savitzky-Golay).
    Identical to phase5a smoothing logic."""

    raw_angles = pd.Series([pf.knee_angle_deg for pf in pose_frames])

    # Stage 1: Median filter (NaN-aware)
    median_filtered = raw_angles.rolling(
        window=MEDIAN_WINDOW, center=True, min_periods=1
    ).median()
    median_filtered = median_filtered.where(raw_angles.notna(), np.nan)

    # Stage 2: Savitzky-Golay (NaN-aware)
    if median_filtered.notna().any():
        gap_filled = median_filtered.interpolate(
            method="linear", limit_direction="both"
        )
        smoothed_array = scipy.signal.savgol_filter(
            gap_filled.values,
            window_length=min(SG_WINDOW, len(gap_filled)),
            polyorder=min(SG_POLYORDER, min(SG_WINDOW, len(gap_filled)) - 1),
        )
        smoothed = pd.Series(smoothed_array, index=raw_angles.index).where(
            median_filtered.notna(), np.nan
        )
    else:
        smoothed = pd.Series(np.nan, index=raw_angles.index)

    return smoothed.round(4)


# ---------------------------------------------------------------------------
# Stage 3: Biomarker Extraction
# ---------------------------------------------------------------------------
def extract_biomarkers(smoothed_angles: pd.Series) -> BiomarkerResult:
    """Extract biomarkers from smoothed knee angle trajectory.
    Identical to phase5a biomarker logic."""

    result = BiomarkerResult()
    result.total_frames = len(smoothed_angles)
    result.valid_frames = int(smoothed_angles.notna().sum())

    result.peak_flexion_deg = nan_safe_min(smoothed_angles)
    result.peak_extension_deg = nan_safe_max(smoothed_angles)

    if not (np.isnan(result.peak_flexion_deg) or np.isnan(result.peak_extension_deg)):
        result.rom_deg = result.peak_extension_deg - result.peak_flexion_deg
    else:
        result.rom_deg = np.nan

    # Start/contact flexion = 180 - peak_extension
    if not np.isnan(result.peak_extension_deg):
        result.start_flexion_deg = 180.0 - result.peak_extension_deg

    # Peak flexion frame
    if smoothed_angles.notna().any():
        bottom_frame_idx = smoothed_angles.idxmin()
    else:
        bottom_frame_idx = None

    first_valid = smoothed_angles.first_valid_index()
    last_valid = smoothed_angles.last_valid_index()

    # Phase detection
    nan_count = smoothed_angles.isna().sum()
    pct_nan = nan_count / result.total_frames if result.total_frames > 0 else 1.0

    is_failed = False
    if pct_nan > 0.30:
        is_failed = True
    if bottom_frame_idx is None or first_valid is None or last_valid is None:
        is_failed = True
    elif bottom_frame_idx == first_valid or bottom_frame_idx == last_valid:
        is_failed = True

    if is_failed:
        result.phase_status = "failed"
    else:
        result.phase_status = "ok"
        result.descent_frames = int(bottom_frame_idx - first_valid)
        result.ascent_frames = int(last_valid - bottom_frame_idx)
        result.total_rep_frames = result.descent_frames + result.ascent_frames

        # Velocity computation
        delta_angle = pd.Series(np.diff(smoothed_angles), index=smoothed_angles.index[:-1])
        descent_deltas = delta_angle.loc[first_valid : bottom_frame_idx - 1]
        ascent_deltas = delta_angle.loc[bottom_frame_idx : last_valid - 1]

        result.peak_descent_velocity_deg_per_frame = nan_safe_min(descent_deltas)
        result.peak_ascent_velocity_deg_per_frame = nan_safe_max(ascent_deltas)
        result.mean_descent_velocity_deg_per_frame = nan_safe_mean(descent_deltas)
        result.mean_ascent_velocity_deg_per_frame = nan_safe_mean(ascent_deltas)

    # Jerk proxy
    second_diff = np.diff(np.diff(smoothed_angles))
    second_diff_clean = second_diff[~np.isnan(second_diff)]
    if len(second_diff_clean) > 1:
        result.jerk_proxy_std = float(np.std(second_diff_clean, ddof=1))
    else:
        result.jerk_proxy_std = np.nan

    return result


# ---------------------------------------------------------------------------
# Stage 4: Baseline Loading
# ---------------------------------------------------------------------------
def load_cohort_baseline(exercise_type: str) -> dict:
    """Load cohort median baseline from pre-computed REHAB24 biomarkers.
    Used as fallback when no personal baseline exists."""

    if exercise_type.lower() == "squat" and SQUAT_BIOMARKERS_CSV.exists():
        df = pd.read_csv(SQUAT_BIOMARKERS_CSV)
    elif exercise_type.lower() == "lunge" and LUNGE_BIOMARKERS_CSV.exists():
        df = pd.read_csv(LUNGE_BIOMARKERS_CSV)
    else:
        # Default baseline for drop-jump or missing data
        return {
            "peak_flexion": 70.0,
            "rom": 100.0,
            "velocity": 50.0,
        }

    # Filter to correct reps only for baseline
    df_correct = df[df["correctness_label"] == 1]
    if len(df_correct) == 0:
        df_correct = df

    baseline = {
        "peak_flexion": float(df_correct["peak_flexion_deg"].median()),
        "rom": float(df_correct["rom_deg"].median()),
        "velocity": abs(float(df_correct["mean_descent_velocity_deg_per_frame"].median())) * ASSUMED_FPS,
    }
    return baseline


# ---------------------------------------------------------------------------
# Stage 5: Rule-Based Screening
# ---------------------------------------------------------------------------
def run_screening(biomarkers: BiomarkerResult, baseline: dict,
                  baseline_source: str = "cohort_median") -> ScreeningResult:
    """Apply rule-based screening. Identical logic to phase10_rule_screening.py."""

    result = ScreeningResult()
    result.baseline_source = baseline_source
    result.baseline_peak_flexion = baseline["peak_flexion"]
    result.baseline_rom = baseline["rom"]
    result.baseline_velocity = baseline["velocity"]

    # Measured values
    val_peak = biomarkers.peak_flexion_deg
    val_rom = biomarkers.rom_deg
    val_velocity = abs(biomarkers.mean_descent_velocity_deg_per_frame) * ASSUMED_FPS

    result.val_peak_flexion = val_peak
    result.val_rom = val_rom
    result.val_velocity = val_velocity

    # Thresholds (identical to phase10)
    t_depth = baseline["peak_flexion"] - NOISE_FLOORS["peak_flexion"]
    t_rom = baseline["rom"] + NOISE_FLOORS["rom"]
    t_velocity = baseline["velocity"] + NOISE_FLOORS["velocity"]

    result.threshold_depth = t_depth
    result.threshold_rom = t_rom
    result.threshold_velocity = t_velocity

    fired_rules = []

    # Rule 1: EXCESS_DEPTH
    if not np.isnan(val_peak) and val_peak < t_depth:
        fired_rules.append("EXCESS_DEPTH")
        result.peak_flexion_margin = round(t_depth - val_peak, 4)

    # Rule 2: EXCESS_VELOCITY
    if not np.isnan(val_velocity) and val_velocity > t_velocity:
        fired_rules.append("EXCESS_VELOCITY")
        result.velocity_margin = round(val_velocity - t_velocity, 4)

    # Rule 3: EXCESS_ROM
    if not np.isnan(val_rom) and val_rom > t_rom:
        fired_rules.append("EXCESS_ROM")
        result.rom_margin = round(val_rom - t_rom, 4)

    result.fired_rules = fired_rules
    result.flag = "SCREENING_POSITIVE" if len(fired_rules) > 0 else "NOT_FLAGGED"

    return result


# ---------------------------------------------------------------------------
# Stage 6: Counterfactual XAI
# ---------------------------------------------------------------------------
def generate_xai(screening: ScreeningResult) -> XAIResult:
    """Generate counterfactual explanations.
    Identical logic to phase11_counterfactual_xai.py."""

    result = XAIResult()

    if screening.flag != "SCREENING_POSITIVE":
        return result

    explanations = []

    # EXCESS_DEPTH
    if "EXCESS_DEPTH" in screening.fired_rules:
        margin = screening.peak_flexion_margin
        val = screening.val_peak_flexion
        thresh = screening.threshold_depth
        buffer_val = 0.5 * NOISE_FLOORS["peak_flexion"]
        confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"

        text = (
            f"Depth margin: {margin:.2f}\u00b0. "
            f"Peak knee flexion ({val:.2f}\u00b0) was {margin:.2f}\u00b0 below "
            f"the baseline threshold ({thresh:.2f}\u00b0). "
            f"Had the peak flexion been at least {thresh:.2f}\u00b0 "
            f"(a shallower bend of {margin:.2f}\u00b0 less depth), "
            f"the EXCESS_DEPTH flag would not have fired."
        )
        if confidence != "HIGH":
            text += (
                f" Note: The margin ({margin:.2f}\u00b0) is near the "
                f"validated measurement uncertainty boundary. "
                f"Interpret with caution."
            )
        explanations.append({
            "rule": "EXCESS_DEPTH",
            "margin": margin,
            "confidence": confidence,
            "text": text,
        })

    # EXCESS_VELOCITY
    if "EXCESS_VELOCITY" in screening.fired_rules:
        margin = screening.velocity_margin
        val = screening.val_velocity
        thresh = screening.threshold_velocity
        buffer_val = 0.5 * NOISE_FLOORS["velocity"]
        confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"

        text = (
            f"Velocity margin: {margin:.2f}\u00b0/s. "
            f"Descent velocity ({val:.2f}\u00b0/s) was {margin:.2f}\u00b0/s above "
            f"the baseline threshold ({thresh:.2f}\u00b0/s). "
            f"Had the velocity been no more than {thresh:.2f}\u00b0/s "
            f"({margin:.2f}\u00b0/s slower), "
            f"the EXCESS_VELOCITY flag would not have fired."
        )
        if confidence != "HIGH":
            text += (
                f" Note: The margin ({margin:.2f}\u00b0/s) is near the "
                f"validated measurement uncertainty boundary. "
                f"Interpret with caution."
            )
        explanations.append({
            "rule": "EXCESS_VELOCITY",
            "margin": margin,
            "confidence": confidence,
            "text": text,
        })

    # EXCESS_ROM
    if "EXCESS_ROM" in screening.fired_rules:
        margin = screening.rom_margin
        val = screening.val_rom
        thresh = screening.threshold_rom
        buffer_val = 0.5 * NOISE_FLOORS["rom"]
        confidence = "HIGH" if margin > buffer_val else "LOW (Near Noise Floor)"

        text = (
            f"ROM margin: {margin:.2f}\u00b0. "
            f"Range of motion ({val:.2f}\u00b0) was {margin:.2f}\u00b0 above "
            f"the baseline threshold ({thresh:.2f}\u00b0). "
            f"Had the ROM been no more than {thresh:.2f}\u00b0 "
            f"({margin:.2f}\u00b0 less excursion), "
            f"the EXCESS_ROM flag would not have fired."
        )
        if confidence != "HIGH":
            text += (
                f" Note: The margin ({margin:.2f}\u00b0) is near the "
                f"validated measurement uncertainty boundary. "
                f"Interpret with caution."
            )
        explanations.append({
            "rule": "EXCESS_ROM",
            "margin": margin,
            "confidence": confidence,
            "text": text,
        })

    result.explanations = explanations

    # Minimal Kinematic Intervention (MKI)
    depth_margin = screening.peak_flexion_margin
    rom_margin = screening.rom_margin
    vel_margin = screening.velocity_margin

    mki_text = ""
    if "EXCESS_DEPTH" in screening.fired_rules and "EXCESS_ROM" in screening.fired_rules:
        mki_val = max(depth_margin, rom_margin)
        mki_text = (
            f"Minimal Kinematic Intervention: the screening flags would not have "
            f"fired if peak knee flexion had been at least {mki_val:.2f}\u00b0 "
            f"shallower (which, assuming ROM scales with depth under a constant "
            f"standing extension, would simultaneously clear both EXCESS_DEPTH "
            f"and EXCESS_ROM)"
        )
        if "EXCESS_VELOCITY" in screening.fired_rules:
            mki_text += f" AND descent velocity had been at least {vel_margin:.2f}\u00b0/s slower."
        else:
            mki_text += "."
    elif "EXCESS_DEPTH" in screening.fired_rules:
        mki_text = (
            f"Minimal Kinematic Intervention: reduce depth deviation by "
            f"{depth_margin:.2f}\u00b0 to bring within screening-clean band"
        )
        if "EXCESS_VELOCITY" in screening.fired_rules:
            mki_text += f" AND reduce descent velocity by {vel_margin:.2f}\u00b0/s."
        else:
            mki_text += "."
    elif "EXCESS_ROM" in screening.fired_rules:
        mki_text = (
            f"Minimal Kinematic Intervention: reduce range of motion by "
            f"{rom_margin:.2f}\u00b0 to bring within screening-clean band"
        )
        if "EXCESS_VELOCITY" in screening.fired_rules:
            mki_text += f" AND reduce descent velocity by {vel_margin:.2f}\u00b0/s."
        else:
            mki_text += "."
    elif "EXCESS_VELOCITY" in screening.fired_rules:
        mki_text = (
            f"Minimal Kinematic Intervention: reduce descent velocity by "
            f"{vel_margin:.2f}\u00b0/s to bring within screening-clean band."
        )

    result.mki_text = mki_text
    return result


# ---------------------------------------------------------------------------
# Stage 7: Pose Overlay Frame
# ---------------------------------------------------------------------------
def generate_overlay_frame(video_path: str, pose_frames: list,
                           smoothed_angles: pd.Series) -> tuple:
    """Generate a representative frame with pose overlay.
    Selects the frame at peak flexion (deepest point of the movement).
    Returns (overlay_image_bgr, frame_index)."""

    # Find representative frame: peak flexion (minimum angle)
    if smoothed_angles.notna().any():
        rep_idx = int(smoothed_angles.idxmin())
    else:
        # Fallback to middle frame
        rep_idx = len(pose_frames) // 2

    # Ensure the frame has landmarks
    if rep_idx < len(pose_frames) and pose_frames[rep_idx].landmarks is None:
        # Find nearest frame with landmarks
        for offset in range(1, len(pose_frames)):
            for candidate in [rep_idx + offset, rep_idx - offset]:
                if 0 <= candidate < len(pose_frames) and pose_frames[candidate].landmarks is not None:
                    rep_idx = candidate
                    break
            else:
                continue
            break

    # Read the specific frame from video
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, rep_idx)
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return None, rep_idx

    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Draw skeleton if we have landmarks
    pf = pose_frames[rep_idx] if rep_idx < len(pose_frames) else None
    if pf and pf.landmarks:
        landmarks = pf.landmarks

        # Draw connections
        for a, b in POSE_CONNECTIONS:
            lm_a = landmarks[a]
            lm_b = landmarks[b]
            if lm_a.visibility >= 0.5 and lm_b.visibility >= 0.5:
                pt_a = (int(lm_a.x * w), int(lm_a.y * h))
                pt_b = (int(lm_b.x * w), int(lm_b.y * h))
                cv2.line(overlay, pt_a, pt_b, color=(0, 255, 0), thickness=2)

        # Draw landmark dots
        for lm in landmarks:
            if lm.visibility >= 0.5:
                px = int(lm.x * w)
                py = int(lm.y * h)
                cv2.circle(overlay, (px, py), 4, (0, 0, 255), -1)

    return overlay, rep_idx


# ---------------------------------------------------------------------------
# Full Pipeline Runner
# ---------------------------------------------------------------------------
def run_pipeline(video_path: str, exercise_type: str,
                 subject_id: str = "",
                 progress_callback=None) -> PipelineResult:
    """Run the complete screening pipeline on a single uploaded video.

    Args:
        video_path: Path to the video file on disk.
        exercise_type: One of 'Squat', 'Lunge', 'Drop-Jump'.
        subject_id: Optional subject ID for personalised baseline.
        progress_callback: Callable(stage_name: str, progress: float)

    Returns:
        PipelineResult with all outputs.
    """
    result = PipelineResult()

    try:
        # --- Stage 1: Pose Extraction ---
        def pose_progress(frac):
            if progress_callback:
                progress_callback("Extracting pose...", frac * 0.4)

        if progress_callback:
            progress_callback("Extracting pose...", 0.0)

        pose_frames = extract_poses(video_path, progress_callback=pose_progress)
        result.pose_frames = pose_frames

        # --- Stage 2: Smoothing ---
        if progress_callback:
            progress_callback("Computing biomarkers...", 0.4)

        smoothed_angles = smooth_trajectory(pose_frames)
        result.smoothed_angles = smoothed_angles

        # --- Stage 3: Biomarker Extraction ---
        if progress_callback:
            progress_callback("Computing biomarkers...", 0.5)

        biomarkers = extract_biomarkers(smoothed_angles)
        result.biomarkers = biomarkers

        if biomarkers.phase_status == "failed":
            # Still continue — we can report what we have
            pass

        # --- Stage 4: Baseline + Screening ---
        if progress_callback:
            progress_callback("Running screening layer...", 0.6)

        baseline = load_cohort_baseline(exercise_type)
        baseline_source = "cohort_median"

        screening = run_screening(biomarkers, baseline, baseline_source)
        result.screening = screening

        # --- Stage 5: XAI ---
        if progress_callback:
            progress_callback("Generating XAI explanation...", 0.8)

        xai = generate_xai(screening)
        result.xai = xai

        # --- Stage 6: Overlay frame ---
        if progress_callback:
            progress_callback("Generating pose overlay...", 0.9)

        overlay_frame, rep_frame_idx = generate_overlay_frame(
            video_path, pose_frames, smoothed_angles
        )
        result.overlay_frame = overlay_frame
        result.representative_frame_index = rep_frame_idx

        result.success = True

        if progress_callback:
            progress_callback("Complete", 1.0)

    except ValueError as e:
        result.success = False
        result.error_message = str(e)
    except FileNotFoundError as e:
        result.success = False
        result.error_message = str(e)
    except Exception as e:
        result.success = False
        result.error_message = f"Unexpected error: {str(e)}"

    return result
