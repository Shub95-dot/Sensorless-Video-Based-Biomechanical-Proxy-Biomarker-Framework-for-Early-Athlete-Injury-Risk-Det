# Chapter 12: Counterfactual Explainable AI (XAI)

This chapter presents the design, implementation, and verification of the counterfactual Explainable AI (XAI) layer (Step 11 of the biomechanical processing pipeline). Biomechanical screening tools must not only identify movement deviations but also communicate their decisions transparently to clinical users. This chapter details a counterfactual explanation component that defines the exact physical joint boundaries required to clear active screening flags.

---

## 12.1. Purpose and Step 11 Novelty Framing

The counterfactual XAI layer represents Step 11 of the primary pipeline architecture and constitutes **Novelty Contribution #4** of this dissertation [source: 21_xai_outputs/xai_design.md].

The primary purpose of this layer is to translate the binary decisions of the Step 10 screening layer into clinical explanations [source: 21_xai_outputs/xai_design.md]. For any repetition flagged as `SCREENING_POSITIVE`, the XAI layer computes a counterfactual explanation: a statement defining the exact kinematic conditions under which the screening flags would *not* have fired [source: 21_xai_outputs/xai_design.md]. Rather than providing abstract, post-hoc feature importance scores (which show that a biomarker was "important" without defining how it must change), counterfactuals provide concrete, physical joint values. This bridges raw joint coordinate tracking and clinical decision-making, helping practitioners understand the precise boundary between a normal baseline pattern and a detected deviation.

---

## 12.2. Research Origin and SHAP/LIME Deprecation

The design of the explainability component underwent a major methodological shift during development:
*   **Initial Scaffold & Deprecation**: The original workspace structure featured placeholder directories (`8_xai/`) for model-agnostic post-hoc explanation frameworks, specifically SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) [source: 21_xai_outputs/xai_design.md]. However, SHAP and LIME are approximation tools designed for black-box machine learning models (such as deep neural networks) by perturbing inputs locally to reconstruct decision boundaries [source: 21_xai_outputs/xai_design.md].
*   **Pipeline Realignment**: Because the Step 10 screening layer is a deterministic, transparent logic gate with explicit thresholds, fitting a post-hoc surrogate model introduces unnecessary approximation error and explanation infidelity [source: 21_xai_outputs/xai_design.md]. Consequently, SHAP and LIME were deprecated in favor of a direct, exact counterfactual engine that calculates margins directly from the pipeline's active thresholds [source: 21_xai_outputs/xai_design.md].

---

## 12.3. Faithfulness by Construction

The defining advantage of the direct counterfactual explanation layer is **faithfulness by construction** [source: 21_xai_outputs/xai_design.md].

In black-box explanation methods, there is a constant trade-off between interpretability and faithfulness because the local surrogate model is only an approximation of the primary model's behavior [source: 21_xai_outputs/xai_design.md]. In this framework, the decision rules defined in Step 10 *are* the decision boundaries [source: 21_xai_outputs/xai_design.md]. The counterfactual engine calculates the deviation margin ($M_i$) directly from the active threshold ($T_i$) and the measured joint value ($x_i$):
$$M_{\text{depth}} = T_{\text{depth}} - x_{\text{peak}}$$
$$M_{\text{rom}} = x_{\text{rom}} - T_{\text{rom}}$$
$$M_{\text{velocity}} = x_{\text{velocity}} - T_{\text{velocity}}$$

Because explanations are derived from these exact algebraic margins, they exhibit **zero approximation error** [source: 21_xai_outputs/xai_design.md]. Unlike local surrogate models that can produce unstable explanations across neighboring samples, this glass-box engine is guaranteed to be a mathematically perfect representation of the underlying screening decision. This faithfulness by construction represents a major methodological contribution of the Track A architecture.

---

## 12.4. Counterfactual Templates and Wording Direction

The XAI layer utilizes predefined wording templates to generate explanations. Because knee angles use the included-angle convention (extension $\approx 180^\circ$, smaller angles = deeper flexion), template directions are verified to prevent clinical contradictions [source: 21_xai_outputs/xai_design.md]:

1.  **EXCESS_DEPTH (Peak Knee Flexion)**:
    *   Fires if peak included angle $x_{\text{peak}} < T_{\text{depth}}$ (smaller knee angle, deeper bend) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_DEPTH because peak knee flexion joint angle (x_peak°) was M_depth° below the active baseline threshold (T_depth°). Had the peak flexion angle been at least T_depth° (representing a shallower bend of M_depth° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/xai_design.md].
    *   *Direction Verification*: Since $T_{\text{depth}}$ is algebraically larger than $x_{\text{peak}}$, requiring the angle to be "at least $T_{\text{depth}}$" physically corresponds to a shallower flexion bend.
2.  **EXCESS_ROM (Range of Motion Excursion)**:
    *   Fires if range of motion $x_{\text{rom}} > T_{\text{rom}}$ (larger excursion) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_ROM because knee range of motion (x_rom°) was M_rom° above the active baseline threshold (T_rom°). Had the range of motion been no more than T_rom° (representing a restricted excursion of M_rom° less joint travel), the EXCESS_ROM flag would not have fired."` [source: 21_xai_outputs/xai_design.md].
3.  **EXCESS_VELOCITY (Eccentric Descent Velocity)**:
    *   Fires if descent velocity $x_{\text{velocity}} > T_{\text{velocity}}$ (faster speed) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_VELOCITY because descent joint velocity (x_velocity°/s) was M_velocity°/s above the active baseline threshold (T_velocity°/s). Had the descent velocity been no more than T_velocity°/s (representing a slower movement of M_velocity°/s less speed), the EXCESS_VELOCITY flag would not have fired."` [source: 21_xai_outputs/xai_design.md].

Explanations are phrased **descriptively** (describing the mathematical boundary condition that would satisfy the gate), never **prescriptively** (instructing the athlete on how they must perform the movement) [source: 21_xai_outputs/xai_design.md].

---

## 12.5. Minimal Kinematic Intervention (MKI)

When a repetition triggers multiple screening rules, joint parameter adjustments are physically coupled. For example, peak flexion depth and joint range of motion (ROM) are structurally linked: restricting a squat's depth simultaneously restricts its range of motion.

To account for this coupling, the XAI layer implements a **Minimal Kinematic Intervention (MKI)** arithmetic [source: 21_xai_outputs/xai_design.md]. Under the biomechanical assumption that range of motion scales directly with peak flexion depth (assuming a constant standing extension start point, $x_{\text{rom}} \approx x_{\text{extension}} - x_{\text{peak}}$), the MKI computes the maximum of the two required peak flexion changes:
$$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$

The MKI output consolidates coupled explanations into a single descriptive statement defining the minimum flexion adjustment that satisfies both rule conditions simultaneously, avoiding contradictory multi-variable recommendations [source: 21_xai_outputs/xai_design.md]. Independent biomarkers (such as descent velocity) are appended as a separate condition in a set of requirements:
$$\text{MKI Statement} = \left\{ \Delta \theta_{\text{MKI}} \text{ shallower peak flexion} \right\} \cup \left\{ M_{\text{velocity}} \text{ slower joint speed} \right\}$$

This MKI coupling assumption is an illustrative simplification for demonstrating multi-variable explanations, rather than an absolute biomechanical law [source: 21_xai_outputs/xai_design.md].

---

## 12.6. Uncertainty-Aware Confidence Grading

To prevent clinical users from over-interpreting minor tracking variations, counterfactual explanations incorporate Phase 7 validated camera noise floors to grade explanation confidence [source: 21_xai_outputs/xai_design.md]. Each deviation margin ($M_i$) is evaluated against a confidence buffer ($B_i = 0.5 \times NF_i$):
*   **`HIGH CONFIDENCE` ($M_i > B_i$)**: Margin is large enough to be clearly distinguished from monocular projection noise [source: 21_xai_outputs/xai_design.md].
*   **`LOW CONFIDENCE (Near Noise Floor)` ($M_i \le B_i$)**: Margin is close to uncertainty boundaries, appending a caution note:
    > *"Note: The deviation margin (M_i) is close to the monocular camera's validated measurement uncertainty boundaries. This flag should be interpreted with caution as minor tracking fluctuations could have triggered it."* [source: 21_xai_outputs/xai_design.md].

This confidence grading threads ground-truth optoelectronic validation (Chapter 6) through to XAI outputs.

---

## 12.7. Applied Explanations Results

Counterfactual explanations were executed on Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) from `REHAB24-6` [source: 21_xai_outputs/worked_example_explanations.json].

### 12.7.1. Squat Worked Example: Subject `PM_113` Repetition 6
Subject `PM_113` Repetition 6 triggered `EXCESS_DEPTH`, `EXCESS_ROM`, and `EXCESS_VELOCITY` [source: 21_xai_outputs/worked_example_explanations.json]. Active noise floors ($NF_{\text{peak}} = 11.99^\circ$, $NF_{\text{rom}} = 23.17^\circ$, $NF_{\text{velocity}} = 40.86^\circ/\text{s}$) defined confidence buffers of $5.99^\circ$, $11.58^\circ$, and $20.43^\circ/\text{s}$ [source: 22_dissertation_writing/results_screening_layer_v1.md]:
*   **`EXCESS_DEPTH` Explanation**: Peak flexion angle was $43.22^\circ$ (threshold: $60.99^\circ$), margin **$17.77^\circ$** ($17.77^\circ > 5.99^\circ \rightarrow$ **`HIGH CONFIDENCE`**):
    > `"Flagged EXCESS_DEPTH because peak knee flexion joint angle (43.22°) was 17.77° below the active baseline threshold (60.99°). Had the peak flexion angle been at least 60.99° (representing a shallower bend of 17.77° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_ROM` Explanation**: Range of motion was $136.50^\circ$ (threshold: $128.67^\circ$), margin **$7.83^\circ$** ($7.83^\circ \le 11.58^\circ \rightarrow$ **`LOW CONFIDENCE (Near Noise Floor)`**):
    > `"Flagged EXCESS_ROM because knee range of motion (136.50°) was 7.83° above the active baseline threshold (128.67°). Had the range of motion been no more than 128.67° (representing a restricted excursion of 7.83° less joint travel), the EXCESS_ROM flag would not have fired. [Note: Near noise floor caution appended.]"` [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_VELOCITY` Explanation**: Descent velocity was $110.62^\circ/\text{s}$ (threshold: $90.80^\circ/\text{s}$), margin **$19.82^\circ/\text{s}$** ($19.82^\circ/\text{s} \le 20.43^\circ/\text{s} \rightarrow$ **`LOW CONFIDENCE (Near Noise Floor)`**) [source: 21_xai_outputs/worked_example_explanations.json].
*   **Minimal Kinematic Intervention (MKI)**: Flexion adjustment was $\max(17.77^\circ, 7.83^\circ) = 17.77^\circ$ [source: 21_xai_outputs/worked_example_explanations.json]. Velocity was independent ($19.82^\circ/\text{s}$). MKI rendered as:
    > `"The screening flags would not have fired if peak knee flexion joint angle had been at least 17.77° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags) AND descent joint velocity had been at least 19.82°/s slower."` [source: 21_xai_outputs/worked_example_explanations.json].

### 12.7.2. Lunge Worked Example: Subject `PM_104` Repetition 6
Subject `PM_104` Repetition 6 triggered `EXCESS_DEPTH` and `EXCESS_ROM` [source: 21_xai_outputs/worked_example_explanations.json]:
*   **`EXCESS_DEPTH` Explanation**: Flexion angle $59.12^\circ$ (threshold: $72.68^\circ$), margin **$13.55^\circ$** (**`HIGH CONFIDENCE`**) [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_ROM` Explanation**: ROM $117.28^\circ$ (threshold: $99.95^\circ$), margin **$17.33^\circ$** ($17.33^\circ > 11.58^\circ \rightarrow$ **`HIGH CONFIDENCE`**) [source: 21_xai_outputs/worked_example_explanations.json].
*   **Minimal Kinematic Intervention (MKI)**: Computed as $\max(13.55^\circ, 17.33^\circ) = 17.33^\circ$ [source: 21_xai_outputs/worked_example_explanations.json].
    > `"The screening flags would not have fired if peak knee flexion joint angle had been at least 17.33° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags)."` [source: 21_xai_outputs/worked_example_explanations.json].

Because the ROM margin ($17.33^\circ$) exceeded the peak flexion depth margin ($13.55^\circ$), max-coupling selected the larger constraint, clearing both rules simultaneously.

### 12.7.3. Empirical Verification Summary
Faithfulness by construction was empirically confirmed by cross-checking every flagged repetition's rendered counterfactual margin against the screening layer's independently-computed threshold (`worked_example_screening.csv` vs `worked_example_explanations.json`). The complete side-by-side verification parameter table cross-checking raw values and rendered margins is presented in Appendix C (Table C.1).

---

## 12.8. Boundaries and What This Layer Does NOT Claim

To maintain scientific integrity and align with screening scope across this dissertation:
*   **Rule Explanations Only**: Explains rule-firing logic (why a flag was raised given biomarker values); does **NOT** explain injury causation, biomechanical mechanisms, or clinical outcomes.
*   **No Diagnostics**: Does not provide clinical diagnostic interpretations or predict future joint injury.
*   **No Prescriptive Training Advice**: Counterfactuals describe mathematical conditions required to clear flags; they do **not** recommend physical corrections or prescribe training interventions.
*   **No Black-Box Approximations**: Does not explain neural networks or approximate black-box models (not SHAP/LIME); remains mathematically faithful to deterministic screening logic.
