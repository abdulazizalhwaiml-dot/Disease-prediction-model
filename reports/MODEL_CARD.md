# Model card and actual held-out results

Release: `20261023T131025Z-6012cdf9`. Seed: 42. Python: 3.12.14.

## Intended use and limits

Research into cross-sectional disease-label associations in US NHANES participants
aged 20–59, excluding known/indeterminate pregnancy and incomplete body/DXA exams.
No model has been clinically or externally validated. These are not forecasts of
future disease, diagnostic tests, rule-out tools, or treatment recommendations.

## Cohort

Initial participants: 39,156. After filtering: **10,623**.

2011–2014: 80% model fitting, 20% independent sigmoid calibration (stratified per target).
2015–2016: algorithm selection by average precision; operating threshold by maximum F2.
2017–2018: untouched final evaluation. Selected models are not refit on validation or test.

## Test results

| Target | Algorithm | Positive / N | Recall | Precision | F1 | ROC-AUC | Average precision |
|---|---|---:|---:|---:|---:|---:|---:|
| High cholesterol | logistic_regression | 606 / 2106 | 0.939 | 0.348 | 0.507 | 0.719 | 0.490 |
| High blood pressure | logistic_regression | 624 / 2139 | 0.923 | 0.392 | 0.550 | 0.773 | 0.563 |
| Diabetes | logistic_regression | 226 / 2088 | 0.814 | 0.255 | 0.389 | 0.829 | 0.389 |
| Coronary artery disease | logistic_regression | 25 / 2195 | 0.120 | 0.081 | 0.097 | 0.871 | 0.073 |
| Heart attack | random_forest | 33 / 2192 | 0.606 | 0.059 | 0.107 | 0.828 | 0.067 |
| Angina | logistic_regression | 24 / 2192 | 0.167 | 0.068 | 0.096 | 0.844 | 0.057 |
| Congestive heart failure | logistic_regression | 17 / 2194 | 0.294 | 0.036 | 0.065 | 0.801 | 0.029 |
| Stroke | logistic_regression | 42 / 2195 | 0.357 | 0.128 | 0.189 | 0.792 | 0.079 |

All four algorithms were actually compared for each target; see `model_comparison.csv`.
Selected algorithms: logistic_regression, random_forest. No winner is hardcoded.
The selection protocol is locked before test evaluation; poor test results are reported,
not repaired by tuning against the held-out data.

Rare outcomes have few positive test cases and unstable thresholds. Low recall or
precision is flagged per disease in the manifest and remains visible in the app.
An above/below study threshold result must not be interpreted as a diagnosis or rule-out.

## Calibration, uncertainty and fairness

Class-weighted models receive sigmoid calibration on natural-prevalence held-out training
rows. Calibration is measured with Brier score, not assumed perfect. `test_metrics.json`
includes confusion matrices, prevalence, 95% participant-bootstrap intervals (300 resamples),
and recorded-sex/background subgroup metrics with sparse-cell flags. Intervals are
unweighted and do not account for NHANES cluster/stratum sampling. MEC weights and
design variables are retained for future survey-aware analysis but not used in this
predictive benchmark. These results do not establish national prevalence or group parity.

## Explanation and deployment

Permutation SHAP explains calibrated probability over the original eight inputs using
32 fitting rows. BMI and both masses are recomputed inside every model evaluation.
Contributions are additive and checked against each model output. The baseline is a
background-model average, not prevalence. Correlated inputs can share attribution.
SHAP is not causal. Eight user inputs generate BMI, fat mass and fat-free mass identically
in training and inference. Ethnicity, BMC and DXA lean soft tissue are not model inputs.
Body fat was measured by DXA in NHANES; BIA smart-scale transfer is not validated.
This temporal test cycle was also examined in the previous software version; this
comparison is not a new independent external validation. No test results tune this run.

Engineering validation and container packaging do not establish clinical readiness.
Before patient-care deployment, independently validate performance, calibration, subgroup
behavior and clinical operating thresholds in the intended population and measurement setting.
