"""Home / landing page - Vercel-style cinematic hero."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import inject_css, hide_sidebar, load_models


def render():
    inject_css()
    hide_sidebar()  # Home is the entry point - sidebar appears on subsequent pages

    # ------------------------------------------------------------------
    # Hero: two columns - large title on the left, meta strip on the right
    # ------------------------------------------------------------------
    st.markdown(
        """
        <div class='hero'>
          <div class='hero__inner'>
            <span class='hero__badge'>IIITDM-SIES</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(
            """
            <h1 class='hero__title'>
              Ergonomic<br>
              <span class='muted'>Risk Screening</span>
            </h1>
            <p class='hero__tagline'>
              Per-rider screening for the six standard ergonomic risk
              factors in last-mile quick-commerce delivery, on top of six
              trained machine-learning classifiers.
            </p>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class='meta-strip'>
              <div class='meta-line'><span class='k'>FOR</span> QUICK-COMMERCE RIDERS</div>
              <div class='meta-line'><span class='k'>ON</span> 182-RIDER DATASET</div>
              <div class='meta-line'><span class='k'>WITH</span> RULA / QEC / NMQ / BORG / NASA-TLX</div>
              <div class='meta-line'><span class='k'>AND</span> SIX TRAINED CLASSIFIERS</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ------------------------------------------------------------------
    # Pill CTAs
    # ------------------------------------------------------------------
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 3], gap="small")
    with c1:
        if st.button("Start Assessment", type="primary",
                     use_container_width=True):
            st.switch_page("views/assessment.py")
    with c2:
        if st.button("Methodology", use_container_width=True):
            st.switch_page("views/methodology.py")

    # Warm the model cache while the user reads
    load_models()

    # ------------------------------------------------------------------
    # Stats row (Vercel-style tabular)
    # ------------------------------------------------------------------
    st.markdown("<hr>", unsafe_allow_html=True)

    stats = [
        ("182",  "riders in training data"),
        ("6",    "trained classifiers"),
        ("63",   "encoded features"),
        ("97%",  "posture accuracy"),
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

    # ------------------------------------------------------------------
    # Acronym strip at the bottom - mimics Vercel's customer-logo row
    # ------------------------------------------------------------------
    st.markdown(
        """
        <div class='acronym-strip'>
          <span class='item'>RULA</span>
          <span class='item'>QEC</span>
          <span class='item'>NMQ</span>
          <span class='item'>NASA-TLX</span>
          <span class='item'>BORG CR10</span>
          <span class='item'>SMOTE</span>
          <span class='item'>XGBOOST</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


render()
