# Chapter 11: Biomechanical Digital Twin

This chapter presents the design and demonstration of a continuously-updating personalised "Digital Twin" framework. Static baseline references—such as the session baseline developed in Chapter 9—establish a fixed movement template from early repetitions [source: 22_dissertation_writing/results_baseline_v1.md]. However, in clinical rehabilitation and athletic monitoring, a subject's movement patterns change dynamically across days or weeks. To capture these shifts, a digital twin must update its reference state continuously as new movement data is ingested. This chapter describes an architectural framework that applies a conditional update rule: the twin absorbs repetitions that fall within the camera's validated noise floor, while rejecting anomalous, deviant trials to prevent baseline contamination. First, we outline the purpose and design motivation of the framework. Second, we present the mathematical update rules. Third, we demonstrate the twin's behavior using squat and lunge repetition sequences. Fourth, we describe the explainable exclusion feature and discuss how it motivates transient-vs-sustained adaptation. Finally, we establish the framework's limitations and scope boundaries.

---

## 11.1. Purpose and Design Motivation

The static personalised baseline presented in Chapter 9 demonstrates that a single sagittal camera can detect individual joint angle deviations relative to a fixed early-session baseline [source: 22_dissertation_writing/results_baseline_v1.md]. While useful for short-term form checking, a static template cannot accommodate natural movement drift. An athlete's kinematics shift over time due to warm-up effects, muscular fatigue, learning adaptations, or clinical recovery. A clinical screening framework must therefore adapt to these slow, normal variations.

The primary objective of this chapter is to demonstrate an architectural extension of the personalised baseline: a continuous-update "Digital Twin" [source: 19_digital_twin_outputs/twin_design.md]. The twin maintains a lightweight, rolling statistical profile of the user's active kinematics. When a new movement is performed, the twin gates it against the current reference using the Chapter 8 validated projection noise floor [source: 22_dissertation_writing/results_uncertainty_framework_v1.md]. To ensure stability, the twin applies a **conditional update rule**: it incorporates the repetition into the reference mean if the trial is within the noise floor, but rejects the update if a deviation is detected. This prevents the twin's reference from being corrupted by isolated technique breakdowns or fatigue-induced compensation strategies.

### 11.1.1. Hard Architectural Constraints and Scope
To align with the screening scope established across this dissertation, we define several hard guardrails for this demonstration [source: 19_digital_twin_outputs/twin_design.md]:
1.  **Non-Predictive**: The twin does not predict or forecast future movement trajectories, performance metrics, or injury risk. It strictly updates and characterises the active reference state.
2.  **No Learned Parameters**: It is not a machine learning model. It does not utilize training weights, learning rates, state decay, or neural networks. The update mechanism is a simple arithmetic running mean.
3.  **Pseudo-Session Axis**: Consistent with Chapter 9, because available physical therapy datasets are single-session, we utilize within-session repetition order to construct sequential **pseudo-sessions** [source: 22_dissertation_writing/results_baseline_v1.md]. True longitudinal tracking across days is deferred.

---

## 11.2. Continuous-Update Mechanism

The digital twin state for biomarker $i$ at time step $t$ consists of a running reference mean ($\mu_{t, i}$), a running baseline sample size ($N_{t, i}$), a descriptive baseline standard deviation ($SD_{t, i}$), and the fixed validated noise floor ($NF_i$) [source: 19_digital_twin_outputs/twin_design.md].

### 11.2.1. Mathematical Conditional Update Rules
When a new repetition $x_{t+1, i}$ is ingested, the absolute deviation ($\Delta_i$) from the current active reference mean is evaluated:
$$\Delta_i = |x_{t+1, i} - \mu_{t, i}|$$

The twin state is updated according to the following conditional logic [source: 19_digital_twin_outputs/twin_design.md]:
*   **`WITHIN-NOISE` Update ($\Delta_i \le NF_i$)**: The repetition falls within normal measurement variation, indicating stable execution. The twin updates the running mean incrementally:
    $$\mu_{t+1, i} = \frac{N_{t, i} \cdot \mu_{t, i} + x_{t+1, i}}{N_{t, i} + 1}$$
    $$N_{t+1, i} = N_{t, i} + 1$$
*   **`DEVIATION DETECTED` Rejection ($\Delta_i > NF_i$)**: The repetition represents a significant kinematic shift. To prevent the baseline reference from being contaminated by anomalous technique changes, the repetition is **excluded** from the update:
    $$\mu_{t+1, i} = \mu_{t, i}$$
    $$N_{t+1, i} = N_{t, i}$$

This conditional update rule ensures self-stabilization: the reference tracks slow, normal kinematic shifts while isolating movement faults without allowing them to drift the baseline. Crucially, excluded repetitions are not silently discarded; they are counted, flagged, and assigned a transparent, measurement-based explanation.

---

## 11.3. Results -- Reference Evolution and Locking Flat

The continuous-update mechanism was validated by partitioning the 10-repetition sequences of Squat Subject 8 (`PM_113`) and Lunge Subject 6 (`PM_104`) into three sequential pseudo-sessions [source: 19_digital_twin_outputs/twin_design.md]:
1.  **Pseudo-Session 1 (Initialization - Reps 1–2)**: Correct repetitions used to calculate the initial twin reference ($\mu_0$).
2.  **Pseudo-Session 2 (Normal Practice - Reps 3–5)**: Correct repetitions used to evaluate the twin's reference adaptation.
3.  **Pseudo-Session 3 (Deviated Practice - Reps 6–10)**: Incorrect repetitions used to evaluate the twin's deviation rejection.

### 11.3.1. Squat Demonstration (Subject `PM_113`)
Subject `PM_113` performed $5$ correct squats followed by $5$ shallower, restricted-depth squats [source: 19_digital_twin_outputs/twin_design.md].
*   **Initialization (Reps 1–2)**: Established the initial reference mean peak flexion at **$72.98^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Evolution (Reps 3–5)**: Each rep fell within the peak flexion noise floor ($\pm 11.99^\circ$), updating the running mean. The peak flexion reference mean evolved from $72.98^\circ$ to **$72.30^\circ$** (after Rep 3), **$70.59^\circ$** (after Rep 4), and finally **$69.21^\circ$** (after Rep 5) as the twin absorbed the kinematics [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Locking Flat (Reps 6–10)**: Rep 6 peak flexion dropped to $43.22^\circ$, yielding a deviation of **$25.99^\circ$** relative to the active reference ($69.21^\circ$), exceeding the $\pm 11.99^\circ$ noise floor [source: 19_digital_twin_outputs/worked_example_twin.csv]. The repetition was flagged as `DEVIATION DETECTED` and excluded from the update. Across Reps 6–10, all peak flexion joint angles dropped, yielding deltas from reference ranging from **$19.47^\circ$ to $31.90^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv]. Consequently, the peak flexion reference locked flat at **$69.21^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

### 11.3.2. Lunge Demonstration (Subject `PM_104`)
Subject `PM_104` performed $5$ correct lunges followed by $5$ shallower lunges [source: 19_digital_twin_outputs/twin_design.md].
*   **Initialization (Reps 1–2)**: Established the initial reference mean peak flexion at **$84.66^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Evolution (Reps 3–5)**: Each correct rep updated the reference mean. The peak flexion reference evolved to **$85.11^\circ$** (after Rep 3), **$84.00^\circ$** (after Rep 4), and **$85.48^\circ$** (after Rep 5) [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Reference Locking Flat (Reps 6–10)**: Incorrect reps dropped, yielding peak flexion deviations relative to active reference ($85.48^\circ$) ranging from **$20.91^\circ$ to $32.80^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv]. Because they exceeded the $\pm 11.99^\circ$ noise floor, all five reps were flagged as `DEVIATION DETECTED`, and the reference locked flat at **$85.48^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

Crucially, because the 95% noise-floor band ($NF_i$) is computed relative to the active reference, the shaded uncertainty band tracks the evolving reference dynamically across Pseudo-Session 2 before locking during Pseudo-Session 3.

---

## 11.4. Per-Biomarker Update Independence

A key design feature of the digital twin is that the update logic operates independently for each biomarker on the same repetition. Because joint angles, ranges of motion, and movement velocities represent distinct kinematic dimensions, they can be in different gating states during the same trial.

This independent gating is clearly demonstrated on **Repetition 7** of Squat Subject `PM_113` [source: 19_digital_twin_outputs/worked_example_twin.csv]:
*   **Peak Flexion (`DEVIATION DETECTED`)**: The peak flexion angle of $49.75^\circ$ deviated from the active reference ($69.21^\circ$) by $19.47^\circ$, exceeding the $\pm 11.99^\circ$ noise floor [source: 19_digital_twin_outputs/worked_example_twin.csv]. The update was withheld, and the reference locked flat at **$69.21^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Range of Motion (`WITHIN-NOISE`)**: The joint ROM of $129.84^\circ$ deviated from the active ROM reference ($109.48^\circ$) by $20.36^\circ$, which was smaller than the $\pm 23.17^\circ$ ROM noise floor [source: 19_digital_twin_outputs/worked_example_twin.csv]. Consequently, the ROM reference mean updated from $109.48^\circ$ to **$112.88^\circ$** [source: 19_digital_twin_outputs/worked_example_twin.csv].
*   **Descent Velocity (`WITHIN-NOISE`)**: The joint velocity of $62.83^\circ/\text{s}$ deviated from the active velocity reference ($45.03^\circ/\text{s}$) by $17.79^\circ/\text{s}$, well within the $\pm 40.86^\circ/\text{s}$ velocity noise floor [source: 19_digital_twin_outputs/worked_example_twin.csv]. The velocity reference mean updated from $45.03^\circ/\text{s}$ to **$48.00^\circ/\text{s}$** [source: 19_digital_twin_outputs/worked_example_twin.csv].

This confirms that the digital twin does not reject the entire repetition if a single biomarker fails. Instead, it selectively updates the reference components that fall within normal tracking limits, maximizing the utilization of valid joint data while isolating specific deviations.

---

## 11.5. Explainable Exclusion and Epistemic Humility

When the digital twin excludes a repetition from the reference update, it generates a transparent, measurement-based exclusion explanation. For example, during Squat Subject `PM_113` Repetition 6, the framework generated the following message for the peak flexion biomarker [source: 19_digital_twin_outputs/worked_example_twin.csv]:

> *"Rep 6 deviated from your baseline beyond validated measurement uncertainty (on biomarker peak flexion). The twin does not update the reference from this rep, because from a single observation it cannot distinguish a transient fluctuation from a genuine sustained change — that distinction would require the deviation to persist across multiple sessions."*

This explainable exclusion design represents a deliberate contrast with typical black-box AI classification models. Rather than declaring a repetition to be "bad" or issuing a clinical quality verdict, the explanation is framed around **epistemic humility** and **measurement logic**:
*   It states that the update is withheld because of the ambiguity of a single observation.
*   It explains the mathematical reason (exceeding validated camera uncertainty bounds).
*   It transparently communicates the limits of the tracking logic.

---

## 11.6. Transient-vs-Sustained Adaptation (Future Work)

The explainable exclusion message directly motivates the primary limitation and future-work direction of the continuous-update architecture:
*   **Transient Fluctuations**: In this demonstration, the restricted-depth repetitions represent a temporary technique deviation within a single practice session. For isolating and flagging these transient form-breakdowns, the twin's rejection logic performs correctly: it isolates the deviations and keeps the baseline stable [source: 19_digital_twin_outputs/twin_design.md].
*   **Sustained Adaptation**: However, if an athlete permanently shifts their movement strategy (due to clinical recovery or learning a new technique), the twin's current logic would indefinitely reject all future repetitions, locking the baseline forever.
*   **Future Longitudinal Twin**: To address this, a deployed longitudinal twin must incorporate a temporal rule: if a deviation persists across multiple real sessions, the twin must absorb the change, adapting the reference mean to the new movement template. Designing this multi-session temporal absorption logic is queued as a key future research item.

---

## 11.7. Does Not Claim

To maintain scientific integrity and align with the screening scope established across this dissertation, we outline the boundaries of the digital twin framework:
*   **No Predictive Forecasting**: The twin does not forecast future movement parameters, muscular fatigue, or clinical recovery.
*   **No Injury Risk Scoring**: It does not calculate a risk index or evaluate injury likelihood.
*   **No Correctness Verdicts**: The twin flags kinematic deviations from baseline, not correctness. Cohort correctness labels are used only as a validation check to evaluate the twin's rejection logic, never as the twin's own output [source: 19_digital_twin_outputs/twin_design.md].
*   **Not a Deployed Clinical System**: It is a software prototype demonstrating baseline updating and gating logic.

---

## 11.8. Figures and Provenance

The findings presented in this chapter are supported by the following publication-ready figure, with data provenance detailed in `19_digital_twin_outputs/` [source: 19_digital_twin_outputs/twin_tracking.png]:

*   **Figure 11.1: Continuously-Updating Personalised Digital Twin with Conditional Update Gating**
    *   *Source file*: `19_digital_twin_outputs/twin_tracking.png`
    *   *Description*: Time-series plots for squat subject `PM_113` and lunge subject `PM_104` across 10 repetitions, showing the active reference mean dynamically adapting to correct reps (Reps 1–5), locking flat to exclude deviant reps (Reps 6–10), and the 95% projection noise floor band tracking the moving reference.
