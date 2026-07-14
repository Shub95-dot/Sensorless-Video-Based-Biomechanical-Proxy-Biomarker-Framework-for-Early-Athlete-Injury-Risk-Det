# Chapter 12: Counterfactual Explainable AI (XAI)

This chapter presents the design, implementation, and verification of the counterfactual Explainable AI (XAI) layer (Step 11 of the biomechanical processing pipeline). Biomechanical screening tools must not only identify movement deviations but also communicate their decisions transparently to clinical users. This chapter details a counterfactual explanation component that defines the exact physical joint boundaries required to clear active screening flags. First, we outline the purpose and framing of the XAI layer as the fourth core novelty contribution of this dissertation. Second, we discuss the design evolution that led to the deprecation of local model-approximate methods. Third, we establish the central claim of faithfulness by construction. Fourth, we present the counterfactual wording templates. Fifth, we describe the Minimal Kinematic Intervention (MKI) arithmetic for coupled joint parameters. Finally, we demonstrate the applied results using squat and lunge worked examples and establish the boundaries of the explanation layer's claims.

---

## 12.1. Purpose and Step 11 Novelty Framing

The counterfactual XAI layer represents Step 11 of the primary pipeline architecture and constitutes **Novelty Contribution #4** of this dissertation [source: 21_xai_outputs/xai_design.md]. 

The primary purpose of this layer is to translate the binary decisions of the Step 10 screening layer into clinical explanations [source: 21_xai_outputs/xai_design.md]. For any repetition flagged as `SCREENING_POSITIVE`, the XAI layer computes a counterfactual explanation: a statement defining the exact kinematic conditions under which the screening flags would *not* have fired [source: 21_xai_outputs/xai_design.md]. Rather than providing abstract, post-hoc feature importance scores (which show that a biomarker was "important" without defining how it must change), counterfactuals provide concrete, physical joint values. This helps clinical practitioners understand the precise boundary between a normal baseline pattern and a detected deviation, facilitating transparency in markerless screening.

---

## 12.2. Research Origin and SHAP/LIME Deprecation

The design of the explainability component underwent a major methodological shift during the research process:
*   **Initial Scaffold**: The original workspace structure featured empty placeholder directories (`8_xai/`) dedicated to model-agnostic post-hoc explanation frameworks, specifically SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) [source: 21_xai_outputs/xai_design.md].
*   **Methodological Deprecation**: During development, this approach was recognized as mathematically inappropriate for the screening layer. SHAP and LIME are approximation tools designed to explain black-box machine learning models (such as deep neural networks) by perturbing inputs locally to reconstruct decision boundaries [source: 21_xai_outputs/xai_design.md].
*   **Rationale for Direct Counterfactuals**: Because the Step 10 screening layer is designed as a deterministic, transparent logic gate using explicit joint thresholds, there is no black box to approximate [source: 21_xai_outputs/xai_design.md]. Fitting a post-hoc approximation model onto a glass-box system would introduce unnecessary approximation error, leading to explanation infidelity [source: 21_xai_outputs/xai_design.md]. 
*   **Pipeline Realignment**: Consequently, the SHAP/LIME directories were deprecated. This process established that explainability must align with decision architecture: a transparent rule-based screening layer (Chapter 10) must be paired with a direct, exact counterfactual engine (Chapter 12) that calculates margins directly from the pipeline's active thresholds [source: 21_xai_outputs/xai_design.md].

---

## 12.3. Faithfulness by Construction

The defining advantage of the direct counterfactual explanation layer is **faithfulness by construction** [source: 21_xai_outputs/xai_design.md]. 
*   In black-box explanation methods, there is a constant trade-off between interpretability and faithfulness; the local surrogate model is only an approximation of the primary model's behavior [source: 21_xai_outputs/xai_design.md].
*   In this framework, the decision rules defined in Step 10 *are* the decision boundaries [source: 21_xai_outputs/xai_design.md].
*   The counterfactual engine calculates the deviation margin ($M_i$) directly from the active threshold ($T_i$) and the measured joint value ($x_i$):
    $$M_{\text{depth}} = T_{\text{depth}} - x_{\text{peak}}$$
    $$M_{\text{rom}} = x_{\text{rom}} - T_{\text{rom}}$$
    $$M_{\text{velocity}} = x_{\text{velocity}} - T_{\text{velocity}}$$
*   Because the explanations are derived from these exact algebraic margins, they exhibit **zero approximation error** [source: 21_xai_outputs/xai_design.md]. The explanation is guaranteed to be a mathematically perfect representation of the underlying screening decision. This faithfulness by construction represents a major methodological contribution of the Track A architecture.

---

## 12.4. Counterfactual Templates and Wording Direction

The XAI layer utilizes predefined wording templates to generate explanations. Because knee angles are analyzed using the included-angle convention (extension $\approx 180^\circ$, smaller angles representing deeper flexion), the direction of the counterfactual statements must be carefully verified to avoid clinical contradictions [source: 21_xai_outputs/xai_design.md]:

1.  **EXCESS_DEPTH (Peak Knee Flexion)**:
    *   Fires if peak included angle $x_{\text{peak}} < T_{\text{depth}}$ (smaller knee angle, deeper bend) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_DEPTH because peak knee flexion joint angle (x_peak°) was M_depth° below the active baseline threshold (T_depth°). Had the peak flexion angle been at least T_depth° (representing a shallower bend of M_depth° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/xai_design.md].
    *   *Direction Verification*: Since $T_{\text{depth}}$ is algebraically larger than $x_{\text{peak}}$, requiring the angle to be "at least $T_{\text{depth}}$" physically corresponds to a shallower flexion bend. The template direction is correct.
2.  **EXCESS_ROM (Range of Motion Excursion)**:
    *   Fires if range of motion $x_{\text{rom}} > T_{\text{rom}}$ (larger excursion) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_ROM because knee range of motion (x_rom°) was M_rom° above the active baseline threshold (T_rom°). Had the range of motion been no more than T_rom° (representing a restricted excursion of M_rom° less joint travel), the EXCESS_ROM flag would not have fired."` [source: 21_xai_outputs/xai_design.md].
3.  **EXCESS_VELOCITY (Eccentric Descent Velocity)**:
    *   Fires if descent velocity $x_{\text{velocity}} > T_{\text{velocity}}$ (faster speed) [source: 21_xai_outputs/xai_design.md].
    *   *Counterfactual template*: `"Flagged EXCESS_VELOCITY because descent joint velocity (x_velocity°/s) was M_velocity°/s above the active baseline threshold (T_velocity°/s). Had the descent velocity been no more than T_velocity°/s (representing a slower movement of M_velocity°/s less speed), the EXCESS_VELOCITY flag would not have fired."` [source: 21_xai_outputs/xai_design.md].

Explanations are phrased **descriptively** (describing the mathematical boundary condition that would satisfy the gate), never **prescriptively** (instructing the athlete on how they must perform the squat) [source: 21_xai_outputs/xai_design.md].

---

## 12.5. Minimal Kinematic Intervention (MKI)

When a repetition triggers multiple screening rules, the joint parameter adjustments are physically coupled. For example, peak flexion depth and joint range of motion (ROM) are structurally linked: restricting a squat's depth will simultaneously restrict its range of motion.

To account for this coupling, the XAI layer implements a **Minimal Kinematic Intervention (MKI)** arithmetic [source: 21_xai_outputs/xai_design.md]. Under the biomechanical assumption that range of motion scales directly with peak flexion depth (assuming a constant standing extension start point, i.e., $x_{\text{rom}} \approx x_{\text{extension}} - x_{\text{peak}}$), the MKI computes the maximum of the two required peak flexion changes:
$$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$

The MKI output consolidates the coupled explanations into a single descriptive statement, defining the minimum flexion adjustment that would satisfy both rule conditions simultaneously [source: 21_xai_outputs/xai_design.md]. If an independent biomarker (such as joint descent velocity) also fires, it is appended to the MKI output as a separate condition in a set of requirements, rather than folded into the flexion angle calculation:
$$\text{MKI Statement} = \left\{ \Delta \theta_{\text{MKI}} \text{ shallower peak flexion} \right\} \cup \left\{ M_{\text{velocity}} \text{ slower joint speed} \right\}$$

This MKI coupling assumption is presented as an illustrative simplification for demonstrating multi-variable explanations, rather than an absolute biomechanical law [source: 21_xai_outputs/xai_design.md].

---

## 12.6. Uncertainty-Aware Confidence Grading

To prevent clinical users from over-interpreting minor tracking variations, the counterfactual explanations incorporate the Phase 7 validated camera noise floors to grade explanation confidence [source: 21_xai_outputs/xai_design.md].

For each rule, the deviation margin ($M_i$) is evaluated against a confidence buffer ($B_i$) defined as half the biomarker's validated noise floor ($NF_i$):
$$B_i = 0.5 \times NF_i$$

*   **`HIGH CONFIDENCE` ($M_i > B_i$)**: The deviation margin is large enough to be clearly distinguished from monocular projection noise [source: 21_xai_outputs/xai_design.md].
*   **`LOW CONFIDENCE (Near Noise Floor)` ($M_i \le B_i$)**: The deviation is close to the camera's measurement uncertainty boundaries. The XAI layer automatically appends a caution note:
    > *"Note: The deviation margin (M_i) is close to the monocular camera's validated measurement uncertainty boundaries. This flag should be interpreted with caution as minor tracking fluctuations could have triggered it."* [source: 21_xai_outputs/xai_design.md].

This confidence grading mathematically threads the ground-truth optoelectronic validation (Chapter 6) through to the final XAI text, communicating the physical limits of monocular tracking to clinical users.

---

## 12.7. Applied Explanations Results

The counterfactual explanations were executed on the screening outputs of Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) from the `REHAB24-6` dataset [source: 21_xai_outputs/worked_example_explanations.json].

### 12.7.1. Squat Worked Example: Subject `PM_113` Repetition 6
On Repetition 6, Subject `PM_113` triggered three screening rules: `EXCESS_DEPTH`, `EXCESS_ROM`, and `EXCESS_VELOCITY` [source: 21_xai_outputs/worked_example_explanations.json]. The active noise floors were $NF_{\text{peak}} = 11.99^\circ$, $NF_{\text{rom}} = 23.17^\circ$, and $NF_{\text{velocity}} = 40.86^\circ/\text{s}$, yielding confidence buffers of $5.99^\circ$, $11.58^\circ$, and $20.43^\circ/\text{s}$ [source: 22_dissertation_writing/results_screening_layer_v1.md].
*   **`EXCESS_DEPTH` Explanation**: The peak flexion included angle was $43.22^\circ$ (threshold: $60.99^\circ$), yielding a margin of **$17.77^\circ$** [source: 21_xai_outputs/worked_example_explanations.json]. Because $17.77^\circ > 5.99^\circ$, it was graded as **`HIGH CONFIDENCE`**:
    > `"Flagged EXCESS_DEPTH because peak knee flexion joint angle (43.22°) was 17.77° below the active baseline threshold (60.99°). Had the peak flexion angle been at least 60.99° (representing a shallower bend of 17.77° less depth), the EXCESS_DEPTH flag would not have fired."` [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_ROM` Explanation**: The range of motion was $136.50^\circ$ (threshold: $128.67^\circ$), yielding a margin of **$7.83^\circ$** [source: 21_xai_outputs/worked_example_explanations.json]. Because $7.83^\circ \le 11.58^\circ$, it was graded as **`LOW CONFIDENCE (Near Noise Floor)`**:
    > `"Flagged EXCESS_ROM because knee range of motion (136.50°) was 7.83° above the active baseline threshold (128.67°). Had the range of motion been no more than 128.67° (representing a restricted excursion of 7.83° less joint travel), the EXCESS_ROM flag would not have fired. [Note: Near noise floor caution appended.]"` [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_VELOCITY` Explanation**: The descent joint velocity was $110.62^\circ/\text{s}$ (threshold: $90.80^\circ/\text{s}$), yielding a margin of **$19.82^\circ/\text{s}$** [source: 21_xai_outputs/worked_example_explanations.json]. Because $19.82^\circ/\text{s} \le 20.43^\circ/\text{s}$, it was graded as **`LOW CONFIDENCE (Near Noise Floor)`** [source: 21_xai_outputs/worked_example_explanations.json].
*   **Minimal Kinematic Intervention (MKI)**: Peak flexion and ROM margins were coupled. The MKI flexion adjustment was $\max(17.77^\circ, 7.83^\circ) = 17.77^\circ$ [source: 21_xai_outputs/worked_example_explanations.json]. The velocity was independent. The MKI output was rendered as:
    > `"The screening flags would not have fired if peak knee flexion joint angle had been at least 17.77° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags) AND descent joint velocity had been at least 19.82°/s slower."` [source: 21_xai_outputs/worked_example_explanations.json].

### 10.7.2. Lunge Worked Example: Subject `PM_104` Repetition 6
On Repetition 6, Subject `PM_104` triggered `EXCESS_DEPTH` and `EXCESS_ROM` [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_DEPTH` Explanation**: Knee flexion angle was $59.12^\circ$ (threshold: $72.68^\circ$), yielding a margin of **$13.55^\circ$** (graded as **`HIGH CONFIDENCE`**) [source: 21_xai_outputs/worked_example_explanations.json].
*   **`EXCESS_ROM` Explanation**: Range of motion was $117.28^\circ$ (threshold: $99.95^\circ$), yielding a margin of **$17.33^\circ$** (graded as **`HIGH CONFIDENCE`**, since $17.33^\circ > 11.58^\circ$) [source: 21_xai_outputs/worked_example_explanations.json].
*   **Minimal Kinematic Intervention (MKI)**: Peak flexion and ROM were coupled. The MKI was computed as $\max(13.55^\circ, 17.33^\circ) = 17.33^\circ$ [source: 21_xai_outputs/worked_example_explanations.json].
    > `"The screening flags would not have fired if peak knee flexion joint angle had been at least 17.33° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags)."` [source: 21_xai_outputs/worked_example_explanations.json].

This lunge example highlights the clinical value of the MKI coupling logic. Because the ROM margin ($17.33^\circ$) exceeded the peak flexion depth margin ($13.55^\circ$), the max-coupling operator successfully selected the larger ROM constraint, ensuring that the counterfactual flexion adjustment satisfies both rules simultaneously. All calculated margins and texts match the Step 10 screening outputs precisely, confirming mathematical consistency.

---

## 10.8. Does Not Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of the counterfactual explanation layer:
*   **Rule Explanations only**: The XAI layer explains rule-firing logic (why a flag was raised given biomarker values); it does **NOT** explain injury causation, biomechanical mechanism, or clinical outcome.
*   **No Diagnostics**: It does not provide clinical diagnostic interpretations or predict future joint injury.
*   **No Prescriptive Training Advice**: The counterfactuals describe mathematical conditions required to clear the flags; they do **not** recommend physical corrections or prescribe training corrections.
*   **No Black-Box Approximations**: It does not explain neural networks or approximate black-box models (not SHAP/LIME); it remains mathematically faithful to the deterministic screening logic.
