# Model card and actual held-out results

Release: `20261023T052300Z-6e2717eb`. Seed: 42. Python: 3.12.14.

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
| High cholesterol | logistic_regression | 606 / 2106 | 0.889 | 0.369 | 0.522 | 0.720 | 0.475 |
| High blood pressure | logistic_regression | 624 / 2139 | 0.869 | 0.429 | 0.574 | 0.779 | 0.580 |
| Diabetes | logistic_regression | 226 / 2088 | 0.752 | 0.256 | 0.382 | 0.816 | 0.348 |
| Coronary artery disease | logistic_regression | 25 / 2195 | 0.120 | 0.086 | 0.100 | 0.790 | 0.046 |
| Heart attack | logistic_regression | 33 / 2192 | 0.636 | 0.059 | 0.108 | 0.815 | 0.047 |
| Angina | logistic_regression | 24 / 2192 | 0.000 | 0.000 | 0.000 | 0.692 | 0.028 |
| Congestive heart failure | logistic_regression | 17 / 2194 | 0.059 | 0.010 | 0.017 | 0.682 | 0.017 |
| Stroke | logistic_regression | 42 / 2195 | 0.262 | 0.060 | 0.098 | 0.788 | 0.058 |

All four algorithms were actually compared for each target; see `model_comparison.csv`.
Selected algorithms: logistic_regression. No winner is hardcoded.
The selection protocol is locked before test evaluation; poor test results are reported,
not repaired by tuning against the held-out data.

Rare outcomes have few positive test cases and unstable thresholds. In the initial run,
angina sensitivity was zero and other cardiac labels had low recall and/or precision.
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

Permutation SHAP explains the calibrated positive-class probability using 32 fitting rows
as background. Contributions are additive and checked against each model output.
The baseline is a background-model average, not disease prevalence. Correlated features
and independently perturbed one-hot columns can share/distort attribution; SHAP is not causal.

Engineering validation and container packaging do not establish clinical readiness.
Before patient-care deployment, independently validate performance, calibration, subgroup
behavior and clinical operating thresholds in the intended population and measurement setting.
