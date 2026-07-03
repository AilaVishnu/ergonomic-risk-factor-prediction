"""Results page - shows the prediction from session_state."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import FACTORS, FACTOR_LABEL, LEVEL_COLOUR, inject_css


RECOMMENDATIONS = {
    "force": {
        "Medium": "Encourage safer lifting technique and rest at handover.",
        "High":   "Cap carried-package weight per drop and enforce a two-person "
                  "protocol for heavy loads.",
    },
    "repetition": {
        "Medium": "Space deliveries across a full shift; avoid batching.",
        "High":   "Introduce delivery-rate caps and mandatory five-minute "
                  "breaks every eight drops.",
    },
    "duration": {
        "Medium": "Add a mid-shift 15-minute break.",
        "High":   "Cap shift length; mandatory rest every 2 hours; rotate "
                  "riders across morning / evening slots.",
    },
    "vibration": {
        "Medium": "Provide gel handlebar grips and check tyre pressure weekly.",
        "High":   "Move rider to a scooter if available; reduce daily hours; "
                  "monitor for hand-arm vibration symptoms.",
    },
    "contact_stress": {
        "Medium": "Switch from handheld bag to backpack or bike storage.",
        "High":   "Mandatory bike-storage box; padded strap on backpack; "
                  "shorter carrying distance per drop.",
    },
    "posture": {
        "Medium": "Ergonomic check of handlebar height and seat position.",
        "High":   "Ergonomic review of seat height and handlebar angle. "
                  "Neck / back stretching protocol before shifts. Annual "
                  "physiotherapy screen for riders flagged here.",
    },
}


SCORE = {"Low": 1, "Medium": 2, "High": 3}


def _summary_text(predictions):
    high = sum(1 for v in predictions.values() if v == "High")
    med  = sum(1 for v in predictions.values() if v == "Medium")
    low  = sum(1 for v in predictions.values() if v == "Low")

    # Three-column summary strip
    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        st.markdown(
            f"<div class='stat' style='border-left-color:#d13d2f;'>"
            f"<span class='value'>{high}</span>"
            f"<span class='label'>High-risk factors</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='stat' style='border-left-color:#e0a800;'>"
            f"<span class='value'>{med}</span>"
            f"<span class='label'>Medium-risk factors</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='stat' style='border-left-color:#27ae60;'>"
            f"<span class='value'>{low}</span>"
            f"<span class='label'>Low-risk factors</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    if high >= 3:
        st.error(
            f"**High-burden profile.** {high} of 6 factors flagged High. "
            "See Recommended actions below for the priority interventions."
        )
    elif high + med >= 4:
        st.warning(
            f"**Moderate burden.** {high} High plus {med} Medium risk "
            "factors — several modifiable exposures identified."
        )
    else:
        st.success(
            "**Predominantly low risk.** Acceptable exposures across the "
            "six factors."
        )


def _factor_cards(predictions):
    for row_start in (0, 3):
        cols = st.columns(3, gap="large")
        for offset in range(3):
            factor = FACTORS[row_start + offset]
            level  = predictions[factor]
            with cols[offset]:
                st.markdown(
                    f"""
                    <div class='risk-card risk-{level.lower()}'>
                        <div class='factor-name'>{FACTOR_LABEL[factor]}</div>
                        <div class='level'>{level}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        if row_start == 0:
            st.markdown("<div style='height: 1.2rem;'></div>",
                        unsafe_allow_html=True)


def _radar_chart(predictions):
    labels = [FACTOR_LABEL[f] for f in FACTORS]
    scores = [SCORE[predictions[f]] for f in FACTORS]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[3] * len(FACTORS) + [3],
        theta=labels + [labels[0]],
        mode="lines",
        line=dict(color="rgba(231, 76, 60, 0.20)", width=1, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
    ))
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        mode="lines+markers",
        fill="toself",
        line=dict(color="#2E86AB", width=2),
        marker=dict(size=10,
                    color=[LEVEL_COLOUR[predictions[f]] for f in FACTORS]
                          + [LEVEL_COLOUR[predictions[FACTORS[0]]]],
                    line=dict(width=1.5, color="#ffffff")),
        fillcolor="rgba(46, 134, 171, 0.20)",
        showlegend=False,
        hovertemplate="<b>%{theta}</b><br>Risk: %{customdata}<extra></extra>",
        customdata=[predictions[f] for f in FACTORS]
                   + [predictions[FACTORS[0]]],
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[0, 3],
                tickmode="array", tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"],
                tickfont=dict(color="#aaaaaa", size=10),
                gridcolor="rgba(255,255,255,0.10)",
                linecolor="rgba(255,255,255,0.15)",
                angle=90, tickangle=90,
            ),
            angularaxis=dict(
                tickfont=dict(color="#eeeeee", size=12),
                gridcolor="rgba(255,255,255,0.10)",
                linecolor="rgba(255,255,255,0.20)",
                rotation=90, direction="clockwise",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


def _factor_table(predictions):
    rows = []
    for factor in FACTORS:
        level = predictions[factor]
        rows.append({
            "Risk factor":     FACTOR_LABEL[factor],
            "Predicted level": level,
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True)


def render():
    inject_css()

    predictions = st.session_state.get("last_predictions")
    features    = st.session_state.get("last_features")

    if predictions is None:
        st.title("Prediction Results")
        st.markdown(
            "<div class='card' style='text-align:center; padding: 3rem 2rem;'>"
            "<h3>No prediction yet</h3>"
            "<p style='margin-top: 0.6rem; margin-bottom: 1.4rem;'>"
            "Run a rider through the Assessment page to see their six-factor "
            "risk profile here."
            "</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Go to Assessment", type="primary",
                         use_container_width=True):
                st.switch_page("views/assessment.py")
        return

    st.title("Prediction Results")
    st.caption(
        "Six-factor ergonomic risk profile from the trained classifiers."
    )

    _summary_text(predictions)

    st.markdown(
        "<div class='section-title'>Per-factor risk level</div>",
        unsafe_allow_html=True,
    )
    _factor_cards(predictions)

    left, right = st.columns([3, 4])
    with left:
        st.markdown(
            "<div class='section-title'>Risk profile radar</div>",
            unsafe_allow_html=True,
        )
        st.caption(
            "Each axis is a risk factor. Larger area = higher risk. "
            "Dashed outer hexagon marks maximum risk on all six factors."
        )
        _radar_chart(predictions)

    with right:
        st.markdown(
            "<div class='section-title'>Tabular result</div>",
            unsafe_allow_html=True,
        )
        _factor_table(predictions)
        st.caption(
            "Posture: the training-data minimum RULA Table-C score is 3 "
            "(Medium). The Posture classifier therefore has only "
            "Medium and High classes; Low cannot be predicted."
        )

    st.markdown(
        "<div class='section-title'>Recommended actions</div>",
        unsafe_allow_html=True,
    )
    actionable = [f for f in FACTORS if predictions[f] in ("Medium", "High")]
    if not actionable:
        st.info(
            "All six factors are Low. No immediate intervention flagged for "
            "this rider."
        )
    else:
        for factor in actionable:
            level = predictions[factor]
            with st.expander(
                f"{FACTOR_LABEL[factor]} — {level}",
                expanded=(level == "High"),
            ):
                st.write(RECOMMENDATIONS[factor][level])

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    if c1.button("Run another assessment", use_container_width=True):
        st.switch_page("views/assessment.py")
    if c2.button("Methodology", use_container_width=True):
        st.switch_page("views/methodology.py")
    if c3.button("About", use_container_width=True):
        st.switch_page("views/about.py")

    if features is not None:
        with st.expander(f"Show the {len(features)} encoded features "
                         "passed to the classifiers"):
            st.json(features)


render()
