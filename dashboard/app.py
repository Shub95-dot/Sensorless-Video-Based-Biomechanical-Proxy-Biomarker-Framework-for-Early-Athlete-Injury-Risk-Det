"""
app.py
======
Sensorless Kinematic Screening Dashboard

Main Streamlit application. Wraps the existing kinematic screening pipeline
with an academic, clean UI for viva demonstration.
Produces two distinct outputs after every run:
1. Technical Screening Output (for clinicians, biomechanists, examiners)
2. Layman-Friendly Final Result Page (for athletes, coaches, general audience)

NO raw HTML, code, or table markup. Built strictly with native Streamlit components.

Author  : Shubham Shirodkar
Project : MSc AI/Data Science Dissertation, Southampton Solent University
Run     : streamlit run app.py
"""

import sys
import tempfile
from pathlib import Path

import cv2
import streamlit as st

# Ensure dashboard directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from constants import (
    SUPPORTED_VIDEO_TYPES,
    EXERCISE_TYPES,
)
from pipeline_wrapper import run_pipeline
from ui_components import (
    render_disclaimer,
    render_biomarker_table,
    render_screening_card,
    render_xai_text,
    render_uncertainty_chart,
    render_layman_page,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Kinematic Screening Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Sensorless Kinematic Screening Dashboard")
st.caption(
    "MSc AI/Data Science Dissertation — Shubham Shirodkar — Southampton Solent University"
)

# ---------------------------------------------------------------------------
# Persistent Disclaimer
# ---------------------------------------------------------------------------
render_disclaimer()

# ---------------------------------------------------------------------------
# Input Section
# ---------------------------------------------------------------------------
st.subheader("Input Video & Parameters")

col_upload, col_options = st.columns([2, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Upload exercise video",
        type=SUPPORTED_VIDEO_TYPES,
        help="Accepted formats: MP4, MOV, AVI. Recommended: 5-10 second clip of a single exercise repetition.",
    )

with col_options:
    exercise_type = st.selectbox(
        "Exercise type",
        options=EXERCISE_TYPES,
        index=0,
    )
    subject_id = st.text_input(
        "Subject ID (optional)",
        value="",
        help="Enter a subject identifier for personalised baseline tracking. "
             "Leave blank to use cohort median baseline.",
    )

# Run button
run_disabled = uploaded_file is None
run_clicked = st.button(
    "Run Screening",
    disabled=run_disabled,
    use_container_width=True,
    type="primary",
)

# ---------------------------------------------------------------------------
# Processing and Output
# ---------------------------------------------------------------------------
if run_clicked and uploaded_file is not None:
    # Save uploaded file to a temp location
    suffix = Path(uploaded_file.name).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()

    def progress_callback(stage_name: str, progress: float):
        progress_bar.progress(min(progress, 1.0))
        status_text.caption(f"Processing stage: {stage_name}")

    # Run pipeline
    with st.spinner("Processing video through kinematic pipeline..."):
        result = run_pipeline(
            video_path=tmp_path,
            exercise_type=exercise_type,
            subject_id=subject_id,
            progress_callback=progress_callback,
        )

    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()

    # --- Handle errors ---
    if not result.success:
        st.error(
            f"**Screening could not be completed.**\n\n"
            f"{result.error_message}"
        )
        # Cleanup
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass
    else:
        # ===================================================================
        # TWO COMPREHENSIVE OUTPUTS AFTER EVERY SCREENING RUN
        # ===================================================================
        st.divider()

        tab_tech, tab_layman = st.tabs([
            "🔬 Technical Screening Output (Clinicians & Examiners)",
            "👤 Layman-Friendly Final Result Page (Athlete Summary)",
        ])

        # -------------------------------------------------------------------
        # 1. Technical Screening Output
        # -------------------------------------------------------------------
        with tab_tech:
            bio = result.biomarkers

            # Quick metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total Frames", bio.total_frames)
            col_m2.metric("Valid Frames", bio.valid_frames)
            col_m3.metric("Phase Detection", bio.phase_status.upper())
            col_m4.metric("Exercise Type", exercise_type)

            st.divider()

            # Side-by-side Video Playback and Pose Overlay
            st.subheader("Video Playback & Pose Overlay")
            col_video, col_overlay = st.columns(2)

            with col_video:
                st.write("**Original Video Playback**")
                st.video(uploaded_file)

            with col_overlay:
                st.write(
                    f"**Pose Overlay (Frame {result.representative_frame_index} — Peak Flexion)**"
                )
                if result.overlay_frame is not None:
                    overlay_rgb = cv2.cvtColor(result.overlay_frame, cv2.COLOR_BGR2RGB)
                    st.image(overlay_rgb, use_container_width=True)
                else:
                    st.info("Pose overlay could not be generated for this video.")

            st.divider()

            # Biomarker Summary & Screening Decision Card
            col_table, col_card = st.columns([3, 2])

            with col_table:
                render_biomarker_table(result.biomarkers, result.screening)

            with col_card:
                render_screening_card(result.screening)

            st.divider()

            # Counterfactual Explanation & Uncertainty Distribution
            col_xai, col_weights = st.columns([3, 2])

            with col_xai:
                render_xai_text(result.xai)

            with col_weights:
                render_uncertainty_chart(result.screening)

            # Phase detection note if failed
            if bio.phase_status == "failed":
                st.warning(
                    "**Note on Phase Detection:** Descent/ascent identification could not be fully completed "
                    "for this video. This may occur if the movement trajectory lacks a clear flexion-extension "
                    "cycle or has missing frames. Velocity-based biomarkers may be unavailable."
                )

        # -------------------------------------------------------------------
        # 2. Layman-Friendly Final Result Page
        # -------------------------------------------------------------------
        with tab_layman:
            render_layman_page(result.screening, result.biomarkers, exercise_type)

        # Cleanup temp file
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    "Sensorless Markerless Screening Framework — "
    "COM726 MSc Dissertation — "
    "Southampton Solent University — 2026"
)
