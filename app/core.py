"""
Shared logic for the multi-page Streamlit web app.

Everything that used to live in the top of streamlit_app.py is here so
each page module can import the same encoding maps, model loader, and
prediction helpers.
"""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

ROOT    = Path(__file__).resolve().parents[1]
MODELS  = ROOT / "outputs" / "models"
FACTORS = ["force", "repetition", "duration", "vibration", "contact_stress", "posture"]
LABELS  = ["Low", "Medium", "High"]
FACTOR_LABEL = {
    "force":          "Force",
    "repetition":     "Repetition",
    "duration":       "Duration",
    "vibration":      "Vibration",
    "contact_stress": "Contact Stress",
    "posture":        "Posture",
}
FACTOR_ICON = {
    "force": "", "repetition": "", "duration": "",
    "vibration": "", "contact_stress": "", "posture": "",
}
FACTOR_DESC = {
    "force":          "Lifting and carrying effort per shift, from the Borg CR10 lifting item.",
    "repetition":     "Deliveries per hour, computed as deliveries_num / work_hours_num.",
    "duration":       "Continuous riding time per shift, in hours.",
    "vibration":      "Vibration exposure, approximated as vehicle_rank * work_hours_num.",
    "contact_stress": "Load pressing against the body, weighted by carrying mode, hours, and age.",
    "posture":        "Awkward body angles held while riding and carrying, from RULA Table C.",
}
LEVEL_COLOUR = {"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e74c3c"}
LEVEL_EMOJI  = {"Low": "",         "Medium": "",         "High": ""}


# ---------------------------------------------------------------------------
# Encoding maps (mirror Phase 2 exactly)
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Sample profiles for the one-click Try buttons
# ---------------------------------------------------------------------------

PRESETS = {
    "low": {
        "age": "<25", "gender": "Male", "region": "Local", "marital_status": "Unmarried",
        "income": "10,000-19,999", "education": "Degree / Master's",
        "job_duration": "<6 months",
        "work_hours": "6-8 hrs", "work_days": "3-4", "deliveries": "11-20",
        "rest_break": "> 30 min", "type_of_break": "Even",
        "delivery_platform": "Blinkit", "vehicle": "Scooter",
        "carrying": "Bike storage / carrier",
        "tobacco": "Never", "alcohol": "Never",
        "nmq": ["No"]*9, "d7": ["No"]*4,
        "outcomes": ["No"]*5,
        "nasa": [25, 25, 25, 25, 25, 25],
        "borg": [2, 2, 2, 2, 2, 2],
        "rula": [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        "qec":  [14, 14, 14, 10, 4, 4, 1, 1],
    },
    "average": {
        "age": "25-35", "gender": "Male", "region": "Local", "marital_status": "Unmarried",
        "income": "20,000-35,000", "education": "Degree / Master's",
        "job_duration": "12-24 months",
        "work_hours": "6-8 hrs", "work_days": "5-6", "deliveries": "21-30",
        "rest_break": "5-15 min", "type_of_break": "Uneven",
        "delivery_platform": "Blinkit", "vehicle": "Motor bike",
        "carrying": "Backpack",
        "tobacco": "Never", "alcohol": "Never",
        "nmq": ["No", "Yes", "No", "Yes", "No", "Yes", "No", "No", "No"],
        "d7": ["No", "Yes", "No", "No"],
        "outcomes": ["No", "No", "No", "Yes", "Yes"],
        "nasa": [50, 50, 50, 25, 75, 50],
        "borg": [4, 4, 3, 4, 5, 5],
        "rula": [2, 2, 2, 1, 2, 2, 1, 0, 1, 0, 1],
        "qec":  [28, 28, 26, 18, 8, 6, 6, 8],
    },
    "high": {
        "age": ">=46", "gender": "Male", "region": "Non-Local", "marital_status": "Married",
        "income": "10,000-19,999", "education": "High school",
        "job_duration": ">24 months",
        "work_hours": "> 8 hrs", "work_days": "7", "deliveries": ">= 31",
        "rest_break": "< 5 min", "type_of_break": "Uneven",
        "delivery_platform": "Zepto", "vehicle": "Motor bike",
        "carrying": "Handheld",
        "tobacco": "Regularly", "alcohol": "Regularly",
        "nmq": ["Yes"]*9, "d7": ["Yes"]*4,
        "outcomes": ["Yes"]*5,
        "nasa": [90, 90, 95, 100, 100, 95],
        "borg": [9, 9, 8, 10, 10, 10],
        "rula": [4, 3, 3, 2, 4, 4, 2, 1, 3, 1, 3],
        "qec":  [46, 56, 46, 36, 16, 9, 10, 16],
    },
}


# ---------------------------------------------------------------------------
# Model loading, encoding, prediction
# ---------------------------------------------------------------------------

@st.cache_resource
def load_models():
    return {f: joblib.load(MODELS / f"best_{f}.pkl") for f in FACTORS}


def encode_rider(raw):
    """Raw survey answers -> the 63 features the models consume."""
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


def preset_to_raw(name):
    """Turn a preset name into the raw dict encode_rider expects."""
    p = PRESETS[name]
    return dict(
        age=p["age"], gender=p["gender"], region=p["region"],
        marital_status=p["marital_status"],
        income=p["income"], education=p["education"], job_duration=p["job_duration"],
        work_hours=p["work_hours"], work_days=p["work_days"], deliveries=p["deliveries"],
        rest_break=p["rest_break"], type_of_break=p["type_of_break"],
        delivery_platform=p["delivery_platform"], vehicle=p["vehicle"],
        carrying=p["carrying"],
        tobacco=p["tobacco"], alcohol=p["alcohol"],
        nmq=p["nmq"], d7=p["d7"],
        out_reduced_perf=p["outcomes"][0], out_taken_leave=p["outcomes"][1],
        out_consulted_doctor=p["outcomes"][2], out_riding_worsens=p["outcomes"][3],
        out_carrying_worsens=p["outcomes"][4],
        nasa={"mental": p["nasa"][0], "physical": p["nasa"][1],
              "time_pressure": p["nasa"][2], "dissatisfied": p["nasa"][3],
              "effort": p["nasa"][4], "frustration": p["nasa"][5]},
        borg={"overall": p["borg"][0], "legs": p["borg"][1],
              "breathing": p["borg"][2], "lifting": p["borg"][3],
              "traffic": p["borg"][4], "exhaustion": p["borg"][5]},
        rula=dict(zip(RULA_KEYS, p["rula"])),
        qec=dict(zip(QEC_KEYS, p["qec"])),
    )


# ---------------------------------------------------------------------------
# Shared CSS - injected on every page for consistent theming
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
<style>
/* ---------- Reset default Streamlit chrome ---------- */
#MainMenu, footer, header[data-testid='stHeader'], .stDeployButton {
    visibility: hidden;
    display: none;
}

/* ---------- Base layout ---------- */
.block-container {
    padding-top: 3rem;
    padding-bottom: 4rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1180px;
}

/* ---------- Typography ---------- */
html, body, [class*='st-'] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: -0.01em;
    color: #f5f7fa;
    line-height: 1.3;
}
h1 { font-size: 2.1rem; font-weight: 700; margin-bottom: 0.4rem; }
h2 { font-size: 1.55rem; font-weight: 600; margin-top: 2rem; margin-bottom: 0.8rem; }
h3 { font-size: 1.2rem; font-weight: 600; }
h4 { font-size: 1.02rem; font-weight: 600; color: #d5dae0; }
p, li, label { line-height: 1.6; color: #cfd4d9; }

/* Caption tightened */
[data-testid='stCaptionContainer'] p {
    color: #8a919b;
    font-size: 0.88rem;
}

/* ---------- Consistent card ---------- */
.card {
    background: #171b25;
    border: 1px solid #2a3040;
    border-radius: 6px;
    padding: 1.3rem 1.5rem;
    margin: 0.75rem 0;
    transition: border-color 0.15s ease;
}
.card:hover { border-color: #3a4055; }
.card h3 {
    margin: 0 0 0.45rem 0;
    color: #f5f7fa;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: -0.01em;
}
.card p {
    margin: 0;
    color: #a9b0ba;
    line-height: 1.6;
    font-size: 0.94rem;
}

/* ---------- Risk cards on Results ---------- */
.risk-card {
    border-radius: 6px;
    padding: 1.3rem 1.2rem;
    text-align: center;
    border: 1px solid rgba(0, 0, 0, 0.15);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
}
.risk-card .factor-name {
    font-size: 0.78rem;
    color: rgba(255, 255, 255, 0.92);
    text-transform: uppercase;
    letter-spacing: 0.10em;
    margin-bottom: 0.55rem;
    font-weight: 500;
}
.risk-card .level {
    font-size: 1.95rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0.25rem 0 0.05rem 0;
    letter-spacing: -0.01em;
}
.risk-low    { background: #27ae60; }
.risk-medium { background: #e0a800; }
.risk-high   { background: #d13d2f; }

/* ---------- Stat block ---------- */
.stat {
    padding: 0.8rem 0 0.8rem 1.1rem;
    border-left: 3px solid #2E86AB;
    margin: 0.4rem 0;
}
.stat .value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    display: block;
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.stat .label {
    font-size: 0.83rem;
    color: #8a919b;
    margin-top: 0.2rem;
    display: block;
}

/* ---------- Section headers ---------- */
.section-title {
    color: #f5f7fa;
    font-size: 1.35rem;
    font-weight: 600;
    margin: 2.5rem 0 1rem 0;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid #2a3040;
    letter-spacing: -0.01em;
}

/* ---------- Streamlit buttons ---------- */
.stButton > button {
    border-radius: 6px;
    border: 1px solid #2a3040;
    padding: 0.55rem 1.2rem;
    font-weight: 500;
    font-size: 0.94rem;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    border-color: #2E86AB;
    color: #ffffff;
}
.stButton > button[kind='primary'] {
    background: #2E86AB;
    border-color: #2E86AB;
    color: #ffffff;
    font-weight: 600;
}
.stButton > button[kind='primary']:hover {
    background: #256d8c;
    border-color: #256d8c;
    color: #ffffff;
}

/* ---------- Sidebar polish ---------- */
[data-testid='stSidebar'] {
    background: #0b0e14;
    border-right: 1px solid #1c2130;
}
[data-testid='stSidebar'] [data-testid='stMarkdown'] p {
    color: #a9b0ba;
    font-size: 0.87rem;
}

/* ---------- Form input polish ---------- */
[data-testid='stSelectbox'] > div > div,
[data-testid='stNumberInput'] > div > div > input,
[data-testid='stTextInput'] > div > div > input {
    background: #171b25;
    border: 1px solid #2a3040;
    border-radius: 5px;
}

/* Slider track colour */
.stSlider [data-baseweb='slider'] div[role='slider'] {
    background: #2E86AB;
    border-color: #2E86AB;
}

/* ---------- Dataframe polish ---------- */
[data-testid='stDataFrame'] {
    border: 1px solid #2a3040;
    border-radius: 6px;
    overflow: hidden;
}

/* ---------- Expander polish ---------- */
[data-testid='stExpander'] {
    border: 1px solid #2a3040;
    border-radius: 6px;
    background: #171b25;
    margin: 0.5rem 0;
}
[data-testid='stExpander'] summary {
    padding: 0.7rem 1rem;
    font-weight: 500;
}

/* ---------- Section-nav bar for Assessment ---------- */
.section-nav {
    background: #171b25;
    border: 1px solid #2a3040;
    border-radius: 6px;
    padding: 0.8rem 1.2rem;
    margin: 1rem 0 2rem 0;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    font-size: 0.88rem;
    color: #8a919b;
}
.section-nav strong { color: #f5f7fa; font-weight: 500; }
.section-nav .divider { color: #2a3040; }

/* ---------- Definition list for About / Methodology ---------- */
.def-list { margin: 0.5rem 0 1.5rem 0; }
.def-list dt {
    color: #8a919b;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.7rem;
    font-weight: 500;
}
.def-list dd {
    color: #f5f7fa;
    font-size: 1rem;
    margin: 0.15rem 0 0 0;
}
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def page_setup(title, icon=None):
    """Standard st.set_page_config + CSS injection. Call once per page."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide",
                       initial_sidebar_state="expanded")
    inject_css()
