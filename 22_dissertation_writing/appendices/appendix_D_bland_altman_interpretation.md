# Appendix D: Bland-Altman Biomarker Interpretation

This appendix provides detailed biomarker-level interpretation for the Bland-Altman agreement analysis on the OpenCap drop-jump dataset ($n = 48$ trials across 8 subjects), supplementing Chapter 6 (Section 6.3) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.1. Biomarker #1: Contact Flexion
* **Metrics**: Video Mean = $13.51^\circ$, IK Mean = $20.20^\circ$, Bias = $-6.69^\circ$, 95% LoA = $[-26.77^\circ, 13.39^\circ]$, Pearson $r = 0.3209$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Accurate (low bias, moderate variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Initial contact occurs at shallow flexion ($\sim 20^\circ$). In this upright pose, 2D sagittal plane foreshortening is minimal compared to deep flexion, yielding a small systematic underestimation bias of $-6.69^\circ$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. However, ground impact induces transient pose tracking jitter, causing moderate trial variance ($\text{LoA} \text{ width} = 40.16^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.2. Biomarker #2: Peak Landing Flexion
* **Metrics**: Video Mean = $120.23^\circ$, IK Mean = $100.51^\circ$, Bias = $+19.72^\circ$ (peak-to-peak) / $+10.52^\circ$ (static timing-clean), 95% LoA = $[7.73^\circ, 31.71^\circ]$, Pearson $r = 0.8238$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Biased-systematic (constant overestimation, low variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Peak landing flexion exhibits a strong linear correlation ($r = 0.8238$) between video and 3D motion capture, demonstrating that monocular tracking reliably preserves rank order across subjects [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. The measurement exhibits a systematic positive bias ($+19.72^\circ$ uncorrected peak-to-peak; $+10.52^\circ$ timing-clean static frame) driven by out-of-plane projection foreshortening as the knee flexes deeply ($\sim 100^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. Because error distribution is tightly bounded with low residual variance, this bias represents a predictable geometric artefact suitable for downstream calibration [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.3. Biomarker #3: Landing Range of Motion (ROM)
* **Metrics**: Video Mean = $106.72^\circ$, IK Mean = $80.31^\circ$, Bias = $+26.41^\circ$, 95% LoA = $[2.34^\circ, 50.48^\circ]$, Pearson $r = 0.4020$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: Biased-systematic (constant overestimation, high variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Landing ROM is calculated as $\text{ROM} = \text{PA1} - \text{IC1}$ [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because peak flexion (PA1) is systematically overestimated ($+19.72^\circ$) while contact flexion (IC1) is systematically underestimated ($-6.69^\circ$), these opposing directional biases compound mathematically ($\Delta = +19.72^\circ - (-6.69^\circ) = +26.41^\circ$) [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. This offset propagation increases measurement variance ($\text{LoA} \text{ width} = 48.14^\circ$), making raw uncalibrated monocular ROM estimates unreliable without baseline offset correction [source: 16_opencap_dropjump_outputs/phase6_final_report.md].

---

## D.4. Biomarker #6: Flexion Loading Rate
* **Metrics**: Video Mean = $286.14^\circ/\text{s}$, IK Mean = $272.84^\circ/\text{s}$, Bias = $+13.30^\circ/\text{s}$, 95% LoA = $[-115.92^\circ/\text{s}, 142.51^\circ/\text{s}]$, Pearson $r = 0.6076$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: High-variance (moderate bias, extremely high variance) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Flexion loading rate quantifies average angular velocity during early landing absorption ($IC1 \rightarrow \text{early absorption}$) [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Although cohort mean velocity bias is small ($+13.30^\circ/\text{s}$), 95% limits of agreement span $258.43^\circ/\text{s}$ [source: 16_opencap_dropjump_outputs/phase6_final_report.md]. High variance stems from sub-frame sampling differences between 60 FPS video and reference signals (100 Hz Mocap / 2000 Hz force plates), combined with numerical differentiation noise during rapid landing deceleration [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].

---

## D.5. Biomarker #5: Inter-Limb Asymmetry
* **Metrics**: IK Mean = $2.07^\circ$ (SD = $2.06^\circ$); Video measurement = N/A [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Trustworthiness Verdict**: IK-only, not video-validated (far-leg contralateral occlusion) [source: 16_opencap_dropjump_outputs/phase6_final_report.md].
* **Biomechanical Interpretation**: Inter-limb asymmetry evaluates bilateral peak flexion differences [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. In single-camera sagittal video recordings, the ipsilateral (closer) limb maintains $\sim 100\%$ landmark tracking visibility, whereas the contralateral (farther) limb drops to $\sim 0\%$ visibility during deep landing absorption due to self-occlusion [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md]. Because monocular tracking cannot resolve occluded landmarks, asymmetry is demoted to a 3D Mocap IK reference metric and excluded from video-only evaluation rules [source: 16_opencap_dropjump_outputs/metadata/phase6_stage0_report.md].
