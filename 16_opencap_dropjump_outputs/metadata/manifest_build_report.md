# OpenCap Drop Jump Manifest Build Report

This report summarizes the creation of the OpenCap Drop Jump dataset manifest, including cohort coverage, camera assignments, resolved files, and validation stills.

---

## 1. Cohort Summary
*   **Total Video-Capable Subjects**: 8 (subject2, subject3, subject4, subject5, subject7, subject8, subject10, subject11).
    *   *Note: `subject6` was excluded from this cohort as the videos are private.*
*   **Total Drop Jump Trials**: 48
*   **Symmetric Trials**: 24
*   **Asymmetric Trials**: 24

### Per-Subject Trial Breakdown
| Subject ID | Symmetric Trials | Asymmetric Trials |
| :--- | :---: | :---: |
| subject10 | 3 | 3 |
| subject11 | 3 | 3 |
| subject2 | 3 | 3 |
| subject3 | 3 | 3 |
| subject4 | 3 | 3 |
| subject5 | 3 | 3 |
| subject7 | 3 | 3 |
| subject8 | 3 | 3 |

---

## 2. Camera Selection & Verification
*   **Default Camera**: `Cam4` was selected as the primary sagittal view for all subjects where available.
*   **Exceptions**:
    *   **subject8**: Only `Cam0` was present on disk. It was used consistently for this subject.

---

## 3. Synced Videos & Mocap IK Verification
*   **Synced Video Status**: All trials have their synchronized video (`_syncdWithMocap.avi`) present.
*   **Mocap IK Status**: All trials have their corresponding ground-truth Mocap IK `.mot` files present.
*   **Force Data Status**: All trials have their ground-truth ForceData `.mot` files present (ready for force-sync validation).

---

## 4. Verification Stills Saved
The following still frames have been extracted and saved to `16_opencap_dropjump_outputs/cam_angle_check/manifest_check/` to visually verify the sagittal profile view before processing:

- **subject2_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject2_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject2_Cam4_DJ1.png)
- **subject3_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject3_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject3_Cam4_DJ1.png)
- **subject4_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject4_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject4_Cam4_DJ1.png)
- **subject5_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject5_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject5_Cam4_DJ1.png)
- **subject7_Cam4_DJ2.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject7_Cam4_DJ2.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject7_Cam4_DJ2.png)
- **subject8_Cam0_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject8_Cam0_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject8_Cam0_DJ1.png)
- **subject10_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject10_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject10_Cam4_DJ1.png)
- **subject11_Cam4_DJ1.png**: Located at [16_opencap_dropjump_outputs/cam_angle_check/manifest_check/subject11_Cam4_DJ1.png](file:///C:\Users\shiro\OneDrive\Desktop\Python files\BIOMECHANICAL ANALYSIS OF INJURY\16_opencap_dropjump_outputs\cam_angle_check\manifest_check\subject11_Cam4_DJ1.png)
