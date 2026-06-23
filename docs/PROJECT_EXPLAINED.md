# Project write-up

A walk-through of the whole project so anyone (mentor, future me, anyone
who has not seen the codebase) can follow what we did and why.

## Background

Food-delivery riders for platforms like Blinkit and Zepto spend long
hours on bikes, climb stairs, carry packages, and ride in heavy traffic.
Over time this kind of work causes musculoskeletal disorders (MSDs):
back pain, shoulder pain, wrist injuries, knee problems. The risk is
not the same for every rider. Someone who is 22 and works 4 hours a day
on a scooter is in a very different situation from a 45-year-old who
works 10 hours a day on a motorbike with a handheld bag.

Ergonomists have standard ways of measuring this kind of strain. RULA
(Rapid Upper Limb Assessment) scores the posture of a worker's upper
body. QEC (Quick Exposure Check) gives a composite of body-region and
exposure scores. The Nordic Musculoskeletal Questionnaire (NMQ) records
pain across 9 body areas. NASA-TLX rates mental workload. Borg CR10
records perceived physical effort on a 0 to 10 scale. Each gives useful
information on its own. The project takes all of them together and
produces a single per-rider risk profile across six ergonomic
dimensions: Force, Repetition, Posture, Duration, Contact Stress,
Vibration.

## What the project does

We collected survey responses from 182 riders along with 182 RULA + QEC
observation records. The pipeline cleans this data, applies standard
ergonomic thresholds to compute Low / Medium / High labels for each of
the six risk factors, then trains a separate classifier per factor so a
new rider's profile can be screened automatically. The output is wired
into a Streamlit web app where someone can fill in the rider's
questionnaire (plus optional RULA and QEC scores), click Predict, and
read six coloured risk levels.

The work is split across seven Jupyter notebooks:

- `01_data_cleaning` normalises the raw CSV and validates row counts
- `02_feature_engineering` encodes categoricals, derives composite
  scores, and merges the posture observations into the survey by
  severity rank
- `03_risk_scoring` applies standard thresholds to compute the six
  Low/Medium/High labels per rider
- `04_eda` produces the demographics, NMQ prevalence, risk
  distribution, discomfort-by-group, and correlation-heatmap figures
- `05_stats` runs chi-square and logistic regression
- `06_modeling` runs SMOTE + GridSearchCV across 7 algorithms per
  target and keeps the best by F1 macro
- `07_evaluation` produces confusion matrices, ROC curves, and feature
  importance plots

Two helper scripts produce polished outputs. `src/build_results_deck.py`
appends the Phase 4-7 figures and result tables onto the original
presentation deck. `src/build_project_doc.py` builds the Word version of
this write-up.

## The six risk factors

Each factor is computed in Phase 3 using a standard ergonomic method
and binned into Low, Medium, or High.

**Force.** How hard the rider has to lift or push. We use the Borg CR10
lifting item. Conventional Borg action levels: 0-3 Low (acceptable),
4-6 Medium (monitor), 7-10 High (intervene).

**Repetition.** Deliveries per hour, computed as `deliveries_num /
work_hours_num`. The earlier Phase 3 binning used `pandas.qcut(q=3)`
into terciles, but the upper tercile boundary landed exactly on
35 / 9 = 3.889 (the worst real combination in the sample) and 55 of 182
riders tied at that value, all falling into Medium. We switched to
fixed cuts at 2.5 and 3.75 so the worst case ends up in High. The
trade-off is discussed under Limitations.

**Posture.** RULA Table C, the final score from the standard RULA
worksheet. Conventional action levels are 1-2 Low, 3-4 Medium, 5 or
higher High.

**Duration.** Continuous riding hours. 5 hours or less is Low, 6-7 is
Medium, more than 7 is High.

**Contact Stress.** How much load presses against the rider's body. A
composite of carrying mode (storage box, backpack, handlebar,
handheld), working hours, and a small age multiplier. We bin into
terciles.

**Vibration.** Vehicle type multiplied by working hours per day.
Scooter is 1, motor bike is 2, so a motorbike rider working 9 hours
scores 18 (the worst observed). This is a proxy because we did not have
per-rider accelerometer data; what we can measure is the relative
exposure.

## Data

Two files.

`data/raw/delivery_rider_survey.csv` has 182 rows and 48 columns.
Questions 1-17 cover demographics, lifestyle, and work pattern. Q18 is
the Nordic 12-month body-pain inventory across 9 body areas. Q19
covers the previous 7 days for 4 areas. Q20-24 are follow-up Yes/No
items about whether discomfort affected performance, whether the rider
took leave, saw a doctor, and so on. Q25-30 are the six NASA-TLX 0-100
sliders. Q31-36 are the six Borg CR10 0-10 items.

`data/raw/posture_data.xlsx` has 182 observation records. Each record
carries 11 RULA components (`upper_arm`, `lower_arm`, `wrist`,
`wrist_twist`, `neck_position`, `trunk_position`, `legs`, `muscle_a`,
`force_a`, `muscle_b`, `force_b`), 3 derived RULA Table scores (a, b,
c), and 8 QEC scores (`qec_back`, `qec_shoulder_arm`, `qec_wrist_hand`,
`qec_neck`, `qec_driving`, `qec_vibration`, `qec_work_pace`,
`qec_stress`).

The observation records do not carry a rider identifier. Phase 2 Step 8
pairs them to the survey using a severity-rank merge. Riders get ranked
by an exposure-severity score (`NMQ count + fatigue_score +
work_hours_num`, each normalised), the observation rows get ranked by
`rula_table_c`, and the two are joined rank to rank. The implication
shows up under Limitations.

## Feature engineering

Phase 2 turns the raw values into the columns the models can consume.
Binned categoricals get ordinal codes (`age_ord`, `education_ord`,
`income_ord`, `job_duration_ord`). Bins that come as ranges get numeric
midpoints (`work_hours_num`, `deliveries_num`, `work_days_num`,
`rest_break_num`). Yes/No questions become 0/1. Vehicle type and
carrying mode are ranked from least to most strenuous. The six NASA-TLX
items collapse into `workload_score`. The six Borg items collapse into
`fatigue_score`. `force_exertion` is the Borg lifting item by itself.
`vibration_index` is `vehicle_rank * work_hours_num`.

Five interaction features get added so a model can pick up that, for
example, an older rider with high workload is at extra risk:
`workload_x_fatigue`, `workload_x_age`, `force_x_age`,
`fatigue_x_jobdur`, `deliv_x_days`. Phase 2 Step 5b adds gender,
region, marital status, delivery platform, type of break, tobacco use,
and alcohol use as ordinal ranks. Step 4b creates short-name aliases
for the 18 Yes/No items (`nmq_*`, `d7_*`, `out_*`) so the feature pool
stays readable. The posture observations get merged in Step 8.

`data/processed/model_ready.csv` ends up with 182 rows and 121 columns.

## Risk scoring

Phase 3 takes `model_ready.csv` and applies the thresholds described
above. It writes `data/processed/risk_profile.csv` with the six string
labels (`force_risk`, `repetition_risk`, etc.) and their integer codes
(`force_risk_code`, etc., 0/1/2 for Low/Medium/High).

## Models

Phase 6 trains a separate classifier per risk factor. Seven candidate
algorithms run on each target: LogisticRegression, DecisionTree,
RandomForest, ExtraTrees, HistGradientBoosting, XGBoost, and a
StackingClassifier that combines RF, ExtraTrees, XGBoost, and HistGBM
with a LogisticRegression meta-learner. Each candidate is wrapped in an
`imblearn.Pipeline` that runs SMOTE inside every CV fold to balance the
minority class. Hyperparameters are tuned via `GridSearchCV` on
`f1_macro` with `StratifiedKFold(5)`. The best-by-F1 model per target
is refit on the full sample and saved to
`outputs/models/best_<factor>.pkl`.

Each saved bundle is a dict with three keys: `model` (the fitted
imbalanced-learn pipeline), `features` (the exact list of feature names
the model was trained on), and `classes` (the original integer class
codes so the LabelEncoded output can be mapped back). `src/predict.py`
reads the `features` list straight from the bundle, so adding new
features in Phase 2 needs no code change in `predict.py`.

Each factor's defining input is excluded from its own feature pool;
otherwise the model would memorise the Stage-1 rule.

- Force excludes `force_exertion` and `force_x_age`.
- Repetition excludes `deliveries_num`, `work_hours_num`, and
  `deliv_x_days`.
- Duration excludes `work_hours_num` and `vibration_index` (the second
  was a leakage discovery, see Limitations).
- Vibration excludes `vibration_index`, `vehicle_rank`, and
  `work_hours_num`.
- Contact Stress excludes `carrying_contact_rank` and `work_hours_num`.
- Posture does not exclude anything from the survey pool but is also
  given the 11 RULA components and 8 QEC scores; the three derived
  RULA Table scores are excluded as direct leakage because
  `posture_risk` is `rula_table_c` binned.

## Sample and findings

The sample is 152 male and 30 female. Age skews young: 78 riders under
25, 66 in the 25-35 band, 30 in 36-45, and 8 in 46 and above. 49
percent of the sample works more than 8 hours per day. 94 ride
scooters and 88 ride motor bikes. Blinkit accounts for 97 riders,
Zepto for 80, with 5 working both platforms.

84.6 percent of the riders reported pain in at least one body area in
the last 12 months. Lower back is the most common complaint at 61.5
percent, followed by upper back (49.5%), shoulders (46.7%), wrists and
hands (45.1%), hips and thighs (41.2%), ankles and feet (40.7%), knees
(39.6%), neck (37.9%), and elbows (33.5%).

### Stage-1 distribution

| Factor | Low | Medium | High |
|---|---|---|---|
| Force | 90 | 57 | 35 |
| Repetition | 26 | 82 | **74** |
| Duration | 37 | 56 | **89** |
| Vibration | 67 | 68 | 47 |
| Contact Stress | 68 | 58 | 56 |
| Posture | 0 | 29 | **153** |

Posture, Duration, and Repetition are the three factors where the High
band dominates. Posture is at 84 percent High (153 of 182 observations),
Duration at 49 percent, Repetition at 41 percent after the binning fix.

### Stage-2 model performance

| Factor | Best model | Accuracy | F1 macro | AUC | Features |
|---|---|---|---|---|---|
| Force | HistGradientBoosting | 62% | 57% | 71% | 42 |
| Repetition | RandomForest | 62% | 57% | 73% | 41 |
| Duration | RandomForest | 61% | 58% | 76% | 42 |
| Vibration | ExtraTrees | 58% | 57% | 72% | 41 |
| Contact Stress | RandomForest | 60% | 59% | 74% | 42 |
| Posture | HistGradientBoosting | **97%** | **95%** | **98%** | 63 |

The five survey-derived factors land between 58 and 62 percent accuracy
with macro AUC in the 71-76 percent range. Posture reaches 97 percent
accuracy and 98 percent AUC because it is the only model that receives
real observation inputs (11 RULA components and 8 QEC scores) on top
of the survey features.

### Statistical predictors of discomfort

Phase 5 fits a multivariable logistic regression with discomfort (any
NMQ 12-month pain) as the outcome. The strongest individual predictor
is age: each step up in the age band multiplies the odds of discomfort
by 3.6 (95% CI 1.70-7.56, p = 0.0008). Job duration is next at 2.89 per
step (p = 0.001). Education runs the other way as a protective factor
(OR 0.33, p = 0.04). Income, fatigue score, workload score, and
deliveries per day are all significant at smaller magnitudes. The
chi-square test in the same phase finds that Posture and Force are the
only two risk factors with a significant association with discomfort
in this sample.

## The web app

Start it with:

```
streamlit run app/streamlit_app.py
```

The form has six sections that together cover every column from the
CSV and the xlsx.

- Section 1: demographics and work pattern, Q1-17
- Section 2: NMQ 12-month items, 7-day discomfort, Q20-24 follow-ups
- Section 3: six NASA-TLX sliders (Q28 was rephrased from
  *How satisfied* to *How dissatisfied* so all six sliders run in the
  same direction)
- Section 4: six Borg CR10 sliders
- Section 5: 11 RULA components with help text per item
- Section 6: 8 QEC scores as number inputs with min/max set to the
  observed ranges in the training data

`encode_rider()` turns the form values into the feature vector each
model expects (44 survey features plus 5 interactions plus, for
Posture, 11 RULA + 8 QEC). `predict_risks()` loops over the 6 saved
bundles and returns a dict of factor to Low/Medium/High. Output is a
colour-coded table with a summary banner; an expandable JSON view
shows the exact feature values that were fed in, which is useful for
showing a mentor that every form field actually does end up in the
prediction.

The same prediction is also available from the command line:

```
python src/predict.py --json data/example_rider.json
```

## Limitations

Worth stating up front rather than burying at the end.

**Self-report bias.** Most of the model inputs come from the rider's
own answers (NMQ pain, NASA-TLX workload, Borg fatigue, the demographic
items). A rider in a bad mood reports more pain than the same rider
would on a good day. Nothing in the pipeline can correct for this.

**The Posture link is approximate.** The 182 RULA + QEC observations
do not carry rider identifiers. The Phase 2 Step 8 severity-rank merge
pairs them to the survey by ranking riders by exposure severity (NMQ
pain count + fatigue + working hours) and posture observations by
RULA Table C, then matching the two ranks one to one. This means rider
1 in severity gets observation 1 in RULA, and so on. The 97 percent
Posture accuracy is therefore the upper bound of what the linked data
can support. A study where every rider is observed individually would
settle slightly lower because rider-to-observation noise would
re-enter.

**Repetition binning fix.** The earlier Phase 3 used
`pandas.qcut(q=3)` on `deliveries_per_hour`. The 75th percentile fell
exactly on 3.889 dph (= 35 deliveries / 9 hours), which is the worst
real combination in the sample. 55 of 182 riders tied at that value
and were all binned into Medium because qcut is right-inclusive at the
upper edge. The Stage-2 model could never predict High for the worst
real rider, no matter what features it was given. The fix replaces
qcut with fixed cuts at 2.5 and 3.75 so the worst case ends up in
High where it should. Stage-1 High count went from 19 to 74. Stage-2
accuracy went from 74 percent to 62 percent. The drop is the honest
trade: the model is now learning a real High class of 74 examples
instead of memorising a 19-example minority.

**Duration leakage fix.** An earlier Phase 6 run reported 100 percent
CV accuracy on Duration. After investigating we found that
`vibration_index` (= `vehicle_rank * work_hours_num`) was still in the
feature pool, so the trees were recovering `work_hours_num` from it.
We added `vibration_index` to the Duration exclusion list and capped
`max_depth` + `min_samples_leaf`. Duration settled at 61 percent
accuracy and 76 percent AUC.

**Cross-sectional design.** Each rider was surveyed once. The fact
that older riders report more pain could mean that long delivery
careers cause MSDs, or that riders who develop MSDs quit, leaving the
survivors. A follow-up study would settle this.

**Sample size and region.** n = 182 is reasonable for descriptive
statistics but small for multivariable ML. The cross-validation
results have a natural wobble of around 5 percentage points. All
riders came from one regional platform deployment, so the numbers may
not transfer to other regions.

**Proxy inputs for Vibration and Repetition.** Without per-shift
accelerometer data, Vibration is approximated as
`vehicle_rank * work_hours_num`. Without per-task timing, Repetition
is approximated as deliveries-per-hour. Both proxies map onto what the
survey can capture but neither carries the per-event signal a wearable
would.

## Recommendations

Five interventions come out of the analysis, ordered by how many
riders they would reach.

1. **Cap daily hours.** Roughly half the sample works more than 8
   hours per day, so a shift-length cap has the biggest population
   reach.
2. **Posture training and equipment review.** 84 percent of observed
   postures sit at RULA action level 5 or above, which usually means
   handle grips, helmet ergonomics, seat adjustment, or bag strap
   design.
3. **Push for storage-box carrying over handheld bags.** The
   storage-box riders in the sample had the lowest contact stress.
4. **Age-targeted screening.** Discomfort climbs from 72 percent in
   riders under 25 to 100 percent in those 46 and above. An annual MSD
   screen for the 36-plus cohort would catch problems earlier.
5. **Workload management at the platform level.** Smoother route
   batching and fewer rush-window pushes would reduce NASA-TLX scores
   and, through that channel, predicted risk.

## Where things live in the repo

```
Ergonomic_Project/
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
    models/    the six saved joblib bundles
```
