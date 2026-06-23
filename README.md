# Ergonomic Risk Factor Prediction — Delivery Riders

AI/ML project predicting 6 ergonomic risk factors for food-delivery riders from
a 182-rider survey + 182-observation RULA/QEC posture dataset.

## The 6 risk factors
Force · Repetition · Posture · Duration · Contact Stress · Vibration

> **Project write-up:** [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) and the Word version [`docs/PROJECT_REPORT.docx`](docs/PROJECT_REPORT.docx). Single comprehensive report covering background, every phase of the pipeline (with formulae, thresholds, and hyperparameters), results, web app, limitations, and reproducibility.

## Design (2 stages)
- **Stage 1** — calculate each risk factor with a recognised method (Borg CR10
  action levels, RULA, sample terciles) → Low/Medium/High labels.
- **Stage 2** — train ML (LogReg / DT / RF / ExtraTrees / HistGBM / XGBoost /
  Stacking) to reproduce those labels from a rider's profile = automated
  ergonomic screening tool.

## Folder structure
```
Ergonomic_Project/
  data/raw/         delivery_rider_survey.csv, posture_data.xlsx
  data/processed/   cleaned.csv, model_ready.csv, risk_profile.csv
  notebooks/        01_data_cleaning … 07_evaluation (7 notebooks)
  src/              predict.py, build_results_deck.py, finalize_deck.py
  app/              streamlit_app.py (web demo)
  deck/             Final.pptx + WITH_RESULTS.pptx (+ archive backups)
  outputs/          figures/, tables/, models/
  docs/             development_plan.md, results.md
```

## Pipeline status
| Phase | Notebook / file | Output |
|---|---|---|
| 1 Cleaning            | notebooks/01_data_cleaning.ipynb       | data/processed/cleaned.csv |
| 2 Feature engineering | notebooks/02_feature_engineering.ipynb | data/processed/model_ready.csv |
| 3 Risk scoring        | notebooks/03_risk_scoring.ipynb        | data/processed/risk_profile.csv |
| 4 EDA                 | notebooks/04_eda.ipynb                 | 6 figures in outputs/figures/ |
| 5 Statistics          | notebooks/05_stats.ipynb               | 5 tables in outputs/tables/ |
| 6 ML modelling        | notebooks/06_modeling.ipynb            | 6 pickled models + 5 result tables |
| 7 Evaluation          | notebooks/07_evaluation.ipynb          | 3 figures + 3 tables |
| 8 Results write-up    | docs/results.md                        | full mentor-facing write-up |
| 9 Deck                | src/build_results_deck.py              | deck/...WITH_RESULTS.pptx (53 slides) |

All 9 phases complete.

## Predict for a new rider

### Web app (recommended for demos)
```bash
streamlit run app/streamlit_app.py
```
Opens a form in the browser. Fill in the rider's survey answers, hit
**Predict risk levels**, see Low / Medium / High for all 6 factors with
colour-coded badges.

### Command line
```bash
# From a row already in model_ready.csv
python src/predict.py --rider-id 0

# From a JSON profile you wrote (see data/example_rider.json for the schema)
python src/predict.py --json data/example_rider.json

# List the features each model expects
python src/predict.py --list-features
```

### Python API
```python
from src.predict import predict_rider
predict_rider({'workload_score': 55, 'age_ord': 1, ...})
# -> {'force': 'Low', 'repetition': 'Medium', 'duration': 'Low',
#     'vibration': 'Low', 'contact_stress': 'Low', 'posture': 'Medium'}
```

## Setup
```bash
pip install pandas numpy scikit-learn scipy matplotlib seaborn xgboost \
            statsmodels imbalanced-learn python-pptx joblib streamlit \
            openpyxl
```

## Documentation
- `docs/PROJECT_REPORT.md` / `.docx` - single comprehensive project
  report (background, methods, results, web app, limitations,
  reproducibility, output-file index)
- `docs/development_plan.md` - original execution plan
