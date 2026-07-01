"""About page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import inject_css


def render():
    inject_css()

    st.title("About the project")

    st.markdown(
        "<div class='section-title'>Project title</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "*A Predictive Machine Learning Framework for Ergonomic Risk in "
        "Last-Mile Quick-Commerce Delivery Operations*"
    )

    st.markdown(
        "<div class='section-title'>Internship</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "This tool is a deliverable of an internship carried out under "
        "the **IIITDM-SIES Programme** in the **School of "
        "Interdisciplinary Design and Innovation (SIDI)** at the Indian "
        "Institute of Information Technology, Design and Manufacturing, "
        "Kancheepuram."
    )

    st.markdown(
        "<div class='section-title'>Author</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**AILA VISHNU VARDHAN**  \n"
        "Vidya Jyothi Institute of Technology"
    )

    st.markdown(
        "<div class='section-title'>Mentor</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Dr. Arunachalam Muthiah**  \n"
        "School of Interdisciplinary Design and Innovation (SIDI), IIITDM "
        "Kancheepuram"
    )

    st.markdown(
        "<div class='section-title'>Report and code</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "The full internship report (`docs/report.docx`) and the "
        "seven-notebook analysis pipeline are versioned in the project "
        "repository. Each phase, from data cleaning through model "
        "evaluation, can be regenerated end-to-end with a fixed random "
        "seed."
    )

    st.markdown(
        "<div class='section-title'>Tech stack</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Python 3.13, scikit-learn, XGBoost, imbalanced-learn, statsmodels, "
        "pandas, matplotlib, Plotly, Altair, Streamlit."
    )


render()
