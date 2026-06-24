"""
Web demo for the 6 ergonomic risk-factor models.

Run with:
    python -m streamlit run app/streamlit_app.py

Form mirrors the full 36-question rider questionnaire (Demographic + NMQ +
Discomfort follow-ups + NASA-TLX + Borg CR10) plus the RULA and QEC
observation worksheets. Every answer is encoded into the feature vector
the trained models consume.
"""

from pathlib import Path

import altair as alt
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
RULA_KEYS = ["upper_arm", "lower_arm", "wrist", "wrist_twist",
             "neck_position", "trunk_position", "legs",
             "muscle_a", "force_a", "muscle_b", "force_b"]
QEC_KEYS  = ["qec_back", "qec_shoulder_arm", "qec_wrist_hand", "qec_neck",
             "qec_driving", "qec_vibration", "qec_work_pace", "qec_stress"]

# Sample profiles - one click to populate the whole form
PRESETS = {
    "low": {
        "age": "<25", "gender": "Male", "region": "Local", "marital_status": "Unmarried",
        "income": "10,000-19,999", "education": "Degree / Master's",
        "job_duration": "<6 months",
        "work_hours": "< 3 hrs", "work_days": "< 3", "deliveries": "<= 10",
        "rest_break": "> 30 min", "type_of_break": "Even",
        "delivery_platform": "Blinkit", "vehicle": "Scooter",
        "carrying": "Bike storage / carrier",
        "tobacco": "Never", "alcohol": "Never",
        "nmq": ["No"]*9, "d7": ["No"]*4,
        "outcomes": ["No"]*5,
        "nasa": [10, 10, 20, 20, 10, 10],  # mental, physical, time, dissatisfied, effort, frustration
        "borg": [1, 1, 1, 1, 1, 1],
        "rula": [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        "qec":  [14, 14, 14, 10, 4, 4, 1, 1],
    },
    "average": {
        "age": "25-35", "gender": "Male", "region": "Local", "marital_status": "Unmarried",
        "income": "20,000-35,000", "education": "Degree / Master's",
        "job_duration": "12-24 months",
        "work_hours": "6-8 hrs", "work_days": "5-6", "deliveries": "21-30",
        "rest_break": "5-15 min", "type_of_break": "Uneven",
        "delivery_platform": "Blinkit", "vehicle": "Motor bike", "carrying": "Backpack",
        "tobacco": "Never", "alcohol": "Never",
        "nmq": ["No","Yes","No","Yes","No","Yes","No","No","No"],
        "d7": ["No","Yes","No","No"],
        "outcomes": ["No","No","No","Yes","Yes"],
        "nasa": [50, 50, 50, 50, 75, 50],
        "borg": [4, 4, 3, 4, 5, 5],
        "rula": [2, 2, 2, 1, 2, 2, 1, 0, 1, 0, 1],
        "qec":  [28, 28, 26, 18, 8, 6, 6, 8],
    },
    "high": {
        "age": ">=46", "gender": "Male", "region": "Local", "marital_status": "Married",
        "income": ">35,000", "education": "Degree / Master's",
        "job_duration": ">24 months",
        "work_hours": "> 8 hrs", "work_days": "7", "deliveries": ">= 31",
        "rest_break": "< 5 min", "type_of_break": "Uneven",
        "delivery_platform": "Both", "vehicle": "Motor bike", "carrying": "Handheld",
        "tobacco": "Regularly", "alcohol": "Regularly",
        "nmq": ["Yes"]*9, "d7": ["Yes"]*4,
        "outcomes": ["Yes"]*5,
        "nasa": [100, 100, 100, 100, 100, 100],
        "borg": [10, 10, 10, 10, 10, 10],
        "rula": [4, 3, 3, 2, 4, 4, 2, 1, 3, 1, 3],
        "qec":  [46, 56, 46, 36, 16, 9, 10, 16],
    },
}

# Per-factor recommendation shown when prediction is Medium / High
RECOMMENDATIONS = {
    "force": {
        "High":   "Reduce maximum carried weight. Train safer lifting technique. "
                  "Provide trolleys for heavier multi-drop runs.",
        "Medium": "Monitor force exposure. Encourage two-handed carry and "
                  "shorter weight-bearing intervals.",
    },
    "repetition": {
        "High":   "Cap deliveries-per-hour at the platform level. Build "
                  "longer batching windows so riders are not pushed into "
                  "extreme dispatch rates.",
        "Medium": "Review route-batching policy. Avoid back-to-back dense "
                  "drop clusters in the same shift block.",
    },
    "duration": {
        "High":   "Cap daily shift length. Mandatory 15-minute rest break "
                  "every 2 hours. Hardest-hitting intervention overall.",
        "Medium": "Encourage off-app breaks. Discourage chaining shifts "
                  "across platforms.",
    },
    "vibration": {
        "High":   "Anti-vibration grips and seat cushion. Tyre pressure check. "
                  "Where possible, reassign motor-bike riders to short routes.",
        "Medium": "Tyre pressure check. Inspect for worn handlebar grips.",
    },
    "contact_stress": {
        "High":   "Switch from handheld bag to bike-storage box or padded "
                  "backpack. Padded straps where carrying is unavoidable.",
        "Medium": "Audit carrying mode for awkward grip postures. Offer "
                  "padded backpack as standard issue.",
    },
    "posture": {
        "High":   "Ergonomic review of seat height and handlebar angle. "
                  "Neck/back stretching protocol before shifts. Annual "
                  "physiotherapy screen for riders flagged here.",
        "Medium": "Posture micro-breaks every 30 minutes. Helmet weight "
                  "check (heavy helmets aggravate neck flexion).",
    },
}


@st.cache_resource
def load_models():
    return {f: joblib.load(MODELS / f"best_{f}.pkl") for f in FACTORS}


def encode_rider(raw):
    """Raw survey answers -> the 44+11+8 features the models consume."""
    nasa = raw["nasa"]
    borg = raw["borg"]

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


def apply_preset(preset_key):
    """Push a preset into session_state so the form re-renders with those values."""
    p = PRESETS[preset_key]
    for slot, value in [
        ("age", p["age"]), ("gender", p["gender"]), ("region", p["region"]),
        ("marital", p["marital_status"]), ("income", p["income"]),
        ("education", p["education"]), ("job_duration", p["job_duration"]),
        ("work_hours", p["work_hours"]), ("work_days", p["work_days"]),
        ("deliveries", p["deliveries"]), ("rest_break", p["rest_break"]),
        ("break_type", p["type_of_break"]), ("platform", p["delivery_platform"]),
        ("vehicle", p["vehicle"]), ("carrying", p["carrying"]),
        ("tobacco", p["tobacco"]), ("alcohol", p["alcohol"]),
        ("out_reduced_perf",     p["outcomes"][0]),
        ("out_taken_leave",      p["outcomes"][1]),
        ("out_consulted_doctor", p["outcomes"][2]),
        ("out_riding_worsens",   p["outcomes"][3]),
        ("out_carrying_worsens", p["outcomes"][4]),
        ("nasa_mental",       p["nasa"][0]),
        ("nasa_physical",     p["nasa"][1]),
        ("nasa_time",         p["nasa"][2]),
        ("nasa_dissatisfied", p["nasa"][3]),
        ("nasa_effort",       p["nasa"][4]),
        ("nasa_frustration",  p["nasa"][5]),
        ("borg_overall",    p["borg"][0]),
        ("borg_legs",       p["borg"][1]),
        ("borg_breathing",  p["borg"][2]),
        ("borg_lifting",    p["borg"][3]),
        ("borg_traffic",    p["borg"][4]),
        ("borg_exhaustion", p["borg"][5]),
        ("upper_arm",      p["rula"][0]),
        ("lower_arm",      p["rula"][1]),
        ("wrist",          p["rula"][2]),
        ("wrist_twist",    p["rula"][3]),
        ("neck_position",  p["rula"][4]),
        ("trunk_position", p["rula"][5]),
        ("legs",           p["rula"][6]),
        ("muscle_a",       p["rula"][7]),
        ("force_a",        p["rula"][8]),
        ("muscle_b",       p["rula"][9]),
        ("force_b",        p["rula"][10]),
        ("qec_back",         p["qec"][0]),
        ("qec_shoulder_arm", p["qec"][1]),
        ("qec_wrist_hand",   p["qec"][2]),
        ("qec_neck",         p["qec"][3]),
        ("qec_driving",      p["qec"][4]),
        ("qec_vibration",    p["qec"][5]),
        ("qec_work_pace",    p["qec"][6]),
        ("qec_stress",       p["qec"][7]),
    ]:
        st.session_state[slot] = value
    for i, v in enumerate(p["nmq"]):
        st.session_state[f"nmq_{i}"] = v
    for i, v in enumerate(p["d7"]):
        st.session_state[f"d7_{i}"] = v


# ---- Page ----

st.set_page_config(page_title="Ergonomic Risk Predictor", page_icon="🛵", layout="wide")

with st.sidebar:
    st.title("About this tool")
    st.markdown(
        "**Ergonomic Risk Predictor** screens a food-delivery rider across "
        "six ergonomic risk factors using six trained classifiers."
    )
    st.markdown("**The six factors**")
    st.markdown(
        "- **Force** - lifting / carrying load\n"
        "- **Repetition** - deliveries per hour\n"
        "- **Posture** - RULA Table C action level\n"
        "- **Duration** - continuous riding hours\n"
        "- **Contact Stress** - load against the body\n"
        "- **Vibration** - vehicle x hours"
    )
    st.markdown("**Inputs**")
    st.markdown(
        "- 36 questionnaire items (demographics, NMQ pain, NASA-TLX, Borg CR10)\n"
        "- 11 RULA observation components\n"
        "- 8 QEC scores"
    )
    st.markdown("**Output**")
    st.markdown(
        "Low / Medium / High level per factor, plus a recommendations panel "
        "for any factor flagged at Medium or High."
    )
    st.divider()
    st.caption("Full project write-up: `docs/PROJECT_REPORT.md`. Models: "
               "`outputs/models/best_*.pkl`. Phase 6 CV accuracy ranges from "
               "58% (Vibration) to 97% (Posture).")

st.title("🛵 Ergonomic Risk Predictor")
st.markdown(
    "Per-rider ergonomic risk screening across six factors. "
    "Answer the questionnaire and observation sections below, "
    "then press **Predict** to see the six risk levels and any recommendations."
)

# Quick-start preset bar (sits outside the form so clicks immediately re-render)
st.markdown("**Try a sample profile**  (one click pre-fills the whole form)")
c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
with c1:
    if st.button("Low-risk rider", use_container_width=True):
        apply_preset("low")
        st.rerun()
with c2:
    if st.button("Average rider", use_container_width=True):
        apply_preset("average")
        st.rerun()
with c3:
    if st.button("High-risk rider", use_container_width=True):
        apply_preset("high")
        st.rerun()

st.divider()

models = load_models()

with st.form("rider_form"):

    # ============ SECTION 1: DEMOGRAPHIC (Q1-17) ============
    st.header("Demographic")
    col1, col2, col3 = st.columns(3)
    with col1:
        gender       = st.selectbox("1. Gender", list(GENDER_MAP.keys()), key="gender")
        age          = st.selectbox("2. Age", list(AGE_MAP.keys()), key="age",
                                    index=list(AGE_MAP.keys()).index(st.session_state.get("age", "25-35")))
        education    = st.selectbox("3. Education", list(EDUCATION_MAP.keys()), key="education",
                                    index=list(EDUCATION_MAP.keys()).index(
                                        st.session_state.get("education", "Degree / Master's")))
        region       = st.selectbox("4. Region", list(REGION_MAP.keys()), key="region")
        marital      = st.selectbox("5. Marital status", list(MARITAL_MAP.keys()), key="marital")
        platform     = st.selectbox("6. Delivery platform", list(PLATFORM_MAP.keys()), key="platform")
    with col2:
        job_duration = st.selectbox("7. Job duration (experience)",
                                    list(JOB_DURATION_MAP.keys()), key="job_duration",
                                    index=list(JOB_DURATION_MAP.keys()).index(
                                        st.session_state.get("job_duration", "12-24 months")))
        income       = st.selectbox("8. Monthly income (INR)",
                                    list(INCOME_MAP.keys()), key="income",
                                    index=list(INCOME_MAP.keys()).index(
                                        st.session_state.get("income", "20,000-35,000")))
        vehicle      = st.selectbox("9. Type of vehicle", list(VEHICLE_MAP.keys()), key="vehicle",
                                    index=list(VEHICLE_MAP.keys()).index(
                                        st.session_state.get("vehicle", "Motor bike")))
        carrying     = st.selectbox("10. Mode of carrying deliveries",
                                    list(CARRYING_MAP.keys()), key="carrying",
                                    index=list(CARRYING_MAP.keys()).index(
                                        st.session_state.get("carrying", "Backpack")))
        work_hours   = st.selectbox("11. Working hours per day",
                                    list(WORK_HOURS_MAP.keys()), key="work_hours",
                                    index=list(WORK_HOURS_MAP.keys()).index(
                                        st.session_state.get("work_hours", "6-8 hrs")))
        work_days    = st.selectbox("12. Working days per week",
                                    list(WORK_DAYS_MAP.keys()), key="work_days",
                                    index=list(WORK_DAYS_MAP.keys()).index(
                                        st.session_state.get("work_days", "5-6")))
    with col3:
        deliveries   = st.selectbox("13. Number of deliveries per day",
                                    list(DELIVERIES_MAP.keys()), key="deliveries",
                                    index=list(DELIVERIES_MAP.keys()).index(
                                        st.session_state.get("deliveries", "21-30")))
        rest_break   = st.selectbox("14. Duration of rest break",
                                    list(REST_BREAK_MAP.keys()), key="rest_break",
                                    index=list(REST_BREAK_MAP.keys()).index(
                                        st.session_state.get("rest_break", "5-15 min")))
        break_type   = st.selectbox("15. Type of break", list(BREAK_TYPE_MAP.keys()), key="break_type")
        tobacco      = st.selectbox("16. Tobacco consumption", list(SUBSTANCE_MAP.keys()), key="tobacco")
        alcohol      = st.selectbox("17. Alcohol consumption", list(SUBSTANCE_MAP.keys()), key="alcohol")

    st.divider()

    # ============ SECTION 2: NORDIC + DISCOMFORT (Q18-24) ============
    st.header("Nordic Musculoskeletal Questionnaire (NMQ)")

    st.markdown("**18. In the past 12 months, have you experienced pain, discomfort, "
                "or numbness in the following body areas due to delivery work?**")
    nmq = []
    cols = st.columns(3)
    for i, area in enumerate(NMQ_AREAS):
        with cols[i % 3]:
            nmq.append(st.radio(area, YES_NO,
                                index=YES_NO.index(st.session_state.get(f"nmq_{i}", "No")),
                                horizontal=True, key=f"nmq_{i}"))

    st.markdown("**19. In the past 7 days, have you experienced discomfort in:**")
    d7 = []
    cols = st.columns(4)
    for i, area in enumerate(D7_AREAS):
        with cols[i]:
            d7.append(st.radio(area, YES_NO,
                               index=YES_NO.index(st.session_state.get(f"d7_{i}", "No")),
                               horizontal=True, key=f"d7_{i}"))

    st.markdown("**Discomfort follow-ups (Q20-Q24)**")
    cols = st.columns(2)
    with cols[0]:
        out_reduced_perf  = st.radio("20. Has discomfort reduced your delivery performance?",
                                     YES_NO,
                                     index=YES_NO.index(st.session_state.get("out_reduced_perf", "No")),
                                     horizontal=True, key="out_reduced_perf")
        out_taken_leave   = st.radio("21. Have you ever taken leave due to body pain caused by delivery work?",
                                     YES_NO,
                                     index=YES_NO.index(st.session_state.get("out_taken_leave", "No")),
                                     horizontal=True, key="out_taken_leave")
        out_consulted_doctor = st.radio("22. Have you consulted a doctor or physiotherapist for work-related pain?",
                                        YES_NO,
                                        index=YES_NO.index(st.session_state.get("out_consulted_doctor", "No")),
                                        horizontal=True, key="out_consulted_doctor")
    with cols[1]:
        out_riding_worsens   = st.radio("23. Does riding/driving for long hours increase your discomfort?",
                                        YES_NO,
                                        index=YES_NO.index(st.session_state.get("out_riding_worsens", "No")),
                                        horizontal=True, key="out_riding_worsens")
        out_carrying_worsens = st.radio("24. Does carrying heavy packages worsen your discomfort?",
                                        YES_NO,
                                        index=YES_NO.index(st.session_state.get("out_carrying_worsens", "No")),
                                        horizontal=True, key="out_carrying_worsens")

    st.divider()

    # ============ SECTION 3: NASA-TLX (Q25-30) ============
    st.header("NASA-TLX workload   (Low 0 — 100 High)")
    cols = st.columns(2)
    with cols[0]:
        nasa_mental    = st.slider("25. How mentally demanding was your delivery shift?",
                                   0, 100, st.session_state.get("nasa_mental", 50), 25, key="nasa_mental")
        nasa_physical  = st.slider("26. How physically demanding was your delivery shift?",
                                   0, 100, st.session_state.get("nasa_physical", 50), 25, key="nasa_physical")
        nasa_time      = st.slider("27. How rushed or time-pressured did you feel?",
                                   0, 100, st.session_state.get("nasa_time", 50), 25, key="nasa_time")
    with cols[1]:
        nasa_dissatisfied = st.slider("28. How DISSATISFIED were you with your ability to "
                                      "complete deliveries accurately and on time?",
                                      0, 100, st.session_state.get("nasa_dissatisfied", 25), 25,
                                      key="nasa_dissatisfied",
                                      help="0 = very satisfied, 100 = very dissatisfied. "
                                           "All 6 NASA sliders point the same way.")
        nasa_effort    = st.slider("29. How much effort did you put in to maintain performance?",
                                   0, 100, st.session_state.get("nasa_effort", 75), 25, key="nasa_effort")
        nasa_frustration = st.slider("30. How stressed, frustrated, or emotionally strained did you feel?",
                                     0, 100, st.session_state.get("nasa_frustration", 50), 25,
                                     key="nasa_frustration")

    st.divider()

    # ============ SECTION 4: BORG CR10 (Q31-36) ============
    st.header("Borg CR10 fatigue   (0 = Extremely Easy, 10 = Extremely Hard)")
    cols = st.columns(2)
    with cols[0]:
        borg_overall    = st.slider("31. Overall, how hard did your delivery work feel today?",
                                    0, 10, st.session_state.get("borg_overall", 4), key="borg_overall")
        borg_legs       = st.slider("32. How tired did your legs feel while walking/riding?",
                                    0, 10, st.session_state.get("borg_legs", 4), key="borg_legs")
        borg_breathing  = st.slider("33. How hard was it to breathe during deliveries?",
                                    0, 10, st.session_state.get("borg_breathing", 3), key="borg_breathing")
    with cols[1]:
        borg_lifting    = st.slider("34. How hard did lifting or carrying parcels feel?",
                                    0, 10, st.session_state.get("borg_lifting", 4), key="borg_lifting")
        borg_traffic    = st.slider("35. How physically stressful was working in traffic/weather conditions?",
                                    0, 10, st.session_state.get("borg_traffic", 5), key="borg_traffic")
        borg_exhaustion = st.slider("36. At the end of your shift, how exhausted did your body feel?",
                                    0, 10, st.session_state.get("borg_exhaustion", 5), key="borg_exhaustion")

    st.divider()

    # ============ SECTION 5: RULA OBSERVATION (Posture model) ============
    st.header("Posture observation (RULA)")
    st.caption("Score each item using the standard RULA worksheet. These 11 inputs "
               "drive the Posture model directly. If unsure, leave defaults.")
    cols = st.columns(3)
    with cols[0]:
        st.markdown("**Group A - Arm & wrist**")
        upper_arm   = st.selectbox("Upper arm (1-4)",   [1, 2, 3, 4],
                                   index=[1,2,3,4].index(st.session_state.get("upper_arm", 2)),
                                   key="upper_arm",
                                   help="1 = 20° flex/ext, 4 = >90° flex")
        lower_arm   = st.selectbox("Lower arm (1-3)",   [1, 2, 3],
                                   index=[1,2,3].index(st.session_state.get("lower_arm", 1)),
                                   key="lower_arm",
                                   help="1 = 60-100° flex, 2 = <60° or >100°, 3 = across body")
        wrist       = st.selectbox("Wrist (1-3)",       [1, 2, 3],
                                   index=[1,2,3].index(st.session_state.get("wrist", 1)),
                                   key="wrist",
                                   help="1 = neutral, 2 = +/-15°, 3 = >15°")
        wrist_twist = st.selectbox("Wrist twist (1-2)", [1, 2],
                                   index=[1,2].index(st.session_state.get("wrist_twist", 1)),
                                   key="wrist_twist",
                                   help="1 = midrange, 2 = at end of range")
    with cols[1]:
        st.markdown("**Group B - Neck, trunk, legs**")
        neck_position  = st.selectbox("Neck position (1-4)",  [1, 2, 3, 4],
                                      index=[1,2,3,4].index(st.session_state.get("neck_position", 2)),
                                      key="neck_position",
                                      help="1 = 0-10° flex, 4 = extension")
        trunk_position = st.selectbox("Trunk position (1-4)", [1, 2, 3, 4],
                                      index=[1,2,3,4].index(st.session_state.get("trunk_position", 2)),
                                      key="trunk_position",
                                      help="1 = upright, 4 = >60° flex")
        legs           = st.selectbox("Legs (1-2)",           [1, 2],
                                      index=[1,2].index(st.session_state.get("legs", 1)),
                                      key="legs",
                                      help="1 = supported balanced, 2 = unbalanced")
    with cols[2]:
        st.markdown("**Muscle & force adjustments**")
        muscle_a = st.selectbox("Muscle A (0-1)", [0, 1],
                                index=[0,1].index(st.session_state.get("muscle_a", 0)),
                                key="muscle_a",
                                help="+1 if static >1 min or repeating >4/min (Group A)")
        force_a  = st.selectbox("Force A (0-3)",  [0, 1, 2, 3],
                                index=[0,1,2,3].index(st.session_state.get("force_a", 0)),
                                key="force_a",
                                help="0 = <2kg intermittent, 3 = >10kg or shock")
        muscle_b = st.selectbox("Muscle B (0-1)", [0, 1],
                                index=[0,1].index(st.session_state.get("muscle_b", 0)),
                                key="muscle_b",
                                help="+1 if static >1 min or repeating >4/min (Group B)")
        force_b  = st.selectbox("Force B (0-3)",  [0, 1, 2, 3],
                                index=[0,1,2,3].index(st.session_state.get("force_b", 0)),
                                key="force_b")

    st.divider()

    # ============ SECTION 6: QEC OBSERVATION (Posture model) ============
    st.header("Quick Exposure Check (QEC)")
    st.caption("QEC sums standard worksheet items into 8 region/exposure scores. "
               "Values match the observed ranges in the training data. "
               "If unsure, leave defaults.")
    cols = st.columns(4)
    with cols[0]:
        st.markdown("**Body regions**")
        qec_back         = st.number_input("Back (14-46)", min_value=14, max_value=46,
                                           value=st.session_state.get("qec_back", 28),
                                           step=2, key="qec_back")
        qec_shoulder_arm = st.number_input("Shoulder/Arm (14-56)", min_value=14, max_value=56,
                                           value=st.session_state.get("qec_shoulder_arm", 28),
                                           step=2, key="qec_shoulder_arm")
    with cols[1]:
        st.markdown("**Body regions**")
        qec_wrist_hand   = st.number_input("Wrist/Hand (14-46)", min_value=14, max_value=46,
                                           value=st.session_state.get("qec_wrist_hand", 26),
                                           step=2, key="qec_wrist_hand")
        qec_neck         = st.number_input("Neck (10-36)", min_value=10, max_value=36,
                                           value=st.session_state.get("qec_neck", 18),
                                           step=2, key="qec_neck")
    with cols[2]:
        st.markdown("**Exposures**")
        qec_driving      = st.number_input("Driving (4-16)", min_value=4, max_value=16,
                                           value=st.session_state.get("qec_driving", 8),
                                           step=1, key="qec_driving")
        qec_vibration    = st.number_input("Vibration (4-9)", min_value=4, max_value=9,
                                           value=st.session_state.get("qec_vibration", 6),
                                           step=1, key="qec_vibration")
    with cols[3]:
        st.markdown("**Exposures**")
        qec_work_pace    = st.number_input("Work pace (1-10)", min_value=1, max_value=10,
                                           value=st.session_state.get("qec_work_pace", 6),
                                           step=1, key="qec_work_pace")
        qec_stress       = st.number_input("Stress (1-16)", min_value=1, max_value=16,
                                           value=st.session_state.get("qec_stress", 8),
                                           step=1, key="qec_stress")

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
    st.subheader("Predicted risk profile")

    nice  = {"force": "Force", "repetition": "Repetition", "duration": "Duration",
             "vibration": "Vibration", "contact_stress": "Contact Stress", "posture": "Posture"}
    badge = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
    score = {"Low": 1, "Medium": 2, "High": 3}
    colour = {"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e74c3c"}

    # Metric strip - one big card per factor
    cols = st.columns(6)
    for c, factor in zip(cols, FACTORS):
        with c:
            level = predictions[factor]
            st.metric(nice[factor], f"{badge[level]} {level}")

    # Horizontal bar chart, ordered to match the metric strip, colour-coded
    # by risk level. Altair gives us proper control over both, unlike
    # st.bar_chart which alphabetises and accepts only a single colour.
    chart_df = pd.DataFrame({
        "Factor": [nice[f] for f in FACTORS],
        "Level":  [predictions[f] for f in FACTORS],
        "Score":  [score[predictions[f]] for f in FACTORS],
    })
    factor_order = [nice[f] for f in FACTORS]
    chart = (
        alt.Chart(chart_df)
        .mark_bar(cornerRadiusEnd=4, size=26)
        .encode(
            y=alt.Y("Factor:N", sort=factor_order, title=None,
                    axis=alt.Axis(labelFontSize=13, labelPadding=8)),
            x=alt.X("Score:Q",
                    scale=alt.Scale(domain=[0, 3]),
                    axis=alt.Axis(values=[1, 2, 3], title=None,
                                  labelExpr="{'1':'Low','2':'Medium','3':'High'}[datum.label]",
                                  labelFontSize=12)),
            color=alt.Color("Level:N",
                            scale=alt.Scale(domain=["Low", "Medium", "High"],
                                            range=["#2ecc71", "#f1c40f", "#e74c3c"]),
                            legend=None),
            tooltip=[alt.Tooltip("Factor:N"), alt.Tooltip("Level:N")],
        )
        .properties(height=240)
        .configure_view(strokeWidth=0)
    )
    st.altair_chart(chart, use_container_width=True)

    # Summary banner
    high = sum(v == "High" for v in predictions.values())
    med  = sum(v == "Medium" for v in predictions.values())
    if high >= 3:
        st.error(f"⚠ {high} of 6 factors are HIGH risk - high-burden ergonomic profile.")
    elif high + med >= 4:
        st.warning(f"{high} High and {med} Medium risk factors - several modifiable exposures.")
    else:
        st.success("Predominantly low-to-medium risk profile across the 6 factors.")

    # Recommendations panel - only show factors at Medium / High
    flagged = [(f, predictions[f]) for f in FACTORS if predictions[f] in ("Medium", "High")]
    if flagged:
        st.subheader("Recommended actions")
        for f, level in flagged:
            rec = RECOMMENDATIONS[f].get(level)
            if not rec:
                continue
            tone = "🔴" if level == "High" else "🟡"
            with st.expander(f"{tone} {nice[f]} ({level})", expanded=(level == "High")):
                st.write(rec)

    with st.expander(f"Show the {len(features)} encoded feature values"):
        st.json(features)
