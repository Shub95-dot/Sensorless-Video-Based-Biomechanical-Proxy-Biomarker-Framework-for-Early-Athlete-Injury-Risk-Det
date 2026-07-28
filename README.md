# Sensorless Markerless Screening Framework: A Monocular Kinematic Screening Pipeline with Uncertainty-Weighted Transfer and Counterfactual XAI

This project delivers a validated sensorless, single-camera markerless kinematic screening framework that extracts comparable sagittal-plane movement patterns across bilateral squats, unilateral lunges, and dynamic drop-jump landings using consumer-grade video. By mapping optoelectronic limits of agreement to transferable projection uncertainty, the framework propagates validated confidence bounds to qualify screening decisions while providing faithful-by-construction counterfactual explanations for rule-based flags.

---

## 📁 Repository Structure Map

| Folder | Content | Dissertation Chapter |
| :--- | :--- | :---: |
| **`1_raw_datasets`** | REHAB24-6, OpenCap, Penn Action raw video/frame data | Chs 4, 5, 6 |
| **`3_metadata`** | Dataset manifests and inclusion audits | Ch 2 |
| **`4_pose_outputs`** | MediaPipe pose extraction outputs | Ch 2 |
| **`5_biomarkers`** | Computed knee-angle biomarkers | Ch 2 |
| **`6_visualizations`** | Diagnostic figures | Chs 4, 5, 6 |
| **`8_xai`** | Deprecated post-hoc SHAP/LIME scaffold (preserved per Ch 12/14 narrative) | Chs 12, 14 |
| **`11_scripts`** | Pipeline processing scripts | Ch 2 |
| **`12_models`** | MediaPipe pose landmarker model | Ch 2 |
| **`14_rehab24_outputs`** | REHAB24-6 squat outputs | Ch 4 |
| **`15_rehab24_lunge_outputs`** | REHAB24-6 lunge outputs | Ch 5 |
| **`16_opencap_dropjump_outputs`** | OpenCap drop-jump validation outputs | Ch 6 |
| **`17_uncertainty_framework_outputs`** | Uncertainty framework outputs | Ch 8 |
| **`18_personalised_baseline_outputs`** | Personalised baseline outputs | Ch 9 |
| **`19_digital_twin_outputs`** | Digital twin outputs | Ch 11 |
| **`20_screening_outputs`** | Rule-based screening outputs | Ch 10 |
| **`21_xai_outputs`** | Counterfactual XAI outputs | Ch 12 |
| **`22_dissertation_writing`** | Dissertation chapters and appendices | All |
| **`23_temporal_model_outputs`** | LSTM temporal model outputs | Ch 13 |

---

## 🎓 Academic Context

*   **Degree / Module**: MSc Dissertation Project, Southampton Solent University (Module `COM726`).
*   **Submission Date**: September 2026.
*   **Academic Supervisor**: Dr Raza Hasan.

---

## 📚 Primary Dataset Citations

1.  **REHAB24-6**: Physical therapy movement dataset (squat and lunge cohorts).
2.  **OpenCap**: Uhlrich et al. (2023), *"OpenCap: 3D kinematics and dynamics from smartphone video"*, PLOS Computational Biology / Nature Communications dataset.
3.  **Penn Action**: Zhang, Zhu & Derpanis (2013), *"From Actemes to Action: A Strongly-Supervised Representation for Detailed Action Understanding"*, ICCV 2013.
