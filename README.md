# Ergonomic Risk Factor Prediction — Delivery Riders

AI/ML project predicting 6 ergonomic risk factors for food-delivery riders from survey data.

## Folder structure
```
Ergonomic_Project/
  data/raw/         delivery_rider_survey.csv      survey responses (182 riders)
  data/processed/   cleaned / model-ready / risk-profile tables (generated)
  notebooks/        01_data_cleaning.ipynb …       per-phase Jupyter notebooks
  src/              optional .py versions of the pipeline
  deck/             Ergonomic_Risk_Factor_Prediction_Project_Plan_Final.pptx
  outputs/          figures/ , tables/ , models/   (generated)
  docs/             development_plan.md
```

## The 6 risk factors
Force · Repetition · Posture · Duration · Contact Stress · Vibration

## Design (2 stages)
- **Stage 1** — calculate each risk factor with a recognised method → Low/Med/High labels.
- **Stage 2** — train ML to reproduce those levels from a rider's profile = automated
  ergonomic screening tool.

## Status
- ✅ Data available: survey CSV (182 responses)
- ✅ Borg CR10 emoji scale decoded (😁 = 0 Extremely Easy → 😭 = 10 Extremely Hard)
- ✅ Phase 1 — Data cleaning complete (`notebooks/01_data_cleaning.ipynb` → `data/processed/cleaned.csv`)
- ⏳ Pending: RULA & QEC posture data (under process) → the **Posture** factor is deferred

## Pipeline (see docs/development_plan.md for detail)
Phase 1 cleaning → 2 feature engineering → 3 risk scoring → 4 EDA → 5 statistics →
6 ML modeling → 7 evaluation → 8 results → 9 finalize deck
