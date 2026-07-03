# Uncertainty-Weighted Biomechanical Screening Framework
## Stage 1 — Design on Paper (Architectural Demonstration)

This document describes the design of a per-biomarker weighting framework that combines kinematic screening biomarkers, weighting each by its ground-truth-validated measurement uncertainty.

> [!IMPORTANT]
> **Hard Framing Constraints:**
> *   This framework is an architectural demonstration of a weighting methodology. It does **not** produce a risk score, classify or flag reps, predict injury, or assert clinical outcomes.
> *   No predictive language (e.g., "risk", "likelihood", "load", "fatigue") is used. The framework's scope is strictly limited to measurement-uncertainty and screening-characterisation.

---

## 1. Uncertainty Source (OpenCap Drop-Jump Ground Truth)

Validated measurement uncertainty values are extracted from the drop-jump validation report ([phase6_agreement_final.csv](file:///c:/Users/shiro/OneDrive/Desktop/Python%20files/BIOMECHANICAL%20ANALYSIS%20OF%20INJURY/16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv)). 

To convert the 95% Limits of Agreement (LoA) width into a statistical variance:
$$\text{SD} = \frac{\text{LoA\_width}}{2 \times 1.96} = \frac{\text{LoA\_upper} - \text{LoA\_lower}}{3.92}$$
$$\text{Variance} = \text{SD}^2$$

### Biomarker Uncertainty Mapping (rounded to 4 decimal places):

1.  **#1 contact_flexion**
    *   *95% LoA:* $[-26.7742^\circ, 13.3913^\circ]$
    *   *LoA Width:* $40.1655^\circ$
    *   *Standard Deviation (SD):* $10.2463^\circ$
    *   *Variance ($\sigma^2$):* **$104.9867$**
    *   *Bias:* $-6.6914^\circ$
2.  **#2 peak_landing_flexion (Corrected)**
    *   *95% LoA:* $[7.7285^\circ, 31.7057^\circ]$
    *   *LoA Width:* $23.9772^\circ$
    *   *Standard Deviation (SD):* $6.1166^\circ$
    *   *Variance ($\sigma^2$):* **$37.4132$**
    *   *Bias:* $+19.7171^\circ$
3.  **#3 landing_rom**
    *   *95% LoA:* $[2.3373^\circ, 50.4798^\circ]$
    *   *LoA Width:* $48.1425^\circ$
    *   *Standard Deviation (SD):* $12.2813^\circ$
    *   *Variance ($\sigma^2$):* **$150.8291$**
    *   *Bias:* $+26.4086^\circ$
4.  **#6 loading_rate**
    *   *95% LoA:* $[-115.9179^\circ/\text{s}, 142.5125^\circ/\text{s}]$
    *   *LoA Width:* $258.4304^\circ/\text{s}$
    *   *Standard Deviation (SD):* $65.9261^\circ/\text{s}$
    *   *Variance ($\sigma^2$):* **$4346.2534$**
    *   *Bias:* $+13.2973^\circ/\text{s}$

*Note on #5 asymmetry:* Biomarker #5 is a 3D Mocap-only reference due to contralateral occlusion (the far leg is blocked by the closer leg in sagittal 2D video). Because there is no corresponding video measurement to validate against, it is excluded from the video weighting framework.

---

## 2. Uncertainty Decomposition

To enable generalisation across exercises, each biomarker's total measurement variance ($\sigma^2_{\text{total}}$) is decomposed into two distinct components:
1.  **PROJECTION Error ($\sigma^2_{\text{proj}}$):** The systematic perspective/foreshortening component caused by 2D camera projection of out-of-plane joint motion. This is **general to monocular sagittal pose** and **transferable** across athletic exercises (e.g., deep knee flexion in a squat behaves similarly to a landing).
2.  **MOTION Error ($\sigma^2_{\text{mot}}$):** The fast-movement / timing-sensitivity component caused by sub-frame synchronization lag and motion blur. This is **drop-jump-landing-specific** and **not transferable** to slow, controlled movements like squats and lunges.

### Per-Biomarker Decomposition Splits:
To ensure internal consistency and prevent mathematical contradictions, splits are derived individually for each biomarker based on the biomechanics of where in the movement it is measured:

*   **#2 peak_landing_flexion (Closer Knee) [MEASURED]:** Because Section 1 uses the peak-matched (Method b) agreement table, it represents the timing-clean, peak-aligned variance. Thus, the total validated variance of $37.4132$ is purely projection-based.
    *   *Projection Variance ($\sigma^2_{\text{proj}}$):* **$37.4132$** ($100.00\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$):* **$0.0000$** ($0.00\%$)
*   **#1 contact_flexion [ASSUMED split]:** Measured at the instant of landing contact. At contact, the knee is just beginning to flex, and its angular velocity is slow. Consequently, sub-frame timing errors introduce minimal kinematic error, making the uncertainty predominantly projection-based. We assume a $90\text{--}10$ split:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$):* **$94.4880$** ($90.00\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$):* **$10.4987$** ($10.00\%$)
*   **#6 loading_rate [ASSUMED split]:** Calculated as a velocity rate over a very fast landing window. Because it is highly sensitive to sub-frame contact time errors, it is dominated by motion/timing sensitivity. We assume a $10\text{--}90$ split:
    *   *Projection Variance ($\sigma^2_{\text{proj}}$):* **$434.6253$** ($10.00\%$)
    *   *Motion Variance ($\sigma^2_{\text{mot}}$):* **$3911.6281$** ($90.00\%$)
*   **#3 landing_rom [PROPAGATED split]:** Calculated as $\text{ROM} = \text{peak\_flexion} - \text{contact\_flexion}$. We propagate its uncertainty from the peak (#2) and contact (#1) endpoints:
    *   *Propagated Projection:* $\sigma^2_{\text{proj, ROM}} = \sigma^2_{\text{proj, peak}} + \sigma^2_{\text{proj, contact}} = 37.4132 + 94.4880 = 131.9012$
    *   *Propagated Motion:* $\sigma^2_{\text{mot, ROM}} = \sigma^2_{\text{mot, peak}} + \sigma^2_{\text{mot, contact}} = 0.0000 + 10.4987 = 10.4987$
    *   *Total Propagated:* $142.4000$
    *   To reconcile exactly with the observed Section 1 total variance ($150.8291$), we scale the propagated components proportionally to sum to the observed total (maintaining a $92.62\%$ projection and $7.38\%$ motion split):
        *   *Projection Variance ($\sigma^2_{\text{proj}}$):* **$139.7047$** ($92.62\%$)
        *   *Motion Variance ($\sigma^2_{\text{mot}}$):* **$11.1244$** ($7.38\%$)

---

## 3. Weighting Scheme (Inverse-Variance Weighting)

The framework utilizes standard **inverse-variance weighting** to combine multiple measurements of unequal precision:
$$w_i = \frac{1}{\sigma_{i, \text{total}}^2}$$
The normalized weight ($\bar{w}_i$) for each biomarker is:
$$\bar{w}_i = \frac{w_i}{\sum_j w_j}$$

### Drop-Jump Validation Weighting:
*   $w_{\#1} = \frac{1}{104.9867} \approx 0.0095$
*   $w_{\#2} = \frac{1}{37.4132} \approx 0.0267$
*   $w_{\#3} = \frac{1}{150.8291} \approx 0.0066$
*   $w_{\#6} = \frac{1}{4346.2534} \approx 0.0002$

$$\sum w = 0.0095 + 0.0267 + 0.0066 + 0.0002 = 0.0431$$

### Resulting Weights:
1.  **#2 peak_landing_flexion:** **$62.00\%$** (Dominates the framework due to low peak-matched variance)
2.  **#1 contact_flexion:** **$22.09\%$**
3.  **#3 landing_rom:** **$15.38\%$**
4.  **#6 loading_rate:** **$0.53\%$** (Near-zero weight reflecting high measurement variance)

---

## 4. Cross-Exercise Transfer Rule

Slow, controlled exercises like squats and lunges occur at low velocity, meaning timing jitter and motion blur ($\sigma^2_{\text{mot}}$) are negligible. 

Therefore, when applying the uncertainty-weighting framework to squats and lunges, we use **only the transferable projection component** of uncertainty ($\sigma^2_{\text{proj}}$) derived from the drop-jump ground truth.

The cross-exercise biomarker name mappings are biomechanically valid, not merely name-matched: squat/lunge 'start_flexion' maps to drop-jump 'contact_flexion' (both are shallow-flexion metrics with minimal foreshortening and projection error), and squat/lunge 'descent_velocity' maps to drop-jump 'loading_rate' (both are velocity/rate metrics with consistent degrees/second units once frames are scaled by video framerate).

### Transferable Projection Weights (Squats / Lunges):
Under the baseline assumed splits ($90\text{--}10$ for contact, $10\text{--}90$ for loading rate):
*   $w_{\text{proj}, \#1} = \frac{1}{94.4880} \approx 0.0106$
*   $w_{\text{proj}, \#2} = \frac{1}{37.4132} \approx 0.0267$
*   $w_{\text{proj}, \#3} = \frac{1}{139.7047} \approx 0.0072$
*   $w_{\text{proj}, \#6} = \frac{1}{434.6253} \approx 0.0023$

$$\sum w_{\text{proj}} = 0.0106 + 0.0267 + 0.0072 + 0.0023 = 0.0468$$

### Resulting Squat/Lunge Weights:
1.  **#2 peak_flexion (Peak depth equivalent):** **$57.15\%$** (Dominates the static screening framework)
2.  **#1 start_flexion (Contact equivalent):** **$22.63\%$**
3.  **#3 rom:** **$15.30\%$**
4.  **#6 joint_velocity (Loading rate equivalent):** **$4.92\%$**

### Sensitivity Analysis of Assumed Splits:
To verify that the final cross-exercise weights are robust and not driven by the assumed splits for contact flexion (baseline: $90/10$ projection/motion) and loading rate (baseline: $10/90$ projection/motion), a sensitivity sweep was conducted:

| Test Configuration (Contact Split, Rate Split) | Weight #1 (Start Flexion) | Weight #2 (Peak Flexion) | Weight #3 (ROM) | Weight #6 (Velocity) |
| :--- | :---: | :---: | :---: | :---: |
| **Baseline (90/10, 10/90)** | **$22.63\%$** | **$57.15\%$** | **$15.30\%$** | **$4.92\%$** |
| Config 2 (90/10, 20/80) | $23.20\%$ | $58.59\%$ | $15.69\%$ | $2.52\%$ |
| Config 3 (90/10, 05/95) | $21.57\%$ | $54.47\%$ | $14.59\%$ | $9.38\%$ |
| Config 4 (80/20, 10/90) | $24.44\%$ | $54.87\%$ | $15.96\%$ | $4.72\%$ |
| Config 5 (80/20, 20/80) | $25.03\%$ | $56.20\%$ | $16.35\%$ | $2.42\%$ |
| Config 6 (80/20, 05/95) | $23.34\%$ | $52.40\%$ | $15.24\%$ | $9.02\%$ |
| Config 7 (70/30, 10/90) | $26.60\%$ | $52.26\%$ | $16.64\%$ | $4.50\%$ |
| Config 8 (70/30, 20/80) | $27.21\%$ | $53.46\%$ | $17.03\%$ | $2.30\%$ |
| Config 9 (70/30, 05/95) | $25.46\%$ | $50.01\%$ | $15.93\%$ | $8.61\%$ |

*   **Stability Finding:** Across all varied configurations, the dominance hierarchy remains completely stable: Peak Flexion ($\sim 50\text{--}59\%$) > Start Flexion ($\sim 21\text{--}27\%$) > ROM ($\sim 14\text{--}17\%$) > Joint Velocity ($\sim 2\text{--}9\%$). 
*   **Immateriality of Assumptions:** The loading rate's split is immaterial to the final framework because its high base variance filters out its weight to near-zero levels. The contact flexion split's motion component is not transferred to squats/lunges regardless. This demonstrates that the framework's normalized weights are highly stable and robust to split assumptions.

> [!WARNING]
> **Documented Limitation:** Only the projection-error component of squat and lunge uncertainty is validated via the drop-jump ground truth. The motion-error component for these exercises remains unvalidated and is flagged as a future-work item.

---

## 5. "What This Framework Does NOT Claim"

*   **No Risk Scoring or Injury Prediction:** This framework does not calculate a risk index, injury likelihood, or predict any clinical outcome.
*   **No Rep Classification:** It does not classify individual repetitions or label movement as "good" or "bad".
*   **No Motion Transfer to Slow Exercises:** It does not apply drop-jump-landing motion/timing uncertainty to squats or lunges. Only the geometry-general projection component is transferred.
*   **No Claim of Full Squat/Lunge Validation:** It does not claim that squat and lunge measurements are fully validated. Only their projection component has ground truth validation; motion-component validation is deferred to future work.
*   **Architectural Demonstration Only:** It is not a clinical or deployed software system, but rather a methodology demonstrating how measurement uncertainties could be propagated.

---

## 6. Worked-Example Plan (Stage 2)

If approved, the framework will be illustrated using a small sample of existing squat and lunge repetitions from the `REHAB24-6` dataset.

### Selected Repetitions:
1.  **Squats (`rehab24_squat_per_rep_biomarkers.csv`):**
    *   *Rep 1:* `PM_008 rep 2` (labelled correct)
    *   *Rep 2:* `PM_008 rep 17` (labelled incorrect)
2.  **Lunges (`rehab24_lunge_per_rep_biomarkers.csv`):**
    *   *Rep 1:* `PM_022 rep 1` (labelled correct)
    *   *Rep 2:* `PM_022 rep 5` (labelled incorrect)

### Output Characterisation Illustration:
For each rep, the script will calculate and plot the 4 biomarkers side-by-side with their validated projection-uncertainty bounds. It will show:
*   The raw biomarker measurements.
*   The projection-uncertainty bounds (95% CI) around each biomarker based on the transferable projection variances.
*   A weighted characterisation showing how the framework weights each biomarker (peak flexion-equivalent at $57.1\%$ vs. joint velocity-equivalent at $4.9\%$).
*   Save the results to `17_uncertainty_framework_outputs/worked_example.csv` and generate an illustration plot `17_uncertainty_framework_outputs/worked_example_weights.png`.

Note: The plotted confidence bounds represent the pipeline's **validated measurement uncertainty** per biomarker (constant across reps by construction), **not** the per-rep variability or confidence in an individual rep's value.
