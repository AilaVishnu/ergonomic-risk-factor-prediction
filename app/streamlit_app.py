"""
Web demo for the 6 ergonomic risk-factor models.

Run with:
    streamlit run app/streamlit_app.py

Form mirrors the full 36-question rider questionnaire (Demographic +
NMQ + Discomfort follow-ups + NASA-TLX + Borg CR10). Every answer is
encoded into one of the 44 features the trained models consume.
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT    = Path(__file__).resolve().parents[1]
MODELS  = ROOT / "outputs" / "models"
FACTORS = ["force", "repetition", "duration", "vibration", "contact_stress", "posture"]
LABELS  = ["Low", "Medium", "High"]


# --- Encoding maps (mirror Phase 2 exactly) ---

AGE_MAP          = {"<25": 0, "25-35": 1, "36-45": 2, ">=46": 3}
INCOME_MAP       = {"<10,000": 0, "10,000-19,999": 1, "20,000-35,000": 2, ">35,000": 3}
EDUCATION_MAP    = {"Middle / Primary school": 0, "High school": 1, "Degree / Master's": 2}
JOB_DURATION_MAP = {"<6 months": 0, "6-12 months": 1, "12-24 months": 2, ">24 months": 3}
WORK_HOURS_MAP   = {"< 3 hrs": 2, "3-5 hrs": 4, "6-8 hrs": 7, "> 8 hrs": 9}
WORK_DAYS_MAP    = {"< 3": 2, "3-4": 3.5, "5-6": 5.5, "7": 7}
DELIVERIES_MAP   = {"<= 10": 5, "11-20": 15, "21-30": 25, ">= 31": 35}
REST_BREAK_MAP   = {"< 5 min": 2.5, "5-15 min": 10, "16-30 min": 23, "> 30 min": 40}
VEHICLE_MAP      = {"Scooter": 1, "Motor bike": 2}
CARRYING_MAP     = {"Bike storage / carrier": 1, "Backpack": 2, "Bike handle": 3, "Handheld": 4}

GENDER_MAP     = {"Male": 1, "Female": 2}
REGION_MAP     = {"Local": 1, "Non-Local": 2}
MARITAL_MAP    = {"Unmarried": 0, "Married": 1}
PLATFORM_MAP   = {"Blinkit": 1, "Zepto": 2, "Both": 3}
BREAK_TYPE_MAP = {"Uneven": 0, "Even": 1}
SUBSTANCE_MAP  = {"Never": 0, "Former User": 1, "Occasionally": 2, "Regularly": 3}

YES_NO = ["No", "Yes"]
NMQ_AREAS = ["Neck", "Shoulders", "Upper back", "Lower back", "Elbows",
             "Wrists / Hands", "Hips / Thighs", "Knees", "Ankles / Feet"]
NMQ_KEYS  = ["nmq_neck", "nmq_shoulders", "nmq_upper_back", "nmq_lower_back",
             "nmq_elbows", "nmq_wrists_hands", "nmq_hips_thighs", "nmq_knees",
             "nmq_ankles_feet"]
D7_AREAS  = ["Neck", "Lower back", "Knees", "Wrist / Hands"]
D7_KEYS   = ["d7_neck", "d7_lower_back", "d7_knees", "d7_wrist_hands"]

# RULA observation components (Posture model uses these directly)
RULA_KEYS = ["upper_arm", "lower_arm", "wrist", "wrist_twist",
             "neck_position", "trunk_position", "legs",
             "muscle_a", "force_a", "muscle_b", "force_b"]

# QEC observation scores (Quick Exposure Check, also for Posture model)
QEC_KEYS = ["qec_back", "qec_shoulder_arm", "qec_wrist_hand", "qec_neck",
            "qec_driving", "qec_vibration", "qec_work_pace", "qec_stress"]


@st.cache_resource
def load_models():
    return {f: joblib.load(MODELS / f"best_{f}.pkl") for f in FACTORS}


def encode_rider(raw):
    """Raw survey answers -> the 44 features the models consume."""
    nasa = raw["nasa"]
    borg = raw["borg"]

    # nasa["dissatisfied"] already runs in load-direction (100 = high load), so no flip needed
    workload_score = round((nasa["mental"] + nasa["physical"] + nasa["time_pressure"]
                            + nasa["dissatisfied"]
                            + nasa["effort"] + nasa["frustration"]) / 6, 1)
    fatigue_score  = round((borg["overall"] + borg["legs"] + borg["breathing"]
                            + borg["lifting"] + borg["traffic"] + borg["exhaustion"]) / 6, 2)
    force_exertion = borg["lifting"]

    age_ord               = AGE_MAP[raw["age"]]
    income_ord            = INCOME_MAP[raw["income"]]
    education_ord         = EDUCATION_MAP[raw["education"]]
    job_duration_ord      = JOB_DURATION_MAP[raw["job_duration"]]
    work_hours_num        = WORK_HOURS_MAP[raw["work_hours"]]
    work_days_num         = WORK_DAYS_MAP[raw["work_days"]]
    deliveries_num        = DELIVERIES_MAP[raw["deliveries"]]
    rest_break_num        = REST_BREAK_MAP[raw["rest_break"]]
    vehicle_rank          = VEHICLE_MAP[raw["vehicle"]]
    carrying_contact_rank = CARRYING_MAP[raw["carrying"]]
    vibration_index       = vehicle_rank * work_hours_num

    feats = {
        "workload_score":        workload_score,
        "fatigue_score":         fatigue_score,
        "age_ord":               age_ord,
        "income_ord":            income_ord,
        "education_ord":         education_ord,
        "job_duration_ord":      job_duration_ord,
        "work_hours_num":        work_hours_num,
        "work_days_num":         work_days_num,
        "deliveries_num":        deliveries_num,
        "rest_break_num":        rest_break_num,
        "vehicle_rank":          vehicle_rank,
        "carrying_contact_rank": carrying_contact_rank,
        "force_exertion":        force_exertion,
        "vibration_index":       vibration_index,
        "workload_x_fatigue":    round(workload_score * fatigue_score / 100, 3),
        "workload_x_age":        round(workload_score * age_ord / 10, 3),
        "force_x_age":           round(force_exertion * age_ord, 2),
        "fatigue_x_jobdur":      round(fatigue_score * job_duration_ord, 2),
        "deliv_x_days":          round(deliveries_num * work_days_num, 1),
        "gender_rank":           GENDER_MAP[raw["gender"]],
        "region_rank":           REGION_MAP[raw["region"]],
        "marital_rank":          MARITAL_MAP[raw["marital_status"]],
        "platform_rank":         PLATFORM_MAP[raw["delivery_platform"]],
        "break_type_rank":       BREAK_TYPE_MAP[raw["type_of_break"]],
        "tobacco_ord":           SUBSTANCE_MAP[raw["tobacco"]],
        "alcohol_ord":           SUBSTANCE_MAP[raw["alcohol"]],
    }
    for k, ans in zip(NMQ_KEYS, raw["nmq"]):
        feats[k] = 1 if ans == "Yes" else 0
    for k, ans in zip(D7_KEYS, raw["d7"]):
        feats[k] = 1 if ans == "Yes" else 0
    for k in ["out_reduced_perf", "out_taken_leave", "out_consulted_doctor",
              "out_riding_worsens", "out_carrying_worsens"]:
        feats[k] = 1 if raw[k] == "Yes" else 0
    for k in RULA_KEYS:
        feats[k] = raw["rula"][k]
    for k in QEC_KEYS:
        feats[k] = raw["qec"][k]
    return feats


def predict_risks(features, models):
    df_row = pd.DataFrame([features])
    out = {}
    for factor in FACTORS:
        bundle = models[factor]
        pred_idx = int(bundle["model"].predict(df_row[bundle["features"]])[0])
        code = int(bundle["classes"][pred_idx])
        out[factor] = LABELS[code]
    return out


# ---- Page ----

st.set_page_config(page_title="Ergonomic Risk Predictor", page_icon="🛵", layout="wide")
st.title("🛵 Ergonomic Risk Predictor — Food-Delivery Riders")
st.caption("Answer the 36 questions from the rider questionnaire. The six trained "
           "models return a Low / Medium / High level for each ergonomic risk factor.")

models = load_models()

with st.form("rider_form"):

    # ============ SECTION 1: DEMOGRAPHIC (Q1-17) ============
    st.header("Demographic")
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

    # ============ SECTION 2: NORDIC + DISCOMFORT (Q18-24) ============
    st.header("Nordic Musculoskeletal Questionnaire (NMQ)")

    st.markdown("**18. In the past 12 months, have you experienced pain, discomfort, "
                "or numbness in the following body areas due to delivery work?**")
    nmq = []
    cols = st.columns(3)
    for i, area in enumerate(NMQ_AREAS):
        with cols[i % 3]:
            nmq.append(st.radio(area, YES_NO, index=0, horizontal=True, key=f"nmq_{i}"))

    st.markdown("**19. In the past 7 days, have you experienced discomfort in:**")
    d7 = []
    cols = st.columns(4)
    for i, area in enumerate(D7_AREAS):
        with cols[i]:
            d7.append(st.radio(area, YES_NO, index=0, horizontal=True, key=f"d7_{i}"))

    st.markdown("**Discomfort follow-ups (Q20-Q24)**")
    cols = st.columns(2)
    with cols[0]:
        out_reduced_perf  = st.radio("20. Has discomfort reduced your delivery performance?",
                                     YES_NO, index=0, horizontal=True)
        out_taken_leave   = st.radio("21. Have you ever taken leave due to body pain caused by delivery work?",
                                     YES_NO, index=0, horizontal=True)
        out_consulted_doctor = st.radio("22. Have you consulted a doctor or physiotherapist for work-related pain?",
                                        YES_NO, index=0, horizontal=True)
    with cols[1]:
        out_riding_worsens   = st.radio("23. Does riding/driving for long hours increase your discomfort?",
                                        YES_NO, index=0, horizontal=True)
        out_carrying_worsens = st.radio("24. Does carrying heavy packages worsen your discomfort?",
                                        YES_NO, index=0, horizontal=True)

    st.divider()

    # ============ SECTION 3: NASA-TLX (Q25-30) ============
    st.header("NASA-TLX workload   (Low 0 — 100 High)")
    cols = st.columns(2)
    with cols[0]:
        nasa_mental    = st.slider("25. How mentally demanding was your delivery shift?",
                                   0, 100, 50, 25)
        nasa_physical  = st.slider("26. How physically demanding was your delivery shift?",
                                   0, 100, 50, 25)
        nasa_time      = st.slider("27. How rushed or time-pressured did you feel?",
                                   0, 100, 50, 25)
    with cols[1]:
        nasa_dissatisfied = st.slider("28. How DISSATISFIED were you with your ability to "
                                      "complete deliveries accurately and on time?",
                                      0, 100, 25, 25,
                                      help="0 = very satisfied, 100 = very dissatisfied. "
                                           "All 6 NASA sliders now point the same way.")
        nasa_effort    = st.slider("29. How much effort did you put in to maintain performance?",
                                   0, 100, 75, 25)
        nasa_frustration = st.slider("30. How stressed, frustrated, or emotionally strained did you feel?",
                                     0, 100, 50, 25)

    st.divider()

    # ============ SECTION 4: BORG CR10 (Q31-36) ============
    st.header("Borg CR10 fatigue   (0 = Extremely Easy, 10 = Extremely Hard)")
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

    # ============ SECTION 5: RULA OBSERVATION (Posture model) ============
    st.header("Posture observation (RULA)")
    st.caption("Score each item using the standard RULA worksheet. These 11 inputs "
               "drive the Posture model directly — no observation data, no honest "
               "posture prediction. If unsure, leave defaults.")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Group A — Arm & wrist**")
        upper_arm   = st.selectbox("Upper arm (1-4)",   [1, 2, 3, 4], index=1,
                                   help="1 = 20° flex/ext, 4 = >90° flex")
        lower_arm   = st.selectbox("Lower arm (1-3)",   [1, 2, 3],    index=0,
                                   help="1 = 60-100° flex, 2 = <60° or >100°, 3 = across body")
        wrist       = st.selectbox("Wrist (1-3)",       [1, 2, 3],    index=0,
                                   help="1 = neutral, 2 = ±15°, 3 = >15°")
        wrist_twist = st.selectbox("Wrist twist (1-2)", [1, 2],       index=0,
                                   help="1 = midrange, 2 = at end of range")
    with cols[1]:
        st.markdown("**Group B — Neck, trunk, legs**")
        neck_position  = st.selectbox("Neck position (1-4)",  [1, 2, 3, 4], index=1,
                                      help="1 = 0-10° flex, 4 = extension")
        trunk_position = st.selectbox("Trunk position (1-4)", [1, 2, 3, 4], index=1,
                                      help="1 = upright, 4 = >60° flex")
        legs           = st.selectbox("Legs (1-2)",           [1, 2],       index=0,
                                      help="1 = supported balanced, 2 = unbalanced")
    with cols[2]:
        st.markdown("**Muscle & force adjustments**")
        muscle_a = st.selectbox("Muscle A (0-1)", [0, 1], index=0,
                                help="+1 if static >1 min or repeating >4/min (Group A)")
        force_a  = st.selectbox("Force A (0-3)",  [0, 1, 2, 3], index=0,
                                help="0 = <2kg intermittent, 3 = >10kg or shock")
        muscle_b = st.selectbox("Muscle B (0-1)", [0, 1], index=0,
                                help="+1 if static >1 min or repeating >4/min (Group B)")
        force_b  = st.selectbox("Force B (0-3)",  [0, 1, 2, 3], index=0)

    st.divider()

    # ============ SECTION 6: QEC OBSERVATION (Posture model) ============
    st.header("Quick Exposure Check (QEC)")
    st.caption("QEC sums standard worksheet items into 8 region/exposure scores. "
               "Values match the observed ranges in the training data. "
               "If unsure, leave defaults.")
    cols = st.columns(4)
    with cols[0]:
        st.markdown("**Body regions**")
        qec_back         = st.number_input("Back (14-46)",         min_value=14, max_value=46, value=28, step=2)
        qec_shoulder_arm = st.number_input("Shoulder/Arm (14-56)", min_value=14, max_value=56, value=28, step=2)
    with cols[1]:
        st.markdown("**Body regions**")
        qec_wrist_hand   = st.number_input("Wrist/Hand (14-46)",   min_value=14, max_value=46, value=26, step=2)
        qec_neck         = st.number_input("Neck (10-36)",         min_value=10, max_value=36, value=18, step=2)
    with cols[2]:
        st.markdown("**Exposures**")
        qec_driving      = st.number_input("Driving (4-16)",       min_value=4,  max_value=16, value=8,  step=1)
        qec_vibration    = st.number_input("Vibration (4-9)",      min_value=4,  max_value=9,  value=6,  step=1)
    with cols[3]:
        st.markdown("**Exposures**")
        qec_work_pace    = st.number_input("Work pace (1-10)",     min_value=1,  max_value=10, value=6,  step=1)
        qec_stress       = st.number_input("Stress (1-16)",        min_value=1,  max_value=16, value=8,  step=1)

    st.divider()
    submitted = st.form_submit_button("Predict risk levels",
                                      use_container_width=True, type="primary")


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
        borg={"overall": borg_overall, "legs": borg_legs, "breathing": borg_breathing,
              "lifting": borg_lifting, "traffic": borg_traffic, "exhaustion": borg_exhaustion},
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
    features = encode_rider(raw)
    predictions = predict_risks(features, models)

    st.divider()
    st.subheader("Predicted risk levels")

    badge = {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}
    nice  = {"force": "Force", "repetition": "Repetition", "duration": "Duration",
             "vibration": "Vibration", "contact_stress": "Contact Stress", "posture": "Posture"}

    rows = [{"Risk factor": nice[f], "Predicted level": badge[predictions[f]]}
            for f in FACTORS]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    high = sum(v == "High" for v in predictions.values())
    med  = sum(v == "Medium" for v in predictions.values())
    if high >= 3:
        st.error(f"⚠ {high} factors are HIGH risk — high-burden ergonomic profile.")
    elif high + med >= 4:
        st.warning(f"{high} High + {med} Medium risk factors — several modifiable exposures.")
    else:
        st.success("Predominantly low-to-medium risk profile across the 6 factors.")

    with st.expander(f"Show the {len(features)} encoded feature values"):
        st.json(features)
