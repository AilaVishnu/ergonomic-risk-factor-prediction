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
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800;900&family=Geist+Mono:wght@400;500&display=swap');

/* -----------------------------------------------------------------
   Vercel-inspired: pure black canvas, Geist typography, pill buttons
   ----------------------------------------------------------------- */

/* Hide Streamlit chrome but keep the header (it contains the sidebar
   toggle button). We just make the header transparent and hide its
   deploy / main-menu / status widgets. */
#MainMenu, footer, .stDeployButton, [data-testid='stStatusWidget'] {
    visibility: hidden !important;
    display: none !important;
}

/* Hide Streamlit Community Cloud's Fork button + "View source on GitHub"
   icon that get injected on the top-right of deployed apps.  These are
   unhideable via config on public-repo free-tier deploys, so we nuke
   them via CSS.  Selectors cover multiple versions of the injected DOM.
   NB: keep the "Made with Streamlit" bottom-right badge intact — the
   free-tier terms require it. */
#GithubIcon,
[data-testid='stToolbar'] a[href*='github.com'],
[data-testid='stActionButtonIcon'],
[data-testid='stAppDeployButton'],
button[title='Fork this app'],
a[title='View app source'],
a[href*='/streamlit/streamlit'] {
    display: none !important;
    visibility: hidden !important;
}
header[data-testid='stHeader'] {
    background: transparent !important;
    height: auto !important;
}
header[data-testid='stHeader'] button {
    color: #ededed !important;
}

/* Pure black canvas */
[data-testid='stAppViewContainer'],
[data-testid='stAppViewContainer'] > .main,
.stApp {
    background: #000000 !important;
}

/* Base */
html, body {
    font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #ededed;
    letter-spacing: -0.01em;
}
.stMarkdown, .stText, .stMetric, .stCaption,
.stButton, .stSelectbox, .stTextInput, .stNumberInput, .stRadio,
.stCheckbox, .stSlider, .stExpander, .stTabs, .stDataFrame,
p, li, label, h1, h2, h3, h4, h5, h6 {
    font-family: 'Geist', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 sans-serif;
}
code, pre {
    font-family: 'Geist Mono', 'JetBrains Mono', ui-monospace, monospace;
}

/* Preserve Streamlit's Material Symbols icon font so glyphs render as
   chevrons / arrows and not literal text like 'arrow_right' */
[data-testid='stIconMaterial'],
span[data-testid='stIconMaterial'],
[class*='material-icons'],
[class*='material-symbols'],
.material-symbols-rounded,
.material-symbols-outlined {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined',
                 'Material Icons' !important;
    letter-spacing: 0 !important;
    font-feature-settings: 'liga';
    -webkit-font-feature-settings: 'liga';
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.block-container {
    padding-top: 5rem;
    padding-bottom: 6rem;
    padding-left: 3rem;
    padding-right: 3rem;
    max-width: 1280px;
}

/* Narrow viewport - shrink padding and adjust hero title so main
   content is not pushed off-screen when the sidebar is open */
@media (max-width: 900px) {
    .block-container {
        padding-top: 2rem;
        padding-left: 1.25rem;
        padding-right: 1.25rem;
    }
    h1 { font-size: 3rem !important; }
    .hero__title { font-size: 3rem !important; }
    .hero { padding: 2rem 0; }
    .meta-strip { text-align: left; padding-top: 1.5rem; }
    .acronym-strip { gap: 1.5rem; }
    .section-title { font-size: 1.5rem; }
}
@media (max-width: 600px) {
    h1 { font-size: 2.25rem !important; }
    .hero__title { font-size: 2.25rem !important; }
    .stat .value { font-size: 1.75rem; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}

/* Typography scale */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1.05;
    font-weight: 600;
}
h1 { font-size: 4.5rem; font-weight: 700; letter-spacing: -0.045em; }
h2 { font-size: 2.5rem; font-weight: 600; letter-spacing: -0.035em;
     margin-top: 3rem; margin-bottom: 1rem; }
h3 { font-size: 1.25rem; font-weight: 600; letter-spacing: -0.02em; }
h4 { font-size: 1rem;    font-weight: 500; color: #a1a1a1; }
p, li, label { color: #a1a1a1; line-height: 1.55; font-size: 0.95rem; }
a { color: #ededed; text-decoration: none; }
a:hover { color: #ffffff; }

/* Muted caption */
[data-testid='stCaptionContainer'] p {
    color: #737373;
    font-size: 0.85rem;
}

/* -----------------------------------------------------------------
   Buttons - pill shape (Vercel "Deploy Now" / "Talk to Sales").
   Covers both st.button (.stButton) AND st.form_submit_button
   (.stFormSubmitButton / [data-testid='stFormSubmitButton']).
   ----------------------------------------------------------------- */
.stButton > button,
.stFormSubmitButton > button,
[data-testid='stFormSubmitButton'] > button {
    border-radius: 999px !important;
    padding: 0.75rem 1.75rem !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    border: 1px solid #333333 !important;
    background: #171717 !important;
    color: #ededed !important;
    letter-spacing: -0.005em;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover,
[data-testid='stFormSubmitButton'] > button:hover {
    background: #262626 !important;
    border-color: #525252 !important;
    color: #ffffff !important;
}

/* Primary variants: white pill with high-contrast black text.
   Includes the form-submit button which Streamlit does NOT tag with
   kind='primary' in the DOM even when passed type='primary' -- that's
   why the label was rendering faint on white before.  Use the parent
   testid to catch it regardless. */
.stButton > button[kind='primary'],
.stFormSubmitButton > button,
[data-testid='stFormSubmitButton'] > button {
    background: #ffffff !important;
    border-color: #ffffff !important;
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.85rem 2rem !important;
}
.stButton > button[kind='primary']:hover,
.stFormSubmitButton > button:hover,
[data-testid='stFormSubmitButton'] > button:hover {
    background: #ededed !important;
    border-color: #ededed !important;
    color: #000000 !important;
    transform: translateY(-1px);
}

/* Force text colour to inherit from the button element for every
   descendant Streamlit wraps the label in (<p>, <span>, <div>).
   Without this, Streamlit's own paragraph styling overrides the
   button's colour and the label goes faint. */
.stButton > button[kind='primary'] p,
.stButton > button[kind='primary'] span,
.stButton > button[kind='primary'] div,
.stFormSubmitButton > button p,
.stFormSubmitButton > button span,
.stFormSubmitButton > button div,
[data-testid='stFormSubmitButton'] > button p,
[data-testid='stFormSubmitButton'] > button span,
[data-testid='stFormSubmitButton'] > button div {
    color: #000000 !important;
}
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: inherit !important;
}

/* -----------------------------------------------------------------
   Hero (Vercel "Agentic Infrastructure" / triangle spotlight look)
   ----------------------------------------------------------------- */
.hero {
    position: relative;
    padding: 5rem 0 4rem;
    overflow: hidden;
}
.hero::before {
    /* Radial spotlight in the top-right, like the Vercel triangle glow */
    content: "";
    position: absolute;
    top: -20%;
    right: -10%;
    width: 700px;
    height: 700px;
    background: radial-gradient(circle at center,
                rgba(255, 255, 255, 0.15) 0%,
                rgba(255, 255, 255, 0.05) 25%,
                transparent 60%);
    pointer-events: none;
    z-index: 0;
}
.hero__inner { position: relative; z-index: 1; }

.hero__badge {
    display: inline-block;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #a1a1a1;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

.hero__title {
    color: #ffffff !important;
    font-size: 4.5rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.045em !important;
    line-height: 1.02 !important;
    margin: 0 0 1.5rem 0 !important;
    max-width: 900px;
}
.hero__title .muted { color: #737373; }

.hero__tagline {
    color: #a1a1a1;
    font-size: 1.1rem;
    line-height: 1.5;
    max-width: 640px;
    margin: 0 0 2.5rem 0;
}

/* Vercel-style right-aligned meta strip */
.meta-strip {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    text-align: right;
    padding-top: 0.5rem;
}
.meta-strip .meta-line {
    color: #ededed;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.meta-strip .meta-line .k { color: #737373; }

/* -----------------------------------------------------------------
   Cards + sections
   ----------------------------------------------------------------- */
.card {
    background: #0a0a0a;
    border: 1px solid #1f1f1f;
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin: 0.75rem 0;
    transition: border-color 0.2s ease, background 0.2s ease;
}
.card:hover {
    border-color: #333333;
    background: #111111;
}
.card h3 {
    margin: 0 0 0.5rem 0;
    color: #ffffff;
    font-size: 1.05rem;
    font-weight: 600;
    letter-spacing: -0.015em;
}
.card p {
    margin: 0;
    color: #a1a1a1;
    line-height: 1.55;
    font-size: 0.92rem;
}

.section-title {
    color: #ffffff;
    font-size: 2rem;
    font-weight: 600;
    margin: 4rem 0 1.5rem 0;
    letter-spacing: -0.03em;
    padding-bottom: 0;
    border-bottom: none;
}
.section-eyebrow {
    color: #737373;
    font-size: 0.78rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    font-family: 'Geist Mono', ui-monospace, monospace;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

/* Stat block */
.stat {
    padding: 1rem 0;
    border: none;
    background: none;
}
.stat .value {
    font-size: 2.5rem;
    font-weight: 600;
    color: #ffffff;
    display: block;
    letter-spacing: -0.04em;
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.stat .label {
    font-size: 0.8rem;
    color: #737373;
    margin-top: 0.6rem;
    display: block;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 500;
}

/* -----------------------------------------------------------------
   Risk cards (Results page)
   ----------------------------------------------------------------- */
.risk-card {
    border-radius: 12px;
    padding: 1.5rem 1.3rem;
    text-align: center;
    background: #0a0a0a;
    border: 1px solid #1f1f1f;
}
.risk-card .factor-name {
    font-size: 0.72rem;
    color: #737373;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-weight: 500;
}
.risk-card .level {
    font-size: 2rem;
    font-weight: 600;
    color: #ffffff;
    letter-spacing: -0.03em;
    line-height: 1;
}
.risk-low    { border-left: 3px solid #22c55e; }
.risk-medium { border-left: 3px solid #f59e0b; }
.risk-high   { border-left: 3px solid #ef4444; }

/* -----------------------------------------------------------------
   Sidebar - #0a0a0a so it is visually distinct from the pure-black
   main canvas
   ----------------------------------------------------------------- */
[data-testid='stSidebar'] {
    background: #0a0a0a !important;
    border-right: 1px solid #262626 !important;
    padding-top: 1rem;
}
[data-testid='stSidebar'] * { color: #ededed; }
[data-testid='stSidebar'] [data-testid='stMarkdown'] p {
    color: #a1a1a1;
    font-size: 0.85rem;
}
[data-testid='stSidebar'] h3 {
    color: #ffffff;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-top: 0;
    padding: 0 1rem;
}
[data-testid='stSidebar'] hr {
    border-top: 1px solid #262626;
    margin: 1rem 0;
}
/* Nav links (st.navigation) */
[data-testid='stSidebarNav'] {
    padding: 0.5rem 0;
}
[data-testid='stSidebarNav'] a {
    color: #a1a1a1 !important;
    padding: 0.55rem 1rem !important;
    border-radius: 6px !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    margin: 0.1rem 0.5rem !important;
    display: flex !important;
    align-items: center !important;
    transition: background 0.15s ease, color 0.15s ease;
}
[data-testid='stSidebarNav'] a:hover {
    background: #171717 !important;
    color: #ffffff !important;
}
[data-testid='stSidebarNav'] a[aria-current='page'] {
    background: #171717 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}
/* Sidebar collapse arrow */
[data-testid='stSidebarCollapseButton'] {
    color: #a1a1a1 !important;
}

/* -----------------------------------------------------------------
   Form inputs
   ----------------------------------------------------------------- */
[data-testid='stSelectbox'] > div > div,
[data-testid='stNumberInput'] > div > div > input,
[data-testid='stTextInput'] > div > div > input {
    background: #0a0a0a !important;
    border: 1px solid #262626 !important;
    border-radius: 8px !important;
    color: #ededed !important;
}
[data-testid='stSelectbox'] > div > div:focus-within,
[data-testid='stNumberInput'] > div > div:focus-within {
    border-color: #ededed !important;
}

.stSlider [data-baseweb='slider'] div[role='slider'] {
    background: #ffffff;
    border-color: #ffffff;
}

/* Dataframe */
[data-testid='stDataFrame'] {
    border: 1px solid #1f1f1f;
    border-radius: 8px;
    overflow: hidden;
}

/* Expander */
[data-testid='stExpander'] {
    border: 1px solid #1f1f1f;
    border-radius: 8px;
    background: #0a0a0a;
    margin: 0.5rem 0;
}
[data-testid='stExpander'] summary {
    padding: 0.85rem 1.1rem;
    color: #ededed;
    font-weight: 500;
}
[data-testid='stExpander'] summary:hover {
    background: #111111;
}

/* Alerts */
[data-testid='stAlertContainer'] {
    border-radius: 10px !important;
}

/* Section-nav (Assessment) */
.section-nav {
    background: #0a0a0a;
    border: 1px solid #1f1f1f;
    border-radius: 999px;
    padding: 0.7rem 1.5rem;
    margin: 1.5rem 0 3rem 0;
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    font-size: 0.82rem;
    color: #737373;
    font-family: 'Geist Mono', ui-monospace, monospace;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.section-nav strong { color: #ffffff; font-weight: 500; }
.section-nav .divider { color: #333333; }

/* Definition list */
.def-list { margin: 0.5rem 0 2rem 0; }
.def-list dt {
    color: #737373;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.10em;
    margin-top: 1.2rem;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-weight: 500;
}
.def-list dd {
    color: #ffffff;
    font-size: 1.05rem;
    margin: 0.3rem 0 0 0;
    font-weight: 500;
}

/* Radio labels */
[data-testid='stRadio'] label { color: #a1a1a1; }

/* Divider */
hr { border: none; border-top: 1px solid #1f1f1f; margin: 3rem 0; }

/* Trusted-by / acronym strip */
.acronym-strip {
    margin-top: 5rem;
    padding-top: 2.5rem;
    border-top: 1px solid #1f1f1f;
    display: flex;
    gap: 3rem;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
}
.acronym-strip .item {
    color: #525252;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-size: 0.9rem;
    letter-spacing: 0.15em;
    font-weight: 500;
    transition: color 0.15s ease;
}
.acronym-strip .item:hover { color: #ededed; }
</style>
"""


def inject_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


HIDE_SIDEBAR_CSS = """
<style>
/* Hide sidebar completely (used on the Home page - the primary CTA
   is the way in). Other pages keep the sidebar visible. */
[data-testid='stSidebar'],
[data-testid='stSidebarCollapseButton'],
[data-testid='collapsedControl'] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    min-width: 0 !important;
}
/* Reclaim the space the sidebar was taking */
[data-testid='stAppViewContainer'] > .main {
    margin-left: 0 !important;
    padding-left: 0 !important;
}
</style>
"""


def hide_sidebar():
    """Hide the Streamlit sidebar on the current page. Call after
    inject_css() from pages that should not show it."""
    st.markdown(HIDE_SIDEBAR_CSS, unsafe_allow_html=True)


def page_setup(title, icon=None):
    """Standard st.set_page_config + CSS injection. Call once per page."""
    st.set_page_config(page_title=title, page_icon=icon, layout="wide",
                       initial_sidebar_state="expanded")
    inject_css()
