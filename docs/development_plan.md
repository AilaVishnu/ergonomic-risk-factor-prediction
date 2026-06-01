# Ergonomic Risk Factor Prediction — End-to-End Execution Plan (code + deck)

## Context
The user is a student doing an academic project: predicting 6 ergonomic risk factors for
food-delivery riders from a survey dataset. The original plan deck had methodology flaws
found in this conversation: discomfort used as both input and outcome (circular); invented
formulas instead of recognised methods; "predicting" 6 factors with no measured labels.
This plan is the corrected, executable roadmap — a Python pipeline plus the `_Final` deck —
and it must stay **in sync with the deck the user is actively editing**.

**Chosen design ("output the 6 factors" / automation framing):**
- *Stage 1* — calculate each risk factor with a recognised method → Low/Med/High labels.
- *Stage 2* — train ML to reproduce those levels from a rider's input profile = an
  automated ergonomic screening tool (framed honestly as automating the assessment).

## Current deck state — `Ergonomic_Risk_Factor_Prediction_Project_Plan_Final.pptx` (40 slides)
User changes observed (latest read):
- Slide 3 — 6 factors renamed → **Force, Repetition, Posture, Duration, Contact Stress, Vibration**
  (was "Awkward Posture" / "Static Posture").
- Slide 4 — Posture method = **RULA & QEC** (REBA dropped, QEC added).
- Slide 5 — Contact Stress note "(consider age)" added.
- Slide 6 — Vibration table Scooter=1 / Motorcycle=2 (retained); slide 7 "leads to higher" (retained).
- Slide 37 — NEW detailed "Inputs & Outputs" slide with column mapping; Slide 40 — NEW "Thank You".
- Earlier restyle + text fixes + slide 19/20/26/29 layout rebuilds all retained.

**Final factor set (supervisor-confirmed):** Force · Repetition · **Posture** · **Duration** ·
Contact Stress · Vibration. Awkward + Static posture are merged into one **Posture** factor
(measured by RULA & QEC); **Duration** (continuous posture/riding duration) is added → 6 total.

Inconsistencies still in the deck → to fix in Phase 9:
- Slides 10, 32, 36, 37 still say "Awkward Posture Risk / Static Posture Risk" — must change
  to **"Posture Risk" + "Duration Risk"** to match slide 3 and the supervisor's decision.
- Slide 8 has a split word "Data Cleanin g".
- Slides 36 & 37 are near-duplicate "Inputs & Outputs" — keep the detailed one (37).
- Slides 36/37 still list "discomfort indicators" as an *input* (circularity — discomfort is the target).

## Data status
- **Survey CSV** — `f:\Ergonomic_Project\data\raw\delivery_rider_survey.csv`
  (181 responses, 48 cols). Available now.
- **Posture data (RULA & QEC)** — ⏳ *under process; only a few riders will be scored.* The
  **Posture** factor is **deferred**. ⏰ **REMIND THE USER** to add it when ready.
- **Borg fatigue columns** — emoji-encoded (11-face Borg CR10). ✅ Scale decoded & confirmed
  by the user: 😁=0 (Extremely Easy) → 😭=10 (Extremely Hard).

## Project folder — `f:\Ergonomic_Project\` (everything stored here; moved to F drive 2026-05-22)
```
Ergonomic_Project/
  data/raw/         delivery_rider_survey.csv      (the survey CSV, copied + renamed)
  data/processed/   cleaned.csv, model_ready.csv, risk_profile.csv   (generated)
  deck/             Ergonomic_Risk_Factor_Prediction_Project_Plan_Final.pptx + backup(s)
  src/              01_data_cleaning.py … 07_evaluation.py
  outputs/          figures/, tables/, models/
  docs/             development plan / notes
```
All existing project files are consolidated here in Phase 0.

## Phase plan (the code)

**Phase 0 — Create the project folder & set up.**
- Project folder `f:\Ergonomic_Project\` created with the subfolders above. ✅ done
- Copy in existing assets: the survey CSV → `data/raw/delivery_rider_survey.csv`;
  the `_Final.pptx` + `ORIGINAL_BACKUP.pptx` → `deck/`; the development plan → `docs/`.
  (`_Final.pptx` is open in PowerPoint — copy it once PowerPoint is closed.)
- Install Anaconda + pandas, numpy, scikit-learn, scipy, matplotlib, seaborn, xgboost, python-pptx.
- Decode Borg emoji scale from the original Google Form. ✅ done — confirmed 😁=0 → 😭=10.

**Phase 1 — Data cleaning** → `src/01_data_cleaning.py`
Fix mojibake; decode 6 Borg emoji cols → ordinal; standardise labels ("00 ( Low/low )" → 0;
NASA-TLX strings → 0/25/50/75/100); missing values. Output `data/processed/cleaned.csv`.

**Phase 2 — Feature engineering** → `src/02_feature_engineering.py`
Encode bins → ordinal **and** to numeric midpoints for the work-exposure variables that
Phase 3 formulas need (e.g. `Working Hours per Day`: `<3` → 2, `3-5` → 4, `6-8` → 7,
`>8` → 9; same for `Number of deliveries per day`, `Working days per week`, `Rest break`,
`Age`, `Monthly income`). **Binary-encode all Yes/No items → 1/0** (9 Nordic body-area
questions, 4 seven-day discomfort items, the 5 other Yes/No items). Derive `workload_score`
(reverse Performance, mean of 6 NASA-TLX), `fatigue_score` (mean of Borg items),
`force_exertion` (Borg lifting item), `vehicle_rank`, `carrying_contact_rank`,
`vibration_index`, `discomfort` target (Nordic). Output `model_ready.csv`.

**Phase 3 — Stage 1: risk-factor scoring** → `src/03_risk_scoring.py`
Compute & bin to Low/Med/High:
- **Doable now (5):** Force (Borg) · Repetition (deliveries÷hours) · Vibration (working
  hours × vehicle weight; optional ISO 2631 A(8) refine) · Contact Stress (carrying rank ×
  hours, factor in age) · **Duration** (continuous riding/posture duration from working hours).
- **Deferred (1):** **Posture** — needs RULA & QEC data (under process). Placeholder column.
Output `risk_profile.csv` with **both** the string label (`Low` / `Medium` / `High`) **and**
the integer code (`0` / `1` / `2`) for each risk factor, so Phase 6 can use the ordinal form.

**Phase 4 — EDA** → `src/04_eda.py`
Demographics, risk-factor distributions, discomfort prevalence by body area/group → `outputs/figures/`.

**Phase 5 — Statistical analysis** → `src/05_stats.py`
Correlation heatmap; chi-square (risk factor ↔ discomfort); Mann-Whitney / Kruskal-Wallis;
logistic regression with odds ratios → `outputs/tables/`.

**Phase 6 — Stage 2: ML modeling** → `src/06_modeling.py`
Per-factor classifiers: target = each factor's L/M/H label; features = rider profile
**excluding that factor's own defining variable**. Models: Logistic Regression, Decision
Tree, Random Forest, XGBoost. Stratified k-fold CV; class-imbalance handling → `outputs/models/`.

**Phase 7 — Evaluation** → `src/07_evaluation.py`
Accuracy, Precision, Recall, F1, Confusion Matrix, ROC-AUC, feature importance;
train-vs-CV overfitting check; pick best model.

**Phase 8 — Results & recommendations.** Consolidated charts, key findings, rider-safety
recommendations, honest limitations (proxy indices, 181-rider sample, self-report, posture deferred).

**Phase 9 — Finalize the `_Final` deck (40 slides).**
*Not* a fresh build — refine the user's existing `_Final.pptx`:
- Make factor naming consistent everywhere (slides 10/32/36/37 → "Posture Risk" + "Duration Risk").
- Fix slide 8 "Data Cleanin g"; remove the duplicate Inputs&Outputs (keep slide 37).
- Move "discomfort indicators" out of the input list (it is the prediction target).
- Add results placeholders for EDA / modeling / evaluation outputs.
Note: `_Final.pptx` is currently **open in PowerPoint** (`~$` lock present) — must be
closed before it can be overwritten.

## Execution order & scope
- **Do now:** Phases 0–9 for the **5 available factors** + EDA/stats/ML + deck finalize.
- **Do later (when RULA & QEC arrives):** add the Posture factor, re-run Phases 3/6/7 for
  all 6. ⏰ **REMIND THE USER.**

## Critical files (all under `f:\Ergonomic_Project\`)
- `data\raw\delivery_rider_survey.csv` — dataset (181 rows)
- `src\` — pipeline code · `outputs\` — figures/tables/models
- `deck\Ergonomic_Risk_Factor_Prediction_Project_Plan_Final.pptx` — deck, 40 slides

## Verification
- Each `src/0X_*.py` runs without error; outputs saved to `data/processed/` and `outputs/`.
- Cleaned data sanity: row count ≈ 181, no stray missing values, encoded ranges valid.
- Models: report stratified-CV metrics + confusion matrices; flag train-vs-CV gaps.
- Deck: opens, 40 slides, consistent factor naming, all XML parts well-formed.

## Reminders to surface
1. **RULA & QEC posture data is under process** — the Posture factor is deferred; the
   project is completable to 5/6 factors now and finished once that data is in.
