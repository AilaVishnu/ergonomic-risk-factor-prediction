"""About page."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import inject_css


def render():
    inject_css()

    st.markdown(
        "<div class='section-title'>ℹ  About the project</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
        <div class='card'>
            <span class='icon'>📖</span>
            <h3>Project title</h3>
            <p style='font-size: 1.05rem; font-style: italic;'>
                A Predictive Machine Learning Framework for Ergonomic Risk
                in Last-Mile Quick-Commerce Delivery Operations
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class='card'>
            <span class='icon'>🎓</span>
            <h3>Internship report</h3>
            <p>
                This tool is one deliverable of an internship carried out
                under the IIITDM-SIES Programme in the
                <b>School of Interdisciplinary Design and Innovation
                (SIDI)</b> at the Indian Institute of Information
                Technology, Design and Manufacturing, Kancheepuram.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class='card'>
            <span class='icon'>🧑‍💻</span>
            <h3>Author</h3>
            <p>
                <b>AILA VISHNU VARDHAN</b><br>
                Vidya Jyothi Institute of Technology
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class='card'>
            <span class='icon'>👨‍🏫</span>
            <h3>Mentor</h3>
            <p>
                <b>Dr. Arunachalam Muthiah</b><br>
                School of Interdisciplinary Design and Innovation (SIDI),
                IIITDM Kancheepuram
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div class='card'>
            <span class='icon'>📄</span>
            <h3>Report and code</h3>
            <p>
                The full internship report (docs/report.docx) and the
                seven-notebook analysis pipeline are versioned in the
                project repository. Each phase, from data cleaning through
                model evaluation, can be regenerated end-to-end with a fixed
                random seed.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Tech stack</div>",
                unsafe_allow_html=True)

    cols = st.columns(4)
    stack = [
        ("Python 3.13",     "🐍"),
        ("scikit-learn",    "🔬"),
        ("XGBoost",         "⚡"),
        ("imbalanced-learn","⚖️"),
        ("statsmodels",     "📈"),
        ("pandas",          "🐼"),
        ("matplotlib",      "📊"),
        ("Streamlit",       "🎈"),
    ]
    for i, (name, icon) in enumerate(stack):
        with cols[i % 4]:
            st.markdown(f"""
                <div class='card' style='text-align: center; padding: 0.8rem;'>
                    <span class='icon'>{icon}</span>
                    <h3 style='font-size: 1.1rem;'>{name}</h3>
                </div>
                """, unsafe_allow_html=True)


render()
