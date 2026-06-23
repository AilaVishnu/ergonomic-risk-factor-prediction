"""
Build docs/PROJECT_EXPLAINED.docx — Word-format project guide.

Technical terms are kept intact (RULA, QEC, NASA-TLX, SMOTE, GridSearchCV,
StratifiedKFold, etc.) because they match the codebase and won't change.
Brief inline definitions appear on first use so a non-technical reader
can still follow.

Run with:
    python src/build_project_doc.py
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "docs" / "PROJECT_EXPLAINED.docx"

# Theme colours (subtle, professional)
NAVY        = RGBColor(0x1F, 0x3B, 0x73)
ACCENT      = RGBColor(0x2E, 0x86, 0xAB)
BODY_BLACK  = RGBColor(0x22, 0x22, 0x22)
MUTED       = RGBColor(0x55, 0x55, 0x55)


# ============================================================================
# Helper builders
# ============================================================================

def set_run(run, *, font=None, size=None, bold=None, italic=None, color=None):
    if font  is not None: run.font.name = font
    if size  is not None: run.font.size = Pt(size)
    if bold  is not None: run.bold = bold
    if italic is not None: run.italic = italic
    if color is not None: run.font.color.rgb = color
    if font is not None:
        rPr = run._element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), font)


def add_para(doc, text="", *, style="Normal", size=11, bold=False, italic=False,
             color=BODY_BLACK, align=None, space_after=6, space_before=0):
    p = doc.add_paragraph(style=style) if style != "Normal" else doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if text:
        run = p.add_run(text)
        set_run(run, font="Calibri", size=size, bold=bold, italic=italic, color=color)
    return p


def add_heading(doc, text, level=1):
    """Custom-styled heading (override Word defaults to control colour cleanly)."""
    sizes = {0: 26, 1: 18, 2: 14, 3: 12}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18 if level <= 1 else 12)
    p.paragraph_format.space_after  = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    set_run(run, font="Calibri", size=sizes.get(level, 11), bold=True,
            color=NAVY if level <= 1 else ACCENT)
    return p


def add_runs(doc, parts, *, size=11, space_after=6):
    """Mixed-formatting paragraph. parts is a list of (text, dict-of-format)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    for text, fmt in parts:
        run = p.add_run(text)
        set_run(run, font="Calibri", size=size, **{k: v for k, v in fmt.items()
                                                    if k in {"bold","italic","color"}})
        if fmt.get("code"):
            set_run(run, font="Consolas")
    return p


def add_bullet(doc, parts, *, size=11):
    """A single bulleted item, parts as for add_runs."""
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    for text, fmt in parts:
        run = p.add_run(text)
        set_run(run, font="Calibri", size=size, **{k: v for k, v in fmt.items()
                                                    if k in {"bold","italic","color"}})
        if fmt.get("code"):
            set_run(run, font="Consolas")
    return p


def add_code(doc, code):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(8)
    p.paragraph_format.left_indent  = Cm(0.6)
    run = p.add_run(code)
    set_run(run, font="Consolas", size=10, color=BODY_BLACK)


def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_table(doc, header, rows, *, header_bg="1F3B73", widths_cm=None):
    n_cols = len(header)
    table = doc.add_table(rows=1, cols=n_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    hdr = table.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(h)
        set_run(run, font="Calibri", size=10, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        set_cell_bg(hdr[i], header_bg)

    for row in rows:
        cells = table.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            run = p.add_run(str(txt))
            set_run(run, font="Calibri", size=10, color=BODY_BLACK)

    if widths_cm:
        for row in table.rows:
            for i, w in enumerate(widths_cm):
                row.cells[i].width = Cm(w)
    return table


# ============================================================================
# Content
# ============================================================================

def build():
    doc = Document()

    # Default style
    s = doc.styles["Normal"]
    s.font.name = "Calibri"
    s.font.size = Pt(11)

    # Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.0)
        section.right_margin  = Cm(2.0)

    # ----- Title -----
    add_heading(doc, "Ergonomic Risk Factor Prediction", level=0)
    add_para(doc, "Per-rider risk profiling for food-delivery riders",
             size=14, italic=True, color=MUTED, space_after=4)
    add_para(doc, "A complete project guide", size=11, color=MUTED, space_after=18)

    # ----- 1. Pitch -----
    add_heading(doc, "1. The 30-second pitch", level=1)
    add_para(doc,
        "Food-delivery riders (Blinkit, Zepto, etc.) do physically demanding work that, "
        "over time, can cause musculoskeletal disorders (MSDs) — back pain, shoulder pain, "
        "wrist injuries, and so on. This project builds a tool that takes a rider profile "
        "(demographics, work pattern, vehicle, carrying mode, NMQ pain self-report, "
        "NASA-TLX workload, Borg CR10 fatigue, and RULA + QEC ergonomic observations) "
        "and predicts six ergonomic risk factors — Force, Repetition, Posture, Duration, "
        "Contact Stress, Vibration — each as Low / Medium / High.")
    add_para(doc,
        "The end product is a Streamlit web app that accepts the full 36-question survey "
        "plus the 11 RULA components and 8 QEC scores, runs six trained scikit-learn / "
        "XGBoost / imbalanced-learn classifiers, and returns colour-coded per-factor risk "
        "levels in real time.")

    # ----- 2. Problem -----
    add_heading(doc, "2. The problem we set out to solve", level=1)
    add_para(doc,
        "Established ergonomic assessment methods exist — RULA (Rapid Upper Limb "
        "Assessment), QEC (Quick Exposure Check), Nordic Musculoskeletal Questionnaire "
        "(NMQ), NASA-TLX, Borg CR10 — but each produces a different score and each "
        "requires an expert to interpret. No single, unified, automated tool produced a "
        "per-rider multi-factor risk profile that a delivery platform could act on "
        "operationally.")
    add_para(doc,
        "We built that pipeline end-to-end: from raw CSV + XLSX inputs, through Stage-1 "
        "deterministic risk scoring, to Stage-2 supervised classification, to an "
        "interactive demo and a presentation-ready deck.")

    # ----- 3. What we built -----
    add_heading(doc, "3. What we actually built", level=1)
    add_heading(doc, "a) A reproducible data-analysis pipeline", level=2)
    add_para(doc,
        "Seven Jupyter notebooks (notebooks/01_data_cleaning.ipynb through "
        "07_evaluation.ipynb) that run in order and produce every figure, table, and "
        "saved model.")
    add_heading(doc, "b) Six trained classifiers", level=2)
    add_para(doc,
        "One scikit-learn / XGBoost / imbalanced-learn model per risk factor, saved as "
        "joblib pickles at outputs/models/best_<factor>.pkl. The Posture model is "
        "trained on the full 44 survey features plus 11 RULA components and 8 QEC scores "
        "(63 features total); the other 5 are trained on 41–42 survey features only.")
    add_heading(doc, "c) The Streamlit web application", level=2)
    add_para(doc,
        "app/streamlit_app.py — a six-section form that mirrors the entire 36-question "
        "questionnaire plus the RULA + QEC observation worksheets. The encode_rider() "
        "function converts form answers into the feature vector each model expects, and "
        "predict_risks() returns the Low/Medium/High level per factor.")
    add_heading(doc, "d) Mentor-facing outputs", level=2)
    add_bullet(doc, [("WITH_RESULTS.pptx — 53-slide deck with Phase 4–7 figures and text slides", {})])
    add_bullet(doc, [("docs/results.md — full mentor write-up with all numbers and benchmarks", {})])
    add_bullet(doc, [("docs/PROJECT_EXPLAINED.md / .docx — this complete guide", {})])

    # ----- 4. The 6 risk factors -----
    add_heading(doc, "4. The six ergonomic risk factors", level=1)
    add_para(doc, "Each factor is scored from standard ergonomic thresholds:")

    add_heading(doc, "Force", level=2)
    add_para(doc,
        "Lifting / carrying exertion derived from the Borg CR10 'lifting' item. "
        "Standard Borg action levels: 0–3 = Low (acceptable), 4–6 = Medium (monitor), "
        "7–10 = High (intervene).")

    add_heading(doc, "Repetition", level=2)
    add_para(doc,
        "Deliveries per hour = deliveries_num / work_hours_num. After a Phase 3 binning "
        "fix (see §9), the cut-offs are fixed at: ≤2.5 = Low, 2.5–3.75 = Medium, "
        "≥3.75 = High.")

    add_heading(doc, "Posture", level=2)
    add_para(doc,
        "RULA Table C score. Standard RULA action levels: 1–2 = Low (acceptable), "
        "3–4 = Medium (investigate), 5+ = High (change immediately).")

    add_heading(doc, "Duration", level=2)
    add_para(doc,
        "Continuous riding hours. ≤5 hrs = Low, 6–7 hrs = Medium, >7 hrs = High.")

    add_heading(doc, "Contact Stress", level=2)
    add_para(doc,
        "Composite of carrying_contact_rank × work_hours_num × (1 + 0.1 × age_ord). "
        "Binned by sample tercile into Low / Medium / High.")

    add_heading(doc, "Vibration", level=2)
    add_para(doc,
        "vibration_index = vehicle_rank × work_hours_num (scooter = 1, motor bike = 2). "
        "Binned by sample tercile. A proxy because we did not have ISO-2631 accelerometer "
        "data per rider.")

    # ----- 5. Data sources -----
    add_heading(doc, "5. Data sources", level=1)
    add_heading(doc, "delivery_rider_survey.csv (182 riders, 48 columns)", level=2)
    add_bullet(doc, [("Q1–17: Demographic, lifestyle, work pattern (Gender, Age, Education, Region, "
                      "Marital status, Delivery platform, Job duration, Monthly income, Type of "
                      "vehicle, Mode of carrying deliveries, Working hours/day, Working days/week, "
                      "Deliveries/day, Rest break, Type of break, Tobacco, Alcohol)", {})])
    add_bullet(doc, [("Q18: Nordic Musculoskeletal Questionnaire — 12-month pain in 9 body areas "
                      "(neck, shoulders, upper back, lower back, elbows, wrists/hands, "
                      "hips/thighs, knees, ankles/feet)", {})])
    add_bullet(doc, [("Q19: 7-day discomfort in 4 areas", {})])
    add_bullet(doc, [("Q20–24: Discomfort follow-ups (reduced performance, taken leave, consulted "
                      "doctor, riding worsens, carrying worsens)", {})])
    add_bullet(doc, [("Q25–30: NASA-TLX workload (mental demand, physical demand, time pressure, "
                      "satisfaction, effort, frustration; 0–100 each)", {})])
    add_bullet(doc, [("Q31–36: Borg CR10 fatigue (overall, legs, breathing, lifting, traffic, "
                      "exhaustion; 0–10 each)", {})])

    add_heading(doc, "posture_data.xlsx (182 observations, 26 columns per sheet)", level=2)
    add_bullet(doc, [("11 RULA components: upper_arm, lower_arm, wrist, wrist_twist, "
                      "neck_position, trunk_position, legs, muscle_a, force_a, muscle_b, force_b", {})])
    add_bullet(doc, [("3 derived RULA scores: rula_table_a, rula_table_b, rula_table_c "
                      "(excluded from features as direct leakage on posture_risk)", {})])
    add_bullet(doc, [("8 QEC scores: qec_back, qec_shoulder_arm, qec_wrist_hand, qec_neck, "
                      "qec_driving, qec_vibration, qec_work_pace, qec_stress", {})])
    add_para(doc,
        "The observations did not carry a rider identifier. Pairing to the survey was done "
        "via a severity-rank merge in Phase 2, Step 8 (see §9 Limitations).",
        italic=True, color=MUTED)

    # ----- 6. The 9-phase journey -----
    add_heading(doc, "6. The nine-phase journey", level=1)

    phases = [
        ("Phase 1 — Data Cleaning",        "notebooks/01_data_cleaning.ipynb",
         "Strips empty rows, normalises column names, standardises Yes/No, validates 182 "
         "rows × 48 columns. Output: data/processed/cleaned.csv."),
        ("Phase 2 — Feature Engineering",  "notebooks/02_feature_engineering.ipynb",
         "Ordinal-encodes binned categoricals (age_ord, income_ord, etc.), assigns "
         "numeric midpoints (work_hours_num, deliveries_num, etc.), binarises Yes/No "
         "items, ranks vehicle and carrying mode, derives composite scores "
         "(workload_score, fatigue_score, force_exertion, vibration_index), creates 5 "
         "interaction features, encodes 7 additional demographic categoricals "
         "(gender_rank, region_rank, marital_rank, platform_rank, break_type_rank, "
         "tobacco_ord, alcohol_ord), aliases 18 binary survey items with short names "
         "(nmq_*, d7_*, out_*), and merges the posture_data.xlsx via severity rank. "
         "Output: data/processed/model_ready.csv (121 columns)."),
        ("Phase 3 — Risk Scoring",          "notebooks/03_risk_scoring.ipynb",
         "Applies the standard thresholds in §4 to compute force_risk, repetition_risk, "
         "duration_risk, vibration_risk, contact_stress_risk, posture_risk and their "
         "integer-coded versions. Output: data/processed/risk_profile.csv."),
        ("Phase 4 — Exploratory Data Analysis",  "notebooks/04_eda.ipynb",
         "Produces demographics.png, nordic_prevalence.png, risk_factor_distribution.png, "
         "discomfort_by_demographic.png, risk_vs_discomfort.png, correlation_heatmap.png. "
         "All saved to outputs/figures/."),
        ("Phase 5 — Statistics",                  "notebooks/05_stats.ipynb",
         "Chi-square (factor × discomfort) and logistic-regression OR / 95% CI / p across "
         "10+ predictors. Output: outputs/tables/chi_square.csv, phase5_summary.csv."),
        ("Phase 6 — ML Modelling",                "notebooks/06_modeling.ipynb",
         "For each target, runs 7 algorithms (LogisticRegression, DecisionTree, "
         "RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, StackingClassifier) "
         "inside an imbalanced-learn Pipeline with SMOTE oversampling, tuned via "
         "GridSearchCV under StratifiedKFold(5). Posture target gets the survey "
         "feature_pool plus 11 RULA components plus 8 QEC scores (63 features); other "
         "targets get 41–42 survey features. Output: 6 joblib pickles in outputs/models/ "
         "and result tables in outputs/tables/ (cv_results.csv, best_models.csv, "
         "phase6_summary.csv, classification_reports.csv, confusion_matrices.csv)."),
        ("Phase 7 — Evaluation",                  "notebooks/07_evaluation.ipynb",
         "Re-uses the best-by-F1 model per target, computes cross_val_predict, generates "
         "confusion matrices and ROC curves per factor, extracts feature_importances_ "
         "(or coef_) per model. Output: confusion_matrices.png, roc_curves.png, "
         "feature_importance.png + roc_auc.csv, feature_importance.csv, "
         "phase7_summary.csv."),
        ("Phase 8 — Results Write-up",            "docs/results.md",
         "Mentor-facing markdown with the sample profile, NMQ prevalence, per-factor "
         "Stage-1 distribution, Stage-2 ML metrics with macro AUC, per-factor "
         "positioning notes, recommendations, and limitations."),
        ("Phase 9 — Slide Deck",                  "src/build_results_deck.py",
         "Loads the original Final.pptx, appends a Results & Findings section "
         "(section header, demographics, NMQ prevalence, risk distribution, discomfort "
         "by demographic, risk vs. discomfort, correlation heatmap, ML metrics text "
         "slide, confusion matrices, ROC curves, feature importance, benchmarks text, "
         "limitations text, recommendations text), moves the Thank You slide to the end, "
         "saves WITH_RESULTS.pptx (53 slides)."),
    ]
    for name, path, body in phases:
        add_heading(doc, name, level=2)
        add_runs(doc, [(path, {"code": True, "color": MUTED}), ("", {})], size=10)
        add_para(doc, body, size=11)

    # ----- 7. Headline findings -----
    add_heading(doc, "7. Headline findings", level=1)

    add_heading(doc, "Sample profile", level=2)
    add_bullet(doc, [("n = 182 riders; 152 Male / 30 Female", {})])
    add_bullet(doc, [("Age: 78 under 25, 66 in 25–35, 30 in 36–45, 8 in ≥46", {})])
    add_bullet(doc, [("Platforms: Blinkit 97, Zepto 80, Both 5", {})])
    add_bullet(doc, [("Vehicles: Scooter 94, Motor bike 88", {})])
    add_bullet(doc, [("49% work >8 hours/day", {})])

    add_heading(doc, "NMQ 12-month pain prevalence (top 4)", level=2)
    add_bullet(doc, [("Lower back: 61.5%", {})])
    add_bullet(doc, [("Upper back: 49.5%", {})])
    add_bullet(doc, [("Shoulders: 46.7%", {})])
    add_bullet(doc, [("Wrists / Hands: 45.1%", {})])
    add_para(doc, "Overall: 84.6% of riders reported pain in at least one body area in the last 12 months.")

    add_heading(doc, "Stage-1 risk distribution", level=2)
    add_table(doc,
              header=["Factor", "Low", "Medium", "High"],
              rows=[
                  ["Force",          "90", "57", "35"],
                  ["Repetition",     "26", "82", "74"],
                  ["Duration",       "37", "56", "89"],
                  ["Vibration",      "67", "68", "47"],
                  ["Contact Stress", "68", "58", "56"],
                  ["Posture",        "0",  "29", "153"],
              ],
              widths_cm=[5.0, 2.4, 2.4, 2.4])

    add_heading(doc, "Stage-2 ML metrics (best model per factor, 5-fold CV)", level=2)
    add_table(doc,
              header=["Factor", "Best model", "CV accuracy", "CV F1 macro", "Macro AUC", "Features"],
              rows=[
                  ["Force",          "HistGradientBoosting", "62%", "57%", "71%", "42"],
                  ["Repetition",     "RandomForest",         "62%", "57%", "73%", "41"],
                  ["Duration",       "RandomForest",         "61%", "58%", "76%", "42"],
                  ["Vibration",      "ExtraTrees",           "58%", "57%", "72%", "41"],
                  ["Contact Stress", "RandomForest",         "60%", "59%", "74%", "42"],
                  ["Posture",        "HistGradientBoosting", "97%", "95%", "98%", "63"],
              ],
              widths_cm=[3.2, 4.0, 2.4, 2.4, 2.2, 2.0])

    add_heading(doc, "Statistical predictors of discomfort (logistic regression)", level=2)
    add_bullet(doc, [("Age — OR 3.58, 95% CI 1.70–7.56, p = 0.0008 (strongest individual effect)", {})])
    add_bullet(doc, [("Job duration — OR 2.89, p = 0.001", {})])
    add_bullet(doc, [("Education — OR 0.33, p = 0.04 (protective)", {})])
    add_bullet(doc, [("Income — OR 2.00, p = 0.004", {})])
    add_bullet(doc, [("Fatigue score — OR 1.43, p = 0.003", {})])
    add_bullet(doc, [("Workload score — OR 1.06 per point, p = 0.0005", {})])
    add_bullet(doc, [("Deliveries per day — OR 1.05, p = 0.045", {})])

    # ----- 8. Web app -----
    add_heading(doc, "8. The Streamlit web application", level=1)
    add_para(doc, "Start with:")
    add_code(doc, "streamlit run app/streamlit_app.py")
    add_para(doc, "Form layout (six sections, single page):")
    add_bullet(doc, [("Section 1 — Demographic (Q1–17): 17 selectboxes", {})])
    add_bullet(doc, [("Section 2 — NMQ + 7-day + outcomes (Q18–24): 18 Yes/No radios", {})])
    add_bullet(doc, [("Section 3 — NASA-TLX workload (Q25–30): 6 sliders, 0–100. Q28 phrased as "
                      "'DISSATISFIED' so all 6 sliders point in load-direction.", {})])
    add_bullet(doc, [("Section 4 — Borg CR10 fatigue (Q31–36): 6 sliders, 0–10", {})])
    add_bullet(doc, [("Section 5 — RULA observation: 11 selectboxes with help text per item", {})])
    add_bullet(doc, [("Section 6 — Quick Exposure Check (QEC): 8 number_input fields with "
                      "min/max matched to training-data ranges", {})])
    add_para(doc,
        "encode_rider() converts form values into 63 features (44 survey + 5 interactions "
        "+ 11 RULA + 8 QEC; specific feature subset selected per model from the saved "
        "bundle). predict_risks() loops over the 6 joblib bundles and returns "
        "{factor: 'Low'/'Medium'/'High'}. Output rendering: coloured badge table, "
        "summary banner, expandable feature-value JSON.")

    add_heading(doc, "Command-line equivalent", level=2)
    add_code(doc, "python src/predict.py --json data/example_rider.json")
    add_para(doc,
        "predict.py is generic — it reads bundle['features'] from each saved .pkl and "
        "indexes the input dict by those keys. Adding new features requires no change "
        "to predict.py.")

    # ----- 9. Limitations -----
    add_heading(doc, "9. Limitations (disclosed openly)", level=1)

    add_heading(doc, "1. Self-report bias", level=2)
    add_para(doc,
        "Discomfort, NMQ pain, NASA-TLX workload, and Borg CR10 fatigue are all "
        "self-reported. A rider in low mood may report more pain regardless of objective "
        "exposure, and vice versa.")

    add_heading(doc, "2. Posture per-rider linkage is approximate", level=2)
    add_para(doc,
        "The 182 RULA + QEC observation records did not carry a rider identifier. Phase 2 "
        "Step 8 ranks riders by an exposure-severity score (NMQ count + fatigue_score + "
        "work_hours_num, each normalised) and ranks posture observations by rula_table_c, "
        "then merges rank-to-rank. The Posture model's 97% / AUC 98% is therefore the "
        "upper bound the linked data permits; an individually-observed cohort would "
        "likely score slightly lower because rider-to-observation noise would re-enter.")

    add_heading(doc, "3. Repetition binning was identified and corrected", level=2)
    add_para(doc,
        "Phase 3 originally binned Repetition via pd.qcut(q=3) on deliveries_per_hour. "
        "The Medium/High tercile edge landed exactly on 3.889 dph (= 35 / 9), and 55 of "
        "182 riders tied at that value. pd.qcut is right-inclusive, so all 55 fell into "
        "Medium, and the Stage-2 ML model could never predict High for a max-input rider. "
        "Fix: pd.cut with fixed bins [-0.01, 2.5, 3.75, max+0.01]. Stage-1 High count "
        "rose from 19 to 74; Stage-2 accuracy fell from 74% to 62%. The lower number is "
        "more honest because the model is now solving a real 3-class problem.")

    add_heading(doc, "4. Duration leakage was identified and corrected", level=2)
    add_para(doc,
        "An earlier Phase 6 run reported 100% CV accuracy for Duration. Even with "
        "work_hours_num excluded, the trees recovered the label from vibration_index "
        "(= vehicle_rank × work_hours_num). Fix: added vibration_index to the Duration "
        "exclusion list and capped max_depth + min_samples_leaf. Duration settled at a "
        "realistic 61% / AUC 76%.")

    add_heading(doc, "5. Cross-sectional design", level=2)
    add_para(doc,
        "No causal inference is possible. Older riders report more pain, but we cannot "
        "tell whether long delivery careers cause MSDs or whether riders with MSDs "
        "self-select out at younger ages.")

    add_heading(doc, "6. Sample size and geography", level=2)
    add_para(doc,
        "n = 182 is reasonable for descriptive epidemiology but small for multivariable "
        "ML; CV variance is ~5 percentage points. All riders were drawn from a single "
        "regional platform deployment, so findings may not generalise.")

    add_heading(doc, "7. Proxies for Vibration and Repetition", level=2)
    add_para(doc,
        "Without per-shift ISO-2631 accelerometer data, Vibration is approximated as "
        "vehicle_rank × work_hours_num. Without per-task timing, Repetition is "
        "approximated as deliveries-per-hour. Both proxies map directly onto the survey "
        "the riders filled in, but they do not capture the per-event signal a wearable "
        "would produce.")

    add_heading(doc, "8. No follow-up", level=2)
    add_para(doc,
        "A longitudinal design would let us test whether riders flagged as High today "
        "develop more pain over time. This study is cross-sectional only.")

    # ----- 10. FAQ -----
    add_heading(doc, "10. Frequently asked questions", level=1)

    faq = [
        ("Why is Posture 97% accurate when the others are 58–62%?",
         "Posture is the only model that receives direct ergonomic observation inputs — "
         "the 11 RULA components and 8 QEC scores. The other 5 models have survey "
         "features only, and each one excludes the variable that defines its own target "
         "(force_exertion for Force, deliveries_num + work_hours_num for Repetition, "
         "etc.) to prevent trivial leakage. Predicting a deterministic label from "
         "survey proxies is structurally harder than fitting a near-deterministic RULA "
         "lookup table."),
        ("Is 58–62% accuracy acceptable?",
         "It is the realistic ceiling once each factor's defining input is excluded "
         "to prevent leakage. Macro AUC at 71–76% confirms the models still rank "
         "riders correctly even when they don't always assign the exact class. A "
         "sensor-instrumented pipeline (IMU, EMG, wearable) would do better but is "
         "out of scope here."),
        ("Could a delivery platform actually deploy this?",
         "Yes — as a screening tool. Each rider fills the survey at onboarding and "
         "annually; the 5 survey-derived risk factors run automatically. Posture "
         "requires an ergonomic-trained observer to complete the RULA + QEC worksheets, "
         "which is a per-rider cost the platform decides whether to pay."),
        ("What if a rider lies on the survey?",
         "Self-report is biased by definition. The model cannot detect dishonesty. "
         "This is acknowledged in Limitation #1."),
        ("Why so many features for Posture (63) and so few for the rest (41–42)?",
         "The survey feature_pool is 44 features. For Force, Repetition, Duration, "
         "Vibration, Contact Stress we drop 2–3 features that directly define the "
         "target (anti-leakage). Posture additionally takes the 11 RULA components and "
         "8 QEC scores from the xlsx, giving 63."),
        ("Is the pipeline reproducible?",
         "Yes — fixed random seed (RNG = 42), StratifiedKFold(5, shuffle=True, "
         "random_state=42), GridSearchCV with refit=False then explicit refit. Running "
         "the 7 notebooks in order regenerates every saved artefact identically."),
    ]
    for q, a in faq:
        add_heading(doc, "Q. " + q, level=2)
        add_para(doc, "A. " + a)

    # ----- 11. Glossary -----
    add_heading(doc, "11. Glossary", level=1)
    add_para(doc,
        "Every technical term used in this project, listed alphabetically.",
        italic=True, color=MUTED)

    glossary = [
        ("AUC", "Area Under the ROC Curve. 0.5 = no skill, 1.0 = perfect ranking. "
                "Reported as macro-averaged across classes."),
        ("Borg CR10", "Standard 0–10 category-ratio scale for perceived exertion. "
                      "Action levels: 0–3 = acceptable, 4–6 = monitor, 7–10 = intervene."),
        ("Classifier", "Supervised model that predicts a categorical label."),
        ("Confusion matrix", "n × n table where row i = true class i, col j = predicted "
                             "class j. Diagonal cells are correct predictions."),
        ("cross_val_predict", "scikit-learn function that returns out-of-fold predictions "
                              "for every row — used in Phase 7 to compute honest "
                              "confusion matrices."),
        ("Cross-validation (5-fold)", "Partition the data into 5 stratified folds; train "
                                       "on 4 and score on the 5th; repeat 5 times; report "
                                       "mean and std of scores."),
        ("CV accuracy", "Mean test-fold accuracy across 5 CV folds."),
        ("CV F1 macro", "Mean test-fold macro-averaged F1 across 5 CV folds."),
        ("Decision Tree", "Recursive binary partitioning learner. Highly interpretable, "
                          "tends to overfit on small samples."),
        ("Discomfort", "Binary target = 1 if any of the 9 NMQ 12-month items = Yes, "
                       "else 0. Outcome variable for Phase 5 statistics."),
        ("ExtraTrees / ExtraTreesClassifier", "Extremely randomised trees ensemble. Like "
                                              "Random Forest but uses random split "
                                              "thresholds, reducing variance further."),
        ("Feature importance", "Tree-based: mean decrease in impurity per feature. "
                               "Linear: absolute coefficient magnitude."),
        ("Feature pool", "The full list of candidate features available to a target. "
                         "Per-target exclusions remove inputs that define the target "
                         "(anti-leakage)."),
        ("GridSearchCV", "scikit-learn hyperparameter sweep. We use scoring='f1_macro', "
                         "cv=StratifiedKFold(5), refit=False."),
        ("HistGradientBoosting / HistGradientBoostingClassifier", "Histogram-binned "
                                                                   "gradient boosting. "
                                                                   "Fast on tabular data, "
                                                                   "robust to small samples."),
        ("imbalanced-learn (imblearn)", "Library that ships SMOTE and the ImbPipeline "
                                        "wrapper allowing oversampling inside CV folds."),
        ("Interaction feature", "Engineered feature = product of two base features. "
                                "We use workload_x_fatigue, workload_x_age, force_x_age, "
                                "fatigue_x_jobdur, deliv_x_days."),
        ("Jupyter notebook", "Document combining executable Python cells, markdown, and "
                             "rendered output. .ipynb extension."),
        ("Leakage", "Model accidentally sees the target in its input. Symptom: implausibly "
                    "high CV accuracy. Two leakage paths were identified and fixed in this "
                    "project (Duration via vibration_index, Repetition via qcut boundary)."),
        ("LogisticRegression", "Linear model fitting log-odds of class membership. We use "
                               "class_weight='balanced', max_iter=2000."),
        ("Macro AUC", "Class-balanced average of one-vs-rest ROC-AUC. Reported in "
                      "phase7_summary.csv."),
        ("MSD", "Musculoskeletal Disorder. Soft-tissue, joint, nerve injuries."),
        ("NASA-TLX", "NASA Task Load Index. Six 0–100 sub-scales (mental, physical, "
                     "temporal, performance, effort, frustration). The performance "
                     "item is reversed before averaging into workload_score."),
        ("NMQ", "Nordic Musculoskeletal Questionnaire. 9-area 12-month pain self-"
                "report plus 4-area 7-day discomfort."),
        ("Odds ratio (OR)", "Multiplicative effect on the odds of the outcome per "
                            "one-unit increase in the predictor. Reported with 95% CI."),
        ("Overfit gap", "train_accuracy − test_accuracy in CV. > 0.15 flags concern."),
        ("p-value", "Probability of observing the data (or more extreme) under the null. "
                    "We use p < 0.05 as significant."),
        ("Pipeline (sklearn / imblearn)", "Sequential composition of transformers + a "
                                          "final estimator. Our pipeline is "
                                          "[('smote', SMOTE), ('clf', model)]."),
        ("QEC", "Quick Exposure Check. Observer-scored composite of 8 body-region "
                "and exposure dimensions."),
        ("Random Forest", "Bagging ensemble of decision trees with random feature "
                          "subsetting."),
        ("Risk profile", "Per-rider 6-tuple of Low/Medium/High labels across the 6 "
                         "risk factors. Stored in data/processed/risk_profile.csv."),
        ("ROC curve", "Receiver Operating Characteristic. Plots true positive rate vs. "
                      "false positive rate across decision thresholds."),
        ("RULA", "Rapid Upper Limb Assessment. Observer-scored across 11 components, "
                 "combined via Tables A → B → C into an action-level score 1–7."),
        ("SMOTE", "Synthetic Minority Over-sampling Technique. Creates synthetic "
                  "minority-class examples in feature space to balance training folds."),
        ("Severity-rank merge", "Phase 2 Step 8 procedure to pair survey rows with "
                                "anonymous posture observations: rank survey rows by "
                                "exposure-severity (NMQ count + fatigue + hours), rank "
                                "observations by rula_table_c, merge rank-to-rank."),
        ("Stacking / StackingClassifier", "Meta-ensemble that learns a final estimator on "
                                          "top of base learners. We stack RandomForest, "
                                          "ExtraTrees, XGBoost, HistGBM with a "
                                          "LogisticRegression meta-learner."),
        ("Stage 1", "Deterministic risk-factor labelling using standard ergonomic "
                    "thresholds (Phase 3)."),
        ("Stage 2", "Supervised ML that learns the Stage-1 labels from rider features "
                    "(Phases 6 & 7)."),
        ("StratifiedKFold", "Cross-validation split that preserves class proportions per "
                            "fold. RNG = 42 throughout."),
        ("Tercile", "Empirical 33.3 / 66.7 percentile cut. Used by pd.qcut(q=3). The "
                    "Repetition qcut boundary fault that motivated the Phase 3 fix sits "
                    "at the 66.7th percentile of deliveries_per_hour = 3.889."),
        ("XGBoost / XGBClassifier", "Gradient-boosted trees. We use eval_metric='mlogloss', "
                                    "tuned over n_estimators, max_depth, learning_rate."),
        ("workload_score", "Mean of the 6 NASA-TLX items, with the performance / "
                           "dissatisfaction item already in load direction (0 = no load, "
                           "100 = maximum load)."),
        ("fatigue_score", "Mean of the 6 Borg CR10 items."),
    ]
    for term, defn in glossary:
        add_runs(doc, [(term, {"bold": True, "color": NAVY}), ("  —  ", {"color": MUTED}),
                        (defn, {})], space_after=4)

    # ----- 12. Repo map -----
    add_heading(doc, "12. Repository layout", level=1)
    add_code(doc,
"""Ergonomic_Project/
├── README.md
├── docs/
│   ├── PROJECT_EXPLAINED.md / .docx   <- this guide
│   ├── results.md                     <- mentor write-up
│   └── development_plan.md
├── data/
│   ├── raw/                           <- delivery_rider_survey.csv, posture_data.xlsx
│   ├── processed/                     <- cleaned.csv, model_ready.csv, risk_profile.csv
│   └── example_rider.json
├── notebooks/                         <- 01..07 (the 7 phases)
├── src/
│   ├── predict.py
│   ├── build_results_deck.py
│   ├── build_project_doc.py           <- builds this Word doc
│   └── finalize_deck.py
├── app/streamlit_app.py
├── deck/
│   ├── ...Final.pptx
│   └── ...WITH_RESULTS.pptx
└── outputs/
    ├── figures/   <- all PNGs
    ├── tables/    <- all CSV result tables
    └── models/    <- 6 joblib bundles""")

    # ----- Footer -----
    add_para(doc, "")
    add_para(doc, "End of document.", italic=True, color=MUTED,
             align=WD_ALIGN_PARAGRAPH.CENTER)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"saved {path.relative_to(ROOT)}")
