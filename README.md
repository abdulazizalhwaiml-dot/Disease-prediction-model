# Body & Health AI — NHANES 2011–2018

An end-to-end disease-association modelling system with an English/Arabic Streamlit app,
eight calibrated pipelines, probability-level SHAP explanations, temporal evaluation,
integrity-checked model releases, tests, CI and container packaging.

**Research use, not clinical diagnosis.** The software pipeline is functional, but the
supplied measurements do not support reliable predictions for all eight diseases. Several
rare cardiac labels performed poorly on the untouched test cycle; angina recall was
**0.000** at its validation-selected threshold. The app reports these limitations. The
system has not been clinically or externally validated and is not ready for patient-care
decisions. Cross-sectional NHANES data cannot establish future disease risk.

## Quick start

Use **64-bit Python 3.12**. Run commands from the repository root. The supplied original data
are already in `DATA_SET/`; do not move or download them again.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps -e .
python -m nhanes_ai.train --data DATA_SET --output models --reports reports --jobs 2
python -m streamlit run app/main.py
```

For runtime-only installation, use `requirements.lock`. Linux LightGBM wheels require
`libgomp1` (provided in the Dockerfile); macOS users may need Homebrew `libomp`.
XGBoost uses a CPU-only wheel. No GPU, API key, database or external AI service is required.
Training prints progress and the count remaining after filtering.

### Windows / التشغيل على ويندوز

Install 64-bit Python 3.12, open PowerShell in the extracted repository folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m nhanes_ai.train --jobs 2
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

No PowerShell activation or execution-policy changes are needed. `requirements-windows.lock`
includes Windows-specific transitive dependencies and verified wheel hashes. The Windows
package resolution was checked; actual runtime/UI tests were performed on Linux.
See [الشرح العربي الكامل لتشغيل Windows](docs/WINDOWS.md).

The prepared cloud environment already has the packages and trained models:

```bash
source /workspace/.cloud-setup/disease-prediction-model/activate.sh
cd /workspace/Disease-prediction-model
python -m streamlit run app/main.py --server.address=127.0.0.1
```

## Application features

- Exactly ten entered measurements: recorded sex, self-identified background, age, waist,
  weight, height, bone mineral content, fat percentage, fat mass and lean soft-tissue mass.
- BMI updates automatically and is recalculated by the backend. A random assessment ID
  is generated; ID is never a predictor.
- Eight calibrated probabilities, study thresholds, additive SHAP explanations and full
  held-out evidence. Limited model performance is explicitly marked.
- English and Arabic, including right-to-left layout, translated inputs and chart labels.
- Validates age, units, plausible ranges and composition consistency. Marks extrapolation
  outside development-data ranges and clears stale estimates when inputs/models change.
- Patient measurements remain in session memory; the app does not persist them or call
  an external inference service.

**Country is not used to infer ethnicity.** Nationality does not determine background.
The form offers a direct optional NHANES category selector, including “Not represented /
prefer not to say”, without adding an eleventh input. There is no dedicated Arab category
in the source classification; the app never automatically assigns an Arab user to another group.

## Targets and cohort

| Target | Positive study label |
|---|---|
| High cholesterol | `BPQ080 = 1` OR non-HDL (`LBXTC − LBDHDD`) ≥ **190 mg/dL** |
| High blood pressure | `BPQ020 = 1` OR mean systolic ≥ **140** OR mean diastolic ≥ **90 mmHg** |
| Diabetes | `DIQ010 = 1` OR `LBXGH` ≥ **6.5%** |
| Coronary artery disease | `MCQ160C = 1` (self-reported coronary heart disease proxy) |
| Heart attack | `MCQ160E = 1` |
| Angina | `MCQ160D = 1` |
| Congestive heart failure | `MCQ160B = 1` |
| Stroke | `MCQ160F = 1` |

These are operational study definitions, not confirmed diagnoses. The thresholds can be
changed through CLI options, followed by retraining. Non-HDL is not LDL; an isolated
HbA1c or blood-pressure measurement does not confirm a clinical diagnosis.

The supported cohort is **non-pregnant adults aged 20–59**: adult cardiac questions begin
at 20 and these DXA cycles cover ages 8–59. Known pregnancy, uncertain pregnancy in women
20–44, incomplete exams and missing core body/DXA measurements are excluded. From 39,156
initial records, **10,623 remain**. Unknown disease labels are never imputed as negative.
See [the data dictionary](docs/DATA_DICTIONARY.md).

## Training and actual results

1. **2011–2014:** stratified 80% fitting / 20% separate sigmoid calibration per target.
2. **2015–2016:** compare Logistic Regression, Random Forest, XGBoost and LightGBM.
   Select maximum average precision, then ROC-AUC/F1 for ties. Choose maximum-F2 thresholds
   to emphasize recall. Class weights handle imbalance.
3. **2017–2018:** untouched final test. No fitting, calibration, model choice or threshold
   tuning uses these rows. Exported models are exactly the evaluated pipelines.

Ethnicity uses **`pd.get_dummies()`** with a fixed schema. Median imputation and scaling
are fitted on training rows and saved inside every pipeline. IDs, lab outcomes, pressure
readings, diagnosis questionnaires and cycle identifiers never enter the predictors.

All four algorithms were genuinely compared for every target. Logistic Regression won
all eight validation comparisons in the initial run; winners are not hardcoded.

| Target | Test Recall | Test F1 | Test ROC-AUC | Test average precision |
|---|---:|---:|---:|---:|
| High cholesterol | 0.889 | 0.522 | 0.720 | 0.475 |
| High blood pressure | 0.869 | 0.574 | 0.779 | 0.580 |
| Diabetes | 0.752 | 0.382 | 0.816 | 0.348 |
| Coronary artery disease | 0.120 | 0.100 | 0.790 | 0.046 |
| Heart attack | 0.636 | 0.108 | 0.815 | 0.047 |
| Angina | 0.000 | 0.000 | 0.692 | 0.028 |
| Congestive heart failure | 0.059 | 0.017 | 0.682 | 0.017 |
| Stroke | 0.262 | 0.098 | 0.788 | 0.058 |

Strong-looking ROC-AUC can coexist with poor positive predictive value and sensitivity.
See [the generated model card](reports/MODEL_CARD.md), [all 32 validation comparisons](reports/model_comparison.csv),
[test metrics and subgroup results](reports/test_metrics.json), and
[technical methodology](docs/METHODOLOGY.md).

## Project structure

```text
DATA_SET/                  Original supplied data, unchanged
data/                      Data notes and ignored processed-output location
src/nhanes_ai/
  schema.py                Input contract, categories, targets and thresholds
  data.py                  Validated joins, filtering and nullable target construction
  features.py              Pandas dummy encoding, imputation and scaling
  train.py                 Four algorithms × eight targets, calibration and export
  inference.py             Input validation, trusted model loading and SHAP
app/                       Streamlit UI and English/Arabic translations
models/                    Generated joblib releases and atomic current pointer
notebooks/                 Data/evaluation exploration walkthrough
reports/                   Latest audit, comparisons, model card and test evidence
tests/                     Data, input, model integrity, prediction, SHAP and UI tests
docs/                      Data dictionary, methodology and operations
requirements*.txt          Pinned direct dependencies
requirements*.lock         Transitive pins and verified artifact hashes
Dockerfile                 CPU-only, non-root runtime image
.github/workflows/ci.yml   Lint, real-data training, tests and container build
```

## Verification

```bash
ruff check src app tests
ruff format --check src app tests
pytest -q
```

Train first: model-dependent tests explicitly skip if artifacts are missing. CI trains
before running the full suite. Tests execute the real UI in both languages and verify
all eight SHAP explanations against exported probabilities. Manifests record exact data
and source hashes, dependency versions, thresholds and seed. Failed training cannot replace
the currently active release.

For optional exploration, install `jupyterlab` and `ipykernel` in the same environment,
register it with `python -m ipykernel install --sys-prefix --name disease-prediction-model`,
then open `notebooks/01_data_and_evaluation.ipynb`. Notebook tools are not web runtime dependencies.

## Deployment

```bash
# Train first so the complete models/current.json release exists.
docker build -t nhanes-ai:1.0 .
docker run --rm -p 8501:8501 --memory=2g --cpus=2 nhanes-ai:1.0
```

Keep model artifacts trusted and read-only. Distribute complete binary releases using
GitHub Releases or CI artifacts; generated binaries are ignored by Git. Exposed services
need TLS and authentication through a reverse proxy. See [deployment](docs/DEPLOYMENT.md)
and [security](SECURITY.md). Docker packaging does not establish clinical readiness.

Code is MIT-licensed; NHANES data and dependencies retain their own terms.
