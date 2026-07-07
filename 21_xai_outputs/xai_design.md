# Counterfactual Explainable AI (XAI)
## Stage 1 — Design on Paper (CORE Deliverable - Revised)

This document describes the design of a counterfactual Explainable AI (XAI) layer to explain the decisions of the Step 10 rule-based kinematic screening layer. Because the screening layer is deterministic and rule-based, the counterfactual explanations are **faithful by construction** (exact mathematical calculations of the margins, rather than post-hoc local approximations like SHAP or LIME).

> [!IMPORTANT]
> **Hard Framing Constraints:**
> *   The XAI layer explains *why* a kinematic screening flag fired; it does **not** provide clinical diagnostics, injury prognosis, or injury risk forecasts.
> *   No predictive, prognostic, or clinical language is used.
> *   The explanations are framed strictly in terms of joint kinematics, baseline values, and measurement noise boundaries.

---

## 1. Dependency & Execution Order

The counterfactual XAI layer is designed to run directly downstream of the Step 10 Rule-Based Screening Layer:
1.  **Step 10 (Screening Logic):** Ingests repetitions, references their baseline, evaluates rules against validated noise floors, and outputs:
    *   `screening_flag` (`SCREENING_POSITIVE` or `NOT_FLAGGED`)
    *   `fired_rules` (e.g., `["EXCESS_DEPTH", "EXCESS_ROM"]`)
    *   Kinematic measurements ($x_i$), active baseline means ($\mu_{\text{base}, i}$), noise floors ($NF_i$), and thresholds ($T_i$).
2.  **Step 11 (XAI Explanation Logic):** Ingests Step 10's outputs, computes the excess margins, and generates the counterfactual explanations.
3.  *Note on Application:* The Stage 2 build of Step 11 waits until Step 10's per-rep outputs are generated.

---

## 2. Faithfulness by Construction

Traditional model-explainability methods (e.g. SHAP, LIME) are necessary for black-box neural networks because they must reconstruct decision boundaries through local perturbation. However, these methods are approximations and can suffer from explanation infidelity.

In contrast, our rule-based screening layer represents a transparent, glass-box system:
*   The decision rules are the decision logic.
*   The counterfactual explanations are **exact and mathematically perfect**: they calculate the exact margin by which a joint angle or speed crossed a threshold.
*   There is zero explanation error or approximation bias. This is a primary novelty of the Track A architecture.

---

## 3. Convention Check & Counterfactual Wording Templates

### Flexion Included-Angle Convention:
*   Knee joint angles are measured as the sagittal angle between the thigh and shank. Standing extension corresponds to $\approx 180^\circ$. Flexing the knee decreases this angle (closer to $0^\circ$).
*   Therefore:
    *   **Larger joint angle = Shallower flexion (less bend).**
    *   **Smaller joint angle = Deeper flexion (more bend).**

### Verification of Wording Directions:
1.  **Rule 1: EXCESS_DEPTH**
    *   *Threshold:* $T_{\text{depth}} = \mu_{\text{base}, \text{peak}} - NF_{\text{peak}}$
    *   *Fires if:* $x_{\text{peak}} < T_{\text{depth}}$ (knee angle is smaller/deeper than threshold)
    *   *Margin:* $M_{\text{depth}} = T_{\text{depth}} - x_{\text{peak}} > 0$
    *   *Counterfactual State:* The flag would not fire if $x_{\text{peak}} \ge T_{\text{depth}}$ (which is a larger joint angle, physically representing a shallower bend).
    *   *Template:* `"Flagged EXCESS_DEPTH because peak knee flexion joint angle (x_peak°) was M_depth° below the active baseline threshold (T_depth°). Had the peak flexion angle been at least T_depth° (representing a shallower bend of M_depth° less depth), the EXCESS_DEPTH flag would not have fired."`
    *   *Validation:* In Stage 2, we will explicitly verify that the numeric values align (e.g. if $x_{\text{peak}} = 43^\circ$ and $T = 58^\circ$, then the template states "at least 58.00° (representing a shallower bend of 15.00°)", which is directionally correct since $58^\circ$ is a larger joint angle than $43^\circ$).
2.  **Rule 2: EXCESS_VELOCITY**
    *   *Threshold:* $T_{\text{velocity}} = \mu_{\text{base}, \text{velocity}} + NF_{\text{velocity}}$
    *   *Fires if:* $x_{\text{velocity}} > T_{\text{velocity}}$ (joint speed exceeds threshold)
    *   *Margin:* $M_{\text{velocity}} = x_{\text{velocity}} - T_{\text{velocity}} > 0$
    *   *Counterfactual State:* The flag would not fire if $x_{\text{velocity}} \le T_{\text{velocity}}$ (a slower joint speed).
    *   *Template:* `"Flagged EXCESS_VELOCITY because descent joint velocity (x_velocity°/s) was M_velocity°/s above the active baseline threshold (T_velocity°/s). Had the descent velocity been no more than T_velocity°/s (representing a slower movement of M_velocity°/s less speed), the EXCESS_VELOCITY flag would not have fired."`
3.  **Rule 3: EXCESS_ROM**
    *   *Threshold:* $T_{\text{rom}} = \mu_{\text{base}, \text{rom}} + NF_{\text{rom}}$
    *   *Fires if:* $x_{\text{rom}} > T_{\text{rom}}$ (joint excursion exceeds threshold)
    *   *Margin:* $M_{\text{rom}} = x_{\text{rom}} - T_{\text{rom}} > 0$
    *   *Counterfactual State:* The flag would not fire if $x_{\text{rom}} \le T_{\text{rom}}$ (a smaller range of motion).
    *   *Template:* `"Flagged EXCESS_ROM because knee range of motion (x_rom°) was M_rom° above the active baseline threshold (T_rom°). Had the range of motion been no more than T_rom° (representing a restricted excursion of M_rom° less joint travel), the EXCESS_ROM flag would not have fired."`

---

## 4. Multi-Rule Handling & Minimal Kinematic Intervention (MKI) Arithmetic

When a repetition triggers multiple screening rules, the XAI layer generates descriptions for all fired rules and calculates the **Minimal Kinematic Intervention (MKI)** required to clear them. 

Under the explicit assumption that range of motion scales directly with peak flexion depth (assuming a constant standing extension start point, i.e., $x_{\text{rom}} \approx x_{\text{extension}} - x_{\text{peak}}$):
*   To clear `EXCESS_DEPTH`, the peak flexion angle must increase (become shallower) by at least $M_{\text{depth}}^\circ$.
*   To clear `EXCESS_ROM`, the peak flexion angle must also increase (become shallower) by at least $M_{\text{rom}}^\circ$ to restrict joint range of motion.
*   Therefore, the MKI does **not** assume $M_{\text{depth}}$ is always sufficient. Instead, it computes the exact maximum of the required changes:
    $$\Delta \theta_{\text{MKI}} = \max(M_{\text{depth}}, M_{\text{rom}})$$
*   **MKI Output Statement (Descriptive Set of Changes):**
    `"The screening flags would not have fired if peak knee flexion joint angle had been at least Delta_theta_MKI° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags)."`
    *(Note: If velocity also fires, it is appended to the set of conditions: "AND descent joint velocity had been at least M_velocity°/s slower.")*
*   *Biomechanical Assumption Note:* This MKI calculation explicitly assumes ROM scales directly with peak flexion depth (constant start point). This is a reasonable illustrative computation for demonstrating coupled kinematic adjustments, rather than a universal biomechanical law.

---

## 5. Uncertainty-Aware Confidence Grading

The explanations incorporate the Phase 7 validated measurement noise boundaries to express epistemic confidence:
*   A deviation margin $M_i$ is evaluated against a confidence buffer $B_i$:
    $$B_i = 0.5 \times NF_i$$
*   **Confidence Grading:**
    *   If $M_i > B_i$: Flagged as **HIGH CONFIDENCE**. The deviation is large enough to be clearly distinguished from tracking error.
    *   If $M_i \le B_i$: Flagged as **LOW CONFIDENCE (Near Noise Floor)**.
        *   *Confidence Note appended:* `"Note: The deviation margin (M_i) is close to the monocular camera's validated measurement uncertainty boundaries. This flag should be interpreted with caution as minor tracking fluctuations could have triggered it."`

---

## 6. Output Specification

For each analyzed repetition, the XAI layer will write a structured explanation block to a text log and JSON file:
```json
{
  "rep_number": 6,
  "screening_status": "SCREENING_POSITIVE",
  "fired_rules": ["EXCESS_DEPTH", "EXCESS_ROM"],
  "explanations": [
    {
      "rule": "EXCESS_DEPTH",
      "margin": 15.34,
      "confidence": "HIGH",
      "text": "Flagged EXCESS_DEPTH because peak knee flexion joint angle (43.22°) was 15.34° below the active baseline threshold (58.56°). Had the peak flexion angle been at least 58.56° (representing a shallower bend of 15.34° less depth), the EXCESS_DEPTH flag would not have fired."
    },
    {
      "rule": "EXCESS_ROM",
      "margin": 7.83,
      "confidence": "LOW",
      "text": "Flagged EXCESS_ROM because knee range of motion (136.50°) was 7.83° above the active baseline threshold (128.67°). Had the range of motion been no more than 128.67° (representing a restricted excursion of 7.83° less joint travel), the EXCESS_ROM flag would not have fired. Note: The deviation margin (7.83°) is close to the monocular camera's validated measurement uncertainty boundaries. This flag should be interpreted with caution as minor tracking fluctuations could have triggered it."
    }
  ],
  "minimal_kinematic_intervention": "The screening flags would not have fired if peak knee flexion joint angle had been at least 15.34° shallower (which, assuming range of motion scales directly with peak flexion depth under a constant standing extension start point, would simultaneously restrict joint range of motion sufficiently to clear both the EXCESS_DEPTH and EXCESS_ROM flags)."
}
```

---

## 7. "What This Layer Does NOT Claim" (Guardrails)

*   **No Diagnostic Interpretations:** Explains rule triggers, not physical pathology or clinical diagnoses.
*   **No Prescriptive Advice:** The counterfactuals describe what would mathematically clear the flags; they do **not** recommend physical corrections or prescribe training corrections (e.g. they do not state "you should go shallower," but rather "had the angle been at least T°, the flag would not have fired").
*   **No Model Approximations (SHAP/LIME):** Does not explain neural networks or approximate black-box models; it is faithful to the deterministic rules.
*   **No Deployed System:** It is a research prototype of explainable joint screening.

---

## 8. Application Plan (Stage 2)

Once the Step 10 rules and margins CSV are generated:
1.  Ingest the data for Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`).
2.  Run the counterfactual engine and save JSON/text outputs to `21_xai_outputs/worked_example_explanations.json`.
3.  First Validation Check: Verify that the direction of the rendered text matches the numeric direction of the knee flexion angles (i.e. larger angle = shallower bend).
4.  Print the generated text blocks to the screen for validation.
