"""About page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import inject_css


def render():
    inject_css()

    st.title("About the project")

    # -------- Project title as a highlighted quote block --------
    st.markdown(
        "<div class='card' style='border-left:4px solid #2E86AB; padding:1.3rem 1.6rem;'>"
        "<p style='margin:0; font-size:1.06rem; color:#f5f7fa; font-style:italic;'>"
        "A Predictive Machine Learning Framework for Ergonomic Risk in "
        "Last-Mile Quick-Commerce Delivery Operations"
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # -------- Institutional context --------
    st.markdown(
        "<div class='section-title'>Institutional context</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<dl class='def-list'>"
        "<dt>Programme</dt><dd>IIITDM-SIES Internship</dd>"
        "<dt>Department</dt><dd>School of Interdisciplinary Design and Innovation (SIDI)</dd>"
        "<dt>Institution</dt><dd>Indian Institute of Information Technology, Design and Manufacturing, Kancheepuram</dd>"
        "<dt>Period</dt><dd>May 2026 to July 2026</dd>"
        "</dl>",
        unsafe_allow_html=True,
    )

    # -------- People --------
    st.markdown(
        "<div class='section-title'>People</div>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown(
            "<div class='card'>"
            "<div style='color:#8a919b; font-size:0.82rem; text-transform:uppercase; "
            "letter-spacing:0.08em; margin-bottom:0.3rem;'>Author</div>"
            "<h3 style='margin-bottom:0.2rem;'>AILA VISHNU VARDHAN</h3>"
            "<p>Vidya Jyothi Institute of Technology</p>"
            "</div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            "<div class='card'>"
            "<div style='color:#8a919b; font-size:0.82rem; text-transform:uppercase; "
            "letter-spacing:0.08em; margin-bottom:0.3rem;'>Mentor</div>"
            "<h3 style='margin-bottom:0.2rem;'>Dr. Arunachalam Muthiah</h3>"
            "<p>School of Interdisciplinary Design and Innovation (SIDI), "
            "IIITDM Kancheepuram</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    # -------- Tech stack --------
    st.markdown(
        "<div class='section-title'>Tech stack</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Python 3.13, scikit-learn, XGBoost, imbalanced-learn, statsmodels, "
        "pandas, matplotlib, Plotly, Altair, Streamlit."
    )


render()
