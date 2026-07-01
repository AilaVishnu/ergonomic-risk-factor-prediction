"""Methodology page - explains the pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import inject_css

ROOT = Path(__file__).resolve().parents[2]


def render():
    inject_css()

    st.markdown(
        "<div class='section-title'>📚 Methodology</div>",
        unsafe_allow_html=True,
    )
    st.caption(
        "How the pipeline turns a rider profile into six colour-coded risk "
        "levels."
    )

    # ---------- Pipeline overview ----------
    flowchart = ROOT / "outputs" / "figures" / "methodology_flowchart.png"
    if flowchart.exists():
        st.image(str(flowchart), use_container_width=True,
                 caption="Pipeline overview: raw inputs to interactive prediction.")

    # ---------- Two-stage design ----------
    st.markdown("<div class='section-title'>Two-stage design</div>",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <div class='card'>
                <span class='icon'>🏷️</span>
                <h3>Stage 1 — Deterministic labelling</h3>
                <p>
                    Standard ergonomic methods (Borg CR10 action levels,
                    RULA Table C thresholds, sample terciles or fixed cuts)
                    turn each rider profile into a Low / Medium / High label
                    for each of the six risk factors. These labels are the
                    ground truth Stage 2 tries to learn.
                </p>
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
            <div class='card'>
                <span class='icon'>🤖</span>
                <h3>Stage 2 — Supervised ML</h3>
                <p>
                    Seven candidate classifiers are trained per target with
                    SMOTE oversampling inside 5-fold stratified
                    cross-validation and hyperparameter tuning via
                    GridSearchCV. The best-by-F1-macro model per factor is
                    saved for prediction.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ---------- Data sources ----------
    st.markdown("<div class='section-title'>Data sources</div>",
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
            <div class='card'>
                <span class='icon'>📋</span>
                <h3>Rider survey (n = 182)</h3>
                <p>
                    36-item questionnaire covering demographics, work pattern,
                    Nordic Musculoskeletal Questionnaire (NMQ) pain in nine
                    body areas, seven-day discomfort, five follow-ups, six
                    NASA-TLX workload items, and six Borg CR10 exertion items.
                </p>
            </div>
            """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
            <div class='card'>
                <span class='icon'>👀</span>
                <h3>Posture observations</h3>
                <p>
                    182 ergonomic observation records combining 11 RULA
                    components, three RULA Table scores, and eight QEC
                    scores. Merged into the survey via a severity-rank
                    procedure (documented in the project report).
                </p>
            </div>
            """, unsafe_allow_html=True)

    # ---------- The 7 algorithms ----------
    st.markdown("<div class='section-title'>The seven candidate algorithms</div>",
                unsafe_allow_html=True)

    algorithms = [
        ("LogisticRegression",           "Linear baseline with L2 regularisation and balanced class weights."),
        ("DecisionTreeClassifier",       "A single CART tree with tuned max_depth and min_samples_leaf."),
        ("RandomForestClassifier",       "Bagging ensemble of trees; typically strong on tabular data."),
        ("ExtraTreesClassifier",         "Extremely randomised trees; reduces variance further."),
        ("HistGradientBoostingClassifier", "Histogram-binned gradient boosting; fast on tabular data."),
        ("XGBClassifier",                "Gradient-boosted trees with L1/L2 regularisation."),
        ("StackingClassifier",           "Meta-ensemble combining four base learners with a Logistic Regression combiner."),
    ]
    for name, desc in algorithms:
        st.markdown(f"- **{name}** — {desc}")

    # ---------- Model performance ----------
    st.markdown("<div class='section-title'>Model performance</div>",
                unsafe_allow_html=True)

    perf = [
        ("Force",          "HistGradientBoosting", 62, 71),
        ("Repetition",     "RandomForest",         62, 73),
        ("Duration",       "RandomForest",         61, 76),
        ("Vibration",      "ExtraTrees",           58, 72),
        ("Contact Stress", "RandomForest",         60, 74),
        ("Posture",        "HistGradientBoosting", 97, 98),
    ]
    import pandas as pd
    st.dataframe(
        pd.DataFrame(perf, columns=["Factor", "Best model", "Accuracy (%)", "Macro AUC (%)"]),
        hide_index=True, use_container_width=True,
    )
    st.caption(
        "Posture reaches 97% because it is the only model that receives "
        "real observation inputs (11 RULA components + 8 QEC scores) on top "
        "of the survey features."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶  Run a rider assessment now", type="primary"):
        st.switch_page("views/assessment.py")


render()
