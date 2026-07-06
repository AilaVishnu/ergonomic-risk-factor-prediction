"""
Multi-page Streamlit web app for the ergonomic risk predictor.

Run:
    python -m streamlit run app/streamlit_app.py
"""

from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent


st.set_page_config(
    page_title="Ergonomic Risk Screening Tool",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="auto",  # let Streamlit collapse on narrow viewports
)


pages = [
    st.Page(str(APP_DIR / "views" / "home.py"),
            title="Home",
            default=True),
    st.Page(str(APP_DIR / "views" / "assessment.py"),
            title="Assessment"),
    st.Page(str(APP_DIR / "views" / "results.py"),
            title="Results"),
    st.Page(str(APP_DIR / "views" / "methodology.py"),
            title="Methodology"),
    st.Page(str(APP_DIR / "views" / "about.py"),
            title="About"),
]

nav = st.navigation(pages)


# Sidebar branding
with st.sidebar:
    st.markdown("### Ergonomic Risk Screening Tool")
    st.caption("IIITDM-SIES  |  SIDI research deliverable")
    st.divider()

nav.run()


with st.sidebar:
    st.divider()
    st.caption("AILA VISHNU VARDHAN")
    st.caption("Mentor: Dr. Arunachalam Muthiah")
