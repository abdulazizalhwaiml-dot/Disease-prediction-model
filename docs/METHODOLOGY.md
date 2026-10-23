# MIZAN v2 technical methodology

## Research question and cohort

Estimate eight cross-sectional disease-label associations from eight entered measurements
and family-history answers. This is neither prospective risk prediction nor clinical
diagnosis. NHANES diagnoses may precede measurements or treatment. Smart-scale BIA data
and Saudi populations have not been externally validated against these DXA-trained models.

Version 2 preserves the original 10,623-person complete-DXA cohort, ages 20–59, so the
requested label thresholds and previous cohort remain comparable. Retaining complete-DXA
requirements introduces selection even when BMC is no longer a predictor. Unknown family
answers remain in the cohort; unknown outcomes are excluded separately for each disease.
See the data dictionary for exact exclusions, questions and OR-label semantics.

## Feature engineering and leakage prevention

Inputs: age, sex, height, weight, waist, body-fat percentage, family diabetes and family
heart attack/angina before age 50. Biological father/mother/siblings are included; a spouse
and the participant's own diagnosis are excluded. The under-50 cutoff matches the actual
NHANES questionnaire for either sex, not a different clinical 55/65 definition.

`derive_features()` centrally calculates BMI, fat mass and FFM in training, app inference,
live UI and every SHAP evaluation. Fat mass = weight × fat% /100; FFM = weight − fat mass.
Do not train on independent DXA mass columns and then silently replace them with derived
smart-scale estimates at prediction. Derived features are correlated, not independent
new measurements. Regularization and constrained tree complexity reduce overfitting.

Family 1/2 map to 1/0; refused=7, don't know=9 and blanks become unknown. Fixed
`pd.get_dummies()` no/yes/unknown columns preserve missingness and avoid column drift.
Nine numeric features plus six family dummies yield fifteen encoded features. Median
imputation and standardization are fitted on fitting rows only and stored in each pipeline.
Unknown history is never imputed as a negative answer. The UI requires explicit yes/no.

ID, cycle, survey weights, ethnicity, own-diagnosis questions, BP readings and lab results
are excluded from FEATURES. Labels use clinical evidence, predictors do not. Ethnicity
remains in a separately named column solely for offline subgroup auditing.

## Algorithms, imbalance and calibration

All four candidates are actually trained per target with a fixed seed:

| Candidate | Constraints |
|---|---|
| Logistic Regression | L2, C=0.5, balanced class weights, max_iter=2000 |
| Random Forest | 160 trees, max depth 9, minimum leaf 12, balanced subsample weights |
| XGBoost | 160 depth-3 trees, learning rate .04, subsample/column sample .85, L2=5, minimum child weight 8, fitting-set negative/positive class ratio |
| LightGBM | 160 trees, depth 4, 12 leaves, learning rate .04, minimum leaf 30, L2=5, balanced classes |

These are bounded reproducible configurations, not exhaustive optimization. No SMOTE
is applied to test/calibration data. Class weights address rarity without manufacturing
synthetic clinical records. Weights alter raw probability behavior, so every candidate is
sigmoid-calibrated on a disjoint natural-prevalence development partition. Brier score
measures probability error; calibration is not assumed perfect, especially for rare targets.

## Locked selection and evaluation protocol

- 2011–2014: stratified per target, 80% fitting / 20% calibration, seed 42.
- 2015–2016: select highest average precision, with ROC-AUC then F1 breaking ties.
  Choose operating threshold by maximum F2, weighting recall more strongly.
- 2017–2018: evaluate only after model and operating-point selection. No test tuning,
  threshold repair or post-test refitting. This cycle was inspected in version 1;
  this is temporal evaluation for comparison, not a new independent external validation.

Report recall, precision, F1, F2, ROC-AUC, average precision, Brier, confusion matrices,
prevalence and split sizes. Accuracy is not the selection criterion. Three hundred
participant-bootstrap resamples provide descriptive 95% intervals, not survey-design CIs.
Subgroup metrics by sex, background and family history flag cells with fewer than 20
positives or negatives. No national prevalence or parity claims follow from these reports.
The generated model card always reflects the selected artifacts' actual outcomes.

## SHAP over the original eight inputs

Permutation SHAP receives eight original variables and 32 deterministically sampled
fitting rows as background. Each perturbation recomputes BMI, fat mass and FFM, then
applies the complete trained/calibrated pipeline. This preserves the derived mass and
BMI identities and valid family categories, avoiding independent dummy-column masks.
Use `3 × (2 × 8 + 1)` evaluations and verify baseline + contributions = probability.

All eight contributions are shown in percentage points. The baseline is a background
model average, not prevalence. Independent masking can still create unusual combinations
of correlated original measurements; associations and attributions are not causal effects.

## Interface and artifact integrity

Arabic is default; English and RTL/LTR layouts use one shared implementation. Exactly
five numeric fields plus sex and two family selectors produce eight user inputs. BMI and
both masses update automatically. Native details/summary labels support click, touch,
keyboard and hover explanations. The scope is always visible and age bounds enforced.

Eight cards show real calibrated probabilities. Teal/amber/coral are relative to each
model's research threshold (<.65×, .65–1×, ≥1×); they are not validated clinical risk bands.
Actual poor performance is flagged. A permanent top badge identifies experimental use.
User records stay session-local; changing inputs or release clears results/explanations.

Schema version 2 and an explicit eight-input/eleven-feature contract reject older models.
The registry verifies manifest hashes, exact dependencies, paths and artifact bytes before
deserialization. A new current pointer activates only after a complete successful run.
Hashes detect corruption, not untrusted-pickle safety. Keep model storage trusted/read-only.

Engineering validation does not establish clinical readiness. Clinical deployment requires
new independent population/device validation, calibrated operating points and utility studies.
