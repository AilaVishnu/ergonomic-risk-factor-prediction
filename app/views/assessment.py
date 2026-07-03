"""Assessment page - the six-section form."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from core import (
    AGE_MAP, INCOME_MAP, EDUCATION_MAP, JOB_DURATION_MAP, WORK_HOURS_MAP,
    WORK_DAYS_MAP, DELIVERIES_MAP, REST_BREAK_MAP, VEHICLE_MAP, CARRYING_MAP,
    GENDER_MAP, REGION_MAP, MARITAL_MAP, PLATFORM_MAP, BREAK_TYPE_MAP,
    SUBSTANCE_MAP, YES_NO, NMQ_AREAS, D7_AREAS,
    inject_css, load_models, encode_rider, predict_risks,
    preset_to_raw,
)


def _run_prediction(raw):
    """Encode, predict, stash in session_state, and jump to Results."""
    features = encode_rider(raw)
    predictions = predict_risks(features, load_models())
    st.session_state["last_features"] = features
    st.session_state["last_predictions"] = predictions
    st.switch_page("views/results.py")


def render():
    inject_css()

    st.title("Rider Assessment")
    st.markdown(
        "<p style='color:#a9b0ba; font-size:1.02rem; margin-top:-0.4rem; "
        "max-width: 780px;'>"
        "Answer the 36-item questionnaire below plus the RULA and QEC "
        "observation scores. Or use a sample profile to trigger a "
        "prediction in one click."
        "</p>",
        unsafe_allow_html=True,
    )

    # ---------------- Sample profile shortcuts ----------------
    st.markdown(
        "<div style='color:#8a919b; font-size:0.85rem; text-transform:uppercase; "
        "letter-spacing:0.08em; margin-top:1rem; margin-bottom:0.5rem;'>"
        "Sample profiles"
        "</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3, gap="medium")
    if c1.button("Low-risk rider", use_container_width=True):
        _run_prediction(preset_to_raw("low"))
    if c2.button("Average rider", use_container_width=True):
        _run_prediction(preset_to_raw("average"))
    if c3.button("High-risk rider", use_container_width=True):
        _run_prediction(preset_to_raw("high"))

    # ---------------- Section overview ----------------
    st.markdown(
        "<div class='section-nav'>"
        "<span><strong>Sections:</strong></span>"
        "<span>Demographic <span class='divider'>·</span></span>"
        "<span>NMQ <span class='divider'>·</span></span>"
        "<span>NASA-TLX <span class='divider'>·</span></span>"
        "<span>Borg CR10 <span class='divider'>·</span></span>"
        "<span>RULA <span class='divider'>·</span></span>"
        "<span>QEC</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ---------------- Manual form ----------------
    with st.form("rider_form"):

        # ============ SECTION 1: DEMOGRAPHIC ============
        st.markdown("#### Demographic")
        col1, col2, col3 = st.columns(3)
        with col1:
            gender       = st.selectbox("1. Gender", list(GENDER_MAP.keys()))
            age          = st.selectbox("2. Age", list(AGE_MAP.keys()), index=1)
            education    = st.selectbox("3. Education", list(EDUCATION_MAP.keys()), index=2)
            region       = st.selectbox("4. Region", list(REGION_MAP.keys()))
            marital      = st.selectbox("5. Marital status", list(MARITAL_MAP.keys()))
            platform     = st.selectbox("6. Delivery platform", list(PLATFORM_MAP.keys()))
        with col2:
            job_duration = st.selectbox("7. Job duration (experience)",
                                        list(JOB_DURATION_MAP.keys()), index=2)
            income       = st.selectbox("8. Monthly income (INR)",
                                        list(INCOME_MAP.keys()), index=2)
            vehicle      = st.selectbox("9. Type of vehicle", list(VEHICLE_MAP.keys()), index=1)
            carrying     = st.selectbox("10. Mode of carrying deliveries",
                                        list(CARRYING_MAP.keys()), index=1)
            work_hours   = st.selectbox("11. Working hours per day",
                                        list(WORK_HOURS_MAP.keys()), index=2)
            work_days    = st.selectbox("12. Working days per week",
                                        list(WORK_DAYS_MAP.keys()), index=2)
        with col3:
            deliveries   = st.selectbox("13. Number of deliveries per day",
                                        list(DELIVERIES_MAP.keys()), index=2)
            rest_break   = st.selectbox("14. Duration of rest break",
                                        list(REST_BREAK_MAP.keys()), index=1)
            break_type   = st.selectbox("15. Type of break", list(BREAK_TYPE_MAP.keys()))
            tobacco      = st.selectbox("16. Tobacco consumption", list(SUBSTANCE_MAP.keys()))
            alcohol      = st.selectbox("17. Alcohol consumption", list(SUBSTANCE_MAP.keys()))

        st.divider()

        # ============ SECTION 2: NMQ + DISCOMFORT ============
        st.markdown("#### Nordic Musculoskeletal Questionnaire (NMQ)")
        st.markdown(
            "**18. In the past 12 months, have you experienced pain, "
            "discomfort, or numbness in the following body areas due to "
            "delivery work?**"
        )
        nmq = []
        cols = st.columns(3)
        for i, area in enumerate(NMQ_AREAS):
            with cols[i % 3]:
                nmq.append(st.radio(area, YES_NO, index=0, horizontal=True,
                                    key=f"nmq_{i}"))

        st.markdown("**19. In the past 7 days, have you experienced discomfort in:**")
        d7 = []
        cols = st.columns(4)
        for i, area in enumerate(D7_AREAS):
            with cols[i]:
                d7.append(st.radio(area, YES_NO, index=0, horizontal=True,
                                   key=f"d7_{i}"))

        st.markdown("**Discomfort follow-ups (Q20-Q24)**")
        cols = st.columns(2)
        with cols[0]:
            out_reduced_perf     = st.radio("20. Has discomfort reduced your delivery performance?",
                                            YES_NO, index=0, horizontal=True)
            out_taken_leave      = st.radio("21. Have you ever taken leave due to body pain caused by delivery work?",
                                            YES_NO, index=0, horizontal=True)
            out_consulted_doctor = st.radio("22. Have you consulted a doctor or physiotherapist for work-related pain?",
                                            YES_NO, index=0, horizontal=True)
        with cols[1]:
            out_riding_worsens   = st.radio("23. Does riding/driving for long hours increase your discomfort?",
                                            YES_NO, index=0, horizontal=True)
            out_carrying_worsens = st.radio("24. Does carrying heavy packages worsen your discomfort?",
                                            YES_NO, index=0, horizontal=True)

        st.divider()

        # ============ SECTION 3: NASA-TLX ============
        st.markdown("#### NASA-TLX workload (Low 0 - 100 High)")
        cols = st.columns(2)
        with cols[0]:
            nasa_mental       = st.slider("25. How mentally demanding was your delivery shift?",
                                          0, 100, 50, 25)
            nasa_physical     = st.slider("26. How physically demanding was your delivery shift?",
                                          0, 100, 50, 25)
            nasa_time         = st.slider("27. How rushed or time-pressured did you feel?",
                                          0, 100, 50, 25)
        with cols[1]:
            nasa_dissatisfied = st.slider(
                "28. How DISSATISFIED were you with your ability to "
                "complete deliveries accurately and on time?",
                0, 100, 25, 25,
                help="0 = very satisfied, 100 = very dissatisfied. "
                     "All 6 NASA sliders now point the same way.")
            nasa_effort       = st.slider("29. How much effort did you put in to maintain performance?",
                                          0, 100, 75, 25)
            nasa_frustration  = st.slider("30. How stressed, frustrated, or emotionally strained did you feel?",
                                          0, 100, 50, 25)

        st.divider()

        # ============ SECTION 4: BORG CR10 ============
        st.markdown("#### Borg CR10 fatigue (0 = Extremely Easy, 10 = Extremely Hard)")
        cols = st.columns(2)
        with cols[0]:
            borg_overall    = st.slider("31. Overall, how hard did your delivery work feel today?",
                                        0, 10, 4)
            borg_legs       = st.slider("32. How tired did your legs feel while walking/riding?",
                                        0, 10, 4)
            borg_breathing  = st.slider("33. How hard was it to breathe during deliveries?",
                                        0, 10, 3)
        with cols[1]:
            borg_lifting    = st.slider("34. How hard did lifting or carrying parcels feel?",
                                        0, 10, 4)
            borg_traffic    = st.slider("35. How physically stressful was working in traffic/weather conditions?",
                                        0, 10, 5)
            borg_exhaustion = st.slider("36. At the end of your shift, how exhausted did your body feel?",
                                        0, 10, 5)

        st.divider()

        # ============ SECTION 5: RULA ============
        st.markdown("#### Posture observation (RULA)")
        st.caption(
            "Score each item using the standard RULA worksheet. These 11 "
            "inputs drive the Posture model directly. If unsure, leave defaults."
        )
        cols = st.columns(3)
        with cols[0]:
            st.markdown("**Group A - Arm & wrist**")
            upper_arm   = st.selectbox("Upper arm (1-4)",   [1, 2, 3, 4], index=1)
            lower_arm   = st.selectbox("Lower arm (1-3)",   [1, 2, 3],    index=0)
            wrist       = st.selectbox("Wrist (1-3)",       [1, 2, 3],    index=0)
            wrist_twist = st.selectbox("Wrist twist (1-2)", [1, 2],       index=0)
        with cols[1]:
            st.markdown("**Group B - Neck, trunk, legs**")
            neck_position  = st.selectbox("Neck position (1-4)",  [1, 2, 3, 4], index=1)
            trunk_position = st.selectbox("Trunk position (1-4)", [1, 2, 3, 4], index=1)
            legs           = st.selectbox("Legs (1-2)",           [1, 2],       index=0)
        with cols[2]:
            st.markdown("**Muscle & force adjustments**")
            muscle_a = st.selectbox("Muscle A (0-1)", [0, 1], index=0)
            force_a  = st.selectbox("Force A (0-3)",  [0, 1, 2, 3], index=0)
            muscle_b = st.selectbox("Muscle B (0-1)", [0, 1], index=0)
            force_b  = st.selectbox("Force B (0-3)",  [0, 1, 2, 3], index=0)

        st.divider()

        # ============ SECTION 6: QEC ============
        st.markdown("#### Quick Exposure Check (QEC)")
        st.caption(
            "QEC sums standard worksheet items into 8 region/exposure scores. "
            "Values match the observed ranges in the training data."
        )
        cols = st.columns(4)
        with cols[0]:
            qec_back         = st.number_input("Back (14-46)",         14, 46, 28, 2)
            qec_shoulder_arm = st.number_input("Shoulder/Arm (14-56)", 14, 56, 28, 2)
        with cols[1]:
            qec_wrist_hand   = st.number_input("Wrist/Hand (14-46)",   14, 46, 26, 2)
            qec_neck         = st.number_input("Neck (10-36)",         10, 36, 18, 2)
        with cols[2]:
            qec_driving      = st.number_input("Driving (4-16)",       4,  16, 8,  1)
            qec_vibration    = st.number_input("Vibration (4-9)",      4,  9,  6,  1)
        with cols[3]:
            qec_work_pace    = st.number_input("Work pace (1-10)",     1,  10, 6,  1)
            qec_stress       = st.number_input("Stress (1-16)",        1,  16, 8,  1)

        st.divider()
        submitted = st.form_submit_button("Predict risk levels",
                                          use_container_width=True,
                                          type="primary")

    if submitted:
        raw = dict(
            age=age, gender=gender, region=region, marital_status=marital,
            income=income, education=education, job_duration=job_duration,
            work_hours=work_hours, work_days=work_days, deliveries=deliveries,
            rest_break=rest_break, type_of_break=break_type,
            delivery_platform=platform, vehicle=vehicle, carrying=carrying,
            tobacco=tobacco, alcohol=alcohol,
            nmq=nmq, d7=d7,
            out_reduced_perf=out_reduced_perf,
            out_taken_leave=out_taken_leave,
            out_consulted_doctor=out_consulted_doctor,
            out_riding_worsens=out_riding_worsens,
            out_carrying_worsens=out_carrying_worsens,
            nasa={"mental": nasa_mental, "physical": nasa_physical,
                  "time_pressure": nasa_time, "dissatisfied": nasa_dissatisfied,
                  "effort": nasa_effort, "frustration": nasa_frustration},
            borg={"overall": borg_overall, "legs": borg_legs,
                  "breathing": borg_breathing, "lifting": borg_lifting,
                  "traffic": borg_traffic, "exhaustion": borg_exhaustion},
            rula={"upper_arm": upper_arm, "lower_arm": lower_arm, "wrist": wrist,
                  "wrist_twist": wrist_twist, "neck_position": neck_position,
                  "trunk_position": trunk_position, "legs": legs,
                  "muscle_a": muscle_a, "force_a": force_a,
                  "muscle_b": muscle_b, "force_b": force_b},
            qec={"qec_back": qec_back, "qec_shoulder_arm": qec_shoulder_arm,
                 "qec_wrist_hand": qec_wrist_hand, "qec_neck": qec_neck,
                 "qec_driving": qec_driving, "qec_vibration": qec_vibration,
                 "qec_work_pace": qec_work_pace, "qec_stress": qec_stress},
        )
        _run_prediction(raw)


render()
