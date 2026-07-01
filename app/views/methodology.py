"""Methodology page - explains the pipeline."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st

from core import inject_css

ROOT = Path(__file__).resolve().parents[2]


def render():
    inject_css()

    st.title("Methodology")
    st.caption(
        "How the pipeline turns a rider profile into six colour-coded risk "
        "levels. The full write-up is in the internship report."
    )

    flowchart = ROOT / "outputs" / "figures" / "methodology_flowchart.png"
    if flowchart.exists():
        st.image(str(flowchart), use_container_width=True,
                 caption="Pipeline overview from raw inputs to interactive "
                         "prediction.")

    st.markdown(
        "<div class='section-title'>Two-stage design</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Stage 1** applies standard ergonomic methods (Borg CR10 action "
        "levels, RULA Table C thresholds, sample terciles or fixed cuts) "
        "to compute a Low, Medium, or High label per risk factor. These "
        "labels are deterministic and serve as the ground truth for Stage 2.\n\n"
        "**Stage 2** trains a supervised classifier per risk factor with "
        "SMOTE oversampling inside 5-fold stratified cross-validation. "
        "Per-target feature exclusions remove the inputs that define each "
        "Stage-1 label so the classifier cannot memorise the rule."
    )

    st.markdown(
        "<div class='section-title'>Data sources</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Rider survey (n = 182).** A 36-item questionnaire covering "
        "demographics, work pattern, Nordic Musculoskeletal Questionnaire "
        "(NMQ) pain in nine body areas, seven-day discomfort, five "
        "follow-ups, six NASA-TLX workload items, and six Borg CR10 "
        "perceived-exertion items.\n\n"
        "**Posture observations (n = 182).** Ergonomic observation records "
        "combining 11 RULA components, three derived RULA Table scores, "
        "and eight QEC scores. Merged into the survey via a severity-rank "
        "procedure documented in the report."
    )

    st.markdown(
        "<div class='section-title'>Candidate algorithms</div>",
        unsafe_allow_html=True,
    )
    algorithms = [
        ("LogisticRegression",             "Linear baseline with L2 regularisation and balanced class weights."),
        ("DecisionTreeClassifier",         "A single CART tree with tuned max_depth and min_samples_leaf."),
        ("RandomForestClassifier",         "Bagging ensemble of trees; robust on small tabular datasets."),
        ("ExtraTreesClassifier",           "Extremely randomised trees; reduces variance further."),
        ("HistGradientBoostingClassifier", "Histogram-binned gradient boosting; fast on tabular data."),
        ("XGBClassifier",                  "Gradient-boosted trees with L1 and L2 regularisation."),
        ("StackingClassifier",             "Meta-ensemble combining four base learners with a Logistic Regression combiner."),
    ]
    for name, desc in algorithms:
        st.markdown(f"- **{name}** — {desc}")

    st.markdown(
        "<div class='section-title'>Model performance</div>",
        unsafe_allow_html=True,
    )
    perf = pd.DataFrame(
        [
            ("Force",          "HistGradientBoosting", 62, 71),
            ("Repetition",     "RandomForest",         62, 73),
            ("Duration",       "RandomForest",         61, 76),
            ("Vibration",      "ExtraTrees",           58, 72),
            ("Contact Stress", "RandomForest",         60, 74),
            ("Posture",        "HistGradientBoosting", 97, 98),
        ],
        columns=["Factor", "Best model", "Accuracy (%)", "Macro AUC (%)"],
    )
    st.dataframe(perf, hide_index=True, use_container_width=True)
    st.caption(
        "Posture reaches 97% because it is the only model that receives "
        "real observation inputs (11 RULA components + 8 QEC scores) on "
        "top of the survey features."
    )

    st.markdown("")
    if st.button("Run a rider assessment", type="primary"):
        st.switch_page("views/assessment.py")


render()
