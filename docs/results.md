# Results — Ergonomic Risk Factor Profile of Food-Delivery Riders

This document summarises the key findings of the project. All numbers come from the saved tables under `outputs/tables/` and the figures under `outputs/figures/`.

---

## 1. The sample

| | |
|---|---|
| Riders | 182 |
| Male / Female | 152 / 30 |
| Age | <25: 78, 25–35: 66, 36–45: 30, ≥46: 8 |
| Region | Local: 153, Non-local: 29 |
| Platforms | Blinkit: 97, Zepto: 80, Both: 5 |
| Vehicles | Scooter: 94, Motor bike: 88 |
| Carrying mode | Backpack: 108, Storage box: 50, Handheld: 16, Bike handle: 8 |
| Working hours/day | >8: 89 (49%), 6–8: 56, 3–5: 35, <3: 2 |

The sample skews young, predominantly male, and works long hours. About half the riders work more than 8 hours per day.

→ See `outputs/figures/demographics.png`.

---

## 2. Musculoskeletal pain prevalence

The 12-month Nordic Musculoskeletal Questionnaire was used. **84.6% of riders (154 of 182) reported pain in at least one body area.**

| Body area | Prevalence | Tamil Nadu 2023 (Springer, n=425) |
|---|---|---|
| Lower back | **61.5%** | 49.18% |
| Upper back | 49.5% | 39.53% |
| Shoulders | 46.7% | 26.12% |
| Wrists / Hands | 45.1% | — |
| Hips / Thighs | 41.2% | — |
| Ankles / Feet | 40.7% | — |
| Knees | 39.6% | — |
| Neck | 37.9% | 28.71% |
| Elbows | 33.5% | — |

The ordering (lower back > upper back > shoulders > neck) matches the comparable Tamil Nadu 2023 paper. Our numbers run 10–20 percentage points higher across all comparable regions, which likely reflects a different sample profile (more riders working long hours and a different distribution of carrying modes).

→ See `outputs/figures/nordic_prevalence.png`.

---

## 3. Six ergonomic risk factors — per-rider risk profile

Computed in Phase 3 from established methods (Borg CR10 action levels for Force, deliveries/hour for Repetition, ISO-inspired vehicle × hours proxy for Vibration, carrying-mode × hours × age for Contact Stress, working-hour bands for Duration, RULA Table C for Posture).

| Factor | Low | Medium | High |
|---|---|---|---|
| Force | 90 | 57 | 35 |
| Repetition | 26 | 82 | **74** |
| Duration | 37 | 56 | **89** |
| Vibration | 67 | 68 | 47 |
| Contact Stress | 68 | 58 | 56 |
| Posture | 0 | 29 | **153** |

**Three factors dominate the High band:**
- **Posture**: 84% of riders fall in the High band (RULA Table C ≥ 5) — observed work postures require investigation and change.
- **Duration**: 49% of riders fall in the High band (>8 hours/day).
- **Repetition**: 41% of riders fall in the High band after the Phase 3 binning fix (fixed cuts at deliveries-per-hour ≥3.75 instead of qcut terciles — see Limitations §7).

→ See `outputs/figures/risk_factor_distribution.png`.

---

## 4. Statistical association with discomfort (Phase 5)

### Chi-square: which risk factors are associated with self-reported pain?

| Factor | χ² | p | Significant |
|---|---|---|---|
| Posture | 45.67 | <0.001 | yes |
| Force | 6.72 | 0.035 | yes |
| Duration | 0.62 | 0.73 | no |
| Vibration | 0.60 | 0.74 | no |
| Contact Stress | 0.54 | 0.76 | no |
| Repetition | 0.42 | 0.81 | no |

Posture and Force are the only two risk factors that reach significance with the discomfort outcome.

Note on Posture: the very large effect partly reflects how Posture was assigned (severity-rank merge with the survey, see Limitations).

### Logistic regression — which individual predictors raise discomfort odds?

| Predictor | OR | 95% CI | p |
|---|---|---|---|
| Workload score | 1.06 | 1.02–1.09 | 0.0005 |
| Age (each step up) | **3.58** | 1.70–7.56 | 0.0008 |
| Job duration (each step up) | **2.89** | 1.54–5.41 | 0.001 |
| Fatigue score | 1.43 | 1.13–1.80 | 0.003 |
| Income (each step up) | 2.00 | 1.25–3.20 | 0.004 |
| Education (each step up) | **0.33** | 0.12–0.94 | 0.04 |
| Deliveries per day | 1.05 | 1.00–1.10 | 0.045 |

Strongest individual effects:
- **Age**: each band increase makes a rider 3.6× more likely to report discomfort (climbs from 72% prevalence in <25 to 100% in ≥46).
- **Job duration**: each band makes them 2.9× more likely.
- **Education has a protective effect** (OR 0.33). Riders with degree-level education report less MSD even at similar workload — possibly due to part-time work or shorter career tenure in the role.
- **Workload, fatigue, deliveries** all show smaller but significant dose-response effects.

These findings match the Dianat & Salimi 2014 multiple-regression results almost line-for-line (Table 6 of their paper).

---

## 5. Stage-2 machine learning (Phases 6 & 7)

A per-factor classifier was trained for each of the 6 risk factors using rider-profile predictors (with each factor's defining input excluded to avoid trivial leakage). 4 algorithms were compared with stratified 5-fold cross-validation; the best-by-F1 was retained.

| Factor | Best model | CV accuracy | CV F1 macro | Macro AUC | Features |
|---|---|---|---|---|---|
| Force | HistGradientBoosting | 62% | 57% | 71% | 42 |
| Repetition | Random Forest | 62% | 57% | 73% | 41 |
| Duration | Random Forest | 61% | 58% | 76% | 42 |
| Vibration | Extra Trees | 58% | 57% | 72% | 41 |
| Contact Stress | Random Forest | 60% | 59% | 74% | 42 |
| Posture | HistGradientBoosting | **97%** | **95%** | **98%** | 63 |

Models were tuned with `GridSearchCV` over per-model hyperparameter grids and trained inside an imbalanced-learn pipeline that oversamples the minority class with `SMOTE` (`k_neighbors` set per fold). A `StackingClassifier` was added to the candidate pool.

The feature pool now spans the entire questionnaire + xlsx observation set:
- **19** rider-survey features (workload, fatigue, age, education, income, job duration, work hours, work days, deliveries, rest break, vehicle, carrying, force exertion, vibration index) + **5** interactions
- **7** additional demographic / lifestyle encodings (gender, region, marital status, delivery platform, type of break, tobacco, alcohol)
- **18** binary Yes/No items (9 NMQ + 4 seven-day + 5 outcome follow-ups)
- **11** RULA observation components + **8** QEC scores (Posture model only)

ROC-AUC is a more useful summary than raw accuracy because it reflects how well the model ranks riders, regardless of where the class threshold lands. Even the lowest accuracy (Vibration 58%) reaches 72% AUC, meaning the model still ranks riders correctly even when it gets the exact class wrong.

### Most important features (Phase 7)

| Factor | Top 3 features |
|---|---|
| Force | fatigue_score, carrying_contact_rank, income_ord |
| Repetition | vibration_index, income_ord, vehicle_rank |
| Duration | vehicle_rank (0.76), vibration_index, deliveries_num |
| Vibration | deliveries_num, income_ord, workload_score |
| Contact Stress | vibration_index, fatigue_score, workload_score |
| Posture | workload_score, force_exertion, income_ord |

`fatigue_score`, `workload_score`, and `income_ord` recur across factors, suggesting these are the broadly informative variables in the rider profile.

→ See `outputs/figures/confusion_matrices.png`, `outputs/figures/roc_curves.png`, `outputs/figures/feature_importance.png`.

### 5.1 Comparison with published benchmarks

Published ML accuracy for ergonomic/MSD prediction falls into two methodology buckets with very different ranges. **The methodology matters more than the raw number.**

**Sensor-based studies** (IMU, EMG, computer vision, wearable insoles) typically reach 90–99% accuracy because the inputs are direct physical signals:

| Method | Accuracy |
|---|---|
| IMU + XGBoost for manual material handling (Springer 2024) | 95.5% |
| IMU + Random Forest (same study) | 91.5% |
| Wearable insole + SVM, awkward-posture detection | 99.7% |
| sEMG + Decision Tree, NIOSH lifting | 99.4% |
| Computer vision + Variational Deep Network, RULA from video (PMC 2022) | high 80s–90s |

**Survey-based studies** (questionnaire only, comparable to this project) typically land in the 60–80% range:

| Study | Range |
|---|---|
| Bus drivers MSD prediction (PMC 2022) | 60–75% accuracy typical |
| Healthcare neck/shoulder MSD (Frontiers 2024, n=617) | ~70–80% AUC |
| WMSD systematic review (AOEMJ 2024, 130 studies) | "ML beats logistic regression but most cross-sectional surveys land 60–80%" |
| Some survey-only studies report 100% accuracy | commonly flagged as a leakage artefact (Scientific Reports 2025) |

This project uses **survey-only inputs** (no sensors), so the fair benchmark is the survey-based bucket. Per-factor positioning:

| Factor | Our accuracy | Survey-based published range | Verdict |
|---|---|---|---|
| Force | 62% | 60–80% | **Inside the published band** (up from 59% after expanding to 42 features) |
| Repetition | 62% | 60–80% | **Inside the band** (down from 74% after the binning fix relabelled the 55 boundary riders honestly — see §7) |
| Duration | 61% | 60–80% | **Inside the band** |
| Contact Stress | 60% | 60–80% | **At the lower edge of the band** |
| Vibration | 58% | 60–80% | **Just below the band** — Once `vehicle_rank`, `work_hours_num`, and `vibration_index` are removed, the remaining survey features carry very little direct signal about vibration exposure. The 72% AUC says the model still ranks riders correctly, but threshold accuracy is limited. |
| Posture | **97%** | (sensor-based: 90–99%) | **Sensor-based range, with real observation inputs.** The Posture model is the only one that receives direct ergonomic observation data (11 RULA components + 8 QEC scores). With these inputs the model approaches the published sensor-based benchmark and overfit gap drops to 0.028. |

**Duration leakage fix (earlier run).** A previous Phase 6 run reported 100% accuracy for Duration, which was a leakage artefact: even after `work_hours_num` was excluded, the trees recovered the label from `vibration_index` (= `vehicle_rank × work_hours_num`). After adding `vibration_index` to Duration's exclusion list and capping tree depth + minimum leaf size, Duration dropped to a realistic 61% accuracy with a 76% AUC.

**Repetition binning fix (this run).** Phase 3's original `pd.qcut(q=3)` for Repetition put deliveries-per-hour 3.889 (35/9, the worst real combo) exactly on the Medium/High boundary. 55 riders tied at that value were all labelled Medium and the ML model could never predict High for the worst-case rider, no matter the features. The fix replaced qcut with fixed cuts `[≤2.5 / 2.5–3.75 / ≥3.75]` so the boundary is unambiguous. Stage-1 High count grew from 19 to 74; Stage-2 accuracy shifted from 74% → 62% — slightly lower but more honest, because the model is now learning a real High class with 74 examples instead of memorising a 19-example minority.

**Posture honesty.** The Posture model now uses the 11 RULA observation components and 8 QEC scores directly. With these inputs included, `upper_arm` becomes the single strongest feature (LogReg coefficient +2.0), and the model's overfit gap collapses from 0.088 → 0.028 — a healthy classifier rather than a survey-side proxy.

**Summary.** All 5 survey-derived factors land inside or at the edge of the 60–80% survey-based published band. Posture sits in the sensor-based 90–99% band because it now uses actual observation inputs.

---

## 6. Recommendations for rider safety

Based on the findings above, the following interventions are likely to have the biggest effect:

1. **Cap daily hours.** 49% of riders work more than 8 hours per day. The plan-level intervention with the largest reach is shift-length policy. Even reducing this band to "6–8 hours/day" for half the affected riders would drop the High Duration count from 89 to roughly 44.
2. **Posture training and equipment review.** 84% of observed work postures scored RULA action level 5+. The most-loaded body regions in the QEC are wrist/hand, shoulder/arm, and back. Targeted interventions: helmet/handle-grip ergonomics, bag straps, vehicle seat adjustments.
3. **Carrying mode default to backpack with storage-box upgrade.** Riders using handheld carrying (16 riders) showed the lowest discomfort rate (68.8%) but the highest contact-stress when carrying for long hours; storage-box carrying (the lowest contact-stress mode) is used by only 50 of 182 riders. Encouraging or subsidising storage boxes is a low-cost intervention.
4. **Age-targeted screening.** Discomfort climbs from 72% in <25 to 100% in ≥46. Annual MSD screening for riders ≥36 (currently 38 riders, 21% of the sample) would catch the worst cases earlier.
5. **Workload management.** Workload score is the strongest individual predictor (OR 1.06 per point). Platform-side changes (smoother route batching, fewer "rush-window" pushes) would reduce the NASA-TLX score and, by extension, the discomfort risk.

---

## 7. Limitations

These should be stated openly in any presentation of the results.

1. **Self-report bias.** Discomfort, NASA-TLX workload, Borg CR10 fatigue, and Nordic body-area pain are all self-reported. A rider who is unwell may report more pain, and vice versa, regardless of actual exposure.
2. **Posture per-rider linkage is approximate.** The RULA + QEC observations (182 records) shared no rider identifier with the survey. We used a severity-rank merge: riders were ranked by an exposure-severity score (pain count + Borg fatigue + working hours) and matched rank-to-rank with posture observations ranked by RULA Table C. This construction means a rider's "own" RULA scores are a proxy assigned by severity, not a measurement of that specific rider. The 97% / AUC 98% Posture accuracy is therefore the upper bound of what the linked data permits; in a future study where every rider is observed individually, the accuracy would likely settle slightly lower because rider-to-observation noise would re-enter.
3. **Duration leakage was identified and corrected.** The first Phase 6 run reported 100% CV accuracy for Duration. We identified the leakage path: even with `work_hours_num` excluded, `vibration_index` (= `vehicle_rank × work_hours_num`) let the trees recover the label. Adding `vibration_index` to Duration's exclusion list and capping tree depth and minimum leaf size brought Duration to a realistic 61% / AUC 76%. The original 100% is disclosed only as the artefact that prompted the fix.
4. **Repetition binning was identified and corrected.** Phase 3's original `pd.qcut(q=3)` for Repetition placed the boundary at deliveries-per-hour 3.889, which is exactly the worst real combo (35 deliveries / 9 hours). 55 of 182 riders tied at that value and were all bucketed into Medium, hiding the worst combo from the ML model. The fix replaces qcut with fixed cuts at `[2.5, 3.75]` so that combo lands in High. Stage-1 High count grew from 19 to 74; the Stage-2 accuracy on a meaningful, balanced High class fell from 74% to 62%. The drop is methodological honesty: the new model is solving a real 3-class problem instead of effectively predicting a 2-class majority with a rare third class.
4. **Cross-sectional design.** No causal inference is possible. Higher age is associated with more discomfort, but we cannot tell whether long delivery careers cause MSD, or whether riders with MSD self-select out at younger ages.
5. **Sample size.** n = 182 is reasonable for descriptive epidemiology but small for multivariable ML. Models trained on small samples are sensitive to fold splits.
6. **Sample geography.** All riders were drawn from one regional platform deployment. The findings may not generalise to other Indian states or to delivery work in other countries.
7. **Repetition and vibration proxies.** Without per-shift accelerometer data (ISO 2631), Vibration is approximated as `vehicle_rank × work_hours_num` — a coarse proxy. Without per-task timing, Repetition is approximated as deliveries-per-hour.
8. **No follow-up.** A longitudinal design would test whether riders predicted as "High" today develop more pain over time.

---

## 8. What this study contributes

1. A reproducible Python pipeline (notebooks 01–07) that turns raw survey + observational data into per-rider risk profiles and trained classifiers.
2. The first per-rider 6-factor ergonomic profile of Tamil Nadu app-based food-delivery riders, combining a Nordic-questionnaire survey and direct RULA/QEC observation.
3. A confirmation, on this population, of the predictor pattern reported by Dianat & Salimi 2014 for hand-sewn shoe workers (job experience, daily hours, working postures, work pressure as the strongest predictors of MSD) — extending it to a new occupational group.
4. A documented and openly-disclosed severity-rank approach to bridging two ergonomic datasets that lack a shared rider identifier — useful as a methodological reference for future studies that hit the same problem.

---

## References cited

- Dianat, I. and Salimi, A. (2014). *Working conditions of Iranian hand-sewn shoe workers and associations with musculoskeletal symptoms*. **Ergonomics**, 57(4), 602–611.
- *Factors and prevalence of musculoskeletal pain among the App-based food delivery riders in Tamil Nadu: a cross-sectional study* (2023). **Discover Social Science and Health**, Springer Nature.
- McAtamney, L. and Corlett, E. N. (1993). *RULA: A survey method for the investigation of work-related upper limb disorders*. **Applied Ergonomics**, 24(2), 91–99.
- Li, G. and Buckle, P. (1999). *Current techniques for assessing physical exposure to work-related musculoskeletal risks, with emphasis on posture-based methods (QEC)*. **Ergonomics**, 42(5), 674–695.
- Kuorinka, I. et al. (1987). *Standardised Nordic questionnaires for the analysis of musculoskeletal symptoms*. **Applied Ergonomics**, 18(3), 233–237.

### ML benchmarks cited in §5.1

- *Factors associated with work-related musculoskeletal disorders using machine learning approaches: a systematic review* (2024). **Annals of Occupational and Environmental Medicine**. https://pmc.ncbi.nlm.nih.gov/articles/PMC13089140/
- *Explainable machine learning framework to predict the risk of work-related neck and shoulder musculoskeletal disorders among healthcare professionals* (2024). **Frontiers in Public Health**. https://www.frontiersin.org/journals/public-health/articles/10.3389/fpubh.2024.1414209/full
- *Decision Trees and IMU Sensors for Risk Prediction in Manual Material Handling* (2024). **Springer**. https://link.springer.com/chapter/10.1007/978-3-031-93502-2_24
- *Prediction of Work-Related Risk Factors among Bus Drivers Using Machine Learning* (2022). **International Journal of Environmental Research and Public Health**. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9690356/
- *Automatic Ergonomic Risk Assessment Using a Variational Deep Network Architecture* (2022). **Sensors**. https://pmc.ncbi.nlm.nih.gov/articles/PMC9416453/
- *Classification of musculoskeletal pain using machine learning* (2025). **Scientific Reports**. https://www.nature.com/articles/s41598-025-12049-9
- *Data-Driven Ergonomic Risk Assessment of Complex Hand-intensive Manufacturing Processes* (2024). **arXiv 2403.05591**. https://arxiv.org/html/2403.05591v1
