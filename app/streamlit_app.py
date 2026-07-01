"""
Multi-page Streamlit web app for the ergonomic risk predictor.

Run:
    python -m streamlit run app/streamlit_app.py
"""

from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Ergonomic Risk Predictor",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded",
)


pages = [
    st.Page(str(APP_DIR / "views" / "home.py"),
            title="Home",
            icon="🏠",
            default=True),
    st.Page(str(APP_DIR / "views" / "assessment.py"),
            title="Assessment",
            icon="📋"),
    st.Page(str(APP_DIR / "views" / "results.py"),
            title="Results",
            icon="📊"),
    st.Page(str(APP_DIR / "views" / "methodology.py"),
            title="Methodology",
            icon="📚"),
    st.Page(str(APP_DIR / "views" / "about.py"),
            title="About",
            icon="ℹ️"),
]

nav = st.navigation(pages)


# Persistent sidebar branding
with st.sidebar:
    st.markdown("### 🛵 Ergonomic Risk Predictor")
    st.caption("Per-rider screening tool")
    st.divider()

nav.run()


with st.sidebar:
    st.divider()
    st.caption("Built for IIITDM-SIES Internship")
    st.caption("© AILA VISHNU VARDHAN, 2026")
