"""Home / landing page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import FACTORS, FACTOR_LABEL, FACTOR_DESC, inject_css, load_models


def render():
    inject_css()

    st.title("Ergonomic Risk Screening Tool")
    st.caption(
        "A per-rider screening interface for the six ergonomic risk factors "
        "defined in the internship report."
    )

    st.markdown(
        "This tool runs the six trained classifiers described in the "
        "*Methodology* section on a rider profile assembled from a "
        "standard questionnaire and, optionally, direct RULA and QEC "
        "observation scores. The output is a Low / Medium / High rating "
        "per factor plus per-factor recommendations."
    )

    if st.button("Start Assessment", type="primary"):
        st.switch_page("views/assessment.py")

    st.markdown(
        "<div class='section-title'>Risk factors</div>",
        unsafe_allow_html=True,
    )

    for factor in FACTORS:
        st.markdown(
            f"""
            <div class='card'>
                <h3>{FACTOR_LABEL[factor]}</h3>
                <p>{FACTOR_DESC[factor]}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='section-title'>At a glance</div>",
        unsafe_allow_html=True,
    )
    load_models()  # warm cache

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            "<div class='stat'>"
            "<span class='value'>182</span>"
            "<span class='label'>Riders in training data</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            "<div class='stat'>"
            "<span class='value'>6</span>"
            "<span class='label'>Trained classifiers</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            "<div class='stat'>"
            "<span class='value'>63</span>"
            "<span class='label'>Encoded features</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            "<div class='stat'>"
            "<span class='value'>97%</span>"
            "<span class='label'>Posture model accuracy</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")
    st.caption(
        "For methodology details, see the *Methodology* page. For author, "
        "mentor, and institutional context, see *About*."
    )


render()
