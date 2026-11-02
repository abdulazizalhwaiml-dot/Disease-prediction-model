# MIZAN — trained models

Release: `20261102T140111Z-4ba2271e`; seed 42; schema 3.

Research only: cross-sectional NHANES disease labels, not future risk or diagnosis.
Non-pregnant adults aged 20–79; ages 60–79 come only from 1999–2006.
There is no contemporary external validation for older adults or home scales.

Cohort: 80,630 → **21,117** participants.
Older DXA: retain fully observed scans only; count each participant once.

## Fixed evaluation partitions

- Development: 1999–2000 and 2011–2014; 80% fit / 20% sigmoid calibration per target.
- Validation: 2001–2002 and 2015–2016; select the mean AP across age groups
  20–39, 40–59 and 60–79; ties use overall AP then ROC-AUC. Threshold maximizes F2.
- Test: 2003–2006 and 2017–2018; no refitting or threshold tuning after evaluation.

The 2017–2018 cycle was examined in earlier software; it is not a fresh external test.
Older test cycles provide historical validation, not evidence of current clinical utility.

## Combined test results

| Disease | Algorithm | Positive / N | Recall | Precision | F1 | ROC-AUC | AP | Brier |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| High cholesterol | xgboost | 2025 / 4949 | 0.963 | 0.447 | 0.611 | 0.703 | 0.588 | 0.215 |
| High blood pressure | logistic_regression | 1987 / 6313 | 0.911 | 0.422 | 0.577 | 0.790 | 0.624 | 0.167 |
| Diabetes | lightgbm | 584 / 6213 | 0.813 | 0.222 | 0.349 | 0.834 | 0.358 | 0.072 |
| Coronary artery disease | logistic_regression | 137 / 6457 | 0.613 | 0.089 | 0.155 | 0.841 | 0.109 | 0.020 |
| Heart attack | xgboost | 145 / 6463 | 0.503 | 0.098 | 0.164 | 0.833 | 0.097 | 0.021 |
| Angina | logistic_regression | 113 / 6452 | 0.549 | 0.081 | 0.140 | 0.817 | 0.068 | 0.017 |
| Congestive heart failure | logistic_regression | 88 / 6458 | 0.273 | 0.056 | 0.092 | 0.783 | 0.046 | 0.013 |
| Stroke | logistic_regression | 135 / 6465 | 0.207 | 0.074 | 0.109 | 0.791 | 0.061 | 0.020 |

Four real algorithms per disease: Logistic Regression, Random Forest, XGBoost, LightGBM.
Class weights address imbalance; calibration uses separate natural-prevalence rows.
`model_comparison.csv` contains validation comparisons. `age_validation.csv` and
`test_metrics.json` report performance by age, cycle and era, with sparse-cell flags.
The latter includes 300 participant-bootstrap intervals, not survey-design intervals.
Low precision and false negatives remain possible, especially for rare cardiac labels.
No national prevalence claim: survey weights are metadata, not model-fitting weights.

## Inputs and use

Eight inputs; BMI, fat mass and FFM use the same formulas in training and inference.
No ethnicity, ID, bone mineral, disease labs or own-diagnosis variables are predictors.
Historical family history is reconstructed for parents/siblings; unknown is not no.
All diagnostic thresholds remain unchanged (non-HDL ≥190; BP ≥140/90; HbA1c ≥6.5%).

The app displays fixed general wellness messages according to model thresholds.
They are not personalized treatment or proof of health. No explanation module is used.

Sources, hashes, runtime versions and selected pipeline checksums are in manifest.json.
Historical assay/device changes, complete-case selection and population transfer limit use.
