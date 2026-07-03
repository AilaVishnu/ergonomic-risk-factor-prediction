"""Home / landing page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import FACTORS, FACTOR_LABEL, FACTOR_DESC, inject_css, load_models


def render():
    inject_css()

    # -- Title block --------------------------------------------------------
    st.markdown("### An IIITDM-SIES Internship Deliverable")
    st.title("Ergonomic Risk Screening Tool")
    st.markdown(
        "<p style='color:#a9b0ba; font-size:1.05rem; margin-top:-0.5rem; "
        "max-width: 720px;'>"
        "Per-rider screening for the six standard ergonomic risk factors, "
        "delivered as an interactive web app on top of six trained "
        "classifiers described in the internship report."
        "</p>",
        unsafe_allow_html=True,
    )

    col_cta, col_link = st.columns([1, 3])
    with col_cta:
        if st.button("Start Assessment", type="primary",
                     use_container_width=True):
            st.switch_page("views/assessment.py")
    with col_link:
        st.markdown(
            "<p style='color:#8a919b; padding-top: 0.4rem; font-size: 0.9rem;'>"
            "Or explore the pipeline in <i>Methodology</i>, or the author and "
            "mentor in <i>About</i>."
            "</p>",
            unsafe_allow_html=True,
        )

    # -- Risk factor grid ---------------------------------------------------
    st.markdown(
        "<div class='section-title'>The six risk factors</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8a919b; margin-top: -0.4rem; margin-bottom: 1rem;'>"
        "Each factor is computed from standard ergonomic methods (RULA, QEC, "
        "NMQ, NASA-TLX, Borg CR10, and operational threshold rules)."
        "</p>",
        unsafe_allow_html=True,
    )

    # Two-column grid of factor cards
    for i in range(0, len(FACTORS), 2):
        cols = st.columns(2, gap="medium")
        for j in range(2):
            if i + j < len(FACTORS):
                f = FACTORS[i + j]
                with cols[j]:
                    st.markdown(
                        f"<div class='card'>"
                        f"<h3>{FACTOR_LABEL[f]}</h3>"
                        f"<p>{FACTOR_DESC[f]}</p>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

    # -- Stats strip --------------------------------------------------------
    st.markdown(
        "<div class='section-title'>At a glance</div>",
        unsafe_allow_html=True,
    )
    load_models()  # warm cache while user reads

    stats = [
        ("182",  "riders in training data"),
        ("6",    "trained classifiers"),
        ("63",   "encoded features"),
        ("97%",  "posture model accuracy"),
    ]
    cols = st.columns(4)
    for (value, label), col in zip(stats, cols):
        with col:
            st.markdown(
                f"<div class='stat'>"
                f"<span class='value'>{value}</span>"
                f"<span class='label'>{label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # -- Workflow steps -----------------------------------------------------
    st.markdown(
        "<div class='section-title'>How it works</div>",
        unsafe_allow_html=True,
    )
    workflow = [
        ("1", "Enter a rider profile",
              "36-item questionnaire plus optional RULA and QEC observation "
              "scores. Sample profiles pre-fill the form in one click."),
        ("2", "Run the trained classifiers",
              "Six models (RandomForest, HistGradientBoosting, ExtraTrees) "
              "return the risk level for each factor from 5-fold-CV-selected "
              "hyperparameters."),
        ("3", "Read the results",
              "Colour-coded Low / Medium / High per factor, a radar summary, "
              "and per-factor recommendations for High-risk profiles."),
    ]
    for step, title, desc in workflow:
        st.markdown(
            f"<div class='card' style='display:flex; gap:1.2rem; "
            f"align-items:flex-start;'>"
            f"<div style='font-size:1.6rem; font-weight:700; color:#2E86AB; "
            f"min-width:2rem; text-align:center;'>{step}</div>"
            f"<div style='flex:1;'>"
            f"<h3 style='margin-top:0.2rem;'>{title}</h3>"
            f"<p>{desc}</p>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


render()
