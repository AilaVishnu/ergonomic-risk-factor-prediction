"""
Build docs/PROJECT_EXPLAINED.docx - the Word write-up of the project.

Run:
    python src/build_project_doc.py
"""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT  = ROOT / "docs" / "PROJECT_EXPLAINED.docx"

NAVY   = RGBColor(0x1F, 0x3B, 0x73)
ACCENT = RGBColor(0x2E, 0x86, 0xAB)
BLACK  = RGBColor(0x22, 0x22, 0x22)
MUTED  = RGBColor(0x55, 0x55, 0x55)


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


def para(doc, text="", *, size=11, bold=False, italic=False, color=BLACK,
         align=None, space_after=8, space_before=0):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after  = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if text:
        r = p.add_run(text)
        set_run(r, font="Calibri", size=size, bold=bold, italic=italic, color=color)
    return p


def heading(doc, text, level=1):
    sizes = {0: 24, 1: 16, 2: 13}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16 if level <= 1 else 10)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run(r, font="Calibri", size=sizes.get(level, 11), bold=True,
            color=NAVY if level <= 1 else ACCENT)
    return p


def bullet(doc, text, *, size=11):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    set_run(r, font="Calibri", size=size, color=BLACK)
    return p


def code(doc, txt):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(8)
    p.paragraph_format.left_indent  = Cm(0.6)
    r = p.add_run(txt)
    set_run(r, font="Consolas", size=10, color=BLACK)


def set_cell_bg(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def table(doc, header, rows, widths_cm=None, header_bg="1F3B73"):
    n = len(header)
    t = doc.add_table(rows=1, cols=n)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    hdr = t.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        set_run(r, font="Calibri", size=10, bold=True,
                color=RGBColor(0xFF, 0xFF, 0xFF))
        set_cell_bg(hdr[i], header_bg)
    for row in rows:
        cells = t.add_row().cells
        for i, txt in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(txt))
            set_run(r, font="Calibri", size=10, color=BLACK)
    if widths_cm:
        for row in t.rows:
            for i, w in enumerate(widths_cm):
                row.cells[i].width = Cm(w)
    return t


# ---------------------------------------------------------------------------

def build():
    doc = Document()
    s = doc.styles["Normal"]
    s.font.name = "Calibri"
    s.font.size = Pt(11)
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Cm(2.0)
        section.left_margin = section.right_margin = Cm(2.0)

    # Title
    heading(doc, "Ergonomic Risk Factor Prediction", level=0)
    para(doc, "Per-rider risk profiling for food-delivery riders",
         italic=True, color=MUTED, space_after=18)

    # ----- Background -----
    heading(doc, "Background")
    para(doc,
        "Food-delivery riders for platforms like Blinkit and Zepto spend long hours "
        "on bikes, climb stairs, carry packages, and ride in heavy traffic. Over "
        "time this kind of work causes musculoskeletal disorders (MSDs): back pain, "
        "shoulder pain, wrist injuries, knee problems. The risk is not the same for "
        "every rider. Someone who is 22 and works 4 hours a day on a scooter is in a "
        "very different situation from a 45-year-old who works 10 hours a day on a "
        "motorbike with a handheld bag.")
    para(doc,
        "Ergonomists have standard ways of measuring this kind of strain: RULA "
        "(Rapid Upper Limb Assessment) scores the posture of a worker's upper body; "
        "QEC (Quick Exposure Check) gives a composite of body-region and exposure "
        "scores; the Nordic Musculoskeletal Questionnaire (NMQ) records pain across "
        "9 body areas; NASA-TLX rates the mental workload of a task; Borg CR10 "
        "records perceived physical effort on a 0 to 10 scale. Each of these gives "
        "useful information on its own. The project takes all of them together and "
        "produces a single per-rider risk profile across six ergonomic dimensions: "
        "Force, Repetition, Posture, Duration, Contact Stress, Vibration.")

    # ----- What the project does -----
    heading(doc, "What the project does")
    para(doc,
        "We collected survey responses from 182 riders along with 182 RULA and QEC "
        "observation records. The pipeline cleans this data, applies standard "
        "ergonomic thresholds to compute Low / Medium / High labels for each of the "
        "six risk factors, then trains a separate classifier per factor so a new "
        "rider's profile can be screened automatically. The output is wired into a "
        "Streamlit web app where someone can fill in the rider's questionnaire (plus "
        "optional RULA and QEC scores), click Predict, and read six coloured risk "
        "levels.")
    para(doc, "The work is split across seven Jupyter notebooks:")
    bullet(doc, "01_data_cleaning - normalise the raw CSV and validate")
    bullet(doc, "02_feature_engineering - encode categoricals, derive composite "
                "scores, merge the posture observations into the survey by severity rank")
    bullet(doc, "03_risk_scoring - apply standard thresholds to compute the six "
                "Low/Medium/High labels per rider")
    bullet(doc, "04_eda - figures: demographics, NMQ prevalence, risk distribution, "
                "discomfort by group, correlation heatmap")
    bullet(doc, "05_stats - chi-square and logistic regression")
    bullet(doc, "06_modeling - SMOTE + GridSearchCV across 7 algorithms per target, "
                "keep the best by F1 macro")
    bullet(doc, "07_evaluation - confusion matrices, ROC curves, feature importance")
    para(doc,
        "Two helper scripts produce the polished outputs. src/build_results_deck.py "
        "appends the Phase 4 to 7 figures and result tables onto the original "
        "presentation deck. src/build_project_doc.py (this script) builds the Word "
        "version of the project write-up.")

    # ----- The six risk factors -----
    heading(doc, "The six risk factors")
    para(doc,
        "Each factor is computed in Phase 3 using a standard ergonomic method and "
        "binned into Low, Medium, or High.")

    heading(doc, "Force", level=2)
    para(doc, "How hard the rider has to lift or push. We use the Borg CR10 lifting "
              "item. Action levels are the conventional Borg cut-offs: 0 to 3 is Low "
              "(acceptable), 4 to 6 is Medium (monitor), 7 to 10 is High (intervene).")

    heading(doc, "Repetition", level=2)
    para(doc, "Deliveries per hour, computed as deliveries_num divided by "
              "work_hours_num. The original Phase 3 binning used pandas qcut into "
              "terciles, but the upper tercile boundary landed exactly on 35 / 9 = "
              "3.889 (the worst real combination in the sample) and 55 of 182 riders "
              "tied at that value, all falling into Medium. We switched to fixed "
              "cuts at 2.5 and 3.75 so the worst case ends up in High. The trade-off "
              "is documented in the Limitations section.")

    heading(doc, "Posture", level=2)
    para(doc, "RULA Table C, the final score from the standard RULA worksheet. The "
              "conventional action levels are 1 to 2 Low, 3 to 4 Medium, 5 or higher "
              "High.")

    heading(doc, "Duration", level=2)
    para(doc, "Continuous riding hours. 5 hours or less is Low, 6 to 7 is Medium, "
              "more than 7 is High.")

    heading(doc, "Contact Stress", level=2)
    para(doc, "How much load presses against the rider's body. A composite of "
              "carrying mode (storage box, backpack, handlebar, handheld), working "
              "hours, and a small age multiplier. We bin into terciles.")

    heading(doc, "Vibration", level=2)
    para(doc, "Vehicle type multiplied by working hours per day. Scooter is 1 and "
              "motor bike is 2, so a motorbike rider working 9 hours scores 18 (the "
              "worst observed). This is a proxy because we did not have per-rider "
              "accelerometer data; what we can measure is the relative exposure.")

    # ----- Data -----
    heading(doc, "Data")
    para(doc,
        "Two files. data/raw/delivery_rider_survey.csv has 182 rows and 48 columns. "
        "Questions 1 to 17 cover demographics, lifestyle, and work pattern. Q18 is "
        "the Nordic 12-month body-pain inventory across 9 body areas. Q19 covers the "
        "previous 7 days for 4 areas. Q20 to Q24 are follow-up Yes/No items about "
        "whether discomfort affected performance, whether the rider took leave, saw "
        "a doctor, and so on. Q25 to Q30 are the six NASA-TLX 0-100 sliders. Q31 to "
        "Q36 are the six Borg CR10 0-10 items.")
    para(doc,
        "data/raw/posture_data.xlsx has 182 observation records spread across the "
        "sheets. Each record carries 11 RULA components (upper_arm, lower_arm, "
        "wrist, wrist_twist, neck_position, trunk_position, legs, muscle_a, force_a, "
        "muscle_b, force_b), 3 derived RULA Table scores (a, b, c), and 8 QEC scores "
        "(qec_back, qec_shoulder_arm, qec_wrist_hand, qec_neck, qec_driving, "
        "qec_vibration, qec_work_pace, qec_stress).")
    para(doc,
        "The observation records do not carry a rider identifier. Phase 2 Step 8 "
        "pairs them to the survey using a severity-rank merge: riders are ranked by "
        "an exposure-severity score (NMQ count + fatigue_score + work_hours_num, "
        "each normalised), the observation rows are ranked by rula_table_c, and the "
        "two are joined rank to rank. The implication is discussed under Limitations.")

    # ----- Feature engineering -----
    heading(doc, "Feature engineering")
    para(doc,
        "Phase 2 turns the raw values into the columns the models can consume. "
        "Binned categoricals get ordinal codes (age_ord, education_ord, income_ord, "
        "job_duration_ord). Bins that come as ranges get numeric midpoints "
        "(work_hours_num, deliveries_num, work_days_num, rest_break_num). Yes/No "
        "questions become 0/1. The vehicle type and carrying mode are ranked from "
        "least to most strenuous. Six NASA-TLX items collapse into workload_score "
        "(simple mean, with the satisfaction item running in load-direction). The "
        "six Borg items collapse into fatigue_score. force_exertion is the Borg "
        "lifting item by itself. vibration_index is vehicle_rank multiplied by "
        "work_hours_num.")
    para(doc,
        "Five interaction features are added so a model can pick up that, for "
        "example, an older rider with high workload is at extra risk: "
        "workload_x_fatigue, workload_x_age, force_x_age, fatigue_x_jobdur, "
        "deliv_x_days. Phase 2 Step 5b adds gender, region, marital status, "
        "delivery platform, type of break, tobacco use, and alcohol use as ordinal "
        "ranks. Step 4b creates short-name aliases for the 18 Yes/No NMQ + 7-day + "
        "outcome items so the feature pool stays readable. The Posture observations "
        "are merged in Step 8 by severity rank.")
    para(doc,
        "The resulting data/processed/model_ready.csv has 182 rows and 121 columns.")

    # ----- Risk scoring -----
    heading(doc, "Risk scoring")
    para(doc,
        "Phase 3 takes model_ready.csv and applies the thresholds described under "
        "The six risk factors. It writes data/processed/risk_profile.csv with the "
        "six string labels (force_risk, repetition_risk, etc.) and their integer "
        "codes (force_risk_code etc., 0/1/2 for Low/Medium/High).")

    # ----- Models -----
    heading(doc, "Models")
    para(doc,
        "Phase 6 trains a separate classifier per risk factor. Seven candidate "
        "algorithms are evaluated for each target: Logistic Regression, Decision "
        "Tree, Random Forest, Extra Trees, Hist Gradient Boosting, XGBoost, and a "
        "Stacking ensemble that combines RF, ExtraTrees, XGBoost, and HistGBM with "
        "a Logistic Regression meta-learner. Each candidate is wrapped in an "
        "imbalanced-learn pipeline that runs SMOTE inside every CV fold to balance "
        "the minority class. Hyperparameters are tuned via GridSearchCV on F1 macro "
        "with StratifiedKFold(5). The best-by-F1 model per target is refit on the "
        "full sample and saved to outputs/models/best_<factor>.pkl.")
    para(doc,
        "Each saved bundle is a dict with three keys: model (the fitted "
        "imbalanced-learn pipeline), features (the exact list of feature names the "
        "model was trained on), and classes (the original integer class codes so "
        "the LabelEncoded output can be mapped back). src/predict.py reads the "
        "features list straight from the bundle, so adding new features in Phase 2 "
        "requires no code change in predict.py.")
    para(doc,
        "Each factor's defining input is excluded from its own feature pool, "
        "otherwise the model would simply memorise the Stage-1 rule. Force excludes "
        "force_exertion and force_x_age. Repetition excludes deliveries_num, "
        "work_hours_num, and deliv_x_days. Duration excludes work_hours_num and "
        "vibration_index (the second was a leakage discovery, see Limitations). "
        "Vibration excludes vibration_index, vehicle_rank, and work_hours_num. "
        "Contact Stress excludes carrying_contact_rank and work_hours_num. Posture "
        "does not exclude anything from the survey pool but is also given the 11 "
        "RULA components and 8 QEC scores; the three derived RULA Table scores are "
        "excluded as direct leakage because posture_risk is rula_table_c binned.")

    # ----- Findings -----
    heading(doc, "Sample and findings")
    para(doc,
        "The sample is 152 male and 30 female. Age skews young: 78 riders under 25, "
        "66 in the 25 to 35 band, 30 in 36 to 45, and 8 in 46 and above. 49 percent "
        "of the sample works more than 8 hours per day. 94 ride scooters and 88 "
        "ride motor bikes. Blinkit accounts for 97 riders, Zepto for 80, with 5 "
        "working both platforms.")
    para(doc,
        "84.6 percent of the riders reported pain in at least one body area in the "
        "last 12 months. Lower back is the most common complaint at 61.5 percent, "
        "followed by upper back (49.5%), shoulders (46.7%), wrists and hands (45.1%), "
        "hips and thighs (41.2%), ankles and feet (40.7%), knees (39.6%), neck (37.9%), "
        "and elbows (33.5%).")

    heading(doc, "Stage-1 risk distribution", level=2)
    table(doc,
          header=["Factor", "Low", "Medium", "High"],
          rows=[
              ["Force",          "90", "57",  "35"],
              ["Repetition",     "26", "82",  "74"],
              ["Duration",       "37", "56",  "89"],
              ["Vibration",      "67", "68",  "47"],
              ["Contact Stress", "68", "58",  "56"],
              ["Posture",        "0",  "29",  "153"],
          ],
          widths_cm=[5.0, 2.4, 2.4, 2.4])
    para(doc,
        "Posture, Duration, and Repetition are the three factors where the High "
        "band dominates. Posture is at 84 percent High (153 of 182 observations), "
        "Duration at 49 percent, Repetition at 41 percent after the binning fix.")

    heading(doc, "Stage-2 model performance", level=2)
    table(doc,
          header=["Factor", "Best model", "CV accuracy", "F1 macro", "Macro AUC", "Features"],
          rows=[
              ["Force",          "HistGradientBoosting", "62%", "57%", "71%", "42"],
              ["Repetition",     "RandomForest",         "62%", "57%", "73%", "41"],
              ["Duration",       "RandomForest",         "61%", "58%", "76%", "42"],
              ["Vibration",      "ExtraTrees",           "58%", "57%", "72%", "41"],
              ["Contact Stress", "RandomForest",         "60%", "59%", "74%", "42"],
              ["Posture",        "HistGradientBoosting", "97%", "95%", "98%", "63"],
          ],
          widths_cm=[3.2, 4.0, 2.4, 2.2, 2.2, 2.0])
    para(doc,
        "The five survey-derived factors land between 58 and 62 percent accuracy "
        "with macro AUC in the 71 to 76 percent range. Posture reaches 97 percent "
        "accuracy and 98 percent AUC because it is the only model that receives "
        "real observation inputs (11 RULA components and 8 QEC scores) on top of "
        "the survey features.")

    heading(doc, "Statistical predictors of discomfort", level=2)
    para(doc,
        "Phase 5 fits a multivariable logistic regression with discomfort (any NMQ "
        "12-month pain) as the outcome. The strongest individual predictor is age: "
        "each step up in the age band multiplies the odds of discomfort by 3.6 "
        "(95% CI 1.70 to 7.56, p = 0.0008). Job duration is next at 2.89 per step "
        "(p = 0.001). Education runs the other way as a protective factor (OR 0.33, "
        "p = 0.04). Income, fatigue score, workload score, and deliveries per day "
        "are all significant at smaller magnitudes. The chi-square test in the same "
        "phase finds that Posture and Force are the only two risk factors with a "
        "significant association with discomfort in this sample.")

    # ----- Web app -----
    heading(doc, "The web app")
    para(doc, "Start it with:")
    code(doc, "streamlit run app/streamlit_app.py")
    para(doc,
        "The form has six sections that together cover every column from the CSV "
        "and the xlsx. Section 1 is demographics and work pattern, Q1 to Q17. "
        "Section 2 is the NMQ 12-month items, the 7-day discomfort items, and the "
        "Q20 to Q24 follow-ups. Section 3 is the six NASA-TLX sliders (Q28 was "
        "rephrased from 'How satisfied' to 'How dissatisfied' so all six sliders "
        "run in the same direction). Section 4 is the six Borg CR10 sliders. "
        "Section 5 is the 11 RULA components with help text per item. Section 6 is "
        "the 8 QEC scores as number inputs with min/max set to the observed ranges "
        "in the training data.")
    para(doc,
        "encode_rider() turns the form values into the feature vector each model "
        "expects (44 survey features plus 5 interactions plus, for Posture, 11 "
        "RULA + 8 QEC). predict_risks() loops over the 6 saved bundles and returns "
        "a dict of factor to Low/Medium/High. Output is a colour-coded table with a "
        "summary banner; an expandable JSON view shows the exact feature values "
        "that were fed in, which is useful for showing a mentor that every form "
        "field actually does end up in the prediction.")
    para(doc, "The same prediction is also available from the command line:")
    code(doc, "python src/predict.py --json data/example_rider.json")

    # ----- Limitations -----
    heading(doc, "Limitations")
    para(doc,
        "These should be stated up front rather than buried at the end.")

    heading(doc, "Self-report bias", level=2)
    para(doc,
        "Most of the model inputs come from the rider's own answers (NMQ pain, "
        "NASA-TLX workload, Borg fatigue, the demographic items). A rider in a "
        "bad mood reports more pain than the same rider would on a good day. "
        "Nothing in the pipeline can correct for this.")

    heading(doc, "The Posture link is approximate", level=2)
    para(doc,
        "The 182 RULA + QEC observations do not carry rider identifiers. The "
        "Phase 2 Step 8 severity-rank merge pairs them to the survey by ranking "
        "riders by exposure severity (NMQ pain count + fatigue + working hours) "
        "and posture observations by RULA Table C, then matching the two ranks "
        "one to one. This means rider 1 in severity gets observation 1 in RULA, "
        "and so on. The 97 percent Posture accuracy is therefore the upper bound "
        "of what the linked data can support. A study where every rider is "
        "observed individually would settle slightly lower because rider-to-"
        "observation noise would re-enter.")

    heading(doc, "Repetition binning fix", level=2)
    para(doc,
        "The earlier Phase 3 used pandas qcut(q=3) on deliveries_per_hour. The "
        "75th percentile fell exactly on 3.889 dph (= 35 deliveries / 9 hours), "
        "which is the worst real combination in the sample. 55 of 182 riders tied "
        "at that value and were all binned into Medium because qcut is right-"
        "inclusive at the upper edge. The Stage-2 model could never predict High "
        "for the worst real rider, no matter what features it was given. The fix "
        "replaces qcut with fixed cuts at 2.5 and 3.75 so the worst case ends up "
        "in High where it should. Stage-1 High count went from 19 to 74. Stage-2 "
        "accuracy went from 74 percent to 62 percent. The drop is the honest "
        "trade: the model is now learning a real High class of 74 examples "
        "instead of memorising a 19-example minority.")

    heading(doc, "Duration leakage fix", level=2)
    para(doc,
        "An earlier Phase 6 run reported 100 percent CV accuracy on Duration. "
        "After investigating we found that vibration_index (= vehicle_rank x "
        "work_hours_num) was still in the feature pool, so the trees were "
        "recovering work_hours_num from it. We added vibration_index to the "
        "Duration exclusion list and capped max_depth + min_samples_leaf. Duration "
        "settled at 61 percent accuracy and 76 percent AUC.")

    heading(doc, "Cross-sectional design", level=2)
    para(doc,
        "Each rider was surveyed once. The fact that older riders report more "
        "pain could mean that long delivery careers cause MSDs, or that riders "
        "who develop MSDs quit, leaving the survivors. A follow-up study would "
        "settle this.")

    heading(doc, "Sample size and region", level=2)
    para(doc,
        "n = 182 is reasonable for descriptive statistics but small for "
        "multivariable ML; the cross-validation results have a natural wobble of "
        "around 5 percentage points. All riders came from one regional platform "
        "deployment, so the numbers may not transfer to other regions.")

    heading(doc, "Proxy inputs for Vibration and Repetition", level=2)
    para(doc,
        "Without per-shift accelerometer data, Vibration is approximated as "
        "vehicle_rank x work_hours_num. Without per-task timing, Repetition is "
        "approximated as deliveries-per-hour. Both proxies map onto what the "
        "survey can capture but neither carries the per-event signal a wearable "
        "would.")

    # ----- Recommendations -----
    heading(doc, "Recommendations")
    para(doc,
        "Five interventions come out of the analysis, ordered by how many riders "
        "they would reach. First, cap daily hours. Roughly half the sample works "
        "more than 8 hours per day, so a shift-length cap has the biggest "
        "population reach. Second, posture training and equipment review: "
        "84 percent of observed postures sit at RULA action level 5 or above, "
        "which usually means handle grips, helmet ergonomics, seat adjustment, or "
        "bag strap design. Third, push for storage-box carrying over handheld bags "
        "because the storage-box riders in the sample had the lowest contact "
        "stress. Fourth, age-targeted screening: discomfort climbs from 72 percent "
        "in riders under 25 to 100 percent in those 46 and above, so an annual MSD "
        "screen for the 36-plus cohort would catch problems earlier. Fifth, "
        "workload management at the platform level: smoother route batching and "
        "fewer 'rush' window pushes would reduce NASA-TLX scores and, through that "
        "channel, predicted risk.")

    # ----- Repo map -----
    heading(doc, "Where things live in the repository")
    code(doc,
"""Ergonomic_Project/
  README.md
  docs/
    PROJECT_EXPLAINED.md / .docx   this write-up
    results.md                     numbers and tables for the mentor
    development_plan.md            original execution plan
  data/
    raw/                           delivery_rider_survey.csv, posture_data.xlsx
    processed/                     cleaned.csv, model_ready.csv, risk_profile.csv
    example_rider.json
  notebooks/                       01..07 (the seven phases)
  src/
    predict.py                     command-line predictor
    build_results_deck.py          builds the WITH_RESULTS PowerPoint
    build_project_doc.py           builds this Word doc
  app/streamlit_app.py             interactive demo
  deck/                            Final.pptx and WITH_RESULTS.pptx
  outputs/
    figures/   all PNGs
    tables/    result CSVs
    models/    the six saved joblib bundles""")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    path = build()
    print(f"saved {path.relative_to(ROOT)}")
