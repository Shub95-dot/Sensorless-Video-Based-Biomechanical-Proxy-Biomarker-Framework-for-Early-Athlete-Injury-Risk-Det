# Chapter 11: Biomechanical Digital Twin

This chapter presents the design and demonstration of a continuously-updating personalised "Digital Twin" framework. Static baseline references (Chapter 9) establish a fixed movement template from early repetitions [source: 22_dissertation_writing/results_baseline_v1.md]. However, in clinical rehabilitation and athletic monitoring, movement patterns evolve dynamically due to warm-up effects, fatigue, or recovery. To capture these shifts, a digital twin must update its reference state continuously. We describe an architecture that applies a conditional update rule: the twin absorbs repetitions that fall within the camera's validated noise floor, while rejecting deviant trials to prevent baseline contamination.

---

## 11.1. Purpose and Design Motivation

Unlike the static personalised baseline (Chapter 9), which evaluates joint angle deviations relative to a fixed early-session template [source: 22_dissertation_writing/results_baseline_v1.md], a clinical digital twin must accommodate natural movement drift. An athlete's kinematics shift over time due to warm-up effects, muscular fatigue, learning adaptations, or clinical recovery.

The primary objective of this chapter is to demonstrate an architectural extension of the personalised baseline: a continuous-update "Digital Twin" [source: 19_digital_twin_outputs/twin_design.md]. The twin maintains a rolling statistical reference profile of the user's active kinematics. When a new repetition is performed, the twin gates it against the active reference using the Chapter 8 validated projection noise floor [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]. To ensure stability, the twin applies a **conditional update rule**: it incorporates the repetition into the reference mean if the trial is within the noise floor, but rejects the update if a deviation is detected, preventing the baseline from being corrupted by isolated technique breakdowns.

### 11.1.1. Architectural Constraints and Scope
To align with the screening scope across this dissertation [source: 19_digital_twin_outputs/twin_design.md]:
1.  **Non-Predictive**: The twin does not forecast future movement trajectories, performance, or injury risk; it characterises the active reference state.
2.  **No Learned Parameters**: The update mechanism is an arithmetic running mean without machine learning weights, training rates, or state decay.
3.  **Pseudo-Session Axis**: Consistent with Chapter 9, within-session repetition order forms sequential **pseudo-sessions** [source: 22_dissertation_writing/results_baseline_v1.md]. True longitudinal multi-session tracking across days is deferred to future work.

---

## 11.2. Continuous-Update Mechanism

The digital twin state for biomarker $i$ at time step $t$ consists of a running reference mean ($\mu_{t, i}$), sample size ($N_{t, i}$), descriptive standard deviation ($SD_{t, i}$), and fixed validated noise floor ($NF_i = 1.96 \times SD_{\text{proj}, i}$) transferred from Chapter 8 [source: 19_digital_twin_outputs/twin_design.md].

### 11.2.1. Mathematical Conditional Update Rules
When a new repetition $x_{t+1, i}$ is ingested, its absolute deviation ($\Delta_i = |x_{t+1, i} - \mu_{t, i}|$) from the active reference mean is evaluated [source: 19_digital_twin_outputs/twin_design.md]:
*   **`WITHIN-NOISE` Update ($\Delta_i \le NF_i$)**: The repetition reflects normal variation. The twin updates the running mean incrementally:
    $$\mu_{t+1, i} = \frac{N_{t, i} \cdot \mu_{t, i} + x_{t+1, i}}{N_{t, i} + 1}, \quad N_{t+1, i} = N_{t, i} + 1$$
*   **`DEVIATION DETECTED` Rejection ($\Delta_i > NF_i$)**: The repetition represents a significant kinematic shift. To prevent reference contamination, the repetition is **excluded** from the update:
    $$\mu_{t+1, i} = \mu_{t, i}, \quad N_{t+1, i} = N_{t, i}$$

This conditional update rule ensures self-stabilization: the reference tracks slow, normal kinematic shifts while locking flat during movement faults without allowing them to drift the baseline.

---

## 11.3. Results -- Reference Evolution and Locking Flat

The continuous-update mechanism was validated across three sequential pseudo-sessions using 10-repetition sequences from Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) [source: 19_digital_twin_outputs/twin_design.md]: Initialization (Reps 1–2, $\mu_0$), Normal Practice (Reps 3–5), and Deviated Practice (Reps 6–10).

### 11.3.1. Squat Demonstration (Subject `PM_113`)
Subject `PM_113` performed 5 correct squats followed by 5 restricted-depth squats [source: 19_digital_twin_outputs/twin_design.md]:
*   **Initialization (Reps 1–2)**: Established initial reference mean peak flexion at **$72.98^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Evolution (Reps 3–5)**: Each rep fell within the peak flexion noise floor ($\pm 11.99^\circ$), updating the running mean from $72.98^\circ$ to **$72.30^\circ$** (Rep 3), **$70.59^\circ$** (Rep 4), and **$69.21^\circ$** (Rep 5) [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Locking Flat (Reps 6–10)**: Rep 6 peak flexion dropped to $43.22^\circ$ (deviation: **$25.99^\circ > \pm 11.99^\circ$**), triggering `DEVIATION DETECTED` [source: 19_digital_twin_outputs/worked_example_twin.csv]. Across Reps 6–10, peak flexion deltas ranged from **$19.47^\circ$ to $31.90^\circ$**, causing the peak flexion reference to lock flat at **$69.21^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

### 11.3.2. Lunge Demonstration (Subject `PM_104`)
Subject `PM_104` performed 5 correct lunges followed by 5 restricted-depth lunges [source: 19_digital_twin_outputs/twin_design.md]:
*   **Initialization (Reps 1–2)**: Established initial reference mean peak flexion at **$84.66^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Evolution (Reps 3–5)**: Correct reps updated the reference mean to **$85.11^\circ$** (Rep 3), **$84.00^\circ$** (Rep 4), and **$85.48^\circ$** (Rep 5) [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Locking Flat (Reps 6–10)**: Restricted-depth lunges yielded peak flexion deviations relative to active reference ($85.48^\circ$) ranging from **$20.91^\circ$ to $32.80^\circ > \pm 11.99^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv]. Exceeding the noise floor, all five reps were excluded, locking the reference flat at **$85.48^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

The 95% noise-floor band ($NF_i$) tracks the evolving reference dynamically across Pseudo-Session 2 before locking during Pseudo-Session 3.

---

## 11.4. Per-Biomarker Update Independence

A key design feature is that update logic operates independently for each biomarker on the same repetition. Joint angles, ranges of motion, and velocities represent distinct kinematic dimensions and can exist in different gating states during a single trial.

This is demonstrated on **Repetition 7** of Squat Subject `PM_113` [source: 19_digital_twin_outputs/worked_example_twin.csv]:
*   **Peak Flexion (`DEVIATION DETECTED`)**: Peak flexion ($49.75^\circ$) deviated by $19.47^\circ > \pm 11.99^\circ$ floor; update withheld, reference locked at **$69.21^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Range of Motion (`WITHIN-NOISE`)**: ROM ($129.84^\circ$) deviated by $20.36^\circ \le \pm 23.17^\circ$ floor; reference updated from $109.48^\circ$ to **$112.88^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Descent Velocity (`WITHIN-NOISE`)**: Velocity ($62.83^\circ/\text{s}$) deviated by $17.79^\circ/\text{s} \le \pm 40.86^\circ/\text{s}$ floor; reference updated from $45.03^\circ/\text{s}$ to **$48.00^\circ/\text{s}$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

Rather than rejecting the entire trial, the twin selectively updates valid biomarker components, maximizing data utilization while isolating specific deviations.

---

## 11.5. Explainable Exclusion and Epistemic Humility

When excluding a repetition from the reference update, the twin generates a transparent, measurement-based explanation. During Squat Subject `PM_113` Repetition 6, the framework generated [source: 19_digital_twin_outputs/worked_example_twin.csv]:

> *"Rep 6 deviated from your baseline beyond validated measurement uncertainty (on biomarker peak flexion). The twin does not update the reference from this rep, because from a single observation it cannot distinguish a transient fluctuation from a genuine sustained change — that distinction would require the deviation to persist across multiple sessions."*

This design contrasts with black-box classification models. Rather than declaring a repetition "bad" or issuing a clinical verdict, the message reflects **epistemic humility**: it attributes withholding to single-observation ambiguity, references camera measurement uncertainty logic, and transparently communicates system limits.

---

## 11.6. Transient-vs-Sustained Adaptation (Future Work)

The explainable exclusion message directly motivates future research on continuous update architectures:
*   **Transient Fluctuations**: Restricted-depth reps in this study represent temporary within-session deviations. The twin correctly isolates these faults and keeps the baseline stable [source: 19_digital_twin_outputs/twin_design.md].
*   **Sustained Adaptation**: If an athlete permanently alters movement strategy (clinical recovery or new technique), rejecting all future reps would lock the baseline indefinitely.
*   **Future Longitudinal Persistence**: A deployed longitudinal twin requires multi-session persistence logic: if a deviation persists across multiple real sessions, the twin must absorb the shift, adapting the reference mean to the new movement template.

---

## 11.7. What This Framework Does NOT Claim

To maintain scientific integrity and align with screening scope:
*   **No Predictive Forecasting**: Does not forecast future movement parameters, fatigue, or recovery.
*   **No Injury Risk Scoring**: Does not calculate injury risk indices or likelihoods.
*   **No Correctness Verdicts**: Flags baseline deviations, not correctness. Cohort correctness labels serve only to validate rejection logic [source: 19_digital_twin_outputs/twin_design.md].
*   **Not a Deployed Clinical System**: Serves as a software architectural prototype.

---

## 11.8. Figures and Provenance

Publication-ready figure; data provenance in `19_digital_twin_outputs/` [source: 19_digital_twin_outputs/twin_tracking.png]:

*   **Figure 11.1: Continuously-Updating Personalised Digital Twin with Conditional Update Gating**
    *   `19_digital_twin_outputs/twin_tracking.png` — time-series plots for Squat `PM_113` and Lunge `PM_104` across 10 repetitions, showing active reference mean adapting to correct reps (Reps 1–5), locking flat for deviant reps (Reps 6–10), and moving 95% projection noise floor bands.
