# Appendix C: Counterfactual XAI Parameter Verification Table

This appendix provides the exhaustive parameter cross-check table evaluating the mathematical agreement between the Step 10 Rule-Based Screening Layer (`worked_example_screening.csv`) and the Step 11 Counterfactual Explainable AI (XAI) engine (`worked_example_explanations.json`).

---

## C.1. Verification Overview

To empirically verify the **faithfulness by construction** claim (Chapter 12, Section 12.3), every parameter ingested and rendered by the counterfactual explanation engine was cross-checked against the raw kinematics and deviation margins exported from the screening logic [source: 20_screening_outputs/worked_example_screening.csv / 21_xai_outputs/worked_example_explanations.json].

Because the XAI engine calculates counterfactual margins directly from the screening layer's exact algebraic decision boundaries ($M_{\text{depth}} = T_{\text{depth}} - x_{\text{peak}}$, $M_{\text{rom}} = x_{\text{rom}} - T_{\text{rom}}$, $M_{\text{velocity}} = x_{\text{velocity}} - T_{\text{velocity}}$), the rendered margins exhibit **zero approximation error** [source: 21_xai_outputs/xai_design.md].

---

## C.2. Verification Cross-Check Table

Table C.1 presents the side-by-side parameter verification for Repetition 6 of Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`).

### Table C.1: Step 10 Screening vs. Step 11 XAI Parameter Cross-Check (Repetition 6)

| Subject (Trial) | Biomarker / Rule | Step 10 Screening Value [source: worked_example_screening.csv] | Step 11 Explanation Value [source: worked_example_explanations.json] | Calculated Margin (Step 10) [source: worked_example_screening.csv] | Rendered Margin (Step 11) [source: worked_example_explanations.json] | Faithfulness Agreement |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **PM_113 (Squat)** | Peak Flexion | $43.2178^\circ$ | $43.22^\circ$ | $17.7703^\circ$ | $17.77^\circ$ | **Exact Match** |
| | ROM | $136.4995^\circ$ | $136.50^\circ$ | $7.8325^\circ$ | $7.83^\circ$ | **Exact Match** |
| | Descent Velocity | $110.6160^\circ/\text{s}$ | $110.62^\circ/\text{s}$ | $19.8195^\circ/\text{s}$ | $19.82^\circ/\text{s}$ | **Exact Match** |
| **PM_104 (Lunge)** | Peak Flexion | $59.1212^\circ$ | $59.12^\circ$ | $13.5540^\circ$ | $13.55^\circ$ | **Exact Match** |
| | ROM | $117.2779^\circ$ | $117.28^\circ$ | $17.3306^\circ$ | $17.33^\circ$ | **Exact Match** |
| | Descent Velocity | $59.9580^\circ/\text{s}$ | N/A (Not Fired) | $0.0000^\circ/\text{s}$ | N/A (Not Fired) | **Exact Match** |

The cross-check demonstrates a mathematically exact match across all tracked parameters and derived margins, confirming that the counterfactual explanation layer operates with 100% faithfulness to the underlying screening boundaries, with variations limited strictly to formatting display rounding [source: 21_xai_outputs/worked_example_explanations.json].
