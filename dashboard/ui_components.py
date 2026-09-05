"""
ui_components.py
================
Streamlit UI rendering helpers for the kinematic screening dashboard.
Handles biomarker tables, screening cards, XAI text, uncertainty charts,
and the public-facing final report summary using native Streamlit components.

NO raw code, HTML, or table markup.
NO emojis.
Friendly, accessible academic tone.
"""

import numpy as np
import pandas as pd
import streamlit as st

from constants import (
    NOISE_FLOORS,
    TRANSFER_WEIGHTS,
    WEIGHT_LABELS,
    WEIGHT_PERCENTAGES,
    BORDERLINE_FRACTION,
    ASSUMED_FPS,
    DISCLAIMER_TEXT,
)


def render_disclaimer():
    """Render the persistent disclaimer banner at the top of the page."""
    st.info(f"**Disclaimer:** {DISCLAIMER_TEXT}")


def _get_deviation_status(value, baseline, noise_floor, direction="above", flag_label="FLAGGED"):
    """Determine deviation status without any raw HTML or emojis."""
    if np.isnan(value) or np.isnan(baseline):
        return "N/A"

    if direction == "above":
        threshold = baseline + noise_floor
        is_flagged = value > threshold
        borderline_zone = baseline + noise_floor * (1 - BORDERLINE_FRACTION)
        is_borderline = not is_flagged and value > borderline_zone
    else:  # below
        threshold = baseline - noise_floor
        is_flagged = value < threshold
        borderline_zone = baseline - noise_floor * (1 - BORDERLINE_FRACTION)
        is_borderline = not is_flagged and value < borderline_zone

    if is_flagged:
        return flag_label
    elif is_borderline:
        return "Borderline"
    else:
        return "Within Band"


def render_biomarker_table(biomarkers, screening):
    """
    Render the biomarker summary using a clean Streamlit dataframe.
    No raw HTML, code, or table markup. No emojis.
    """
    st.subheader("Biomarker Summary")

    baseline_peak = screening.baseline_peak_flexion
    baseline_rom = screening.baseline_rom
    baseline_velocity = screening.baseline_velocity

    velocity_deg_s = abs(biomarkers.mean_descent_velocity_deg_per_frame) * ASSUMED_FPS

    status_peak = _get_deviation_status(
        biomarkers.peak_flexion_deg,
        baseline_peak,
        NOISE_FLOORS["peak_flexion"],
        direction="below",
        flag_label="FLAGGED (Excess Depth)",
    )
    status_rom = _get_deviation_status(
        biomarkers.rom_deg,
        baseline_rom,
        NOISE_FLOORS["rom"],
        direction="above",
        flag_label="FLAGGED (Excess ROM)",
    )
    status_vel = _get_deviation_status(
        velocity_deg_s,
        baseline_velocity,
        NOISE_FLOORS["velocity"],
        direction="above",
        flag_label="FLAGGED (Excess Velocity)",
    )

    rows = [
        {
            "Biomarker": "Peak Flexion (Depth)",
            "Measured Value": f"{biomarkers.peak_flexion_deg:.2f}°" if not np.isnan(biomarkers.peak_flexion_deg) else "N/A",
            "Personal Baseline": f"{baseline_peak:.2f}°" if not np.isnan(baseline_peak) else "N/A",
            "Screening Threshold": f"{baseline_peak - NOISE_FLOORS['peak_flexion']:.2f}°" if not np.isnan(baseline_peak) else "N/A",
            "Deviation": f"{abs(biomarkers.peak_flexion_deg - baseline_peak):.2f}°" if not (np.isnan(biomarkers.peak_flexion_deg) or np.isnan(baseline_peak)) else "N/A",
            "Screening Status": status_peak,
        },
        {
            "Biomarker": "Range of Motion (ROM)",
            "Measured Value": f"{biomarkers.rom_deg:.2f}°" if not np.isnan(biomarkers.rom_deg) else "N/A",
            "Personal Baseline": f"{baseline_rom:.2f}°" if not np.isnan(baseline_rom) else "N/A",
            "Screening Threshold": f"{baseline_rom + NOISE_FLOORS['rom']:.2f}°" if not np.isnan(baseline_rom) else "N/A",
            "Deviation": f"{abs(biomarkers.rom_deg - baseline_rom):.2f}°" if not (np.isnan(biomarkers.rom_deg) or np.isnan(baseline_rom)) else "N/A",
            "Screening Status": status_rom,
        },
        {
            "Biomarker": "Descent Velocity",
            "Measured Value": f"{velocity_deg_s:.2f}°/s" if not np.isnan(velocity_deg_s) else "N/A",
            "Personal Baseline": f"{baseline_velocity:.2f}°/s" if not np.isnan(baseline_velocity) else "N/A",
            "Screening Threshold": f"{baseline_velocity + NOISE_FLOORS['velocity']:.2f}°/s" if not np.isnan(baseline_velocity) else "N/A",
            "Deviation": f"{abs(velocity_deg_s - baseline_velocity):.2f}°/s" if not (np.isnan(velocity_deg_s) or np.isnan(baseline_velocity)) else "N/A",
            "Screening Status": status_vel,
        },
        {
            "Biomarker": "Movement Smoothness (Jerk Proxy)",
            "Measured Value": f"{biomarkers.jerk_proxy_std:.4f}" if not np.isnan(biomarkers.jerk_proxy_std) else "N/A",
            "Personal Baseline": "—",
            "Screening Threshold": "—",
            "Deviation": "—",
            "Screening Status": "Informational",
        },
        {
            "Biomarker": "Contact / Start Flexion",
            "Measured Value": f"{biomarkers.start_flexion_deg:.2f}°" if not np.isnan(biomarkers.start_flexion_deg) else "N/A",
            "Personal Baseline": "—",
            "Screening Threshold": "—",
            "Deviation": "—",
            "Screening Status": "Informational",
        },
    ]

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Baseline reference source: {screening.baseline_source.replace('_', ' ').title()}")


def render_screening_card(screening):
    """
    Render the screening decision using native Streamlit alerts and metrics.
    No raw HTML, code, or emojis.
    """
    st.subheader("Screening Decision")

    drivers = []
    if screening.fired_rules:
        rule_margins = []
        if "EXCESS_DEPTH" in screening.fired_rules:
            rule_margins.append(("Peak Flexion (Depth)", screening.peak_flexion_margin))
        if "EXCESS_ROM" in screening.fired_rules:
            rule_margins.append(("Range of Motion", screening.rom_margin))
        if "EXCESS_VELOCITY" in screening.fired_rules:
            rule_margins.append(("Descent Velocity", screening.velocity_margin))
        rule_margins.sort(key=lambda x: x[1], reverse=True)
        drivers = [r[0] for r in rule_margins[:2]]

    if screening.flag == "SCREENING_POSITIVE":
        st.error(
            "**SCREENING DECISION: FLAGGED**\n\n"
            "Kinematic pattern flagged for elevated injury risk association. "
            "One or more biomarkers exceeded clinical noise floor thresholds."
        )
        st.metric(
            label="Screening Status",
            value="FLAGGED",
            delta="Exceeded Noise Floor Threshold",
            delta_color="inverse",
        )
    else:
        st.success(
            "**SCREENING DECISION: PASS**\n\n"
            "Kinematic pattern within screening-clean band. "
            "Movement biomarkers remained within acceptable variation limits."
        )
        st.metric(
            label="Screening Status",
            value="PASS",
            delta="Within Expected Limits",
            delta_color="normal",
        )

    if screening.fired_rules:
        weight_sum = 0.0
        if "EXCESS_DEPTH" in screening.fired_rules:
            weight_sum += TRANSFER_WEIGHTS["peak_flexion"]
        if "EXCESS_ROM" in screening.fired_rules:
            weight_sum += TRANSFER_WEIGHTS["rom"]
        if "EXCESS_VELOCITY" in screening.fired_rules:
            weight_sum += TRANSFER_WEIGHTS["velocity"]
        st.metric(label="Weighted Confidence", value=f"{weight_sum * 100:.1f}%")
        st.write(f"**Driving Biomarkers:** {', '.join(drivers)}")
    else:
        st.metric(label="Weighted Confidence", value="100.0% (Clean)")
        st.caption("No decision rules triggered.")


def render_xai_text(xai):
    """Render counterfactual XAI explanations in clean Streamlit markdown without emojis."""
    st.subheader("Counterfactual Explanation")

    if not xai or not xai.explanations:
        st.success(
            "No kinematic deviations detected. All biomarkers fell within "
            "the screening-clean band relative to the personal baseline."
        )
        return

    for exp in xai.explanations:
        rule_title = exp["rule"].replace("_", " ").title()
        conf = exp["confidence"]
        st.warning(
            f"**{rule_title}** (Confidence: {conf})\n\n"
            f"{exp['text']}"
        )

    if xai.mki_text:
        st.info(
            f"**Multimodal Kinematic Implication:**\n\n"
            f"{xai.mki_text}"
        )


def render_uncertainty_chart(screening):
    """Render horizontal bar chart of uncertainty weights using native Streamlit chart."""
    st.subheader("Uncertainty Weight Distribution")

    fired_rules = set(screening.fired_rules or [])
    fired_map = {
        "peak_flexion": "EXCESS_DEPTH" in fired_rules,
        "rom": "EXCESS_ROM" in fired_rules,
        "velocity": "EXCESS_VELOCITY" in fired_rules,
        "contact_start_flexion": False,
    }

    items = sorted(WEIGHT_PERCENTAGES.items(), key=lambda x: x[1], reverse=True)
    chart_rows = []
    for key, pct in items:
        label = WEIGHT_LABELS[key]
        is_fired = fired_map.get(key, False)
        marker = " (Drove Decision)" if is_fired else ""
        chart_rows.append({
            "Biomarker": f"{label}{marker}",
            "Weight (%)": pct,
        })

    df_chart = pd.DataFrame(chart_rows)
    st.bar_chart(df_chart, x="Biomarker", y="Weight (%)", use_container_width=True)
    st.caption(
        "Weights derived from Phase 7 cross-exercise projection uncertainty analysis. "
        "Peak Flexion carries the highest weight (57.15%) due to lowest measurement uncertainty."
    )


def render_final_report_summary(screening, biomarkers, exercise_type):
    """
    Render the Final Report Summary (Public-Facing Interpretation).
    Written for average people in a friendly, accessible academic tone.
    Short paragraphs.
    NO jargon, NO biomechanics terminology, NO code, NO tables, NO HTML,
    NO biomarker table, NO angles unless necessary, and NO emojis.
    """
    is_flagged = screening.flag == "SCREENING_POSITIVE"
    fired = set(screening.fired_rules or [])

    # Overview Status Banner
    if is_flagged:
        st.warning(
            "**Screening Status: Movement Pattern Flagged**\n\n"
            "The automated analysis observed movement characteristics during your exercise "
            "that differ from standard reference patterns. This is a common finding during movement "
            "assessments and highlights specific opportunities to refine your exercise technique."
        )
    else:
        st.success(
            "**Screening Status: Movement Within Reference Range**\n\n"
            "The automated analysis indicates that your movement pattern aligned closely with "
            "standard reference benchmarks. Your movement control, depth, and pacing demonstrated "
            "consistent and balanced mechanics throughout the repetition."
        )

    st.divider()

    # What the Screening Means
    st.subheader("What This Screening Means")

    st.write(
        "This evaluation reviews how your body moves through a standard exercise. "
        "It focuses on three core elements: how deeply you move, how far your joints travel, "
        "and how smoothly you control your descent."
    )

    if "EXCESS_DEPTH" in fired:
        st.write(
            "**Movement Depth:** You descended noticeably further than the standard benchmark level. "
            "While good flexibility is valuable, dropping too low during weighted or repetitive movements "
            "transfers greater physical load onto the knees and lower back if supporting muscles are not fully prepared."
        )

    if "EXCESS_ROM" in fired:
        st.write(
            "**Movement Travel Range:** Your movement covered an unusually wide span from start to finish. "
            "A wider movement path requires extra muscular endurance to keep your posture steady and stable "
            "through the entire repetition."
        )

    if "EXCESS_VELOCITY" in fired:
        st.write(
            "**Lowering Speed:** You lowered your body relatively fast into the bottom of the movement. "
            "Moving downward too quickly can reduce muscular control and cause an abrupt transition, "
            "shifting stress onto passive connective tissues rather than active working muscles."
        )

    if not fired:
        st.write(
            "Your movement demonstrated steady lowering speed, balanced depth, and solid joint stability. "
            "Maintaining this controlled technique helps distribute physical forces evenly across active muscle groups."
        )

    st.divider()

    # Actionable Advice
    st.subheader("Actionable Advice and Practical Cues")

    st.write(
        "Here are evidence-informed, practical adjustments you can incorporate into your next training session:"
    )

    if "EXCESS_DEPTH" in fired:
        st.write(
            "**Establish a Consistent Target:** Place a sturdy chair or bench behind you at knee height. "
            "Practice gently tapping the target so you stop comfortably when your thighs are parallel to the floor."
        )

    if "EXCESS_VELOCITY" in fired:
        st.write(
            "**Adopt a Three-Second Descent Count:** Lower yourself to a steady count of three seconds. "
            "A controlled tempo ensures that your muscles stay engaged and protects your joints from sudden impact."
        )

    if "EXCESS_ROM" in fired:
        st.write(
            "**Focus on Foot Stability:** Keep your feet firmly planted with even pressure through your heel, "
            "big toe, and outer foot. Solid foot contact provides a stable foundation for the entire movement."
        )

    st.write(
        "**Prepare With a Dynamic Warm-Up:** Spend three to five minutes before your session performing gentle "
        "ankle mobility exercises and hip stretches. Better mobility makes it easier to maintain an upright, balanced posture."
    )

    st.divider()

    # What To Do Next
    st.subheader("What To Do Next")

    st.write(
        "**1. Review With an Instructor or Coach:** "
        "Share this summary and your recorded movement with a certified coach or exercise instructor. "
        "They can help you tailor your foot placement and body alignment."
    )

    st.write(
        "**2. Practice With Video Feedback:** "
        "Record your next practice set from the side using a smartphone. "
        "Comparing your actual movement against the pacing and depth guidance above provides immediate visual learning."
    )

    st.write(
        "**3. Consult a Healthcare Professional if Uncomfortable:** "
        "If you experience any pain, joint pinching, or persistent discomfort during or after exercise, "
        "consult a qualified physiotherapist or sports medicine practitioner for an in-person assessment."
    )

    st.divider()

    # Scope and Screening Distinction
    st.info(
        "**Important Note on Screening Versus Medical Diagnosis:**\n\n"
        "This tool provides automated movement screening, not a medical diagnosis or an injury prediction. "
        "A flagged movement pattern does not mean that an injury is present or inevitable. "
        "Instead, it highlights specific movement habits where small, thoughtful adjustments "
        "can help you move more efficiently, build strength safely, and support long-term physical health."
    )


# Backwards compatibility alias
render_layman_page = render_final_report_summary
