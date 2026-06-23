"""
Web demo for the 6 ergonomic risk-factor models.

Run with:
    streamlit run app/streamlit_app.py

User fills in a rider's survey answers (Age, Vehicle, Hours, Borg, NASA-TLX,
etc.); the app encodes them to the 19 engineered features and runs the six
Phase 6 best-models, then shows Low/Medium/High per factor with colour coding.
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


@st.cache_resource
def load_models():
    return {f: joblib.load(MODELS / f"best_{f}.pkl") for f in FACTORS}


def encode_rider(raw):
    """Raw survey answers -> the 19 engineered features the models expect."""
    nasa = raw["nasa"]
    borg = raw["borg"]

    # Composite scores
    workload_score = round((nasa["mental"] + nasa["physical"] + nasa["time_pressure"]
                            + (100 - nasa["satisfied"])
                            + nasa["effort"] + nasa["frustration"]) / 6, 1)
    fatigue_score  = round((borg["overall"] + borg["legs"] + borg["breathing"]
                            + borg["lifting"] + borg["traffic"] + borg["exhaustion"]) / 6, 2)
    force_exertion = borg["lifting"]

    # Ordinal / midpoint / rank
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

    # Interactions
    return {
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
    }


def predict_risks(features, models):
    df_row = pd.DataFrame([features])
    out = {}
    for factor in FACTORS:
        bundle = models[factor]
        pred_idx = int(bundle["model"].predict(df_row[bundle["features"]])[0])
        code = int(bundle["classes"][pred_idx])
        out[factor] = LABELS[code]
    return out


# --- Streamlit page ---

st.set_page_config(page_title="Ergonomic Risk Predictor", page_icon="🛵", layout="wide")
st.title("🛵 Ergonomic Risk Predictor — Food-Delivery Riders")
st.caption("Enter a rider's survey answers; the app runs the six Phase 6 models and "
           "returns the Low / Medium / High level for each ergonomic risk factor.")

models = load_models()

with st.form("rider_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Demographics & job")
        age           = st.selectbox("Age", list(AGE_MAP.keys()), index=1)
        education     = st.selectbox("Education", list(EDUCATION_MAP.keys()), index=2)
        income        = st.selectbox("Monthly income (INR)", list(INCOME_MAP.keys()), index=2)
        job_duration  = st.selectbox("Job duration", list(JOB_DURATION_MAP.keys()), index=2)

        st.subheader("Work pattern")
        work_hours = st.selectbox("Working hours per day", list(WORK_HOURS_MAP.keys()), index=2)
        work_days  = st.selectbox("Working days per week", list(WORK_DAYS_MAP.keys()), index=2)
        deliveries = st.selectbox("Deliveries per day", list(DELIVERIES_MAP.keys()), index=2)
        rest_break = st.selectbox("Rest-break duration", list(REST_BREAK_MAP.keys()), index=1)

        st.subheader("Vehicle & carrying")
        vehicle  = st.selectbox("Vehicle type", list(VEHICLE_MAP.keys()), index=1)
        carrying = st.selectbox("Carrying mode", list(CARRYING_MAP.keys()), index=1)

    with col2:
        st.subheader("NASA-TLX workload   (0 = Low, 100 = High)")
        nasa = {
            "mental":        st.slider("Mental demand",                0, 100, 50, 25),
            "physical":      st.slider("Physical demand",              0, 100, 50, 25),
            "time_pressure": st.slider("Time pressure (rushed)",       0, 100, 50, 25),
            "satisfied":     st.slider("Satisfaction with performance", 0, 100, 75, 25,
                                       help="Higher = better. Reversed inside the workload score."),
            "effort":        st.slider("Effort",                       0, 100, 75, 25),
            "frustration":   st.slider("Frustration / stress",         0, 100, 50, 25),
        }

        st.subheader("Borg CR10 fatigue   (0 = Extremely Easy, 10 = Extremely Hard)")
        borg = {
            "overall":    st.slider("Overall work effort",             0, 10, 4),
            "legs":       st.slider("Legs tired",                      0, 10, 4),
            "breathing":  st.slider("Breathing effort",                0, 10, 3),
            "lifting":    st.slider("Lifting / carrying parcels",      0, 10, 4),
            "traffic":    st.slider("Traffic / weather stress",        0, 10, 5),
            "exhaustion": st.slider("Exhaustion at shift end",         0, 10, 5),
        }

    submitted = st.form_submit_button("Predict risk levels", use_container_width=True)


if submitted:
    raw = dict(
        age=age, income=income, education=education, job_duration=job_duration,
        work_hours=work_hours, work_days=work_days, deliveries=deliveries,
        rest_break=rest_break, vehicle=vehicle, carrying=carrying,
        nasa=nasa, borg=borg,
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

    with st.expander("Show the 19 engineered feature values fed to the models"):
        st.json(features)
