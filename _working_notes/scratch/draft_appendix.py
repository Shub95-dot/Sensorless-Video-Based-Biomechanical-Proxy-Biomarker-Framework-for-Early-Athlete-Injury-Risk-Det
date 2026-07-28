import os

app_text = r"""# Appendix A: Mathematical Derivation of Kinematic Uncertainty Weighting

This appendix details the mathematical derivation, variance decomposition algebra, inverse-variance weighting formulas, and sensitivity sweep evaluations for the uncertainty-weighted screening framework, supplementing Chapter 8 [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## A.1. Limits of Agreement to Statistical Variance Conversion

Measurement uncertainty bounds were established in Chapter 6 from ground-truth Drop-Jump validation ($n = 48$ trials across 9 subjects) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]. Under the assumption of normally distributed measurement errors, the 95% Limits of Agreement (LoA) span $2 \times 1.96 = 3.92$ standard deviations (SDs) [source: 17_uncertainty_framework_outputs/framework_design.md]:

$$\text{SD} = \frac{\text{LoA}_{\text{upper}} - \text{LoA}_{\text{lower}}}{3.92}$$
$$\sigma^2_{\text{total}} = \text{SD}^2$$

Applying this conversion to validated biomarkers yields:

1. **Contact Flexion (#1)**:
   * 95% LoA: $[-26.7742^\circ, 13.3913^\circ]$ (Width: $40.1655^\circ$, Bias: $-6.6914^\circ$) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
   * $\text{SD} = 40.1655 / 3.92 = 10.2463^\circ \implies \sigma^2_{\text{total}} = 104.9867$ [source: 17_uncertainty_framework_outputs/framework_design.md]

2. **Peak Landing Flexion (#2)**:
   * 95% LoA: $[7.7285^\circ, 31.7057^\circ]$ (Width: $23.9772^\circ$, Bias: $+19.7171^\circ$) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
   * $\text{SD} = 23.9772 / 3.92 = 6.1166^\circ \implies \sigma^2_{\text{total}} = 37.4132$ [source: 17_uncertainty_framework_outputs/framework_design.md]

3. **Landing ROM (#3)**:
   * 95% LoA: $[2.3373^\circ, 50.4798^\circ]$ (Width: $48.1425^\circ$, Bias: $+26.4086^\circ$) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
   * $\text{SD} = 48.1425 / 3.92 = 12.2813^\circ \implies \sigma^2_{\text{total}} = 150.8291$ [source: 17_uncertainty_framework_outputs/framework_design.md]

4. **Flexion Loading Rate (#6)**:
   * 95% LoA: $[-115.9179^\circ/\text{s}, 142.5125^\circ/\text{s}]$ (Width: $258.4304^\circ/\text{s}$, Bias: $+13.2973^\circ/\text{s}$) [source: 16_opencap_dropjump_outputs/metadata/phase6_agreement_final.csv]
   * $\text{SD} = 258.4304 / 3.92 = 65.9261^\circ/\text{s} \implies \sigma^2_{\text{total}} = 4346.2534$ [source: 17_uncertainty_framework_outputs/framework_design.md]

---

## A.2. Projection/Motion Error Decomposition Algebra

Total validated measurement variance is modeled as the sum of orthogonal camera projection geometry error ($\sigma^2_{\text{proj}}$) and dynamic motion/timing error ($\sigma^2_{\text{mot}}$) [source: 17_uncertainty_framework_outputs/framework_design.md]:

$$\sigma^2_{\text{total}} = \sigma^2_{\text{proj}} + \sigma^2_{\text{mot}}$$

The mathematical derivation for each biomarker split proceeds as follows:

* **Peak Flexion (#2)**: Measured at peak absorption where angular velocity $\omega \approx 0$. As verified by Section 6.5.1, timing lag is non-contributory at static peak. Thus, $\sigma^2_{\text{mot}} = 0.0000$ ($0.0\%$) and $\sigma^2_{\text{proj}} = 37.4132$ ($100.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
* **Contact Flexion (#1)**: Measured at initial impact under slow angular velocity. Assuming a $90/10$ projection/motion split yields $\sigma^2_{\text{proj}} = 94.4880$ ($90.0\%$) and $\sigma^2_{\text{mot}} = 10.4987$ ($10.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
* **Flexion Loading Rate (#6)**: Rapid impact velocity metric highly sensitive to sub-frame contact timing. Assuming a $10/90$ projection/motion split yields $\sigma^2_{\text{proj}} = 434.6253$ ($10.0\%$) and $\sigma^2_{\text{mot}} = 3911.6281$ ($90.0\%$) [source: 17_uncertainty_framework_outputs/framework_design.md].
* **Landing ROM (#3)**: Propagated from peak (#2) and contact (#1) endpoints:
  $$\sigma^2_{\text{proj, ROM}} = \sigma^2_{\text{proj, peak}} + \sigma^2_{\text{proj, contact}} = 37.4132 + 94.4880 = 131.9012$$
  $$\sigma^2_{\text{mot, ROM}} = \sigma^2_{\text{mot, peak}} + \sigma^2_{\text{mot, contact}} = 0.0000 + 10.4987 = 10.4987$$
  Total propagated variance $= 142.4000$. Scaling to observed total ($150.8291$) maintains the $92.62\% / 7.38\%$ split, giving $\sigma^2_{\text{proj}} = 139.7047$ and $\sigma^2_{\text{mot}} = 11.1244$ [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## A.3. Inverse-Variance Weighting Derivation

Under inverse-variance weighting, each measurement weight $w_i$ and normalized weight $\bar{w}_i$ are given by [CITE: inverse_variance_weighting]:

$$w_i = \frac{1}{\sigma_i^2}, \quad \bar{w}_i = \frac{w_i}{\sum_{j=1}^K w_j}$$

### A.3.1. Drop-Jump Total Validation Weights
Using total variances $\sigma^2_{\text{total}}$:
* $w_{\#1} = 1/104.9867 = 0.009525$
* $w_{\#2} = 1/37.4132 = 0.026729$
* $w_{\#3} = 1/150.8291 = 0.006630$
* $w_{\#6} = 1/4346.2534 = 0.000230$
* Sum $\sum w_j = 0.043114$

Normalized weights: Peak Flexion **62.00%**, Contact Flexion **22.09%**, Landing ROM **15.38%**, Loading Rate **0.53%** [source: 17_uncertainty_framework_outputs/framework_design.md].

### A.3.2. Cross-Exercise Transferable Projection Weights
Discarding non-transferable motion variance $\sigma^2_{\text{mot}}$ for slow exercises (squats/lunges), raw projection weights $w_{\text{proj}, i} = 1 / \sigma^2_{\text{proj}, i}$ are:
* $w_{\text{proj}, \#1} = 1/94.4880 = 0.010583$
* $w_{\text{proj}, \#2} = 1/37.4132 = 0.026729$
* $w_{\text{proj}, \#3} = 1/139.7047 = 0.007158$
* $w_{\text{proj}, \#6} = 1/434.6253 = 0.002301$
* Sum $\sum w_{\text{proj}, j} = 0.046771$

Normalized transfer weights: Peak Flexion **57.15%**, Start Flexion **22.63%**, ROM **15.30%**, Joint Velocity **4.92%** [source: 17_uncertainty_framework_outputs/framework_design.md].

---

## A.4. Sensitivity Analysis of Assumed Variance Splits

To test framework stability against assumed projection/motion splits for contact flexion and loading rate, a $3 \times 3$ grid sweep (9 configurations) was evaluated [source: 17_uncertainty_framework_outputs/framework_design.md]. Table A.1 summarizes the resulting transfer weights.

### Table A.1: Sensitivity Sweep of Assumed Variance Splits Across 9 Configurations

| Config | Contact Split (Proj/Mot) | Loading Rate Split (Proj/Mot) | Peak Weight (%) | Start Weight (%) | ROM Weight (%) | Velocity Weight (%) | Hierarchy Stable? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline** | **90 / 10** | **10 / 90** | **57.15%** | **22.63%** | **15.30%** | **4.92%** | **YES** |
| C1 | 90 / 10 | 20 / 80 | 54.80% | 21.70% | 14.67% | 8.83% | YES |
| C2 | 90 / 10 | 5 / 95 | 58.40% | 23.13% | 15.63% | 2.58% | YES |
| C3 | 80 / 20 | 10 / 90 | 55.70% | 24.64% | 14.73% | 4.93% | YES |
| C4 | 80 / 20 | 20 / 80 | 53.47% | 23.65% | 14.14% | 8.74% | YES |
| C5 | 80 / 20 | 5 / 95 | 56.89% | 25.17% | 15.05% | 2.89% | YES |
| C6 | 70 / 30 | 10 / 90 | 54.02% | 26.97% | 14.10% | 4.91% | YES |
| C7 | 70 / 30 | 20 / 80 | 51.93% | 25.93% | 13.55% | 8.59% | YES |
| C8 | 70 / 30 | 5 / 95 | 55.14% | 27.53% | 14.39% | 2.94% | YES |

Across all configurations, the weighting hierarchy remains completely invariant: Peak Flexion ($51.93\%\text{--}58.40\%$) > Start Flexion ($21.70\%\text{--}27.53\%$) > ROM ($13.55\%\text{--}15.63\%$) > Joint Velocity ($2.58\%\text{--}8.83\%$) [source: 17_uncertainty_framework_outputs/framework_design.md]. The maximum weight variation across parameter choices is under $8.6\%$, demonstrating that transfer weights are highly robust to the assumed split parameters.
"""

print("Appendix A Word Count:", len(app_text.split()))
