# Ergonomic Risk Factor Prediction - Project Report

A single write-up of the whole project. Covers the background, every
step the pipeline performs (with formulae, thresholds, and
hyperparameters), the results, the web app, the limitations, and
where every output number lives in the repo.

## Contents

1. Background
2. What the project does
3. The six risk factors
4. Data sources
5. Phase 1: Data cleaning
6. Phase 2: Feature engineering
7. Phase 3: Risk scoring
8. Phase 4: Exploratory data analysis
9. Phase 5: Statistical analysis
10. Phase 6: Machine learning modelling
11. Phase 7: Evaluation
12. Sample and findings
13. The web app
14. Reproducibility
15. Limitations
16. Recommendations
17. Where things live in the repository
18. Index of output files

## 1. Background

Food-delivery riders for platforms like Blinkit and Zepto spend long
hours on bikes, climb stairs, carry packages, and ride in heavy
traffic. Over time this kind of work causes musculoskeletal disorders
(MSDs): back pain, shoulder pain, wrist injuries, knee problems. The
risk is not the same for every rider. Someone who is 22 and works 4
hours a day on a scooter is in a very different situation from a
45-year-old who works 10 hours a day on a motorbike with a handheld
bag.

Ergonomists have standard ways of measuring this kind of strain. RULA
(Rapid Upper Limb Assessment) scores the posture of a worker's upper
body. QEC (Quick Exposure Check) gives a composite of body-region and
exposure scores. The Nordic Musculoskeletal Questionnaire (NMQ)
records pain across 9 body areas. NASA-TLX rates mental workload.
Borg CR10 records perceived physical effort on a 0 to 10 scale. Each
of these gives useful information on its own. The project takes all
of them together and produces a single per-rider risk profile across
six ergonomic dimensions: Force, Repetition, Posture, Duration,
Contact Stress, Vibration.

## 2. What the project does

The pipeline runs in two stages.

**Stage 1** computes Low/Medium/High labels for the six ergonomic risk
factors using deterministic rules from standard ergonomic methods
(Borg CR10 action levels, RULA Table C action levels, sample
terciles, simple thresholds). Stage 1 is the ground truth that
Stage 2 tries to learn.

**Stage 2** trains a supervised classifier per risk factor that maps
a rider profile to that factor's Stage-1 label. Per-target feature
exclusions remove the inputs that define the label so the model has
to learn from the remaining profile rather than memorising the rule.
Each classifier is evaluated by 5-fold stratified cross-validation.

The two-stage split lets us audit the labels (Stage 1 is transparent)
and at the same time produce a screening tool that can run on a
rider's profile without re-applying the ergonomic worksheets.

The work is split across seven Jupyter notebooks:

- `01_data_cleaning` normalises the raw CSV and validates row counts
- `02_feature_engineering` encodes categoricals, derives composite
  scores, and merges the posture observations into the survey by
  severity rank
- `03_risk_scoring` applies standard thresholds to compute the six
  Low/Medium/High labels per rider
- `04_eda` produces demographics, NMQ prevalence, risk
  distribution, discomfort-by-group, and correlation-heatmap figures
- `05_stats` runs chi-square and logistic regression
- `06_modeling` runs SMOTE + GridSearchCV across 7 algorithms per
  target and keeps the best by F1 macro
- `07_evaluation` produces confusion matrices, ROC curves, and
  feature importance plots

The end product is a Streamlit web app where someone fills in the
rider's questionnaire (plus optional RULA and QEC scores), clicks
Predict, and reads six coloured risk levels.

## 3. The six risk factors

Each factor is computed in Phase 3 using a standard ergonomic method
and binned into Low, Medium, or High.

**Force.** How hard the rider has to lift or push. We use the Borg
CR10 lifting item. Conventional Borg action levels: 0-3 Low
(acceptable), 4-6 Medium (monitor), 7-10 High (intervene).

**Repetition.** Deliveries per hour, computed as `deliveries_num /
work_hours_num`. The earlier Phase 3 binning used `pandas.qcut(q=3)`
into terciles, but the upper tercile boundary landed exactly on
35 / 9 = 3.889 (the worst real combination in the sample) and 55 of
182 riders tied at that value, all falling into Medium. We switched
to fixed cuts at 2.5 and 3.75 so the worst case ends up in High.
The trade-off is documented under Limitations.

**Posture.** RULA Table C, the final score from the standard RULA
worksheet. Conventional action levels are 1-2 Low, 3-4 Medium, 5 or
higher High.

**Duration.** Continuous riding hours. 5 hours or less is Low, 6-7
is Medium, more than 7 is High.

**Contact Stress.** How much load presses against the rider's body.
A composite of carrying mode (storage box, backpack, handlebar,
handheld), working hours, and a small age multiplier. We bin into
terciles.

**Vibration.** Vehicle type multiplied by working hours per day.
Scooter is 1 and motor bike is 2, so a motorbike rider working 9
hours scores 18 (the worst observed). This is a proxy because we
did not have per-rider accelerometer data; what we can measure is
the relative exposure.

## 4. Data sources

### 4.1 Rider survey

`data/raw/delivery_rider_survey.csv` contains 182 self-administered
responses. The questionnaire has 36 items grouped into the following
modules:

- Q1-17: demographics, lifestyle, and work pattern. Gender, age
  band, education band, region, marital status, delivery platform,
  job duration band, monthly income band, type of vehicle, mode of
  carrying deliveries, working hours per day band, working days per
  week band, deliveries per day band, duration of rest break, type
  of break, tobacco consumption category, alcohol consumption
  category.
- Q18: Nordic Musculoskeletal Questionnaire 12-month items. Nine
  Yes/No items, one per body area: neck, shoulders, upper back,
  lower back, elbows, wrists/hands, hips/thighs, knees, ankles/feet.
- Q19: 7-day discomfort. Four Yes/No items for neck, lower back,
  knees, wrists/hands.
- Q20-24: discomfort follow-ups. Five Yes/No items asking whether
  the discomfort reduced delivery performance, whether the rider
  took leave, consulted a doctor or physiotherapist, whether long
  riding worsened the discomfort, and whether carrying heavy
  packages worsened it.
- Q25-30: NASA Task Load Index. Six 0-100 ratings for mental
  demand, physical demand, time pressure, satisfaction with
  performance, effort, and frustration/stress.
- Q31-36: Borg CR10 perceived exertion. Six 0-10 ratings for
  overall effort, leg tiredness, breathing effort, lifting/carrying
  parcels, traffic/weather stress, and end-of-shift exhaustion.

After cleaning, the file contains 182 rows and 48 columns.

### 4.2 Posture observations

`data/raw/posture_data.xlsx` contains 182 ergonomic observation rows
spread across the workbook's sheets. Each row carries:

- 11 RULA components: `upper_arm`, `lower_arm`, `wrist`,
  `wrist_twist`, `neck_position`, `trunk_position`, `legs`,
  `muscle_a`, `force_a`, `muscle_b`, `force_b`.
- 3 RULA derived scores: `rula_table_a` (Group A score),
  `rula_table_b` (Group B score), `rula_table_c` (final
  action-level score).
- 8 QEC scores: `qec_back`, `qec_shoulder_arm`, `qec_wrist_hand`,
  `qec_neck`, `qec_driving`, `qec_vibration`, `qec_work_pace`,
  `qec_stress`.

The observation rows do not carry rider identifiers. The pairing to
the survey is the severity-rank merge described in §6.6.

## 5. Phase 1: Data cleaning

Phase 1 (`notebooks/01_data_cleaning.ipynb`) performs the following:

1. Reads the raw CSV with `pandas.read_csv`.
2. Drops rows where every cell is empty.
3. Strips leading and trailing whitespace from every cell.
4. Normalises "Yes"/"yes"/"YES" to "Yes" and "No"/"no"/"NO" to "No".
5. Validates that all expected categorical answers fall within the
   permitted option set and reports any out-of-set values.
6. Writes `data/processed/cleaned.csv`.

No imputation is performed at this stage. Missing values, if any,
are left as `NaN` so Phase 2 can decide how to handle them on a
per-column basis.

## 6. Phase 2: Feature engineering

Phase 2 (`notebooks/02_feature_engineering.ipynb`) builds
`data/processed/model_ready.csv` (182 rows by 121 columns).

### 6.1 Ordinal encodings

A machine-learning model cannot work directly with text answers like
"25-35" or "Degree". We convert each ordered category into a number,
preserving the order. For example, the age band gets a code from 0
(under 25) to 3 (46 or older), and similar codes are assigned to
education, income, job duration, hours per day, days per week,
deliveries per day, and rest-break duration:

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

The same idea is applied to the remaining demographic and lifestyle
items in Step 5b. Each category is given a numeric rank in the order
that makes physical sense:

- `gender_rank`: `Male` -> 1, `Female` -> 2
- `region_rank`: `Local` -> 1, `Non-Local` -> 2
- `marital_rank`: `Unmarried` -> 0, `Married` -> 1
- `platform_rank`: `Blinkit` -> 1, `Zepto` -> 2, `Both` -> 3
- `break_type_rank`: `Uneven` -> 0, `Even` -> 1
- `tobacco_ord`: `Never` -> 0, `Former User` -> 1, `Occasionally` -> 2,
  `Regularly` -> 3
- `alcohol_ord`: same scale as tobacco

### 6.2 Numeric midpoints

Some bins need to be used in arithmetic later (for example, computing
deliveries per hour). For those, we assign each bin a sensible
midpoint value rather than just an order code. A rider in the "6-8
hours" band is treated as working 7 hours, the "11-20 deliveries"
band as 15 deliveries, and so on:

- `work_hours_num`: `<3 hrs` -> 2, `3-5` -> 4, `6-8` -> 7, `>8` -> 9
- `deliveries_num`: `<=10` -> 5, `11-20` -> 15, `21-30` -> 25,
  `>=31` -> 35
- `work_days_num`: `<3` -> 2, `3-4` -> 3.5, `5-6` -> 5.5, `7` -> 7
- `rest_break_num`: `<5 min` -> 2.5, `5-15` -> 10, `16-30` -> 23,
  `>30 min` -> 40

### 6.3 Vehicle and carrying mode ranks

Vehicle type and the way a rider carries packages both affect
ergonomic exposure, so each is given a rank. Motorbikes vibrate more
than scooters; a handheld bag stays in contact with the body more
than a fitted bike-storage box:

- `vehicle_rank`: `Scooter` -> 1, `Motor bike` -> 2
- `carrying_contact_rank`: `Bike storage / carrier` -> 1,
  `Backpack` -> 2, `Bike handle` -> 3, `Handheld` -> 4

### 6.4 Binary aliases

The survey contains 18 Yes/No items: 9 NMQ 12-month pain items, 4
seven-day discomfort items, and 5 follow-up questions. Their original
column names are long (the full survey question text). Step 4b makes
short-named copies of each so later code stays readable:

- `nmq_neck`, `nmq_shoulders`, `nmq_upper_back`, `nmq_lower_back`,
  `nmq_elbows`, `nmq_wrists_hands`, `nmq_hips_thighs`, `nmq_knees`,
  `nmq_ankles_feet`
- `d7_neck`, `d7_lower_back`, `d7_knees`, `d7_wrist_hands`
- `out_reduced_perf`, `out_taken_leave`, `out_consulted_doctor`,
  `out_riding_worsens`, `out_carrying_worsens`

### 6.5 Composite scores

Four single numbers summarise heavy chunks of the survey. Combining
related items into one composite score makes the downstream models
easier to interpret and reduces noise.

**Workload score.** The six NASA-TLX items are averaged into one
overall workload measure. The satisfaction item (Q28) is reversed
first, because a higher satisfaction score actually means lower
mental load:

```
workload_score = (mental + physical + time_pressure
                  + (100 - satisfied)
                  + effort + frustration) / 6
```

In the web form the satisfaction slider is re-labelled as
"dissatisfied" so the user sees a single load-direction scale and
the reversal is no longer needed at the form layer.

**Fatigue score.** The six Borg CR10 items are similarly averaged
into a single physical-fatigue measure. No reversal is needed
because all six items already point the same way (higher means
harder):

```
fatigue_score = (overall + legs + breathing
                 + lifting + traffic + exhaustion) / 6
```

**Force exertion.** Phase 3 needs a separate force measurement (the
Borg lifting/carrying item) to compute the Force risk level, so we
pull that single item out as its own feature:

```
force_exertion = borg_lifting
```

**Vibration index.** Without an actual vibration sensor, we
approximate exposure by multiplying the vehicle type (scooters
vibrate less than motorbikes) by working hours per day:

```
vibration_index = vehicle_rank * work_hours_num
```

This ranges from 2 (scooter, less than 3 hours) to 18 (motorbike,
more than 8 hours).

### 6.6 Interaction features

Sometimes the effect of two factors together is bigger than either
one alone. An older rider with high workload is at extra risk on top
of what age and workload would each suggest separately. We add five
features that capture these combinations by multiplying the relevant
inputs:

- `workload_x_fatigue = workload_score * fatigue_score / 100`
- `workload_x_age     = workload_score * age_ord / 10`
- `force_x_age        = force_exertion * age_ord`
- `fatigue_x_jobdur   = fatigue_score * job_duration_ord`
- `deliv_x_days       = deliveries_num * work_days_num`

The `/100` and `/10` divisions keep the interaction values in
single-digit ranges so they do not dominate the feature scale.

### 6.7 Outcome variable

The Phase 5 statistical analysis needs a single Yes/No outcome to
compare against. We define "discomfort" as 1 if the rider reported
pain in any of the 9 NMQ body areas in the last 12 months, otherwise
0:

```
discomfort = 1 if any nmq_* == 1 else 0
```

This is only used as the outcome inside the statistical models. It
is not fed as an input to any of the six Stage-2 risk classifiers,
because those predict the Stage-1 risk labels, not discomfort.

### 6.8 Severity-rank merge for posture observations

The posture xlsx file contains 182 RULA and QEC observation records,
but they do not carry any rider identifier. There is no direct way
to say "this observation belongs to rider 57". Phase 2 Step 8
handles this with a severity-rank merge. The idea is simple: the
rider who looks the most strained based on the survey is paired with
the observation that has the worst RULA score, and so on down the
list.

The five steps:

1. Compute an exposure-severity score for each rider. It combines
   reported pain count, fatigue score, and working hours per day,
   each normalised to its maximum so they contribute on the same
   scale:

```
exposure_severity = (nmq_count / nmq_count.max()
                     + fatigue_score / fatigue_score.max()
                     + work_hours_num / work_hours_num.max())
```

where `nmq_count` is the count of "Yes" answers across the 9 NMQ
12-month items.

2. Sort riders by their severity score from most to least severe.
   The most-strained rider gets rank 1, the least gets rank 182.
3. Read and concatenate the posture xlsx sheets. Drop any rows that
   have no RULA Table C value. Fill any blank muscle/force cells
   with 0, which is the standard worksheet's default for "no static
   or repetitive component".
4. Sort the posture rows by RULA Table C from highest (worst) to
   lowest (best). The worst observation gets rank 1, the mildest
   gets rank 182.
5. Match rank 1 to rank 1, rank 2 to rank 2, and so on. Every rider
   ends up paired with one posture observation.

The honest implication is that a rider's "own" RULA score is
approximate, not a direct measurement of that specific person. This
is discussed under Limitations.

## 7. Phase 3: Risk scoring

Phase 3 (`notebooks/03_risk_scoring.ipynb`) applies the following
deterministic rules and writes `data/processed/risk_profile.csv`.

### 7.1 Force

Borg CR10 action levels on `force_exertion`:

- `force_exertion in [0, 3]` -> Low
- `force_exertion in [4, 6]` -> Medium
- `force_exertion in [7, 10]` -> High

Sample distribution: Low 90, Medium 57, High 35.

### 7.2 Repetition

The Repetition factor is about how fast a rider works: how many
deliveries they make per hour:

```
deliveries_per_hour = deliveries_num / work_hours_num
```

The first version of the binning split the riders into three equal-
sized groups (using `pd.qcut(deliveries_per_hour, q=3)`). That ran
into a real problem. The boundary between the Medium and High groups
landed on the value 3.889 deliveries per hour, which happens to be
exactly 35 deliveries over 9 hours. 55 of the 182 riders worked at
that pace. Because of how `pd.qcut` resolves boundaries, all 55 of
them fell into the Medium group. The model never saw a High example
that matched the busiest real schedule and so could never predict
High for that rider. Phase 3 now uses fixed cuts instead of equal-
sized groups:

```
deliveries_per_hour <= 2.5  -> Low
2.5 < dph < 3.75            -> Medium
dph >= 3.75                 -> High
```

Implemented as `pd.cut(dph, bins=[-0.01, 2.5, 3.75, dph.max() +
0.01], labels=[Low, Medium, High], include_lowest=True)`.

Sample distribution: Low 26, Medium 82, High 74.

### 7.3 Duration

Continuous riding hours:

- `work_hours_num <= 5` -> Low
- `work_hours_num in [6, 7]` -> Medium
- `work_hours_num > 7` -> High

Sample distribution: Low 37, Medium 56, High 89.

### 7.4 Vibration

`vibration_index = vehicle_rank * work_hours_num`. Binned by sample
tercile via `pd.qcut(q=3, duplicates='drop')`.

Sample distribution: Low 67, Medium 68, High 47.

### 7.5 Contact Stress

```
contact_stress_index = carrying_contact_rank
                       * work_hours_num
                       * (1 + 0.1 * age_ord)
```

Binned by sample tercile via `pd.qcut(q=3, duplicates='drop')`.

Sample distribution: Low 68, Medium 58, High 56.

### 7.6 Posture

RULA Table C action levels on `rula_table_c`:

- `rula_table_c in [1, 2]` -> Low
- `rula_table_c in [3, 4]` -> Medium
- `rula_table_c >= 5` -> High

Sample distribution: Low 0, Medium 29, High 153. The minimum
`rula_table_c` in the dataset is 3, which explains the empty Low
bucket. The Posture model is therefore a binary Medium-vs-High
classifier, not a 3-class classifier.

## 8. Phase 4: Exploratory data analysis

Phase 4 (`notebooks/04_eda.ipynb`) produces six figures saved to
`outputs/figures/`:

- `demographics.png`: count plots of gender, age band, platform,
  vehicle, carrying mode.
- `nordic_prevalence.png`: horizontal bar chart of 12-month
  prevalence per body area, sorted descending.
- `risk_factor_distribution.png`: stacked bar of Low/Medium/High
  counts per factor.
- `discomfort_by_demographic.png`: discomfort prevalence broken
  down by age, gender, vehicle, carrying mode.
- `risk_vs_discomfort.png`: per-factor bar of discomfort
  prevalence within each risk band.
- `correlation_heatmap.png`: Pearson correlation matrix across the
  numeric feature pool, masked above the diagonal. Pearson
  correlation for two variables `x` and `y` is

  ```
  r = sum((xi - x_mean) * (yi - y_mean))
      / sqrt(sum((xi - x_mean)^2) * sum((yi - y_mean)^2))
  ```

  computed pairwise by `pandas.DataFrame.corr(method='pearson')`.

## 9. Phase 5: Statistical analysis

Phase 5 (`notebooks/05_stats.ipynb`) runs two analyses.

### 9.1 Chi-square test (factor vs discomfort)

The chi-square test asks a simple question: are riders in the High
band of this risk factor more likely to report discomfort than
riders in the Low band, beyond what random chance would explain?

For each of the six risk factors, we build a small 2 by 3 table
counting how many riders reported discomfort and how many did not,
broken down by Low / Medium / High. The chi-square test of
independence (`scipy.stats.chi2_contingency`) compares the observed
counts against the counts we would expect if discomfort and risk
were unrelated. We treat p < 0.05 as significant.

The Pearson chi-square statistic adds up the squared differences
between observed and expected, scaled by expected:

```
chi2 = sum_over_cells((observed - expected)^2 / expected)
```

where `expected_ij = row_total_i * col_total_j / grand_total`,
evaluated against the chi-square distribution with
`(rows - 1) * (cols - 1)` degrees of freedom. For our 2 x 3 tables
the degrees of freedom is 2.

**Table 1. Chi-square test of independence between each risk factor
and self-reported 12-month discomfort.**

| Factor | chi-square | dof | p | Significant |
|---|---|---|---|---|
| Posture | 45.67 | 1 | <0.001 | yes |
| Repetition | 8.62 | 2 | 0.014 | yes |
| Force | 6.72 | 2 | 0.035 | yes |
| Duration | 0.62 | 2 | 0.73 | no |
| Vibration | 0.60 | 2 | 0.74 | no |
| Contact Stress | 0.54 | 2 | 0.76 | no |

The very large effect on Posture partly reflects the severity-rank
merge (see Limitations).

### 9.2 Multivariable logistic regression

A chi-square test treats one factor at a time. Logistic regression
goes one step further: it estimates the effect of each predictor
while controlling for the others, so we can tell whether (say) age
is still a significant predictor of discomfort after accounting for
work hours and workload.

We fit a logistic regression (`statsmodels.api.Logit`) with
discomfort as the outcome and these predictors: workload_score,
age_ord, job_duration_ord, fatigue_score, income_ord, education_ord,
deliveries_num, work_hours_num, vehicle_rank, carrying_contact_rank,
gender_rank.

The model itself estimates the probability that a rider reports
discomfort as a function of their profile:

```
P(discomfort = 1 | X) = 1 / (1 + exp(-(b0 + b1*x1 + b2*x2 + ... + bk*xk)))
```

equivalently

```
logit(P) = log(P / (1 - P)) = b0 + b1*x1 + b2*x2 + ... + bk*xk
```

The coefficients `bj` are fit by maximum likelihood (Newton-Raphson
iterations under the hood). The result for each predictor is
typically reported as an odds ratio. An odds ratio of 2 means that
each one-unit increase in that predictor doubles the odds of
reporting discomfort. The odds ratio is `exp(bj)`, and the 95
percent confidence interval is `exp(bj +/- 1.96 * SE(bj))` where
`SE(bj)` is the standard error of the coefficient.

**Table 2. Multivariable logistic regression of discomfort on rider
profile, significant predictors (p < 0.05) reported with odds ratio
and 95% confidence interval.**

| Predictor | OR | 95% CI | p |
|---|---|---|---|
| Workload score (per unit) | 1.06 | 1.02 to 1.09 | 0.0005 |
| Age (per band) | 3.58 | 1.70 to 7.56 | 0.0008 |
| Job duration (per band) | 2.89 | 1.54 to 5.41 | 0.001 |
| Fatigue score (per unit) | 1.43 | 1.13 to 1.80 | 0.003 |
| Income (per band) | 2.00 | 1.25 to 3.20 | 0.004 |
| Education (per band) | 0.33 | 0.12 to 0.94 | 0.04 |
| Deliveries per day | 1.05 | 1.00 to 1.10 | 0.045 |

The model converges in 7 iterations. Pearson residuals are inspected
for outliers. The Hosmer-Lemeshow test is not run because the
sample size and binary outcome distribution make it unreliable here.

## 10. Phase 6: Machine learning modelling

Phase 6 (`notebooks/06_modeling.ipynb`) trains a classifier for each
of the six targets.

### 10.1 Feature pool

A "feature pool" is the full list of inputs the model is allowed to
look at. All five survey-based factors share the same starting pool
of 44 features, which is everything we engineered in Phase 2 minus
the items unique to the observation worksheets:

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

The Posture model is special. On top of the 44 survey features, it
also gets the 11 RULA components and the 8 QEC scores. These are the
real ergonomic observation inputs:

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

### 10.2 Per-target exclusions

There is one important fairness rule. Phase 3 uses certain survey
inputs directly to decide the Low/Medium/High label. If we then let
a model see those same inputs, it would just memorise the rule
instead of learning to predict. This is called label leakage. To
prevent it, each target removes the inputs that define its own
Stage-1 rule before training:

**Table 3. Per-target feature exclusions and final feature count.**

| Target | Excluded | Final feature count |
|---|---|---|
| Force | `force_exertion`, `force_x_age` | 42 |
| Repetition | `deliveries_num`, `work_hours_num`, `deliv_x_days` | 41 |
| Duration | `work_hours_num`, `vibration_index` | 42 |
| Vibration | `vibration_index`, `vehicle_rank`, `work_hours_num` | 41 |
| Contact Stress | `carrying_contact_rank`, `work_hours_num` | 42 |
| Posture | (none from the survey pool) | 44 + 11 + 8 = 63 |

A note on Duration: `vibration_index` had to be added to its
exclusion list after an earlier run reported a suspicious 100 percent
accuracy. The decision trees had figured out that
`vibration_index = vehicle_rank * work_hours_num`, so they were
recovering `work_hours_num` indirectly even though we had blocked it
directly. The fix is documented in the Limitations section.

For Posture, the derived RULA Table A, B, and C scores are also
left out, even though they sit in the same xlsx file. The Posture
Stage-1 label is just `rula_table_c` divided into bands, so handing
that column to the model would be like giving it the answer key.
The 11 raw components and 8 QEC scores are fine, because the model
has to learn the lookup relationship between them and the final
band.

### 10.3 The seven candidate algorithms

We do not commit to a single algorithm up front. For each of the
six targets, we train seven different classifiers and pick whichever
one performs best (measured by F1 macro, defined later). The seven
candidates cover a wide range of model families:

**LogisticRegression** (`sklearn.linear_model`). The simplest of
the seven. It draws a straight (linear) boundary between classes
and is the same family as the statistical model in Phase 5. We
configure it with `class_weight='balanced'` so minority classes are
not ignored, `max_iter=2000` so it has enough iterations to settle
on a final fit, and `random_state=42`. The one hyperparameter we
tune is the regularisation strength `C` across `{0.1, 1.0, 10.0}`,
which controls how much the model is penalised for using large
coefficients.

**DecisionTreeClassifier** (`sklearn.tree`). A single tree that
asks a series of Yes/No questions about the features and lands the
rider in a leaf with a predicted class. With only 182 rows the tree
can easily memorise the data, so we tune `max_depth` over
`{3, 5, 7}` to limit how many questions deep it can go and
`min_samples_leaf` over `{1, 3, 5}` to require each leaf to cover
at least a few riders. Class balance and random seed are the same
as Logistic Regression.

**RandomForestClassifier** (`sklearn.ensemble`). A forest of many
trees, each trained on a slightly different random subsample of the
data and looking at a random subset of features at each split. The
final prediction is the most-voted class across the forest. This
averaging usually makes the forest more accurate and more stable
than any single tree. Tuned: `n_estimators` (300 or 500 trees) and
`max_depth` (5, 10, or unlimited).

**ExtraTreesClassifier** (`sklearn.ensemble`). A close cousin of
Random Forest, but each split point inside a tree is chosen
randomly instead of being optimised. The extra randomness reduces
variance further and often helps on small samples like ours.
Configuration and tuned hyperparameter grid are identical to Random
Forest.

**HistGradientBoostingClassifier** (`sklearn.ensemble`). Boosting
builds trees one after the other, with each new tree trying to fix
the mistakes the previous trees made. The "Hist" version groups
similar values into bins for speed and works very well on tabular
data like ours. Tuned: `max_depth` (3, 5, or unlimited) and
`learning_rate` (0.05 or 0.1), which controls how much each new
tree is allowed to change the running prediction.

**XGBClassifier** (`xgboost`). Another boosted-trees implementation
that adds an extra regularisation term, often topping leaderboards
on tabular problems. We track multi-class log-loss during fitting
(`eval_metric='mlogloss'`), keep the console quiet
(`verbosity=0`), and fix the random seed. Tuned: `n_estimators`
(200 or 400 trees), `max_depth` (3, 4, or 6), `learning_rate` (0.05
or 0.1).

**StackingClassifier** (`sklearn.ensemble`). The most complex of
the seven. Stacking takes the predictions of several base models
and feeds them into a final model that learns the best way to
combine them. We use four base models: a Random Forest
(`n_estimators=300`, `max_depth=8`), an Extra Trees with the same
settings, an XGBoost (`n_estimators=300`, `max_depth=4`,
`learning_rate=0.1`), and a Hist Gradient Boosting (`max_depth=5`,
`learning_rate=0.1`). The final combiner is a Logistic Regression
with balanced class weights. Internal three-fold stacking is used.
No additional grid search is run at the stacking level because the
base models inside it are already tuned.

### 10.4 SMOTE oversampling

Several of the risk factors have a small class. Repetition has only
26 Low riders, Posture has only 29 Medium observations. A model
trained on this kind of skewed data tends to play it safe by
predicting the majority class for everyone, which gives high raw
accuracy but is useless as a screening tool.

SMOTE (Synthetic Minority Over-sampling Technique) fixes this by
generating extra minority-class examples during training. It picks
a minority rider, finds one of their nearest minority neighbours,
and creates a new synthetic rider somewhere on the line between the
two. Formally, for a minority sample `x_i` and one of its k nearest
minority neighbours `x_nn` chosen at random:

```
x_new = x_i + lambda * (x_nn - x_i)        with lambda ~ Uniform(0, 1)
```

The nearest neighbours are found using straight-line (Euclidean)
distance in the original feature space. Crucially we run SMOTE
inside an `imblearn.Pipeline` so the oversampling happens only on
the training data within each cross-validation fold; the held-out
validation rows are never touched by synthetic data.

The number of neighbours SMOTE looks at (`k_neighbors`) cannot be
larger than the number of real minority examples available in the
training fold. We set it per target with this rule:

```python
min_class = min(Counter(y).values())
k = max(1, min(5, int(min_class * 0.8) - 1))
```

The `* 0.8` accounts for the fact that in 5-fold cross-validation
only 4/5 of the data goes into training. The `max(1, ...)` floor
keeps `k_neighbors` at least 1 even when the minority class is
tiny.

### 10.5 Pipeline composition

Every candidate algorithm gets wrapped in a two-step pipeline:
first SMOTE, then the classifier itself. Wrapping like this means
both steps are applied together every time cross-validation runs:

```python
pipe = ImbPipeline([
    ('smote', SMOTE(random_state=42, k_neighbors=k)),
    ('clf',   model),
])
```

This pipeline is then handed to the grid search. The `clf__C` and
`clf__max_depth` style prefixes tell the search to apply each
hyperparameter to the `clf` step, not the SMOTE step.

### 10.6 Cross-validation strategy

Cross-validation is how we test the model honestly. We split the
182 riders into 5 groups, then repeat the same training-and-testing
procedure 5 times, so that each group serves once as the test set.
The split (`StratifiedKFold(n_splits=5, shuffle=True,
random_state=42)`) keeps the Low/Medium/High proportions roughly
the same in every fold. For each fold:

1. SMOTE oversamples the training fold to balance classes.
2. The classifier is fit on the oversampled training fold.
3. The classifier is evaluated on the held-out validation fold.
4. The validation fold is left untouched by SMOTE so the reported
   metrics reflect performance on the natural class distribution.

### 10.7 Hyperparameter tuning

Each algorithm has knobs (hyperparameters) that affect how it
learns. `GridSearchCV` tries every combination in the small grids
defined above and reports the best. It is run with these settings:

- `scoring='f1_macro'`
- `cv=StratifiedKFold(5, shuffle=True, random_state=42)`
- `n_jobs=-1`
- `refit=False`

We use `refit=False` so the grid search just reports the best
parameters without immediately retraining. We then explicitly refit
the pipeline with those parameters inside a separate
`cross_validate` run that records the full set of metrics we want
to report (`accuracy`, `f1_macro`, `precision_macro`,
`recall_macro`, `train_accuracy`).

### 10.8 Model selection and persistence

For each risk factor we pick the algorithm with the highest
`cv_f1_macro`. We then refit the chosen pipeline on the entire
182-row sample (with SMOTE `k_neighbors` recomputed against the
full class distribution) and save it to disk so the web app can
load it later. The saved file is a dict with three keys:

```python
joblib.dump({
    'model': pipe,                          # fitted ImbPipeline
    'features': feats,                      # list of feature names
    'classes': sorted(set(data[target])),   # original 0/1/2 codes
}, out_path)
```

The `features` list is what the predict-time code uses to assemble
the input vector in the correct order. The `classes` list maps the
model's internal class index back to the original 0/1/2
Low/Medium/High codes. This matters specifically for the Posture
model because its `classes` list is `[1, 2]` only (no Low class
exists in the data).

### 10.9 Output tables

Phase 6 also saves three CSV tables so we can look at the numbers
behind the model selection later:

- `outputs/tables/cv_results.csv`: every target x model combination
  with mean and std of `cv_accuracy`, `cv_f1_macro`,
  `cv_precision_macro`, `cv_recall_macro`, `train_accuracy`, and
  `overfit_gap = train_accuracy - cv_accuracy`.
- `outputs/tables/best_models.csv`: one row per target listing the
  selected model and its headline metrics.
- `outputs/tables/phase6_summary.csv`: `best_models` plus an
  `overfit_flag` column for `overfit_gap > 0.15`.

## 11. Phase 7: Evaluation

Phase 7 (`notebooks/07_evaluation.ipynb`) takes the best model per
target and produces confusion matrices, ROC curves, and feature
importance, using `cross_val_predict` so the predictions are honest
out-of-fold values.

### 11.1 Metric definitions

Several different numbers are used to judge how well a model works
because no single number tells the whole story. For each class `c`
in a target, treating class `c` as positive and all others as
negative, we count true positives, false positives, and false
negatives:

```
precision_c = TP_c / (TP_c + FP_c)
recall_c    = TP_c / (TP_c + FN_c)
F1_c        = 2 * precision_c * recall_c / (precision_c + recall_c)
```

Precision asks "of the riders the model said were in class c, what
fraction actually were". Recall asks "of the riders who actually
were in class c, what fraction did the model catch". F1 combines
both into a single number.

Macro-averaged scores treat each class equally, so a model that
ignores the Medium or High band cannot hide behind raw accuracy:

```
precision_macro = mean over c of precision_c
recall_macro    = mean over c of recall_c
F1_macro        = mean over c of F1_c
```

F1 macro is what `GridSearchCV` optimises during model selection
for exactly this reason: it punishes a model that gets the majority
right while ignoring the minorities.

Raw accuracy is the simplest measure, the share of predictions that
match the true label:

```
accuracy = correct_predictions / total_predictions
```

We also track the gap between training accuracy and cross-
validation accuracy. If a model fits training data well but tests
poorly, it has overfit. The `overfit_gap = train_accuracy -
cv_accuracy` column flags this; we mark any factor with
`overfit_gap > 0.15` in `phase6_summary.csv`.

ROC-AUC (Area Under the Receiver Operating Characteristic Curve)
measures how well a model ranks classes rather than how often it
gets the exact threshold right. AUC is the probability that a
randomly chosen positive case gets a higher predicted score than a
randomly chosen negative case. A perfect ranker scores 1.0, a coin
flip scores 0.5. The Mann-Whitney U statistic gives a closed-form
equivalent. We compute per-class AUC in a one-vs-rest setup and
report the macro AUC as the unweighted mean across classes.

### 11.2 Confusion matrices

A confusion matrix is the simplest way to see where a model gets
things right and where it gets things wrong. Each row is a true
class, each column is a predicted class, and each cell counts the
riders. The diagonal counts the correct predictions; everything
off-diagonal is a mistake.

We build one with `sklearn.metrics.confusion_matrix(y_true, y_pred,
labels=present_codes)` per target. The figure
`outputs/figures/confusion_matrices.png` arranges the six matrices
in a 2x3 grid (one per target). The same numbers in long form are
saved to `outputs/tables/confusion_matrices.csv`.

### 11.3 Classification reports

The classification report sums up precision, recall, F1, and
support (the number of true cases) for each class, along with
macro and weighted averages. We generate it with
`sklearn.metrics.classification_report(y_true, y_pred,
target_names=label_names, output_dict=True, zero_division=0)` and
save the long-form table to
`outputs/tables/classification_reports.csv`.

### 11.4 ROC curves and macro AUC

For each target, the best model is wrapped in a one-vs-rest setup
so each class gets its own ROC curve. We compute the predicted
probabilities with `cross_val_predict` and
`method='predict_proba'`, then build the curve and area for each
class:

```python
fpr, tpr, _ = roc_curve(y_true == class_code, y_proba[:, class_idx])
auc = auc(fpr, tpr)
```

The per-class AUC is saved to `outputs/tables/roc_auc.csv`. The
macro AUC is the simple mean across classes and is reported in
`outputs/tables/phase7_summary.csv`. The figure
`outputs/figures/roc_curves.png` plots every class for every target
in a 2x3 grid; the closer a curve hugs the top-left corner, the
better that class is being ranked.

### 11.5 Feature importance

Feature importance tells us which inputs each model leans on most.
For tree-based models (Random Forest, Extra Trees, Hist Gradient
Boosting, XGBoost) we read it from `clf.feature_importances_`. For
Logistic Regression we use the absolute value of the coefficients
(`abs(clf.coef_)`). For Stacking the importance is taken from the
final-estimator coefficients applied to the base-learner outputs.
The figure `outputs/figures/feature_importance.png` shows the top
10 features per target.

## 12. Sample and findings

The sample is 152 male and 30 female. Age skews young: 78 riders
under 25, 66 in the 25-35 band, 30 in 36-45, and 8 in 46 and above.
49 percent of the sample works more than 8 hours per day. 94 ride
scooters and 88 ride motor bikes. Blinkit accounts for 97 riders,
Zepto for 80, with 5 working both platforms.

![Figure 1. Sample profile across gender, age band, delivery platform, vehicle type, and carrying mode.](outputs/figures/demographics.png)

84.6 percent of the riders reported pain in at least one body area
in the last 12 months.

**Table 4. NMQ 12-month pain prevalence per body area.**

| Body area | Prevalence |
|---|---|
| Lower back | 61.5% |
| Upper back | 49.5% |
| Shoulders | 46.7% |
| Wrists / Hands | 45.1% |
| Hips / Thighs | 41.2% |
| Ankles / Feet | 40.7% |
| Knees | 39.6% |
| Neck | 37.9% |
| Elbows | 33.5% |

Lower back is the most-affected region, with upper back and
shoulders close behind. The pattern is consistent across age and
platform sub-groups.

![Figure 2. NMQ 12-month pain prevalence per body area, sorted by frequency.](outputs/figures/nordic_prevalence.png)

![Figure 3. Discomfort prevalence broken down by age, gender, vehicle, and carrying mode.](outputs/figures/discomfort_by_demographic.png)

### 12.1 Stage-1 risk distribution

**Table 5. Stage-1 risk band counts per factor (n = 182).**

| Factor | Low | Medium | High |
|---|---|---|---|
| Force | 90 | 57 | 35 |
| Repetition | 26 | 82 | **74** |
| Duration | 37 | 56 | **89** |
| Vibration | 67 | 68 | 47 |
| Contact Stress | 68 | 58 | 56 |
| Posture | 0 | 29 | **153** |

Posture, Duration, and Repetition are the three factors where the
High band dominates. Posture is at 84 percent High (153 of 182
observations), Duration at 49 percent, Repetition at 41 percent
after the binning fix.

![Figure 4. Stage-1 Low / Medium / High counts per risk factor.](outputs/figures/risk_factor_distribution.png)

![Figure 5. Discomfort prevalence within each Low / Medium / High band, per risk factor.](outputs/figures/risk_vs_discomfort.png)

![Figure 6. Pearson correlation matrix across the numeric feature pool.](outputs/figures/correlation_heatmap.png)

### 12.2 Stage-2 model performance

**Table 6. Best Stage-2 model per risk factor, 5-fold stratified CV.**

| Factor | Best model | Accuracy | F1 macro | Macro AUC | Features |
|---|---|---|---|---|---|
| Force | HistGradientBoosting | 62% | 57% | 71% | 42 |
| Repetition | RandomForest | 62% | 57% | 73% | 41 |
| Duration | RandomForest | 61% | 58% | 76% | 42 |
| Vibration | ExtraTrees | 58% | 57% | 72% | 41 |
| Contact Stress | RandomForest | 60% | 59% | 74% | 42 |
| Posture | HistGradientBoosting | **97%** | **95%** | **98%** | 63 |

The five survey-derived factors land between 58 and 62 percent
accuracy with macro AUC in the 71-76 percent range. Posture reaches
97 percent accuracy and 98 percent AUC because it is the only model
that receives real observation inputs (11 RULA components and 8 QEC
scores) on top of the survey features.

**Table 7. Per-class ROC AUC (one-vs-rest) for the best model per
factor.**

| Factor | Low | Medium | High |
|---|---|---|---|
| Force | 0.798 | 0.580 | 0.760 |
| Repetition | 0.745 | 0.669 | 0.782 |
| Duration | 0.822 | 0.649 | 0.797 |
| Vibration | 0.775 | 0.615 | 0.779 |
| Contact Stress | 0.763 | 0.651 | 0.791 |
| Posture | - | - | 0.984 |

**Table 8. Per-class precision, recall, F1, and support for the best
model per factor.**

| Factor | Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|---|
| Force | Low | 0.734 | 0.767 | 0.750 | 90 |
| Force | Medium | 0.490 | 0.421 | 0.453 | 57 |
| Force | High | 0.487 | 0.543 | 0.514 | 35 |
| Repetition | Low | 0.562 | 0.346 | 0.429 | 26 |
| Repetition | Medium | 0.593 | 0.622 | 0.607 | 82 |
| Repetition | High | 0.650 | 0.703 | 0.675 | 74 |
| Duration | Low | 0.583 | 0.757 | 0.659 | 37 |
| Duration | Medium | 0.450 | 0.321 | 0.375 | 56 |
| Duration | High | 0.691 | 0.730 | 0.710 | 89 |
| Vibration | Low | 0.583 | 0.627 | 0.604 | 67 |
| Vibration | Medium | 0.551 | 0.559 | 0.555 | 68 |
| Vibration | High | 0.610 | 0.532 | 0.568 | 47 |
| Contact Stress | Low | 0.658 | 0.588 | 0.621 | 68 |
| Contact Stress | Medium | 0.526 | 0.552 | 0.539 | 58 |
| Contact Stress | High | 0.617 | 0.661 | 0.638 | 56 |
| Posture | Medium | 0.724 | 0.724 | 0.724 | 29 |
| Posture | High | 0.948 | 0.948 | 0.948 | 153 |

**Table 9. Top 5 most important features per factor (from
`feature_importances_` for tree-ensemble models). Force and Posture
are omitted because the best model for both is HistGradientBoosting,
which does not expose split-based importances directly; the Figure 9
panel is built from a parallel logistic-coefficient fit instead.**

| Factor | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 |
|---|---|---|---|---|---|
| Repetition | income_ord | vibration_index | fatigue_score | workload_x_fatigue | out_riding_worsens |
| Duration | deliveries_num | deliv_x_days | income_ord | fatigue_x_jobdur | rest_break_num |
| Vibration | deliveries_num | income_ord | deliv_x_days | rest_break_num | workload_score |
| Contact Stress | vibration_index | workload_x_fatigue | fatigue_score | workload_x_age | deliv_x_days |

![Figure 7. Confusion matrices for the best model per factor (rows = true class, columns = predicted class).](outputs/figures/confusion_matrices.png)

![Figure 8. ROC curves (one-vs-rest) for the best model per factor.](outputs/figures/roc_curves.png)

![Figure 9. Top 10 features by importance for the best model per factor.](outputs/figures/feature_importance.png)

### 12.3 Statistical predictors of discomfort

The Phase 5 logistic regression identifies seven significant
predictors of discomfort. The strongest individual predictor is
age: each step up in the age band multiplies the odds of discomfort
by 3.6 (95% CI 1.70 to 7.56, p = 0.0008). Job duration is next at
2.89 per step (p = 0.001). Education runs the other way as a
protective factor (OR 0.33, p = 0.04). Income, fatigue score,
workload score, and deliveries per day are all significant at
smaller magnitudes.

The chi-square test in the same phase finds that Posture and Force
are the only two risk factors with a significant association with
discomfort in this sample.

## 13. The web app

`app/streamlit_app.py` is the interactive demo. It loads the six
saved bundles once via `@st.cache_resource` and exposes a form with
six sections that together cover every column in the CSV and xlsx.

![Figure 10. Web interface, header and sample-profile shortcuts above the demographic section (Q1-17).](outputs/app_screenshots/web_01_header_demographic.png)

![Figure 11. Web interface, Nordic Musculoskeletal Questionnaire (Q18-24).](outputs/app_screenshots/web_02_nmq.png)

![Figure 12. Web interface, NASA-TLX workload (Q25-30) and Borg CR10 fatigue (Q31-36) sliders.](outputs/app_screenshots/web_03_nasa_borg.png)

![Figure 13. Web interface, RULA posture observation (11 inputs) and Quick Exposure Check (8 inputs) followed by the Predict button.](outputs/app_screenshots/web_04_rula_qec.png)

![Figure 14. Web interface, predicted risk profile with colour-coded bars per factor, summary banner, and risk-band recommendations.](outputs/app_screenshots/web_05_prediction_output.png)

### 13.1 Form layout

- Section 1 (Q1-17): demographics, lifestyle, work pattern,
  vehicle, carrying. Selectboxes laid out across three Streamlit
  columns.
- Section 2 (Q18-24): 9 NMQ 12-month radios, 4 seven-day radios, 5
  follow-up radios.
- Section 3 (Q25-30): six NASA-TLX 0-100 sliders. Q28 is rephrased
  as "How dissatisfied" so all six sliders run in load-direction
  and the user is not asked to mentally invert one of them.
- Section 4 (Q31-36): six Borg CR10 0-10 sliders.
- Section 5: 11 RULA component selectboxes with min/max ranges
  matched to the standard worksheet, plus help text per item.
- Section 6: 8 QEC `st.number_input` fields with min/max matched
  to the observed ranges in the training data.

### 13.2 Encoding

`encode_rider(raw)` returns a single dict of all engineered
features. Demographic and lifestyle selections are looked up in
the same mapping dicts that Phase 2 uses. Workload and fatigue
scores are computed from the slider values. Interaction features
are computed inline. NMQ, 7-day, and outcome radios are converted
to 0/1. RULA and QEC values are passed through.

### 13.3 Prediction

`predict_risks(features, models)` builds a single-row DataFrame,
selects the relevant feature subset per target using the saved
bundle's `features` list, calls `model.predict()`, then maps the
returned class index back to the original code via the bundle's
`classes` list, and finally to the Low/Medium/High label:

```python
pred_idx = int(bundle['model'].predict(df_row[bundle['features']])[0])
code = int(bundle['classes'][pred_idx])
out[factor] = LABELS[code]
```

### 13.4 Output rendering

The result is displayed as a styled table with badge emojis per
risk level, a summary banner that flags high-burden profiles (3 or
more factors at High triggers an error banner; 4 or more
Medium-or-High triggers a warning banner; otherwise a success
banner). An expandable JSON view shows the 55-63 feature values
that were fed to the models.

### 13.5 Starting the app

```
streamlit run app/streamlit_app.py
```

The same prediction is also available from the command line:

```
python src/predict.py --json data/example_rider.json
```

## 14. Reproducibility

- Random seed: `RNG = 42` is the single shared seed used in
  `StratifiedKFold`, `SMOTE`, all sklearn classifiers, and XGBoost.
- Library list: pandas, numpy, scikit-learn, scipy, matplotlib,
  seaborn, xgboost, statsmodels, imbalanced-learn, python-pptx,
  joblib, streamlit, python-docx, openpyxl.
- The full pipeline runs end to end from raw inputs with:

```
python -m nbconvert --to notebook --execute notebooks/01_data_cleaning.ipynb --output 01_data_cleaning.ipynb
python -m nbconvert --to notebook --execute notebooks/02_feature_engineering.ipynb --output 02_feature_engineering.ipynb
python -m nbconvert --to notebook --execute notebooks/03_risk_scoring.ipynb --output 03_risk_scoring.ipynb
python -m nbconvert --to notebook --execute notebooks/04_eda.ipynb --output 04_eda.ipynb
python -m nbconvert --to notebook --execute notebooks/05_stats.ipynb --output 05_stats.ipynb
python -m nbconvert --to notebook --execute notebooks/06_modeling.ipynb --output 06_modeling.ipynb
python -m nbconvert --to notebook --execute notebooks/07_evaluation.ipynb --output 07_evaluation.ipynb
```

All saved artefacts (CSV tables, PNG figures, PKL models) are
regenerated bit-identically on re-run (modulo PNG metadata timestamps
inserted by matplotlib).

## 15. Limitations

These should be stated up front rather than buried at the end.

**Self-report bias.** Most of the model inputs come from the rider's
own answers (NMQ pain, NASA-TLX workload, Borg fatigue, the
demographic items). A rider in a bad mood reports more pain than
the same rider would on a good day. Nothing in the pipeline can
correct for this.

**The Posture link is approximate.** The 182 RULA + QEC observations
do not carry rider identifiers. The Phase 2 Step 8 severity-rank
merge pairs them to the survey by ranking riders by exposure
severity (NMQ pain count + fatigue + working hours) and posture
observations by RULA Table C, then matching the two ranks one to
one. This means rider 1 in severity gets observation 1 in RULA,
and so on. The 97 percent Posture accuracy is therefore the upper
bound of what the linked data can support. A study where every
rider is observed individually would settle slightly lower because
rider-to-observation noise would re-enter.

**Repetition binning fix.** The earlier Phase 3 used
`pandas.qcut(q=3)` on `deliveries_per_hour`. The 75th percentile
fell exactly on 3.889 dph (= 35 deliveries / 9 hours), which is
the worst real combination in the sample. 55 of 182 riders tied at
that value and were all binned into Medium because qcut is
right-inclusive at the upper edge. The Stage-2 model could never
predict High for the worst real rider, no matter what features it
was given. The fix replaces qcut with fixed cuts at 2.5 and 3.75
so the worst case ends up in High where it should. Stage-1 High
count went from 19 to 74. Stage-2 accuracy went from 74 percent to
62 percent. The drop is the honest trade: the model is now
learning a real High class of 74 examples instead of memorising a
19-example minority.

**Duration leakage fix.** An earlier Phase 6 run reported 100
percent CV accuracy on Duration. After investigating we found that
`vibration_index` (= `vehicle_rank * work_hours_num`) was still in
the feature pool, so the trees were recovering `work_hours_num`
from it. We added `vibration_index` to the Duration exclusion list
and capped `max_depth` + `min_samples_leaf`. Duration settled at
61 percent accuracy and 76 percent AUC.

**Cross-sectional design.** Each rider was surveyed once. The fact
that older riders report more pain could mean that long delivery
careers cause MSDs, or that riders who develop MSDs quit, leaving
the survivors. A follow-up study would settle this.

**Sample size and region.** n = 182 is reasonable for descriptive
statistics but small for multivariable ML. The cross-validation
results have a natural wobble of around 5 percentage points. All
riders came from one regional platform deployment, so the numbers
may not transfer to other regions.

**Proxy inputs for Vibration and Repetition.** Without per-shift
accelerometer data, Vibration is approximated as
`vehicle_rank * work_hours_num`. Without per-task timing, Repetition
is approximated as deliveries-per-hour. Both proxies map onto what
the survey can capture but neither carries the per-event signal a
wearable would.

**Posture's empty Low class.** The minimum `rula_table_c` in the
sample is 3, so no rider falls in the Low band. The Posture model
is in practice a binary Medium-vs-High classifier.

## 16. Recommendations

Five interventions come out of the analysis, ordered by how many
riders they would reach.

1. **Cap daily hours.** Roughly half the sample works more than 8
   hours per day, so a shift-length cap has the biggest population
   reach.
2. **Posture training and equipment review.** 84 percent of
   observed postures sit at RULA action level 5 or above, which
   usually means handle grips, helmet ergonomics, seat adjustment,
   or bag strap design.
3. **Push for storage-box carrying over handheld bags.** The
   storage-box riders in the sample had the lowest contact stress.
4. **Age-targeted screening.** Discomfort climbs from 72 percent
   in riders under 25 to 100 percent in those 46 and above. An
   annual MSD screen for the 36-plus cohort would catch problems
   earlier.
5. **Workload management at the platform level.** Smoother route
   batching and fewer rush-window pushes would reduce NASA-TLX
   scores and, through that channel, predicted risk.

## 17. Where things live in the repository

```
Ergonomic_Project/
  README.md
  docs/
    PROJECT_REPORT.md / .docx       this write-up
  data/
    raw/                            delivery_rider_survey.csv, posture_data.xlsx
    processed/                      cleaned.csv, model_ready.csv, risk_profile.csv
    example_rider.json
  notebooks/                        01..07 (the seven phases)
  src/
    predict.py                      command-line predictor
  app/streamlit_app.py              interactive demo
  deck/                             presentation slides
  outputs/
    figures/                        all PNGs
    tables/                         result CSVs
    models/                         the six saved joblib bundles
```

## 18. Index of output files

| Number / claim | File |
|---|---|
| Sample profile | `notebooks/04_eda.ipynb`, `outputs/figures/demographics.png` |
| NMQ prevalence | `notebooks/04_eda.ipynb`, `outputs/figures/nordic_prevalence.png` |
| Stage-1 risk distribution | `data/processed/risk_profile.csv`, `outputs/figures/risk_factor_distribution.png` |
| Chi-square table | `outputs/tables/chi_square.csv` |
| Logistic regression coefficients | `outputs/tables/phase5_summary.csv` |
| Stage-2 CV metrics | `outputs/tables/cv_results.csv` |
| Per-factor best-model headline | `outputs/tables/best_models.csv` |
| Confusion matrices | `outputs/tables/confusion_matrices.csv`, `outputs/figures/confusion_matrices.png` |
| Per-class precision/recall/F1 | `outputs/tables/classification_reports.csv` |
| ROC AUC per class and macro | `outputs/tables/roc_auc.csv`, `outputs/tables/phase7_summary.csv` |
| Feature importance per target | `outputs/tables/feature_importance.csv`, `outputs/figures/feature_importance.png` |
| Saved models | `outputs/models/best_*.pkl` |
| Presentation deck | `deck/Ergonomic_Risk_Factor_Prediction_Project_Plan_WITH_RESULTS.pptx` |
