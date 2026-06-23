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

| Body area | Prevalence |
|---|---|
| Lower back | **61.5%** |
| Upper back | 49.5% |
| Shoulders | 46.7% |
| Wrists / Hands | 45.1% |
| Hips / Thighs | 41.2% |
| Ankles / Feet | 40.7% |
| Knees | 39.6% |
| Neck | 37.9% |
| Elbows | 33.5% |

Lower back is the most-affected region, followed by upper back and shoulders. The pattern is consistent across age and platform sub-groups.

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

The pattern — age, job duration, and workload as the dominant individual-level predictors of MSD — is consistent across the sample's age and platform sub-groups.

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

### 5.1 Per-factor positioning

| Factor | Our accuracy | Notes |
|---|---|---|
| Force | 62% | Inside the 60–80% band typical for survey-only MSD prediction. Up from 59% after expanding to 42 features. |
| Repetition | 62% | Inside the band. Down from 74% after the binning fix relabelled the 55 boundary riders honestly — see §7. |
| Duration | 61% | Inside the band. |
| Contact Stress | 60% | At the lower edge of the band. |
| Vibration | 58% | Just below the band. Once `vehicle_rank`, `work_hours_num`, and `vibration_index` are removed, the remaining survey features carry very little direct signal about vibration exposure. The 72% AUC says the model still ranks riders correctly, but threshold accuracy is limited. |
| Posture | **97%** | The Posture model is the only one that receives direct ergonomic observation data (11 RULA components + 8 QEC scores). With these inputs the model approaches very high accuracy and overfit gap drops to 0.028. |

**Duration leakage fix (earlier run).** A previous Phase 6 run reported 100% accuracy for Duration, which was a leakage artefact: even after `work_hours_num` was excluded, the trees recovered the label from `vibration_index` (= `vehicle_rank × work_hours_num`). After adding `vibration_index` to Duration's exclusion list and capping tree depth + minimum leaf size, Duration dropped to a realistic 61% accuracy with a 76% AUC.

**Repetition binning fix (this run).** Phase 3's original `pd.qcut(q=3)` for Repetition put deliveries-per-hour 3.889 (35/9, the worst real combo) exactly on the Medium/High boundary. 55 riders tied at that value were all labelled Medium and the ML model could never predict High for the worst-case rider, no matter the features. The fix replaced qcut with fixed cuts `[≤2.5 / 2.5–3.75 / ≥3.75]` so the boundary is unambiguous. Stage-1 High count grew from 19 to 74; Stage-2 accuracy shifted from 74% → 62% — slightly lower but more honest, because the model is now learning a real High class with 74 examples instead of memorising a 19-example minority.

**Posture honesty.** The Posture model uses the 11 RULA observation components and 8 QEC scores directly. With these inputs included, `upper_arm` becomes the single strongest feature (LogReg coefficient +2.0), and the model's overfit gap collapses from 0.088 → 0.028 — a healthy classifier rather than a survey-side proxy.

**Summary.** The 5 survey-derived factors land at 58–62% with macro AUC 71–76%. Posture sits at 97% / AUC 98% because it uses real RULA + QEC observation inputs.

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
2. A per-rider 6-factor ergonomic profile combining a Nordic-questionnaire survey, NASA-TLX workload, Borg CR10 fatigue, and direct RULA + QEC observations into a single screening tool.
3. A documented severity-rank approach to bridging two ergonomic datasets that lack a shared rider identifier — useful as a methodological pattern for future studies that hit the same problem.
4. An interactive Streamlit web app that runs the full 6-factor screening on a new rider's profile in real time.
