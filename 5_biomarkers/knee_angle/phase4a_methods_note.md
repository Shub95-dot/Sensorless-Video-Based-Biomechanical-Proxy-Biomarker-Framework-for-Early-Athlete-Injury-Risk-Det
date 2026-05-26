# Phase 4A Knee Angle Extraction Methods Note

Knee angle was computed using 2D **normalized** MediaPipe hip-knee-ankle coordinates. This is an apparent **2D inter-segmental knee angle** derived from the sagittal-plane projection visible in each frame. It is **not** a clinical 3D knee flexion-extension measure. It is **not** knee valgus. 

The angle is computed as an **unsigned inter-segmental angle** (via `arccos` of the normalized dot product) and is therefore invariant to MediaPipe's image-space y-axis orientation. 

- **Gold_Tier** frames support bilateral knee angle computation.
- **Unilateral_Tier** frames support visible-side knee angle computation.
- **Rejected_Tier** frames were excluded from calculation.

## Plausible Range and Outlier Policy
Plausible range used for outlier flagging was 40°–185° (rationale: standing extension approaches ~180°, deep squat flexion rarely below ~40°; values outside this range likely reflect landmark localisation error rather than true anatomy). Outlier flags are informational, not rejections — outlier rows remain in the main CSV with `angle_status = computed`.
