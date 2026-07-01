"""Home / landing page."""

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import (FACTORS, FACTOR_LABEL, FACTOR_ICON, FACTOR_DESC,
                  inject_css, load_models)


def render():
    inject_css()

    # ---------- Hero ----------
    st.markdown(
        """
        <div class='hero'>
            <h1>🛵 Ergonomic Risk Predictor</h1>
            <p>
                A per-rider screening tool that predicts six standard
                ergonomic risk factors from a 36-question survey plus
                optional RULA and QEC observations. Built for
                food-delivery platforms and occupational-health teams
                to catch preventable musculoskeletal risk early.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Big CTA ----------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Ready to run a screening?")
        if st.button("▶  Start Assessment", type="primary",
                     use_container_width=True):
            st.switch_page("views/assessment.py")
        st.caption("Or explore the pipeline and models from the sidebar.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Six factor cards ----------
    st.markdown("<div class='section-title'>The six risk factors</div>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, factor in enumerate(FACTORS):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class='card'>
                    <span class='icon'>{FACTOR_ICON[factor]}</span>
                    <h3>{FACTOR_LABEL[factor]}</h3>
                    <p>{FACTOR_DESC[factor]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---------- Stats strip ----------
    st.markdown("<div class='section-title'>Under the hood</div>",
                unsafe_allow_html=True)

    load_models()  # warm cache so the Assessment page loads instantly

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
            <div class='stat'>
                <div class='value'>182</div>
                <div class='label'>Riders in training data</div>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='stat'>
                <div class='value'>6</div>
                <div class='label'>Trained ML models</div>
            </div>
            """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
            <div class='stat'>
                <div class='value'>63</div>
                <div class='label'>Encoded features</div>
            </div>
            """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class='stat'>
                <div class='value'>97%</div>
                <div class='label'>Posture accuracy</div>
            </div>
            """, unsafe_allow_html=True)

    # ---------- How it works quick preview ----------
    st.markdown("<div class='section-title'>How it works</div>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
            <div class='card'>
                <span class='icon'>1️⃣</span>
                <h3>Answer the questionnaire</h3>
                <p>36 standard survey items plus optional RULA and QEC
                observation scores. Sample profiles pre-fill the form
                in one click.</p>
            </div>
            """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
            <div class='card'>
                <span class='icon'>2️⃣</span>
                <h3>Six trained models score the rider</h3>
                <p>Random Forest, XGBoost, HistGradientBoosting, Extra
                Trees, and Logistic Regression tuned with GridSearchCV
                and SMOTE per risk factor.</p>
            </div>
            """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
            <div class='card'>
                <span class='icon'>3️⃣</span>
                <h3>Get an actionable risk profile</h3>
                <p>Colour-coded Low / Medium / High rating for each of
                the six factors, plus per-factor recommendations the
                mentor can act on.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Open the sidebar to jump to Assessment, Methodology, or About.")


if __name__ == "__main__" or True:
    render()
