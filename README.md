# Ergonomic Risk Factor Prediction for Delivery Riders

A predictive machine learning framework for ergonomic risk in
last-mile quick-commerce delivery operations. Trained on a 182-rider
survey combined with 182 RULA and QEC observation records.

## Six risk factors

Force, Repetition, Posture, Duration, Contact Stress, Vibration.

## Two-stage design

1. **Stage 1** applies standard ergonomic methods (Borg CR10 action
   levels, RULA Table C thresholds, sample terciles or fixed cuts) to
   compute Low, Medium, or High labels per risk factor.
2. **Stage 2** trains one classifier per factor (LogisticRegression,
   DecisionTree, RandomForest, ExtraTrees, HistGradientBoosting,
   XGBoost, or Stacking) with SMOTE oversampling inside 5-fold
   stratified cross-validation, tuned via GridSearchCV.

## Folder structure

```
Ergonomic_Project/
  data/raw/         delivery_rider_survey.csv, posture_data.xlsx
  data/processed/   cleaned.csv, model_ready.csv, risk_profile.csv
  notebooks/        01_data_cleaning ... 07_evaluation (7 notebooks)
  src/              predict.py
  app/              streamlit_app.py (multi-page web app)
  deck/             Final.pptx and WITH_RESULTS.pptx
  outputs/          figures/, tables/, models/
  docs/             report.docx (IIITDM-SIES internship report)
                    PROJECT_REPORT.md / .docx (detailed technical write-up)
```

## Pipeline

| Phase | Notebook / file | Output |
|---|---|---|
| 1 Cleaning            | notebooks/01_data_cleaning.ipynb       | data/processed/cleaned.csv |
| 2 Feature engineering | notebooks/02_feature_engineering.ipynb | data/processed/model_ready.csv |
| 3 Risk scoring        | notebooks/03_risk_scoring.ipynb        | data/processed/risk_profile.csv |
| 4 EDA                 | notebooks/04_eda.ipynb                 | 6 figures in outputs/figures/ |
| 5 Statistics          | notebooks/05_stats.ipynb               | 5 tables in outputs/tables/ |
| 6 ML modelling        | notebooks/06_modeling.ipynb            | 6 pickled models + 5 result tables |
| 7 Evaluation          | notebooks/07_evaluation.ipynb          | 3 figures + 3 tables |
| 8 Report              | docs/report.docx                       | IIITDM-SIES internship report |
| 9 Deck                | deck/...WITH_RESULTS.pptx              | presentation slides |

## Predict for a new rider

### Web app

```bash
python -m streamlit run app/streamlit_app.py
```

Opens a multi-page interface with Home, Assessment, Results,
Methodology, and About pages.

### Command line

```bash
python src/predict.py --rider-id 0

# From a JSON profile (see data/example_rider.json for the schema)
python src/predict.py --json data/example_rider.json

# List features each model expects
python src/predict.py --list-features
```

### Python API

```python
from src.predict import predict_rider
predict_rider({"workload_score": 55, "age_ord": 1, ...})
# -> {"force": "Low", "repetition": "Medium", "duration": "Low",
#     "vibration": "Low", "contact_stress": "Low", "posture": "Medium"}
```

## Setup

```bash
pip install pandas numpy scikit-learn scipy matplotlib seaborn xgboost \
            statsmodels imbalanced-learn python-pptx joblib streamlit \
            openpyxl plotly altair python-docx
```

## Documentation

- `docs/report.docx` is the IIITDM-SIES internship report in the
  required template (title page, certificate, abstract, contents,
  five chapters, bibliography).
- `docs/PROJECT_REPORT.md` / `.docx` is the detailed technical
  write-up with background, every phase of the pipeline (formulae,
  thresholds, and hyperparameters), results, web app, limitations,
  and reproducibility.
