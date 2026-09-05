"""
constants.py
============
Hardcoded constants for the kinematic screening dashboard.
All noise floors, transfer weights, and design tokens live here.
"""

# ---------------------------------------------------------------------------
# Phase 7 Noise Floors (95% CI = ±1.96 * SD_projection)
# ---------------------------------------------------------------------------
NOISE_FLOORS = {
    "peak_flexion": 11.9885,    # degrees
    "rom": 23.1666,             # degrees
    "velocity": 40.8615,        # degrees/second
}

# ---------------------------------------------------------------------------
# Uncertainty Transfer Weights (from cross-exercise projection analysis)
# ---------------------------------------------------------------------------
TRANSFER_WEIGHTS = {
    "contact_start_flexion": 0.2263,   # 22.63%
    "peak_flexion": 0.5715,            # 57.15%
    "rom": 0.1530,                     # 15.30%
    "velocity": 0.0492,               # 4.92%
}

WEIGHT_LABELS = {
    "contact_start_flexion": "Contact/Start Flexion",
    "peak_flexion": "Peak Flexion",
    "rom": "Range of Motion",
    "velocity": "Descent Velocity",
}

WEIGHT_PERCENTAGES = {
    "contact_start_flexion": 22.63,
    "peak_flexion": 57.15,
    "rom": 15.30,
    "velocity": 4.92,
}

# ---------------------------------------------------------------------------
# MediaPipe Configuration
# ---------------------------------------------------------------------------
MEDIAPIPE_CONFIG = {
    "num_poses": 1,
    "min_pose_detection_confidence": 0.5,
    "min_pose_presence_confidence": 0.5,
    "min_tracking_confidence": 0.5,
}

# Smoothing parameters (match phase5a exactly)
MEDIAN_WINDOW = 5
SG_WINDOW = 7
SG_POLYORDER = 2

# Video FPS assumed for velocity conversion (deg/frame -> deg/s)
ASSUMED_FPS = 30.0

# ---------------------------------------------------------------------------
# Dashboard Disclaimer
# ---------------------------------------------------------------------------
DISCLAIMER_TEXT = (
    "This framework performs kinematic screening based on patterns previously "
    "associated with injury risk in biomechanics literature. It does NOT "
    "predict individual injury outcomes. Clinical interpretation requires a "
    "qualified practitioner."
)

# ---------------------------------------------------------------------------
# Design Palette
# ---------------------------------------------------------------------------
PALETTE = {
    "primary": "#1E2761",       # Deep navy
    "accent": "#C89B3C",        # Gold
    "background": "#FAFAFA",    # Off-white
    "secondary_text": "#5C5C5C", # Muted grey
    "pass_green": "#2E7D32",
    "flag_red": "#C62828",
    "amber": "#F9A825",
    "white": "#FFFFFF",
}

# ---------------------------------------------------------------------------
# Screening deviation thresholds for colour coding
# ---------------------------------------------------------------------------
# Borderline = within 0.5 * noise floor of the threshold
BORDERLINE_FRACTION = 0.5

# ---------------------------------------------------------------------------
# Supported video formats
# ---------------------------------------------------------------------------
SUPPORTED_VIDEO_TYPES = ["mp4", "mov", "avi"]

# ---------------------------------------------------------------------------
# Exercise types
# ---------------------------------------------------------------------------
EXERCISE_TYPES = ["Squat", "Lunge", "Drop-Jump"]

# BlazePose skeleton connections for overlay drawing
POSE_CONNECTIONS = [
    # Face
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Torso
    (11, 12), (11, 23), (12, 24), (23, 24),
    # Left arm
    (11, 13), (13, 15),
    (15, 17), (15, 19), (15, 21), (17, 19),
    # Right arm
    (12, 14), (14, 16),
    (16, 18), (16, 20), (16, 22), (18, 20),
    # Left leg
    (23, 25), (25, 27),
    (27, 29), (29, 31), (27, 31),
    # Right leg
    (24, 26), (26, 28),
    (28, 30), (30, 32), (28, 32),
]

# Lower body landmark indices for completeness checking
LOWER_BODY_LANDMARKS = {
    23: "left_hip",
    24: "right_hip",
    25: "left_knee",
    26: "right_knee",
    27: "left_ankle",
    28: "right_ankle",
}
