"""Results page - shows the prediction from session_state."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import (FACTORS, FACTOR_LABEL, FACTOR_ICON, LEVEL_COLOUR,
                  LEVEL_EMOJI, inject_css)


RECOMMENDATIONS = {
    "force": {
        "Medium": "Encourage safer lifting technique and rest at handover.",
        "High":   "Cap carried-package weight per drop and enforce a 2-person "
                  "protocol for heavy loads.",
    },
    "repetition": {
        "Medium": "Space deliveries across a full shift; avoid batching.",
        "High":   "Introduce delivery-rate caps and mandatory 5-minute breaks "
                  "every 8 drops.",
    },
    "duration": {
        "Medium": "Add a mid-shift 15-minute break.",
        "High":   "Cap shift length; mandatory rest every 2 hours; rotate riders "
                  "across morning / evening slots.",
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


# ---------------------------------------------------------------------------
# Small view helpers
# ---------------------------------------------------------------------------

def _summary_hero(predictions):
    """Big status callout with High / Medium / Low counts."""
    high = sum(1 for v in predictions.values() if v == "High")
    med  = sum(1 for v in predictions.values() if v == "Medium")
    low  = sum(1 for v in predictions.values() if v == "Low")

    if high >= 3:
        headline    = "High-burden ergonomic profile"
        subtext     = f"{high} of 6 factors flagged HIGH. Immediate intervention recommended."
        colour      = "linear-gradient(135deg, #e74c3c, #c0392b)"
    elif high + med >= 4:
        headline    = "Moderate ergonomic burden"
        subtext     = f"{high} High + {med} Medium risk factors. Several modifiable exposures."
        colour      = "linear-gradient(135deg, #f39c12, #d4a017)"
    else:
        headline    = "Low-to-medium risk profile"
        subtext     = "Predominantly acceptable exposures across the six factors."
        colour      = "linear-gradient(135deg, #2ecc71, #27ae60)"

    st.markdown(
        f"""
        <div style="
            background: {colour};
            border-radius: 18px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 2rem;
            flex-wrap: wrap;
        ">
            <div style="flex: 1; min-width: 320px;">
                <div style="color: rgba(255,255,255,0.85); font-size: 0.9rem;
                            text-transform: uppercase; letter-spacing: 0.08em;">
                    Assessment result
                </div>
                <h2 style="color: #ffffff; margin: 0.4rem 0 0.6rem 0;">
                    {headline}
                </h2>
                <p style="color: rgba(255,255,255,0.95); margin: 0; font-size: 1.05rem;">
                    {subtext}
                </p>
            </div>
            <div style="display: flex; gap: 1.5rem;">
                <div style="text-align: center;">
                    <div style="font-size: 2.6rem; font-weight: 800; color: #ffffff;">{high}</div>
                    <div style="color: rgba(255,255,255,0.85); font-size: 0.8rem;
                                text-transform: uppercase; letter-spacing: 0.06em;">High</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.6rem; font-weight: 800; color: #ffffff;">{med}</div>
                    <div style="color: rgba(255,255,255,0.85); font-size: 0.8rem;
                                text-transform: uppercase; letter-spacing: 0.06em;">Medium</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 2.6rem; font-weight: 800; color: #ffffff;">{low}</div>
                    <div style="color: rgba(255,255,255,0.85); font-size: 0.8rem;
                                text-transform: uppercase; letter-spacing: 0.06em;">Low</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _factor_cards(predictions):
    """Six large colour-coded factor cards, rendered in two rows."""
    # Wrap each row in a horizontal-gap container by using st.columns(gap='large')
    # Then add explicit vertical space between the two rows.
    for row_start in (0, 3):
        cols = st.columns(3, gap="large")
        for offset in range(3):
            factor = FACTORS[row_start + offset]
            level  = predictions[factor]
            with cols[offset]:
                st.markdown(
                    f"""
                    <div class='risk-card risk-{level.lower()}'>
                        <div class='factor-name'>{FACTOR_ICON[factor]} {FACTOR_LABEL[factor]}</div>
                        <div class='level'>{level}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        # Vertical gap between the two rows of cards
        if row_start == 0:
            st.markdown("<div style='height: 1.6rem;'></div>",
                        unsafe_allow_html=True)


def _radar_chart(predictions):
    """Plotly radar (spider) chart of the 6 factors on a hexagon."""
    labels  = [FACTOR_LABEL[f] for f in FACTORS]
    scores  = [SCORE[predictions[f]] for f in FACTORS]

    fig = go.Figure()

    # Reference band: max risk baseline (all High) - a subtle dashed hexagon
    fig.add_trace(go.Scatterpolar(
        r=[3] * len(FACTORS) + [3],
        theta=labels + [labels[0]],
        mode="lines",
        line=dict(color="rgba(231, 76, 60, 0.20)", width=1, dash="dash"),
        showlegend=False,
        hoverinfo="skip",
        name="Max risk",
    ))

    # Rider's profile - closed polygon
    fig.add_trace(go.Scatterpolar(
        r=scores + [scores[0]],
        theta=labels + [labels[0]],
        mode="lines+markers",
        fill="toself",
        line=dict(color="#2E86AB", width=3),
        marker=dict(size=12, color=[LEVEL_COLOUR[predictions[f]] for f in FACTORS] + [LEVEL_COLOUR[predictions[FACTORS[0]]]],
                    line=dict(width=2, color="#ffffff")),
        fillcolor="rgba(46, 134, 171, 0.25)",
        showlegend=False,
        hovertemplate="<b>%{theta}</b><br>Risk: %{customdata}<extra></extra>",
        customdata=[predictions[f] for f in FACTORS] + [predictions[FACTORS[0]]],
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True,
                range=[0, 3],
                tickmode="array",
                tickvals=[1, 2, 3],
                ticktext=["Low", "Medium", "High"],
                tickfont=dict(color="#aaaaaa", size=11),
                gridcolor="rgba(255, 255, 255, 0.10)",
                linecolor="rgba(255, 255, 255, 0.15)",
                angle=90,
                tickangle=90,
            ),
            angularaxis=dict(
                tickfont=dict(color="#eeeeee", size=13),
                gridcolor="rgba(255, 255, 255, 0.10)",
                linecolor="rgba(255, 255, 255, 0.20)",
                rotation=90,
                direction="clockwise",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=30, b=30),
        height=440,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


def _factor_breakdown(predictions):
    """Simple table with icons, factor name, level, and a mini bar."""
    for factor in FACTORS:
        level  = predictions[factor]
        colour = LEVEL_COLOUR[level]
        score  = SCORE[level]
        pct    = int((score / 3) * 100)

        col1, col2, col3, col4 = st.columns([1, 2, 5, 2])
        with col1:
            st.markdown(
                f"<div style='font-size: 1.8rem; text-align: center;'>{FACTOR_ICON[factor]}</div>",
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"<div style='font-weight: 600; padding-top: 0.4rem;'>{FACTOR_LABEL[factor]}</div>",
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.05);
                            border-radius: 999px; height: 26px;
                            overflow: hidden; margin-top: 0.5rem;">
                    <div style="background: {colour};
                                width: {pct}%; height: 100%;
                                border-radius: 999px;
                                transition: width 0.4s ease;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""
                <div style="color: {colour}; font-weight: 700;
                            padding-top: 0.4rem; text-align: right;">
                    {LEVEL_EMOJI[level]} {level}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render():
    inject_css()

    predictions = st.session_state.get("last_predictions")
    features    = st.session_state.get("last_features")

    if predictions is None:
        st.warning(
            "No prediction yet. Head over to the **Assessment** page to run one."
        )
        if st.button("▶  Go to Assessment", type="primary"):
            st.switch_page("views/assessment.py")
        return

    st.markdown(
        "<div class='section-title'>📊 Prediction Results</div>",
        unsafe_allow_html=True,
    )

    # 1. Summary hero
    _summary_hero(predictions)

    # 2. Six colour-coded cards
    _factor_cards(predictions)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Radar chart + factor breakdown side-by-side
    left, right = st.columns([3, 4])
    with left:
        st.markdown("#### 🕸  Risk profile radar")
        st.caption("Each axis is a risk factor; the shape shows the rider's "
                   "6-factor profile. Closer to the outer ring = higher risk.")
        _radar_chart(predictions)

    with right:
        st.markdown("#### 📈  Factor breakdown")
        st.caption("Colour-coded bars for each factor; the same information "
                   "as the cards above, in a compact list.")
        st.markdown("<br>", unsafe_allow_html=True)
        _factor_breakdown(predictions)

    st.caption(
        "Posture note: the training-data minimum RULA Table-C score is 3 "
        "(Medium). The Posture model therefore has only Medium and High "
        "classes; Low cannot be predicted."
    )

    # 4. Recommendations
    st.markdown("<div class='section-title'>💡 Recommended actions</div>",
                unsafe_allow_html=True)

    actionable = [f for f in FACTORS if predictions[f] in ("Medium", "High")]
    if not actionable:
        st.success(
            "All six factors are Low. No immediate intervention flagged for "
            "this rider."
        )
    else:
        for factor in actionable:
            level = predictions[factor]
            with st.expander(
                f"{LEVEL_EMOJI[level]}  {FACTOR_LABEL[factor]} ({level})",
                expanded=(level == "High"),
            ):
                st.write(RECOMMENDATIONS[factor][level])

    # 5. Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("↩  Run another assessment", use_container_width=True):
        st.switch_page("views/assessment.py")
    if c2.button("📚  How does this work?", use_container_width=True):
        st.switch_page("views/methodology.py")
    if c3.button("ℹ  About the project", use_container_width=True):
        st.switch_page("views/about.py")

    # 6. Encoded features
    if features is not None:
        with st.expander(f"Show the {len(features)} encoded features fed to the models"):
            st.json(features)


render()
