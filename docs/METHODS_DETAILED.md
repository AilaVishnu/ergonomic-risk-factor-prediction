# Methods, in detail

This is the technical write-up of every step the project performs.
It is meant as paper-preparation material: every algorithm, every
threshold, every hyperparameter, every design choice, with enough
detail that the work can be reproduced from this document plus the
notebooks alone.

## 1. Study design

This is a cross-sectional secondary analysis of two ergonomic datasets
collected from food-delivery riders. The pipeline runs in two stages.

**Stage 1** computes Low/Medium/High labels for six ergonomic risk
factors (Force, Repetition, Posture, Duration, Contact Stress,
Vibration) using deterministic rules from standard ergonomic methods
(Borg CR10 action levels, RULA Table C action levels, sample
terciles, simple thresholds). Stage 1 is the ground truth that
Stage 2 tries to learn.

**Stage 2** trains a supervised classifier per risk factor that maps a
rider profile to that factor's Stage-1 label. Per-target feature
exclusions remove the inputs that define the label so the model has
to learn from the remaining profile rather than memorising the rule.
Each classifier is evaluated by 5-fold stratified cross-validation.

The two-stage split lets us audit the labels (Stage 1 is transparent)
and at the same time produce a screening tool that can run on a
rider's profile without re-applying the ergonomic worksheets.

## 2. Data sources

### 2.1 Rider survey

`data/raw/delivery_rider_survey.csv` contains 182 self-administered
responses from food-delivery riders. The questionnaire has 36 items
spread across the following modules:

- Q1-17: demographics, lifestyle, work pattern. Gender, age band,
  education band, region, marital status, delivery platform, job
  duration band, monthly income band, type of vehicle, mode of
  carrying deliveries, working hours per day band, working days per
  week band, deliveries per day band, duration of rest break, type of
  break, tobacco consumption category, alcohol consumption category.
- Q18: Nordic Musculoskeletal Questionnaire 12-month items. Nine
  Yes/No items, one per body area: neck, shoulders, upper back, lower
  back, elbows, wrists/hands, hips/thighs, knees, ankles/feet.
- Q19: 7-day discomfort. Four Yes/No items for neck, lower back,
  knees, wrists/hands.
- Q20-24: discomfort follow-ups. Five Yes/No items asking whether the
  discomfort reduced delivery performance, whether the rider took
  leave, consulted a doctor or physiotherapist, whether long riding
  worsened the discomfort, and whether carrying heavy packages
  worsened it.
- Q25-30: NASA Task Load Index. Six 0-100 ratings for mental demand,
  physical demand, time pressure, satisfaction with performance,
  effort, and frustration/stress.
- Q31-36: Borg CR10 perceived exertion. Six 0-10 ratings for overall
  effort, leg tiredness, breathing effort, lifting/carrying parcels,
  traffic/weather stress, and end-of-shift exhaustion.

After cleaning, the file contains 182 rows and 48 columns (the 36
questionnaire items plus their structural columns).

### 2.2 Posture observations

`data/raw/posture_data.xlsx` contains 182 ergonomic observation rows
spread across the workbook's sheets. Each row carries:

- 11 RULA components: `upper_arm`, `lower_arm`, `wrist`,
  `wrist_twist`, `neck_position`, `trunk_position`, `legs`,
  `muscle_a`, `force_a`, `muscle_b`, `force_b`.
- 3 RULA derived scores: `rula_table_a` (Group A score), `rula_table_b`
  (Group B score), `rula_table_c` (final action-level score).
- 8 QEC scores: `qec_back`, `qec_shoulder_arm`, `qec_wrist_hand`,
  `qec_neck`, `qec_driving`, `qec_vibration`, `qec_work_pace`,
  `qec_stress`.

The observation rows do not carry rider identifiers. The pairing to
the survey is the severity-rank merge described in §4.3.

## 3. Phase 1: Data cleaning

Phase 1 (`notebooks/01_data_cleaning.ipynb`) performs the following:

1. Reads the raw CSV with `pandas.read_csv`.
2. Drops rows where every cell is empty.
3. Strips leading and trailing whitespace from every cell.
4. Lower-cases and normalises "Yes"/"yes"/"YES" to "Yes" and
   "No"/"no"/"NO" to "No".
5. Validates that all expected categorical answers fall within the
   permitted option set and reports any out-of-set values.
6. Writes `data/processed/cleaned.csv`.

No imputation is performed at this stage. Missing values, if any,
are left as `NaN` so Phase 2 can decide how to handle them on a
per-column basis.

## 4. Phase 2: Feature engineering

Phase 2 (`notebooks/02_feature_engineering.ipynb`) builds
`data/processed/model_ready.csv` (182 rows x 121 columns).

### 4.1 Ordinal encodings

Categorical bins that have a natural order get integer codes:

- `age_ord`: `<25` -> 0, `25-35` -> 1, `36-45` -> 2, `>=46` -> 3
- `education_ord`: `Middle / Primary school` -> 0, `High school` -> 1,
  `Degree / Master's or higher` -> 2
- `income_ord`: `<10,000` -> 0, `10,000-19,999` -> 1,
  `20,000-35,000` -> 2, `>35,000` -> 3
- `job_duration_ord`: `<6 months` -> 0, `6-12 months` -> 1,
  `12-24 months` -> 2, `>24 months` -> 3
- `work_hours_ord`: `<3 hrs` -> 0, `3-5` -> 1, `6-8` -> 2, `>8` -> 3
- `work_days_ord`: `<3` -> 0, `3-4` -> 1, `5-6` -> 2, `7` -> 3
- `deliveries_ord`: `<=10` -> 0, `11-20` -> 1, `21-30` -> 2,
  `>=31` -> 3
- `rest_break_ord`: `<5 min` -> 0, `5-15` -> 1, `16-30` -> 2,
  `>30 min` -> 3

Phase 2 Step 5b adds seven additional ranks:

- `gender_rank`: `Male` -> 1, `Female` -> 2
- `region_rank`: `Local` -> 1, `Non-Local` -> 2
- `marital_rank`: `Unmarried` -> 0, `Married` -> 1
- `platform_rank`: `Blinkit` -> 1, `Zepto` -> 2, `Both` -> 3
- `break_type_rank`: `Uneven` -> 0, `Even` -> 1
- `tobacco_ord`: `Never` -> 0, `Former User` -> 1, `Occasionally` -> 2,
  `Regularly` -> 3
- `alcohol_ord`: same scale as tobacco

### 4.2 Numeric midpoints

Bin ranges that need a number for an arithmetic formula get a
sensible midpoint:

- `work_hours_num`: `<3 hrs` -> 2, `3-5` -> 4, `6-8` -> 7, `>8` -> 9
- `deliveries_num`: `<=10` -> 5, `11-20` -> 15, `21-30` -> 25,
  `>=31` -> 35
- `work_days_num`: `<3` -> 2, `3-4` -> 3.5, `5-6` -> 5.5, `7` -> 7
- `rest_break_num`: `<5 min` -> 2.5, `5-15` -> 10, `16-30` -> 23,
  `>30 min` -> 40

### 4.3 Vehicle and carrying mode ranks

- `vehicle_rank`: `Scooter` -> 1, `Motor bike` -> 2 (motorbikes
  transmit more vibration than scooters)
- `carrying_contact_rank`: `Bike storage / carrier` -> 1, `Backpack` ->
  2, `Bike handle` -> 3, `Handheld` -> 4 (ordered from least to most
  body contact)

### 4.4 Binary aliases

Phase 2 Step 4b creates short-named copies of the 18 Yes/No survey
items so the feature pool remains readable. The originals (long
survey-question strings) are kept as columns; the new short names are
added alongside:

- `nmq_neck`, `nmq_shoulders`, `nmq_upper_back`, `nmq_lower_back`,
  `nmq_elbows`, `nmq_wrists_hands`, `nmq_hips_thighs`, `nmq_knees`,
  `nmq_ankles_feet`
- `d7_neck`, `d7_lower_back`, `d7_knees`, `d7_wrist_hands`
- `out_reduced_perf`, `out_taken_leave`, `out_consulted_doctor`,
  `out_riding_worsens`, `out_carrying_worsens`

### 4.5 Composite scores

**Workload score.** Mean of the six NASA-TLX items, with the
satisfaction item (Q28) reversed so that 100 always means heavy load:

```
workload_score = (mental + physical + time_pressure
                  + (100 - satisfied)
                  + effort + frustration) / 6
```

In the web form the satisfaction slider is re-labelled as
"dissatisfied" so the user sees a single load-direction scale and the
reversal is no longer needed at the form layer.

**Fatigue score.** Simple mean of the six Borg CR10 items:

```
fatigue_score = (overall + legs + breathing
                 + lifting + traffic + exhaustion) / 6
```

**Force exertion.** The Borg lifting/carrying item by itself:

```
force_exertion = borg_lifting
```

**Vibration index.** Vehicle type times working hours:

```
vibration_index = vehicle_rank * work_hours_num
```

This ranges from 2 (scooter, less than 3 hours) to 18 (motorbike,
more than 8 hours).

### 4.6 Interaction features

Five product-form interactions are added so tree models can pick up
non-additive effects:

- `workload_x_fatigue = workload_score * fatigue_score / 100`
- `workload_x_age     = workload_score * age_ord / 10`
- `force_x_age        = force_exertion * age_ord`
- `fatigue_x_jobdur   = fatigue_score * job_duration_ord`
- `deliv_x_days       = deliveries_num * work_days_num`

The `/100` and `/10` divisions keep the resulting interaction values
roughly in single-digit ranges so they do not dominate the feature
scale.

### 4.7 Outcome variable

```
discomfort = 1  if any nmq_* == 1, else 0
```

This is the binary outcome used by Phase 5 (chi-square, logistic
regression). It is not used as an input to any of the six Stage-2
classifiers.

### 4.8 Severity-rank merge for posture observations

The posture observations do not carry rider IDs. Phase 2 Step 8
performs a rank-to-rank merge:

1. Compute a per-rider exposure-severity score:

```
exposure_severity = (nmq_count / nmq_count.max()
                     + fatigue_score / fatigue_score.max()
                     + work_hours_num / work_hours_num.max())
```

where `nmq_count` is the count of "Yes" answers across the 9 NMQ
12-month items.

2. Rank riders by `exposure_severity` descending (`method='first'`
   for tie-breaking), giving each rider a rank 1 to 182.
3. Concatenate the posture xlsx sheets and drop any rows where
   `rula_table_c` is missing. Fill remaining NaN cells in the
   muscle/force columns with 0 (the "no static or repetitive
   component" default for the standard worksheet).
4. Sort the posture rows by `rula_table_c` descending and assign
   posture rank 1 to 182.
5. Inner-join survey rows and posture rows on the shared rank
   column. Every rider ends up paired with one posture observation.

The implication: a rider's "own" RULA score is approximate, not a
direct measurement of that specific rider. This is discussed under
Limitations.

## 5. Phase 3: Risk scoring

Phase 3 (`notebooks/03_risk_scoring.ipynb`) applies the following
deterministic rules and writes `data/processed/risk_profile.csv`.

### 5.1 Force

Borg CR10 action levels on `force_exertion`:

- `force_exertion in [0, 3]` -> Low
- `force_exertion in [4, 6]` -> Medium
- `force_exertion in [7, 10]` -> High

Sample distribution: Low 90, Medium 57, High 35.

### 5.2 Repetition

Deliveries per hour:

```
deliveries_per_hour = deliveries_num / work_hours_num
```

Earlier pipeline versions used `pd.qcut(deliveries_per_hour, q=3)`.
The 66.7th percentile fell on 3.889 dph (= 35 / 9, the worst real
combination), and 55 of 182 riders tied at that value. `pd.qcut` is
right-inclusive at the upper edge, so all 55 tied riders landed in
Medium. The Stage-2 model could not predict High for the worst real
combination no matter what features it was given. Phase 3 now uses
fixed cuts:

```
deliveries_per_hour <= 2.5  -> Low
2.5 < dph < 3.75            -> Medium
dph >= 3.75                 -> High
```

Implemented as `pd.cut(dph, bins=[-0.01, 2.5, 3.75, dph.max() + 0.01],
labels=[Low, Medium, High], include_lowest=True)`.

Sample distribution: Low 26, Medium 82, High 74.

### 5.3 Duration

Continuous riding hours:

- `work_hours_num <= 5` -> Low
- `work_hours_num in [6, 7]` -> Medium
- `work_hours_num > 7` -> High

Sample distribution: Low 37, Medium 56, High 89.

### 5.4 Vibration

`vibration_index = vehicle_rank * work_hours_num`. Binned by sample
tercile via `pd.qcut(q=3, duplicates='drop')`.

Sample distribution: Low 67, Medium 68, High 47.

### 5.5 Contact Stress

```
contact_stress_index = carrying_contact_rank
                       * work_hours_num
                       * (1 + 0.1 * age_ord)
```

Binned by sample tercile via `pd.qcut(q=3, duplicates='drop')`.

Sample distribution: Low 68, Medium 58, High 56.

### 5.6 Posture

RULA Table C action levels on `rula_table_c`:

- `rula_table_c in [1, 2]` -> Low
- `rula_table_c in [3, 4]` -> Medium
- `rula_table_c >= 5` -> High

Sample distribution: Low 0, Medium 29, High 153. The minimum
`rula_table_c` in the dataset is 3, which explains the empty Low
bucket; the Posture model is therefore a binary Medium vs High
classifier, not a 3-class classifier.

## 6. Phase 4: Exploratory data analysis

Phase 4 (`notebooks/04_eda.ipynb`) produces six figures and writes
them to `outputs/figures/`:

- `demographics.png`: count plots of gender, age band, platform,
  vehicle, carrying mode.
- `nordic_prevalence.png`: horizontal bar chart of 12-month
  prevalence per body area, sorted descending.
- `risk_factor_distribution.png`: stacked bar of Low/Medium/High
  counts per factor.
- `discomfort_by_demographic.png`: discomfort prevalence broken down
  by age, gender, vehicle, carrying mode.
- `risk_vs_discomfort.png`: per-factor bar of discomfort prevalence
  within each risk band.
- `correlation_heatmap.png`: Pearson correlation matrix across the
  numeric feature pool, masked above the diagonal.

## 7. Phase 5: Statistical analysis

Phase 5 (`notebooks/05_stats.ipynb`) runs two analyses.

### 7.1 Chi-square test (factor vs discomfort)

For each of the six risk factors, a 2 x 3 contingency table is
built (discomfort = 0/1 vs risk = Low/Medium/High) and the
chi-square test of independence is run with
`scipy.stats.chi2_contingency` at significance threshold p < 0.05.

Results:

| Factor | chi-square | p | Significant |
|---|---|---|---|
| Posture | 45.67 | <0.001 | yes |
| Force | 6.72 | 0.035 | yes |
| Duration | 0.62 | 0.73 | no |
| Vibration | 0.60 | 0.74 | no |
| Contact Stress | 0.54 | 0.76 | no |
| Repetition | 0.42 | 0.81 | no |

The very large effect on Posture partly reflects the severity-rank
merge (see Limitations).

### 7.2 Multivariable logistic regression

`statsmodels.api.Logit` fit with discomfort as outcome and the
following predictors: workload_score, age_ord, job_duration_ord,
fatigue_score, income_ord, education_ord, deliveries_num,
work_hours_num, vehicle_rank, carrying_contact_rank, gender_rank.

Significant predictors (p < 0.05) reported with odds ratio and 95%
confidence interval:

| Predictor | OR | 95% CI | p |
|---|---|---|---|
| Workload score (per unit) | 1.06 | 1.02 to 1.09 | 0.0005 |
| Age (per band) | 3.58 | 1.70 to 7.56 | 0.0008 |
| Job duration (per band) | 2.89 | 1.54 to 5.41 | 0.001 |
| Fatigue score (per unit) | 1.43 | 1.13 to 1.80 | 0.003 |
| Income (per band) | 2.00 | 1.25 to 3.20 | 0.004 |
| Education (per band) | 0.33 | 0.12 to 0.94 | 0.04 |
| Deliveries per day | 1.05 | 1.00 to 1.10 | 0.045 |

The model converges in 7 iterations; Pearson residuals are inspected
for outliers; the Hosmer-Lemeshow test is not run because the sample
size and binary outcome distribution make it unreliable here.

## 8. Phase 6: Machine learning modelling

Phase 6 (`notebooks/06_modeling.ipynb`) trains a classifier for each
of the six targets.

### 8.1 Feature pool

The survey feature pool used by all six targets has 44 features:

```python
feature_pool = [
    'workload_score', 'fatigue_score',
    'age_ord', 'income_ord', 'education_ord', 'job_duration_ord',
    'work_hours_num', 'work_days_num', 'deliveries_num', 'rest_break_num',
    'vehicle_rank', 'carrying_contact_rank',
    'force_exertion', 'vibration_index',
    'workload_x_fatigue', 'workload_x_age', 'force_x_age',
    'fatigue_x_jobdur', 'deliv_x_days',
    'gender_rank', 'region_rank', 'marital_rank', 'platform_rank',
    'break_type_rank', 'tobacco_ord', 'alcohol_ord',
    'nmq_neck', 'nmq_shoulders', 'nmq_upper_back', 'nmq_lower_back',
    'nmq_elbows', 'nmq_wrists_hands', 'nmq_hips_thighs', 'nmq_knees',
    'nmq_ankles_feet',
    'd7_neck', 'd7_lower_back', 'd7_knees', 'd7_wrist_hands',
    'out_reduced_perf', 'out_taken_leave', 'out_consulted_doctor',
    'out_riding_worsens', 'out_carrying_worsens',
]
```

Posture additionally receives 11 RULA components and 8 QEC scores:

```python
rula_components = [
    'upper_arm', 'lower_arm', 'wrist', 'wrist_twist',
    'neck_position', 'trunk_position', 'legs',
    'muscle_a', 'force_a', 'muscle_b', 'force_b',
]
qec_scores = [
    'qec_back', 'qec_shoulder_arm', 'qec_wrist_hand', 'qec_neck',
    'qec_driving', 'qec_vibration', 'qec_work_pace', 'qec_stress',
]
```

### 8.2 Per-target exclusions

To avoid trivial label leakage, each target excludes the inputs that
define its own Stage-1 rule:

| Target | Excluded | Final feature count |
|---|---|---|
| Force | `force_exertion`, `force_x_age` | 42 |
| Repetition | `deliveries_num`, `work_hours_num`, `deliv_x_days` | 41 |
| Duration | `work_hours_num`, `vibration_index` | 42 |
| Vibration | `vibration_index`, `vehicle_rank`, `work_hours_num` | 41 |
| Contact Stress | `carrying_contact_rank`, `work_hours_num` | 42 |
| Posture | (none from the survey pool) | 44 + 11 + 8 = 63 |

`vibration_index` had to be added to the Duration exclusion list
after an earlier run reported 100 percent CV accuracy. The trees
were reconstructing `work_hours_num` from `vibration_index =
vehicle_rank * work_hours_num`. The fix and result are documented in
the Limitations section.

For Posture, the derived RULA Table A, B, and C scores are NOT
included because `posture_risk` is computed by binning
`rula_table_c`. Including any of them would be direct leakage. The
11 components and 8 QEC scores are included because they are the
raw inputs the observer recorded; the model has to learn the lookup
relationships between them and the Stage-1 label.

### 8.3 The seven candidate algorithms

For each of the six targets we evaluate seven algorithms and pick the
best by F1 macro.

**LogisticRegression** (`sklearn.linear_model`). Linear model that
fits log-odds of class membership via maximum likelihood with L2
regularisation by default. Configuration: `class_weight='balanced'`
to weight minority classes inversely to their frequency,
`max_iter=2000` to ensure convergence on this dataset,
`random_state=42`. The tuned hyperparameter is the inverse
regularisation strength `C` over `{0.1, 1.0, 10.0}`.

**DecisionTreeClassifier** (`sklearn.tree`). A single CART tree that
recursively splits the feature space to maximise child-node purity
(Gini impurity by default). Configuration: `class_weight='balanced'`,
`random_state=42`. Tuned: `max_depth` over `{3, 5, 7}` and
`min_samples_leaf` over `{1, 3, 5}` to control overfitting on the
182-row sample.

**RandomForestClassifier** (`sklearn.ensemble`). A bagging ensemble
of CART trees, each trained on a bootstrap sample of the training
data and each split considering a random subset of features. The
class prediction is the modal class across trees. Configuration:
`class_weight='balanced'`, `random_state=42`. Tuned: `n_estimators`
over `{300, 500}` and `max_depth` over `{5, 10, None}`.

**ExtraTreesClassifier** (`sklearn.ensemble`). Like Random Forest
but each split threshold is chosen at random instead of via the
best Gini reduction. This further reduces variance at the cost of a
small bias increase, often helpful on small samples. Configuration
and grid identical to Random Forest.

**HistGradientBoostingClassifier** (`sklearn.ensemble`). A
histogram-binned implementation of gradient boosting. Each tree fits
the negative gradient of the cross-entropy loss with respect to the
current ensemble prediction. Categorical features can be handled
natively but we one-hot encode everything upstream so this is not
used. Configuration: `random_state=42`. Tuned: `max_depth` over
`{3, 5, None}` and `learning_rate` over `{0.05, 0.1}`.

**XGBClassifier** (`xgboost`). The XGBoost gradient-boosted trees
implementation, which adds L1/L2 regularisation on leaf weights and
shrinkage. Configuration: `eval_metric='mlogloss'` for multi-class
log-loss tracking, `verbosity=0`, `random_state=42`. Tuned:
`n_estimators` over `{200, 400}`, `max_depth` over `{3, 4, 6}`, and
`learning_rate` over `{0.05, 0.1}`.

**StackingClassifier** (`sklearn.ensemble`). A meta-ensemble whose
final estimator (Logistic Regression with `class_weight='balanced'`,
`max_iter=2000`, `random_state=42`) is trained on the out-of-fold
predictions of four base learners: a RandomForest (`n_estimators=300`,
`max_depth=8`), an ExtraTrees (same), an XGBoost (`n_estimators=300`,
`max_depth=4`, `learning_rate=0.1`), and a HistGBM (`max_depth=5`,
`learning_rate=0.1`). Internal stacking uses `cv=3`. No additional
hyperparameter grid is searched at the stacking level; the base
learners' configurations are fixed.

### 8.4 SMOTE oversampling

SMOTE (Synthetic Minority Over-sampling Technique) generates synthetic
training examples for minority classes by linearly interpolating
between an existing minority sample and one of its k nearest minority
neighbours. We use `imblearn.over_sampling.SMOTE` inside an
`imblearn.Pipeline` so the resampling happens inside every CV fold,
never on the held-out validation data.

The `k_neighbors` parameter is set per target so it never exceeds
the smallest training-class size minus one. The formula is:

```python
min_class = min(Counter(y).values())
k = max(1, min(5, int(min_class * 0.8) - 1))
```

The `* 0.8` factor accounts for the 4/5 training fraction inside a
5-fold cross-validation. The `max(1, ...)` floor prevents
`k_neighbors=0` in degenerate cases.

### 8.5 Pipeline composition

Each candidate algorithm is wrapped in:

```python
pipe = ImbPipeline([
    ('smote', SMOTE(random_state=42, k_neighbors=k)),
    ('clf',   model),
])
```

This pipeline is then handed to `GridSearchCV` so the parameter grid
prefixes (`clf__C`, `clf__max_depth`, etc.) target the classifier
step inside the pipeline.

### 8.6 Cross-validation strategy

`StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`
preserves class proportions in every fold. For each fold:

1. SMOTE oversamples the training fold to balance classes.
2. The classifier is fit on the oversampled training fold.
3. The classifier is evaluated on the held-out validation fold.
4. The validation fold is left untouched by SMOTE so the reported
   metrics reflect performance on the natural class distribution.

### 8.7 Hyperparameter tuning

`GridSearchCV` is run with:
- `scoring='f1_macro'`
- `cv=StratifiedKFold(5, shuffle=True, random_state=42)`
- `n_jobs=-1`
- `refit=False`

We use `refit=False` so the grid search returns the best parameter
set without retraining on the full dataset. We then explicitly refit
the pipeline with the chosen parameters in a separate
`cross_validate` call that records the full metric set
(`accuracy`, `f1_macro`, `precision_macro`, `recall_macro`,
`train_accuracy`).

### 8.8 Model selection and persistence

For each target, the algorithm with the highest `cv_f1_macro` is
selected. The selected pipeline is refit on the full sample with the
tuned hyperparameters and a SMOTE `k_neighbors` recomputed against
the full class distribution. The fitted pipeline is saved to
`outputs/models/best_<factor>.pkl` as a dict:

```python
joblib.dump({
    'model': pipe,                      # fitted ImbPipeline
    'features': feats,                  # list of feature names
    'classes': sorted(set(data[target])),  # original 0/1/2 codes
}, out_path)
```

The `features` list is what `src/predict.py` uses to index the input
dict. The `classes` list is what maps the LabelEncoded model output
back to the original 0/1/2 codes (this matters specifically for the
Posture model, where the present codes are `[1, 2]` only).

### 8.9 Output tables

Phase 6 writes:
- `outputs/tables/cv_results.csv`: every target x model combination
  with mean and std of `cv_accuracy`, `cv_f1_macro`,
  `cv_precision_macro`, `cv_recall_macro`, `train_accuracy`, and
  `overfit_gap = train_accuracy - cv_accuracy`.
- `outputs/tables/best_models.csv`: one row per target listing the
  selected model and its headline metrics.
- `outputs/tables/phase6_summary.csv`: `best_models` plus an
  `overfit_flag` column for `overfit_gap > 0.15`.

## 9. Phase 7: Evaluation

Phase 7 (`notebooks/07_evaluation.ipynb`) takes the best model per
target and produces confusion matrices, ROC curves, and feature
importance, using `cross_val_predict` so the predictions are honest
out-of-fold values.

### 9.1 Confusion matrices

`sklearn.metrics.confusion_matrix(y_true, y_pred, labels=present_codes)`
produces a square matrix. Rows are true classes, columns are
predicted classes. The figure `outputs/figures/confusion_matrices.png`
arranges the six matrices in a 2x3 grid with one matrix per target.
The data behind the figure is saved to
`outputs/tables/confusion_matrices.csv` in long form.

### 9.2 Classification reports

`sklearn.metrics.classification_report(y_true, y_pred,
target_names=label_names, output_dict=True, zero_division=0)`
returns precision, recall, F1, and support per class plus macro
and weighted averages. The full long-form output is saved to
`outputs/tables/classification_reports.csv`.

### 9.3 ROC curves and macro AUC

For each target, the best model is wrapped in a one-vs-rest setup
and `predict_proba` outputs are computed via `cross_val_predict`
with `method='predict_proba'`. For each class:

```python
fpr, tpr, _ = roc_curve(y_true == class_code, y_proba[:, class_idx])
auc = auc(fpr, tpr)
```

Per-class AUC is saved to `outputs/tables/roc_auc.csv`. Macro AUC
is the simple mean across classes and is reported in
`outputs/tables/phase7_summary.csv`. The figure
`outputs/figures/roc_curves.png` plots all classes for all six
targets in a 2x3 grid.

### 9.4 Feature importance

For tree-based models (`RandomForest`, `ExtraTrees`, `HistGBM`,
`XGBoost`), feature importance is read directly from
`clf.feature_importances_`. For Logistic Regression it is read from
`abs(clf.coef_)`. For Stacking the importance comes from the
final-estimator coefficients applied to the base-learner outputs.
The figure `outputs/figures/feature_importance.png` plots the top
10 features per target.

## 10. The web application

`app/streamlit_app.py` is the interactive demo. It loads the six
saved bundles once via `@st.cache_resource` and exposes a form with
six sections that together cover every column in the CSV and xlsx.

### 10.1 Form layout

- Section 1 (Q1-17): demographics, lifestyle, work pattern, vehicle,
  carrying. Single-column selectboxes laid out across three
  Streamlit columns.
- Section 2 (Q18-24): 9 NMQ 12-month radios, 4 seven-day radios, 5
  follow-up radios.
- Section 3 (Q25-30): six NASA-TLX 0-100 sliders. Q28 is rephrased
  as "How dissatisfied" so all six sliders run in load-direction
  and the user is not asked to mentally invert one of them.
- Section 4 (Q31-36): six Borg CR10 0-10 sliders.
- Section 5: 11 RULA component selectboxes with min/max ranges
  matched to the standard worksheet, plus help text per item.
- Section 6: 8 QEC `st.number_input` fields with min/max matched to
  the observed ranges in the training data.

### 10.2 Encoding

`encode_rider(raw)` returns a single dict of all engineered features.
Demographic and lifestyle selections are looked up in the same
mapping dicts that Phase 2 uses. Workload and fatigue scores are
computed from the slider values. Interaction features are computed
inline. NMQ, 7-day, and outcome radios are converted to 0/1. RULA
and QEC values are passed through.

### 10.3 Prediction

`predict_risks(features, models)` builds a single-row DataFrame,
selects the relevant feature subset per target using the saved
bundle's `features` list, calls `model.predict()`, then maps the
returned class index back to the original code via the bundle's
`classes` list, and finally to the Low/Medium/High label.

```python
pred_idx = int(bundle['model'].predict(df_row[bundle['features']])[0])
code = int(bundle['classes'][pred_idx])
out[factor] = LABELS[code]
```

### 10.4 Output rendering

The result is displayed as a styled table with badge emojis per
risk level, a summary banner that flags high-burden profiles
(`>= 3` factors at High triggers an error banner; `>= 4` Medium-or-
High triggers a warning banner; otherwise a success banner). An
expandable JSON view shows the exact 55-63 feature values that were
fed to the models.

## 11. Reproducibility

- Random seed: `RNG = 42` is the single shared seed used in
  `StratifiedKFold`, `SMOTE`, all sklearn classifiers, and XGBoost.
- Library versions are pinned in the README install command:
  pandas, numpy, scikit-learn, scipy, matplotlib, seaborn, xgboost,
  statsmodels, imbalanced-learn, python-pptx, joblib, streamlit,
  python-docx, openpyxl.
- The full pipeline runs end to end from raw inputs with:

```
python -m nbconvert --to notebook --execute notebooks/01_data_cleaning.ipynb --output 01_data_cleaning.ipynb
# ... repeat for 02 .. 07
python src/build_results_deck.py
python src/build_project_doc.py
```

- All saved artefacts (CSV tables, PNG figures, PKL models, the
  PPTX deck, the DOCX write-up) are regenerated bit-identically
  on re-run (modulo PNG metadata timestamps inserted by matplotlib).

## 12. Limitations (paper-relevant)

1. **Self-report bias.** NMQ pain, NASA-TLX workload, Borg CR10
   fatigue, and the demographic items are all self-reported.
2. **Posture per-rider linkage is approximate** because of the
   severity-rank merge in §4.8; the 97 percent Posture accuracy is
   the upper bound the linked data can support.
3. **Repetition binning** had a tercile-boundary degeneracy that
   the qcut-to-fixed-cut fix corrected; the resulting drop from 74
   percent to 62 percent accuracy is the honest trade.
4. **Duration leakage** through `vibration_index` was identified
   and fixed; the original 100 percent CV accuracy is disclosed
   only as the artefact that prompted the fix.
5. **Cross-sectional design.** No causal inference is possible.
6. **Sample size and region.** n = 182 is small for multivariable
   ML; the cross-validation standard deviation is around 5
   percentage points. All riders came from one regional platform
   deployment.
7. **Proxy inputs.** Vibration is approximated as `vehicle_rank *
   work_hours_num`; Repetition is approximated as
   deliveries-per-hour. Both are operationalisations that map onto
   what the survey can capture, not direct measurements.
8. **Posture's empty Low class.** The minimum `rula_table_c` in the
   sample is 3, so no rider falls in the Low band; the Posture
   model is in practice a binary Medium-vs-High classifier.

## 13. Discussion points worth raising in the paper

- The two-stage design (deterministic labelling, then supervised
  learning) is what makes the pipeline auditable. Stage 1 can be
  reviewed by an ergonomist; Stage 2 can be reviewed by an ML
  reviewer; the two reviews do not interfere with each other.
- SMOTE inside the imblearn pipeline is the right way to handle
  class imbalance in cross-validation; resampling before splitting
  would leak synthetic minority points into validation folds.
- Macro F1 (not raw accuracy) is the right model-selection metric
  for these targets because every class matters operationally; a
  model that achieves high accuracy by predicting Low for everyone
  is useless as a screening tool.
- The 71-76 percent macro AUC for the five survey-derived factors
  is the more informative summary than 58-62 percent accuracy
  because it shows the models still rank riders correctly even
  when they get the exact class wrong.
- Posture's 97 percent accuracy is a methodological consequence of
  giving the model the observation inputs that define the target,
  even after excluding the derived Table scores. A future study
  with proper per-rider linkage would settle slightly lower.
- The Repetition binning fault that hid the worst real combination
  from the Stage-2 model is a generally useful caution for
  cross-sectional ergonomic studies that use sample terciles.

## 14. Where to look for each number

- Sample profile: `notebooks/04_eda.ipynb`, also figure
  `outputs/figures/demographics.png`.
- NMQ prevalence: `notebooks/04_eda.ipynb`, figure
  `outputs/figures/nordic_prevalence.png`.
- Stage-1 risk distribution: `data/processed/risk_profile.csv`,
  figure `outputs/figures/risk_factor_distribution.png`.
- Chi-square table: `outputs/tables/chi_square.csv`.
- Logistic regression coefficients: `outputs/tables/phase5_summary.csv`.
- Stage-2 CV metrics: `outputs/tables/cv_results.csv`.
- Per-factor best-model headline: `outputs/tables/best_models.csv`.
- Confusion matrices: `outputs/tables/confusion_matrices.csv` (long
  form) and `outputs/figures/confusion_matrices.png`.
- Per-class precision/recall/F1: `outputs/tables/classification_reports.csv`.
- ROC AUC per class and macro: `outputs/tables/roc_auc.csv` and
  `outputs/tables/phase7_summary.csv`.
- Feature importance per target: `outputs/tables/feature_importance.csv`
  and figure `outputs/figures/feature_importance.png`.
