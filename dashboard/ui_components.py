"""
ui_components.py
================
Streamlit UI rendering helpers for the kinematic screening dashboard.
Handles biomarker tables, screening cards, XAI text, uncertainty charts,
and the layman-friendly result summary using native Streamlit components.
NO raw HTML, code, or table markup.
"""

import numpy as np
import pandas as pd
import streamlit as st

from constants import (
    PALETTE,
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
    st.info(
        f"**Disclaimer:** {DISCLAIMER_TEXT}",
        icon="ℹ️",
    )


def _get_deviation_status(value, baseline, noise_floor, direction="above", flag_label="FLAGGED"):
    """Determine deviation status without any raw HTML."""
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
        return f"🚨 {flag_label}"
    elif is_borderline:
        return "⚠️ Borderline"
    else:
        return "✅ Within Band"


def render_biomarker_table(biomarkers, screening):
    """
    Render the biomarker summary using a clean Streamlit dataframe.
    No raw HTML or table tags.
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
            "Deviation (Δ)": f"{abs(biomarkers.peak_flexion_deg - baseline_peak):.2f}°" if not (np.isnan(biomarkers.peak_flexion_deg) or np.isnan(baseline_peak)) else "N/A",
            "Screening Status": status_peak,
        },
        {
            "Biomarker": "Range of Motion (ROM)",
            "Measured Value": f"{biomarkers.rom_deg:.2f}°" if not np.isnan(biomarkers.rom_deg) else "N/A",
            "Personal Baseline": f"{baseline_rom:.2f}°" if not np.isnan(baseline_rom) else "N/A",
            "Screening Threshold": f"{baseline_rom + NOISE_FLOORS['rom']:.2f}°" if not np.isnan(baseline_rom) else "N/A",
            "Deviation (Δ)": f"{abs(biomarkers.rom_deg - baseline_rom):.2f}°" if not (np.isnan(biomarkers.rom_deg) or np.isnan(baseline_rom)) else "N/A",
            "Screening Status": status_rom,
        },
        {
            "Biomarker": "Descent Velocity",
            "Measured Value": f"{velocity_deg_s:.2f}°/s" if not np.isnan(velocity_deg_s) else "N/A",
            "Personal Baseline": f"{baseline_velocity:.2f}°/s" if not np.isnan(baseline_velocity) else "N/A",
            "Screening Threshold": f"{baseline_velocity + NOISE_FLOORS['velocity']:.2f}°/s" if not np.isnan(baseline_velocity) else "N/A",
            "Deviation (Δ)": f"{abs(velocity_deg_s - baseline_velocity):.2f}°/s" if not (np.isnan(velocity_deg_s) or np.isnan(baseline_velocity)) else "N/A",
            "Screening Status": status_vel,
        },
        {
            "Biomarker": "Movement Smoothness (Jerk Proxy)",
            "Measured Value": f"{biomarkers.jerk_proxy_std:.4f}" if not np.isnan(biomarkers.jerk_proxy_std) else "N/A",
            "Personal Baseline": "—",
            "Screening Threshold": "—",
            "Deviation (Δ)": "—",
            "Screening Status": "Informational",
        },
        {
            "Biomarker": "Contact / Start Flexion",
            "Measured Value": f"{biomarkers.start_flexion_deg:.2f}°" if not np.isnan(biomarkers.start_flexion_deg) else "N/A",
            "Personal Baseline": "—",
            "Screening Threshold": "—",
            "Deviation (Δ)": "—",
            "Screening Status": "Informational",
        },
    ]

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Baseline reference source: {screening.baseline_source.replace('_', ' ').title()}")


def render_screening_card(screening):
    """
    Render the screening decision using native Streamlit alerts and metrics.
    No raw HTML or custom CSS classes.
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
            "### 🚨 FLAGGED\n"
            "**Kinematic pattern flagged for elevated injury risk association.**\n\n"
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
            "### ✅ PASS\n"
            "**Kinematic pattern within screening-clean band.**\n\n"
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
    """Render counterfactual XAI explanations using native Streamlit callouts."""
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
            f"**{rule_title}** — *Confidence: {conf}*\n\n"
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


def render_layman_page(screening, biomarkers, exercise_type):
    """
    Render a layman-friendly summary page for athletes, coaches, and non-specialists.
    Zero jargon, no angles unless necessary, no biomechanics formulas, no code,
    no biomarker table.
    Provides clear explanation, actionable coaching advice, clear next steps,
    and strongly emphasizes screening vs diagnosis.
    """
    is_flagged = screening.flag == "SCREENING_POSITIVE"
    fired = set(screening.fired_rules or [])

    # 1. Clear, Friendly Status Header
    if is_flagged:
        st.warning(
            "### ⚠️ Technique Flag Identified\n\n"
            "Our automated movement screening noticed one or more movement habits during your exercise "
            "that differ from standard reference benchmarks. This is a very common training observation "
            "and highlights specific areas where fine-tuning your technique can help you move more smoothly and safely."
        )
    else:
        st.success(
            "### ✅ Movement Within Standard Guidelines\n\n"
            "Great work! Your movement pattern stayed within standard reference benchmarks throughout the exercise. "
            "Your movement control, depth, and pacing showed consistent, healthy mechanics."
        )

    st.divider()

    # 2. What Your Screening Means (Plain English, No Jargon)
    st.subheader("What This Means For Your Movement")

    meaning_points = []
    if "EXCESS_DEPTH" in fired:
        meaning_points.append(
            "**Squat Depth (How Low You Go):** You lowered yourself further than the typical reference depth. "
            "While deep mobility is admirable, dropping too deep under heavy load can place unnecessary "
            "strain on your knees and lower back if your hips and ankles lack full stability."
        )
    if "EXCESS_ROM" in fired:
        meaning_points.append(
            "**Total Travel Range:** You moved through an exceptionally wide range of travel. "
            "Moving through a very wide path requires significant muscular endurance to keep your joints stable "
            "from the very start to the bottom and back up."
        )
    if "EXCESS_VELOCITY" in fired:
        meaning_points.append(
            "**Lowering Speed (Descent Control):** You lowered your body relatively fast. "
            "Dropping quickly into the bottom of a movement can cause you to lose muscular tension or bounce, "
            "shifting stress onto tendons and ligaments instead of your muscles."
        )

    if not meaning_points:
        st.write(
            "Your exercise repetition demonstrated balanced joint control, steady lowering tempo, and "
            "appropriate movement depth. Continuing with this controlled form helps distribute physical "
            "forces evenly across your working muscles."
        )
    else:
        for point in meaning_points:
            st.markdown(f"- {point}")

    st.divider()

    # 3. Actionable Advice (Practical Training Cues)
    st.subheader("Practical Training Tips & Coaching Cues")
    st.write(
        "Here are simple, practical adjustments you can try during your next workout session:"
    )

    cues = []
    if "EXCESS_DEPTH" in fired:
        cues.append(
            "**Target Parallel Depth:** Place a bench or knee-height box behind you. Practice tapping it lightly "
            "at parallel (hips level with the top of your knees) so you stop at a strong, stable depth without collapsing."
        )
    if "EXCESS_VELOCITY" in fired:
        cues.append(
            "**Use a 3-Second Lowering Count:** Count '1, 2, 3' steadily on the way down. Slowing down your descent "
            "builds bulletproof tendon strength and ensures your muscles stay in full control the entire time."
        )
    if "EXCESS_ROM" in fired:
        cues.append(
            "**Anchor Your Stance:** Keep your whole foot planted firmly like a tripod (heel, big toe base, pinky toe base). "
            "Avoid letting your heels lift or knees cave inward during the movement."
        )
    # Always provide positive general advice
    cues.append(
        "**Warm-up Mobility:** Spend 3–5 minutes before training doing ankle rocks and hip openers. "
        "Better ankle flexibility makes it much easier to stay upright and balanced."
    )

    for cue in cues:
        st.markdown(f"- {cue}")

    st.divider()

    # 4. What To Do Next (Clear Action Steps)
    st.subheader("Recommended Next Steps")

    col_step1, col_step2, col_step3 = st.columns(3)
    with col_step1:
        st.info(
            "**1. Review Form With a Coach**\n\n"
            "Show this screening result and your video to your strength coach, personal trainer, or instructor "
            "to check your stance and setup."
        )
    with col_step2:
        st.info(
            "**2. Practice With Video Feedback**\n\n"
            "Record your next set from a side angle on your smartphone. Compare your pacing and depth against "
            "the cues above."
        )
    with col_step3:
        st.info(
            "**3. Consult a Clinician If Uncomfortable**\n\n"
            "If you ever experience pain, pinch, or lingering ache in your knees, hips, or back, consult a qualified "
            "physiotherapist."
        )

    # 5. Non-Negotiable Screening vs Diagnosis Clarification
    st.warning(
        "**Important Reminder (Screening vs. Diagnosis):**\n\n"
        "This tool is an **automated kinematic screening system**, not a medical diagnostic device or injury forecast. "
        "A flagged result does **NOT** mean you are injured or that you will get injured. "
        "It simply highlights movement habits where small, mindful adjustments can help you move more smoothly, "
        "efficiently, and sustainably."
    )
