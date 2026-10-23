# Technical methodology

## Scope and interpretation

Eight independent binary classifiers estimate observed study labels, not incident future
disease. NHANES is cross-sectional; some questions concern lifetime diagnosis. Measurements
can follow diagnosis, treatment or behavior changes. Associations therefore do not establish
prospective validity, causality or diagnostic accuracy in a clinical setting.

The cohort excludes ages outside 20–59, pregnancy/uncertain pregnancy as described in the
data dictionary, incomplete exams and missing core composition measurements. Exclusion
uses clinical availability, not model predictions. Missing label evidence remains nullable;
each target has its own known-label population. This complete-case/observed-outcome design
can introduce selection and nonresponse bias.

## Data pipeline and feature engineering

Pandas reads the SAS files and checks required variables and unique nonmissing `SEQN`.
Modules join one-to-one onto demographics within each cycle, followed by a pooled ID
uniqueness check. Original data remain unchanged.

The ten entered variables plus BMI form eleven raw predictors. ID is metadata only.
The recorded-sex code and nine other numeric fields become ten numeric columns, while
ethnicity uses **`pd.get_dummies()`** with six fixed categories plus unknown. The resulting
seventeen-column schema is stable even when a category is absent in fitting data.
Unknown background is never assigned to a known group.

`SimpleImputer(strategy='median', keep_empty_features=True)` and `StandardScaler` follow
encoding. Medians and scaling statistics are fitted on model-fitting rows only. Every
exported pipeline contains the full transformation, so training, inference and explanations
use identical definitions. The UI requires measured core inputs rather than fabricating
an entire DXA scan; the pipeline nevertheless handles residual missing feature values.

BMI, weight, height and composition are strongly correlated. Regularization stabilizes
the linear model, but individual coefficients/attributions must not be treated as causal.
Scaling benefits the linear candidate and preserves split order for trees.

ID, source cycle, survey weights, lab results, pressure readings and diagnosis questions
are explicitly excluded from the feature contract. Label evidence never leaks into input
features. There is no pre-split resampling or fitting preprocessing on validation/test data.

## Four candidate algorithms

| Algorithm | Configuration and rationale |
|---|---|
| Logistic Regression | L2, C=0.5, balanced class weights, max_iter=2000. Stable regularized baseline for correlated measurements and rare labels. |
| Random Forest | 160 trees, depth 9, leaf size ≥12, balanced subsample weights. Nonlinear interactions with constrained tiny-leaf variance. |
| XGBoost | 160 depth-3 histogram trees, learning rate 0.04, subsampling/column sampling 0.85, L2=5, minimum child weight 8. CPU-only; fitting-set negative/positive ratio supplies `scale_pos_weight`. |
| LightGBM | 160 trees, depth 4, 12 leaves, learning rate 0.04, minimum leaf samples 30, L2=5, balanced weights. Efficient constrained nonlinear boosting. |

These are explicit baseline configurations, not exhaustive hyperparameter optimization.
Every candidate is genuinely fitted for every target. Missing libraries or failed fits
stop release creation rather than silently substituting a trivial estimator.

Class weighting addresses imbalance without synthesizing clinical observations and keeps
validation/test prevalence natural. Weighting distorts raw probability estimates, so each
candidate receives sigmoid calibration on separate held-out development rows. Calibration
quality is measured with Brier score; few positive calibration cases still limit reliability.

## Temporal protocol and model selection

2011–2014 rows are split 80% fitting / 20% calibration, stratified per target, seed 42.
At least five cases per class are required in development, validation and test. A
`FrozenEstimator` prevents the sigmoid calibrator from refitting the underlying model.

2015–2016 selects the highest **average precision**, the nontrapezoidal summary of the
precision-recall curve. ROC-AUC and F1 break exact ties. Each candidate's threshold maximizes
validation **F2**: `5 × precision × recall / (4 × precision + recall)`, emphasizing recall.
Small positive counts make such thresholds unstable; crossing a threshold is not diagnosis.

2017–2018 is evaluated only after the algorithm and threshold are fixed. Exported pipelines
are the evaluated models and are not refitted on validation/test afterward. Test outcomes
do not trigger threshold changes. Repeated software-regression evaluation does not alter
the models; further research needs a new independent external evaluation cohort.

## Evaluation and actual findings

The 32-row validation comparison covers all four algorithms and all eight labels. Selected
test reports include Recall, Precision, F1, F2, ROC-AUC, average precision, Brier, prevalence,
confusion matrices and split counts. Accuracy is not a selection criterion. For rare labels,
a small Brier score can mostly reflect low prevalence; it alone does not prove calibration.

Logistic Regression won every initial validation comparison. Test diabetes recall was
0.752, F1 0.382 and ROC-AUC 0.816. Angina recall/F1 were both zero despite ROC-AUC 0.692.
Heart-failure recall was 0.059. These results remain visible in the app and model card.
Rare-label estimates are unsuitable for clinical rule-out and have poor positive predictive
value. Tuning against the test set to remove these failures would invalidate the evaluation.

Uncertainty uses 300 unweighted participant-bootstrap resamples, dropping one-class samples.
95% percentile intervals do not account for NHANES clustering/strata. Recorded-sex and
background subgroup metrics flag groups with fewer than 20 positives or negatives as sparse.
They are descriptive audit outputs, not evidence of group parity or external validity.
MEC weights/design variables are retained but not used for population inference. This is
an unweighted predictive benchmark, not a national prevalence or survey-adjusted analysis.

## SHAP explanations

`PermutationExplainer` explains the **calibrated positive-class probability**, not an
unrelated uncalibrated score. The background is 32 deterministically sampled fitting rows
transformed using the saved preprocessor. Three permutation cycles use
`3 × (2 × number_of_encoded_features + 1)` evaluations.

Every explanation checks `baseline + sum(SHAP contributions) ≈ predicted probability`.
Ethnicity dummy contributions are summed for presentation. All eleven feature/derived-feature
contributions appear in percentage points. The baseline is the average model output on
background rows, not cohort prevalence.

Independent masking after dummy encoding can produce intermediate invalid one-hot
combinations. Correlated BMI/composition variables can share unstable attribution. These
are interventional model explanations, not causal effects or predictions of what happens
if someone changes a measurement. The app states this explicitly.

## Software release and clinical boundaries

Training creates a complete versioned release, then atomically replaces `current.json`.
The loader verifies the manifest and artifact SHA256 hashes, exact model-runtime versions,
schema, expected filenames and paths. It deserializes the same verified bytes. Hashes are
integrity checks, not signatures: trusted read-only artifact storage remains essential
because pickle/joblib can execute code.

The UI recalculates BMI, checks age/units/consistency and marks extrapolation outside
development-data ranges. Model cache is shared and read-only; patient state is session-local.
No external AI service or patient database is involved. Tests exercise real predictions,
all eight additive explanations, both languages, invalid inputs and stale-state clearing.

Engineering tests and container packaging do not establish clinical readiness. Before
patient-care use, independently assess label definitions, measurement-instrument comparability,
discrimination, calibration, subgroup behavior, thresholds and clinical utility in the
intended population. Arabic support does not validate US-derived estimates in Saudi Arabia
or other countries. Older adults and people without complete DXA measurements are outside scope.
