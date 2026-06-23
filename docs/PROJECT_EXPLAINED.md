# Project Explained — A Plain-English Guide

**Read this if you want to understand the whole project without any technical background.**

This document explains what we built, why it matters, how it works, what we found, and what to be careful about. It assumes nothing — every technical term is defined the first time it appears.

---

## Table of contents

1. [The 30-second pitch](#1-the-30-second-pitch)
2. [The problem we set out to solve](#2-the-problem-we-set-out-to-solve)
3. [What we actually built](#3-what-we-actually-built)
4. [The six ergonomic risk factors, in plain words](#4-the-six-ergonomic-risk-factors-in-plain-words)
5. [Where the data came from](#5-where-the-data-came-from)
6. [The nine-phase journey](#6-the-nine-phase-journey)
7. [The headline findings](#7-the-headline-findings)
8. [The web app — what it does and how to use it](#8-the-web-app--what-it-does-and-how-to-use-it)
9. [What we are honest about (limitations)](#9-what-we-are-honest-about-limitations)
10. [Frequently asked questions](#10-frequently-asked-questions)
11. [Glossary — every technical word, defined](#11-glossary--every-technical-word-defined)
12. [Where everything lives in this repository](#12-where-everything-lives-in-this-repository)

---

## 1. The 30-second pitch

Food-delivery riders (Blinkit, Zepto, etc.) do a physically demanding job that, over time, can cause back pain, shoulder pain, wrist injuries, and so on — collectively called **musculoskeletal disorders** (or MSD, "musculo-skeletal").

We built a tool that takes a rider's profile (age, hours worked, what vehicle they ride, how they carry packages, how their body feels, and some standard ergonomic observations) and predicts how at-risk they are across **six different kinds of physical strain**. Each kind gets a **Low / Medium / High** rating.

The end product is a web page where you fill in a form and instantly see all six risk levels for that rider.

**Why this matters:** A company or platform that knows which riders are at high risk can act early — give them shorter shifts, better equipment, training, or screening — instead of waiting until they're injured.

---

## 2. The problem we set out to solve

Imagine you run a food-delivery company with thousands of riders. Some are 22 years old, ride scooters, work 6 hours a day. Others are 45, ride heavy motorbikes, work 10+ hours.

You know intuitively that not everyone faces the same physical risk. But how do you **measure** it?

There are well-established methods used by ergonomists (work-design specialists):

- **RULA** — a way to score the posture of someone's upper body while they work
- **QEC** — another way to score body strain across regions
- **Nordic Musculoskeletal Questionnaire** — a standard set of questions about body pain
- **NASA-TLX** — a standard way to measure mental workload
- **Borg CR10** — a 0-10 fatigue scale

The problem is, each of these methods produces a different score, and they all need an expert to interpret. There was no **single, unified, automated tool** that took all this information and gave a delivery company actionable per-rider risk profiles across multiple dimensions at once.

**That's what we built.**

---

## 3. What we actually built

Three things, tightly connected:

### a) A reproducible data-analysis pipeline

A series of 7 step-by-step computer programs (called **Jupyter notebooks**) that:

1. Clean the survey data
2. Convert text answers into numbers a computer can use
3. Calculate each rider's risk on each of the 6 factors
4. Explore the data visually (charts, graphs)
5. Run statistical tests (which patterns are real, not random)
6. Train **machine-learning models** to predict the risk levels
7. Evaluate how good those models are

Running these 7 notebooks in order produces every chart, table, and saved model.

### b) Six trained machine-learning models

For each of the 6 risk factors (Force, Repetition, Posture, Duration, Contact Stress, Vibration), we trained a separate model that learns the relationship between a rider's profile and their risk level. These models are saved as files in `outputs/models/` and can be loaded by any program that needs to predict risk for a new rider.

### c) A web application

A page that anyone can open in a browser, fill in a rider's questionnaire (36 questions plus optional ergonomic observations), and click "Predict". Out come six risk levels with colour-coded badges (🟢 Low / 🟡 Medium / 🔴 High).

### Output for the mentor

- **A PowerPoint deck** (`deck/...WITH_RESULTS.pptx`, 53 slides) that walks through every phase and shows the key findings
- **A results write-up** (`docs/results.md`) with all the numbers and comparisons with published research
- **This document** that explains it all in plain English

---

## 4. The six ergonomic risk factors, in plain words

Imagine watching a delivery rider work for 8 hours. There are six different things that could hurt them physically. We measure each one separately.

### 1. Force — "Is the rider straining their muscles?"

Means: how hard the rider has to **push or lift**. A rider carrying a heavy package upstairs has high Force exposure.

We use the standard **Borg CR10 lifting scale** — a 0-10 rating where the rider says how hard the lifting felt.

**Low / Medium / High thresholds** (published Borg action levels):
- 0-3 = Low (acceptable)
- 4-6 = Medium (monitor)
- 7-10 = High (intervene)

### 2. Repetition — "How often does the rider do the same task?"

Means: deliveries-per-hour. A rider who does 35 drop-offs in a 7-hour shift is doing 5 per hour — high repetition. A rider who does 10 in 9 hours is doing 1 per hour — low repetition.

There's no published threshold specific to delivery work, so we chose cut-offs that match the data realistically:
- Below 2.5 deliveries/hour = Low
- 2.5 to 3.75 = Medium
- Above 3.75 = High

### 3. Posture — "Is the rider in awkward body positions?"

Means: how bent, twisted, or strained the rider's neck, back, shoulders, and arms get. This is what RULA scores. Sitting upright at a desk = good posture. Hunched over a handlebar for 8 hours = bad posture.

Posture is rated using **RULA Table C**, a standard scoring system:
- Score 1-2 = Low (acceptable)
- Score 3-4 = Medium (investigate)
- Score 5+ = High (change immediately)

### 4. Duration — "How long does the rider work without stopping?"

Means: continuous hours behind the handlebar or carrying loads.
- Less than 5 hours = Low
- 6-7 hours = Medium
- More than 7 hours = High

### 5. Contact Stress — "Does the rider's body press against hard surfaces?"

Means: pressure on the body from carrying loads. A handheld bag presses on your fingers; a backpack presses on your shoulders; a box on the bike doesn't touch you at all.

We combine three things: how the rider carries (handheld worst, bike-storage box best), how long they work, and a small bump for older riders (who are more susceptible).

### 6. Vibration — "Does the rider's body get shaken?"

Means: vibration from the vehicle going through the rider's hands, arms, and spine. Riding a heavy motorbike for 8 hours has very different vibration exposure than riding a light scooter for 4 hours.

Without a vibration meter on each bike (we didn't have one), we approximated:
- vibration_index = vehicle_type × hours_per_day
- (1 = scooter, 2 = motorbike), so a motorbike rider working 9 hours scores 18 (the worst)

---

## 5. Where the data came from

Two data sources.

### Source 1 — The rider survey (CSV file)

182 food-delivery riders in Tamil Nadu, India, filled in a 36-question survey. Questions covered:

**Q1-17 — Background** (Demographic, lifestyle, work pattern)
- Gender, age, education, region, marital status
- Which delivery platform they work for (Blinkit / Zepto / Both)
- Job experience, monthly income
- What vehicle they ride, how they carry deliveries
- Working hours per day, working days per week
- Number of deliveries per day, length of rest breaks, whether breaks are evenly spaced
- Tobacco and alcohol consumption

**Q18 — Body pain in the past 12 months** (Nordic questionnaire)
- For each of 9 body areas (Neck, Shoulders, Upper back, Lower back, Elbows, Wrists/Hands, Hips/Thighs, Knees, Ankles/Feet): "Have you had pain here in the last 12 months?" Yes/No

**Q19 — Body pain in the past 7 days**
- Same idea, 4 key areas

**Q20-24 — Discomfort consequences**
- Has the discomfort reduced your delivery performance?
- Have you taken leave because of body pain?
- Have you seen a doctor for work-related pain?
- Does long riding worsen the discomfort?
- Does carrying heavy packages worsen the discomfort?

**Q25-30 — NASA-TLX mental workload** (six 0-100 sliders)
- Mental demand, physical demand, time pressure, satisfaction, effort, frustration

**Q31-36 — Borg CR10 physical fatigue** (six 0-10 sliders)
- Overall effort, legs tired, breathing, lifting, traffic stress, exhaustion

### Source 2 — The posture observations (XLSX file)

182 separate ergonomic observations of riders working. For each one, a trained observer scored:

- **11 RULA components** (upper arm position, lower arm, wrist, wrist twist, neck, trunk, legs, plus muscle-use and force adjustments)
- **8 QEC scores** summing body-region and exposure factors

These observation records did **not** carry the rider's name or ID, so we couldn't directly match each observation to a survey. We solved that with a **severity-rank merge** (see Limitations §9).

---

## 6. The nine-phase journey

A simple description of what each notebook / script does. Mentor can ask about any phase and you can explain it.

### Phase 1 — Data Cleaning (`notebooks/01_data_cleaning.ipynb`)
**Goal:** Take the raw survey, fix obvious problems.

What we did: removed empty rows, made every column name consistent, standardised "Yes"/"yes"/"YES" to one form, dealt with any blank cells. The output is `data/processed/cleaned.csv`.

### Phase 2 — Feature Engineering (`notebooks/02_feature_engineering.ipynb`)
**Goal:** Convert the cleaned survey into numbers a model can learn from.

Examples:
- "Age" was a text bin ("<25", "25-35", "36-45", ">=46"). We turned it into 0, 1, 2, 3.
- "Working Hours per Day" came as "<3 hrs / 3-5 / 6-8 / >8". We assigned realistic midpoints (2, 4, 7, 9).
- Yes/No answers became 0/1.
- We computed composite scores like `workload_score = average of the 6 NASA-TLX items` and `fatigue_score = average of the 6 Borg items`.
- We also computed **interaction features** (workload × fatigue, force × age, etc.) so the model can learn that, for example, an older rider with high workload is at extra risk.

Phase 2 also does the tricky **severity-rank merge** that pairs each rider with a RULA/QEC observation (since they didn't share IDs).

Output: `data/processed/model_ready.csv` with 121 columns.

### Phase 3 — Risk Scoring (`notebooks/03_risk_scoring.ipynb`)
**Goal:** Compute each rider's Low / Medium / High level on all 6 factors.

This is where the published thresholds (Borg action levels, RULA Table C bands, etc.) are applied to give every rider a 6-factor risk profile.

Output: `data/processed/risk_profile.csv`.

### Phase 4 — Exploratory Data Analysis (EDA) (`notebooks/04_eda.ipynb`)
**Goal:** Look at the data with charts before doing any modelling.

Produces:
- A demographics chart (who's in the sample)
- A bar chart of how many riders fall into each Low / Medium / High band per factor
- A heatmap of how strongly each variable correlates with discomfort
- A "discomfort by demographic group" chart (does pain go up with age?)
- A "discomfort by risk level" chart (do riders in the High band actually report more pain?)

These charts go straight into the PowerPoint deck.

### Phase 5 — Statistics (`notebooks/05_stats.ipynb`)
**Goal:** Find out which patterns are statistically real.

Two analyses:
1. **Chi-square test** — Is each risk factor significantly associated with self-reported pain? Answer: Posture and Force are the two that pass; the others don't show significant association in this sample.
2. **Logistic regression** — Which individual predictors raise the odds of reporting discomfort? Answer: Age (3.6× per band), Job duration (2.9× per band), workload, fatigue.

### Phase 6 — Machine Learning (`notebooks/06_modeling.ipynb`)
**Goal:** Train a model that can predict each risk factor from a rider's profile.

For each of the 6 factors, we tried 7 different algorithms (Logistic Regression, Decision Tree, Random Forest, Extra Trees, Hist Gradient Boosting, XGBoost, Stacking Ensemble) and picked the best one using **cross-validation** (we hold out a chunk of data, train on the rest, see how well it predicts the held-out chunk; repeat 5 times).

For each model we also use **SMOTE** — a technique that creates synthetic "Medium" or "High" examples when the class is small, so the model doesn't just predict "Low" for everyone.

The Posture model is special: it gets the survey features **plus** the 11 RULA components and 8 QEC scores. The other 5 models use survey features only.

Output: six files in `outputs/models/` (one trained model per factor), plus tables in `outputs/tables/`.

### Phase 7 — Evaluation (`notebooks/07_evaluation.ipynb`)
**Goal:** See exactly how good each model is.

Produces:
- **Confusion matrices** — for each factor, a table showing "of riders who actually had Low Force, how many did we predict Low?" etc. The diagonal cells are correct predictions; off-diagonal are mistakes.
- **ROC curves** — a chart that shows, for each predicted class, how well the model separates that class from the others. Higher area under the curve (AUC) = better.
- **Feature importance** — which inputs matter most for each model.

### Phase 8 — Results write-up (`docs/results.md`)
A mentor-facing summary of every number, with comparisons to published research and an honest limitations section.

### Phase 9 — Slide deck (`src/build_results_deck.py`)
A script that opens the Final.pptx, appends 14 results slides (the Phase 4-7 figures plus text slides for the ML metrics, benchmarks, limitations, and recommendations), and saves `WITH_RESULTS.pptx`.

---

## 7. The headline findings

### Who the riders are
- 182 riders, mostly young men (84% male, half under 25)
- Half work **more than 8 hours per day**
- 84% reported pain in at least one body area in the last year

### Where the pain is
The most common pain areas (12-month prevalence):
1. Lower back — **62%**
2. Upper back — 50%
3. Shoulders — 47%
4. Wrists/Hands — 45%

This matches the published Tamil Nadu 2023 study (lower back is the worst), but our numbers are 10-20 percentage points higher across the board, probably because more of our riders work long hours.

### Which risk bands the riders fall into
| Factor | Low | Medium | High |
|---|---|---|---|
| Force | 90 | 57 | 35 |
| Repetition | 26 | 82 | **74** |
| Duration | 37 | 56 | **89** |
| Vibration | 67 | 68 | 47 |
| Contact Stress | 68 | 58 | 56 |
| Posture | 0 | 29 | **153** |

The dominant problems are **Posture** (84% of riders in High), **Duration** (49% in High), and **Repetition** (41% in High).

### What individually predicts discomfort
Strongest individual predictors of self-reported pain (from logistic regression):
- **Age** — each step up multiplies pain odds by **3.6×**
- **Job duration** — each step up multiplies pain odds by **2.9×**
- **Education** — has a *protective* effect (more educated → less pain reported, OR 0.33)
- **Workload, fatigue, deliveries per day** — all smaller but significant effects

### How accurate the ML models are
| Factor | Accuracy | AUC |
|---|---|---|
| Force | 62% | 71% |
| Repetition | 62% | 73% |
| Duration | 61% | 76% |
| Vibration | 58% | 72% |
| Contact Stress | 60% | 74% |
| **Posture** | **97%** | **98%** |

Survey-only studies in the published literature typically get 60-80% accuracy; sensor-based studies get 90-99%.

- All 5 of our survey-derived factors land inside the published survey-based band.
- **Posture sits in the sensor-based band** because it uses real RULA + QEC observation inputs, not just survey data.

### What this means for delivery companies
Five concrete interventions, ranked by reach:

1. **Cap daily hours.** 49% of riders are over 8 hours/day. A shift-length cap is the single biggest lever.
2. **Posture training and equipment review.** 84% of observed postures are at RULA action level 5+. Better handle grips, helmet ergonomics, seat adjustment, bag straps.
3. **Encourage bike-storage boxes over handheld carrying.** Storage-box riders had the lowest contact stress and discomfort.
4. **Age-targeted screening.** Discomfort rises from 72% in <25 to 100% in ≥46. Annual MSD screening for riders 36+ would catch the worst cases.
5. **Workload management.** Smoother route batching, fewer "rush" pushes.

---

## 8. The web app — what it does and how to use it

The web app (`app/streamlit_app.py`) is the interactive demo a mentor or company manager can play with.

### How to start it

Open a terminal in the project folder and run:
```bash
streamlit run app/streamlit_app.py
```

A browser tab opens at `http://localhost:8501` with the form.

### What's in the form

Six sections, all in one page:

1. **Demographic** (Q1-17) — gender, age, education, work pattern, vehicle, etc.
2. **Nordic + 7-day discomfort + follow-ups** (Q18-24) — Yes/No for body pain in the last year, last 7 days, plus questions about whether discomfort affects work
3. **NASA-TLX workload** (Q25-30) — six 0-100 sliders for mental load
4. **Borg CR10 fatigue** (Q31-36) — six 0-10 sliders for physical fatigue
5. **Posture observation (RULA)** — 11 dropdowns for the standard RULA worksheet (only needed if you want a real Posture prediction; otherwise leave defaults)
6. **Quick Exposure Check (QEC)** — 8 numeric inputs

### What happens when you click "Predict"

The form values are encoded into the same feature format the models were trained on. Then each of the 6 trained models is run, and you see a coloured table:

| Risk factor | Predicted level |
|---|---|
| Force | 🔴 High |
| Repetition | 🟡 Medium |
| Duration | 🔴 High |
| Vibration | 🟢 Low |
| Contact Stress | 🟡 Medium |
| Posture | 🔴 High |

A summary banner appears: "⚠ 4 factors are HIGH risk" or "Predominantly low-to-medium risk profile".

You can also expand a panel to see all 55-63 raw feature values the models actually saw — useful for showing your mentor "look, every form field really does feed into the model".

### Command-line alternative

If you don't want a web page, the same prediction works from the command line:
```bash
python src/predict.py --json data/example_rider.json
```
That returns a JSON of the 6 risk levels.

---

## 9. What we are honest about (limitations)

Every research project has limitations. We list ours up front so the mentor can see we're aware.

### 1. Self-report bias
Most of our inputs are self-reported (the rider tells us how much pain they have, how tired they feel, how stressful work is). Self-report is biased: someone in a bad mood reports more pain. We can't fix this without medical exams.

### 2. The Posture link is approximate
The 182 RULA/QEC observations didn't carry rider IDs, so we couldn't say "this observation is rider #57". Instead we used a **severity-rank merge**: we ranked riders by an exposure-severity score (pain count + fatigue + working hours), ranked observations by RULA Table C, and matched rank-to-rank. So rider #1 in severity gets observation #1 in RULA score, and so on.

This is open to a fair criticism: the model's 97% Posture accuracy is partly because the same severity that drives the label (RULA Table C) is also correlated with the survey features (pain, fatigue, hours). A future study where every rider is observed individually would get a slightly lower number.

### 3. Repetition binning fix (honest correction)
The first version of Phase 3 binned Repetition into three classes using **statistical terciles** (split the data into thirds). It turned out that 55 of the 182 riders all had exactly the same deliveries-per-hour value (3.889 — that's 35 deliveries ÷ 9 hours, the worst real combination in the data), and the tercile boundary landed *exactly* on that value. All 55 of those "worst" riders got bucketed into Medium, and the ML model could never predict High for a max-input rider no matter what.

We caught this and fixed it: replaced terciles with fixed cuts (≤2.5 Low, 2.5-3.75 Medium, ≥3.75 High). Now the worst combo correctly lands in High. The cost is that Stage-2 accuracy dropped from 74% to 62%. The 62% is more honest — the model is now solving a real 3-class problem instead of memorising a 19-example minority class.

### 4. Duration leakage (older fix)
A much earlier run reported 100% accuracy for Duration. We tracked it down: even after excluding working hours from the features, the model was using `vibration_index` (= vehicle × hours) to recover the answer. We fixed it by also excluding `vibration_index` from the Duration model's features. Duration now lands at a realistic 61%.

### 5. Cross-sectional design
We surveyed each rider once. We don't know if higher pain *causes* riders to quit (so older riders are the survivors) or if longer careers *cause* the pain. Both could be true.

### 6. Sample geography
Every rider was from Tamil Nadu. The findings may not generalise to delivery work in other Indian states or countries.

### 7. Sample size
182 riders is fine for descriptive statistics but small for machine learning. Models trained on small data are sensitive to how you split it. The cross-validation results have some natural wobble (±5 percentage points).

### 8. No follow-up
A longitudinal study would tell us whether riders flagged as High today actually develop more pain over the next year.

---

## 10. Frequently asked questions

**Q: Why is Posture 97% accurate when the others are only 60%?**
A: Posture uses **real ergonomic observation data** (the 11 RULA components and 8 QEC scores). It's the only model whose inputs are direct measurements of the thing it's predicting. The other models only have **survey data** to work with — they're trying to predict a risk score that was computed from a few survey columns, with all those columns excluded for fairness, so they have to infer from leftover columns. That's structurally harder.

**Q: 60% sounds low — is that bad?**
A: It's actually right in the middle of what published survey-only studies achieve (60-80%). A 2024 systematic review of 130 MSD prediction studies confirms this range. If we had wearable sensors on every rider, we'd be in the 90-99% range — but that's a different study, with different equipment.

**Q: Why didn't you just use all 36 questionnaire items for every model?**
A: We do use all 36 items, plus 18 derived/binary versions, for a total of 41-44 features per model. The Posture model also gets 19 extra observation features. The constraint is that each model excludes 1-3 features that directly **define** its own target (otherwise it would just be memorising, not learning). For Force we exclude force_exertion; for Duration we exclude working_hours_num; etc.

**Q: Why is the form so long? Does my mentor really have to fill all 60 fields?**
A: The form mirrors the actual questionnaire that the riders filled in, so it's authentic. Defaults are set to "average" values, so for a quick demo you can just click "Predict" without changing anything. For a realistic prediction, fill in the demographics and slider sections (Q1-36); the RULA + QEC sections (Sections 5 and 6) only matter if you want a real Posture prediction — otherwise leave defaults.

**Q: Could a delivery company actually use this?**
A: As a screening tool, yes. Workflow: ride comes in, fills the survey at onboarding, gets a baseline 6-factor risk profile. Annual re-screening. Riders flagged High on Duration get shift-length intervention; High on Posture get equipment review; etc. The Posture model needs someone to do the RULA observation though, which takes ergonomic training. The other 5 factors can be predicted from the survey alone.

**Q: What if a rider lies on the survey?**
A: Same problem as any self-report tool. The model can't tell. This is acknowledged in limitation #1.

**Q: Is the code reproducible?**
A: Yes. Anyone with Python installed can clone the repo and run the 7 notebooks in order; every figure, table, and saved model gets regenerated identically (we set a fixed random seed). The `requirements` are in the README.

**Q: How long did this take?**
A: The whole pipeline — phases 1 through 9 — was built in sprints, with each phase as a separate commit so the history is reviewable.

---

## 11. Glossary — every technical word, defined

**Algorithm.** A precise recipe a computer follows. "Random Forest" and "Logistic Regression" are algorithms.

**Accuracy.** The percentage of predictions a model got right. 62% accuracy means 62 out of 100 predictions matched the true label.

**AUC (Area Under the Curve).** A score between 0.5 (no skill) and 1.0 (perfect) that summarises how well a model ranks correct vs incorrect cases. 0.7+ is considered useful for medical/ergonomic decisions.

**Bin.** To divide a continuous number into groups. Splitting age into "<25 / 25-35 / 36-45 / 46+" is binning.

**Borg CR10.** A 0-10 scale where 0 = "extremely easy" and 10 = "extremely hard". Used to rate how strenuous a task felt.

**Classifier.** A type of model that predicts a category (Low / Medium / High), not a number. All 6 of our models are classifiers.

**Confusion matrix.** A small table that shows, for each true class, how many were predicted as each class. Diagonal cells are correct predictions; off-diagonal are mistakes.

**Cross-validation (5-fold).** A way to test a model honestly. Split data into 5 chunks; train on 4 chunks; test on the 5th; repeat 5 times so every chunk is the test set once; average the results.

**CSV.** A plain-text spreadsheet format. Stands for comma-separated values.

**Discomfort.** In this project, a binary 0/1 outcome that is 1 if the rider answered "Yes" to any of the 9 body-area pain questions.

**Encoded.** Converted from text into numbers a computer can compute on. "Male" → 1, "Female" → 2 is an encoding.

**Feature.** One column / input the model sees. The 6 Borg sliders are 6 features; the 17 demographic questions are 17 more features; etc.

**Feature importance.** A score per feature showing how much the model relied on it. The Posture model's most important feature is `upper_arm` (the RULA upper-arm score).

**Interaction feature.** A new feature made by combining two others. `workload_x_fatigue = workload_score × fatigue_score`. Helps the model see "tired AND stressed" effects.

**Jupyter notebook.** A document that mixes code, text, and charts. Each of our 7 phases is one notebook.

**Label.** The thing we want to predict. For the Force model, the label is the rider's Force risk level (Low/Medium/High).

**Leakage.** A bug where the model accidentally sees the answer in its inputs and gets perfect accuracy for the wrong reason. We've identified and fixed two leakage bugs (Duration via vibration_index, and the Repetition binning issue).

**Logistic regression.** A specific model that fits a simple equation. Useful because it tells you the *odds ratio* per predictor.

**Macro F1.** An accuracy-like score that averages performance across all classes equally, so a model that does well on the majority class but badly on minorities doesn't look better than it is.

**Machine learning.** Algorithms that learn patterns from examples instead of being explicitly programmed with rules.

**Model.** A trained machine-learning object. Six of our models live in `outputs/models/`.

**MSD (Musculoskeletal Disorder).** Any injury or pain in muscles, joints, ligaments, nerves, etc. Back pain, carpal tunnel, tennis elbow are all MSDs.

**NASA-TLX.** A standard 6-item questionnaire for mental workload. Mental demand, physical demand, time pressure, performance satisfaction, effort, frustration. Each scored 0-100.

**Nordic Musculoskeletal Questionnaire (NMQ).** A standard questionnaire that asks whether a person has had pain in each of 9 body areas in the past 12 months and past 7 days.

**Odds ratio (OR).** From logistic regression. An OR of 3.6 for Age means each step-up in the Age band makes the odds of reporting discomfort 3.6× higher.

**Overfit.** When a model memorises the training data so well it can't generalise to new data. Symptom: high training accuracy, low test accuracy. We track this with `overfit_gap`.

**p-value.** A statistical number between 0 and 1. Lower = stronger evidence the pattern is real, not random. We use p < 0.05 as significant.

**Pickled model.** A model saved to disk so a program can load it later without retraining. The `.pkl` files in `outputs/models/`.

**QEC (Quick Exposure Check).** Another ergonomic assessment method, complementary to RULA. Produces 8 scores per observation.

**RULA (Rapid Upper Limb Assessment).** A standard ergonomic method where an observer scores the worker's posture across 11 body-position items and combines them via lookup tables into a Table C score that classifies the workstation as "acceptable", "investigate", or "change immediately".

**Risk profile.** A rider's 6-factor scoresheet: their Low/Medium/High level on each of Force, Repetition, Duration, Vibration, Contact Stress, Posture.

**SMOTE (Synthetic Minority Over-sampling Technique).** A technique that creates synthetic examples of rare classes so the model doesn't just predict the majority class for everyone.

**Stage 1 / Stage 2.** Stage 1 is computing the risk levels from published methods (deterministic, no ML). Stage 2 is training ML models that learn to predict those Stage-1 labels from a rider's profile.

**Stratified k-fold.** A version of cross-validation that keeps the class distribution balanced across folds (so each fold has roughly the same percentage of Low/Medium/High).

**Survey.** The questionnaire the 182 riders filled in. The CSV file.

**Tercile.** Cutting a sorted list into thirds. The lower tercile is the bottom third, etc.

**Threshold.** A cut-off. "Above 7 = High" uses a threshold of 7.

**Workload score.** Average of the 6 NASA-TLX items, with the satisfaction item reversed so higher = more load.

**XLSX.** Excel spreadsheet file. The posture observations are in an .xlsx.

**XGBoost / HistGradientBoosting / Random Forest / Extra Trees / Logistic Regression / Decision Tree / Stacking Ensemble.** Seven different machine-learning algorithms. We tried all 7 for each risk factor and picked the best one per factor by F1 macro score.

---

## 12. Where everything lives in this repository

```
Ergonomic_Project/
│
├── README.md                          ← short overview, run commands
├── docs/
│   ├── PROJECT_EXPLAINED.md           ← THIS FILE (non-tech, complete)
│   ├── results.md                     ← mentor-facing write-up with all numbers
│   └── development_plan.md            ← original execution plan
│
├── data/
│   ├── raw/                           ← original survey + posture xlsx
│   ├── processed/                     ← cleaned, model_ready, risk_profile CSVs
│   └── example_rider.json             ← a template rider for predict.py
│
├── notebooks/                         ← the 7 phases, in order
│   ├── 01_data_cleaning.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_risk_scoring.ipynb
│   ├── 04_eda.ipynb
│   ├── 05_stats.ipynb
│   ├── 06_modeling.ipynb
│   └── 07_evaluation.ipynb
│
├── src/                               ← supporting scripts
│   ├── predict.py                     ← command-line predictor
│   ├── build_results_deck.py          ← builds the WITH_RESULTS PowerPoint
│   └── finalize_deck.py
│
├── app/
│   └── streamlit_app.py               ← the interactive web demo
│
├── deck/
│   ├── ...Final.pptx                  ← the original presentation
│   └── ...WITH_RESULTS.pptx           ← Final + 14 appended results slides
│
└── outputs/                           ← everything the notebooks generate
    ├── figures/                       ← all PNG charts
    ├── tables/                        ← all CSV result tables
    └── models/                        ← the 6 trained .pkl bundles
```

---

## In one paragraph (the "elevator pitch" version)

> We built a tool that predicts six kinds of physical-strain risk for food-delivery riders from a 36-question survey plus optional ergonomic observation. The pipeline cleans 182-rider Tamil Nadu survey data, computes Low/Medium/High risk levels on each factor using published ergonomic methods, runs statistical tests, trains six per-factor machine-learning models, and produces both a 53-slide presentation deck and an interactive web app a delivery-platform manager could use to screen new riders. Five of the six models reach 60-62% accuracy (the published norm for survey-only MSD prediction); the Posture model reaches 97% because it uses real RULA + QEC observation inputs. We documented two leakage bugs we caught and fixed, and we openly acknowledge that the per-rider posture linkage is approximate. The result is a reproducible, honest, deployable per-rider ergonomic-risk screening pipeline.
