# Research alert-level review — version 4.2.0

This is a retrospective maintenance comparison on NHANES, not a new independent or clinical validation study. Numeric alert levels were selected on validation rows; the historical test cycles have already been examined in earlier releases and this review.

## What was changed

The first deployment stage covers cholesterol, blood pressure and diabetes, as the initial work proposal specified. Fitted pipelines, sigmoid calibration, all 11 features derived from eight inputs, labels and source data are retained. Only these three research alert levels change. The other five operating points and their artifact bytes are retained.

For each of the three targets, maximize **validation F1** subject to validation recall being at most **10 percentage points** below the same fitted pipeline's maximum-validation-F2 recall. Ties use the highest threshold within absolute score tolerance 1e-12. The allowance is an explicit research preference; it is not a clinically justified sensitivity target. It does not guarantee a 10-point bound on test or future recall.

The complete validation-only decision plan is written and fingerprinted **before any test evaluation**. Code rejects development/test/unknown-partition rows at the selection boundary. The original source hashes and reconstructed cohort are verified before selection.

## Historical test results: adopted levels

Values are before → after. Accuracy is included for transparency, not used as the objective.

| Condition | Accuracy | Recall | Precision | F1 | False positives | False negatives |
|---|---:|---:|---:|---:|---:|---:|
| High cholesterol | 49.8% → 59.1% | 96.3% → 85.6% | 44.7% → 50.0% | 0.611 → 0.631 | 2410 → 1734 | 75 → 291 |
| High blood pressure | 57.9% → 67.6% | 91.1% → 79.6% | 42.2% → 49.1% | 0.577 → 0.607 | 2480 → 1641 | 176 → 406 |
| Diabetes | 71.5% → 76.8% | 81.3% → 74.5% | 22.2% → 25.2% | 0.349 → 0.377 | 1660 → 1290 | 109 → 149 |
| Coronary artery disease | 85.8% → 85.8% | 61.3% → 61.3% | 8.9% → 8.9% | 0.155 → 0.155 | 865 → 865 | 53 → 53 |
| Heart attack | 88.5% → 88.5% | 50.3% → 50.3% | 9.8% → 9.8% | 0.164 → 0.164 | 672 → 672 | 72 → 72 |
| Angina | 88.2% → 88.2% | 54.9% → 54.9% | 8.1% → 8.1% | 0.140 → 0.140 | 708 → 708 | 51 → 51 |
| Heart failure | 92.7% → 92.7% | 27.3% → 27.3% | 5.6% → 5.6% | 0.092 → 0.092 | 407 → 407 | 64 → 64 |
| Stroke | 92.9% → 92.9% | 20.7% → 20.7% | 7.4% → 7.4% | 0.109 → 0.109 | 350 → 350 | 107 → 107 |

**The reduction in false positives comes with more missed cases.** Cholesterol false negatives increase from75 to291; blood-pressure false negatives from176 to406; diabetes false negatives from109 to149. The validation guard is not an unseen-data safety guarantee. No claim is made that all metrics improve.

ROC-AUC, AP and Brier are exactly unchanged because fitted probabilities are unchanged. Every exported pipeline was checked on all21,117 reconstructed cohort rows with maximum probability difference0. The five retained artifacts are byte-identical to the source release.

## Why the five rare-outcome levels are retained

The eight-target exploratory candidate was also evaluated and is fully disclosed in threshold_candidate_review.csv and threshold_candidate_plan.json. Validation F1 gains for the rare outcomes were small or zero; candidate test F1 also regressed for angina and heart failure. The agreed first-stage scope remains the three cardiometabolic targets; rare-outcome candidates are not activated. No further threshold was selected using those test results.

| Exploratory candidate, not adopted for these targets | Validation F1 before → candidate | Historical test F1 before → candidate |
|---|---:|---:|
| Coronary artery disease | 0.163 → 0.164 | 0.155 → 0.156 |
| Heart attack | 0.157 → 0.157 | 0.164 → 0.164 |
| Angina | 0.130 → 0.133 | 0.140 → 0.128 |
| Heart failure | 0.123 → 0.131 | 0.092 → 0.089 |
| Stroke | 0.140 → 0.140 | 0.109 → 0.109 |

Low precision, missed cases, historical older-adult data and weak age-specific discrimination remain. Several adopted points still have accuracy below the majority-class baseline. A model that always predicts the majority class may have high accuracy while detecting no cases. Do not interpret high accuracy or these alert levels as clinical readiness.

## Evidence and reproduction

- [Frozen adopted selection plan](../reports/threshold_selection.json)
- [Adopted before/after metrics on validation and historical test](../reports/threshold_comparison.csv)
- [Exploratory eight-target review](../reports/threshold_candidate_review.csv)
- [Original exploratory validation plan](../reports/threshold_candidate_plan.json)
- [Current model card](../reports/MODEL_CARD.md) and [full test/subgroup/bootstrap results](../reports/test_metrics.json)

From a trusted compatible source release, with original source files available:

```bash
python -m nhanes_ai.rethreshold --data DATA_SET --models models --reports reports
pytest -q
```

The re-selection command does not fit models or calibration. Future full training uses the same target-specific threshold policy. To reduce the remaining errors, study additional independent predictors and contemporary data with sufficient positive cases; select on validation and reserve genuinely new data for final confirmation.

The original baseline is release `20261102T184611Z-ebdefc95`, available in Git history and tag `v4.1.1`. Reproducing the original before/after comparison requires that source release; running on an already updated release reproduces the same new operating points.
