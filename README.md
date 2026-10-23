# ميزان | MIZAN — Body Insights Lab

A bilingual Arabic/English Streamlit research app built from the supplied **NHANES
2011–2018** files. Version 2 takes **exactly eight inputs**, derives three measurements,
and uses eight freshly trained, calibrated models with probability-level SHAP explanations.

**Experimental, not medically validated.** Estimates describe cross-sectional study labels,
not future disease risk or confirmed diagnoses. Some cardiac outcomes still have poor
recall/precision. The interface displays the actual held-out performance and its limitations.

## The eight inputs

1. Age, **20–59 completed years**; intended for non-pregnant adults.
2. Recorded sex: male / female.
3. Height in centimeters.
4. Weight in kilograms.
5. Waist circumference in centimeters, following the NHANES iliac-crest method.
6. Body-fat percentage.
7. Family history of diabetes: yes / no.
8. Early family cardiac history: yes / no.

Every field name is a keyboard-accessible, clickable explanation and has hover help.
Family questions concern biological father, mother, sisters or brothers, living or
deceased. Diabetes has no age restriction. Early cardiac history means a health
professional reported **heart attack or angina before age 50**, for either sex. This
matches `MCQ300A`; it is not a generic question about every kind of heart disease.
The app requires an explicit yes/no selection; unknown history is not silently defaulted to no.

Three values update automatically using the **same function in training, UI, inference and SHAP**:

```text
BMI = weight_kg / (height_cm / 100)²
fat_mass_kg = weight_kg × body_fat_pct / 100
fat_free_mass_kg = weight_kg − fat_mass_kg
```

FFM includes minerals, water, muscle and organs; it is not skeletal muscle mass alone.
There are no ethnicity, bone-mineral, separately entered fat-mass or lean-mass inputs.
The new derived masses use body weight and fat percentage consistently; they are not
the older exports' independently measured DXA masses. Original fat percentage was
measured by DXA: transferring models to BIA smart scales remains unvalidated.

## Windows: easiest start

Install **64-bit Python 3.12** including the `py` launcher, extract the complete project,
and double-click **`START_WINDOWS.bat`**. It creates a local environment, installs the
Windows lock, checks the eight-input model contract, trains if a compatible release is
missing, and starts Streamlit. Open **http://localhost:8501**. Keep the terminal open.

The prepared ZIP includes the current trained models. A source-only GitHub checkout
requires training. Version-1 models cannot be used with the new form.
See [الشرح العربي لتشغيل Windows](docs/WINDOWS.md).

Manual PowerShell commands, one at a time from the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m nhanes_ai.train --jobs 2
.\.venv\Scripts\python.exe -m streamlit run app/main.py
```

## GitHub-connected hosting

The `deploy/streamlit-cloud` branch includes the trusted trained release and the
`streamlit_app.py` entry point. Deploy this branch on Streamlit Community Cloud with
**Python 3.12**; `packages.txt` supplies Linux OpenMP. GitHub Pages cannot execute the
Python app. Follow the [Arabic cloud-hosting guide](docs/STREAMLIT_CLOUD_AR.md).
Account authorization and the final Deploy action occur in your own Streamlit account.

## Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps -e .
python -m nhanes_ai.train --jobs 2
python -m streamlit run app/main.py
```

Runtime-only installations can use `requirements.lock`. Linux LightGBM needs `libgomp1`;
macOS may need `libomp`. No GPU, API key or external inference service is required.
Cloud environment: `source /workspace/.cloud-setup/disease-prediction-model/activate.sh`.

## Interface

- A new teal/navy visual identity, responsive layout and Arabic RTL support; Arabic is default.
- Eight disease cards with real calibrated probabilities, progress bars and study thresholds.
- Colors follow each disease's model threshold: teal below, amber nearby, coral above.
  They are research display bands, **not clinically validated risk categories**.
- Persistent experimental/non-medical badge above the form.
- Click/hover definitions, a measurement guide and actual evaluation tables.
- On-demand SHAP explanations over the original eight inputs, preserving derived identities.
- Automatic clearing of stale results when any input or the model release changes.
- Session-local inputs and downloadable session results; no patient database.

## Study labels — unchanged

| Outcome | Positive label |
|---|---|
| High cholesterol | `BPQ080=1` OR `LBXTC−LBDHDD ≥190 mg/dL` |
| High blood pressure | `BPQ020=1` OR mean systolic ≥140 OR mean diastolic ≥90 mmHg |
| Diabetes | `DIQ010=1` OR HbA1c ≥6.5% |
| Coronary artery disease | `MCQ160C=1`, self-reported coronary heart disease proxy |
| Heart attack | `MCQ160E=1` |
| Angina | `MCQ160D=1` |
| Congestive heart failure | `MCQ160B=1` |
| Stroke | `MCQ160F=1` |

Any positive source establishes a positive. Negative requires all relevant sources to be
known negative; other combinations stay unknown and are excluded per target. Missing
questionnaire answers never become healthy labels. The cholesterol threshold is the
user-selected **190**, not the previously explored 130/160 alternatives.

The existing complete-DXA cohort is preserved for comparability: **39,156 → 10,623**.
Pregnant/indeterminate pregnancy, incomplete exams and missing core measurements remain
excluded. Although BMC is no longer a predictor, original complete-case selection still
requires those measurements; removing that restriction would create a different cohort.

## Model comparison and evaluation

Four algorithms are actually fitted per target: regularized Logistic Regression, Random
Forest, XGBoost and LightGBM. Class weights address imbalance. Independent sigmoid
calibration limits the probability distortion introduced by class weighting.

1. **2011–2014:** stratified 80% model-fitting / 20% calibration per target.
2. **2015–2016:** select by average precision, then ROC-AUC/F1 on ties; operating threshold
   maximizes F2. No accuracy-only selection.
3. **2017–2018:** temporal evaluation after selection. This cycle was already inspected
   in version 1; this is a version comparison, **not a new independent external validation**.

Preprocessing, imputation and scaling are fitted only on fitting rows. Family-history
codes 1/2 become 1/0; 7/9/missing get an explicit unknown dummy category. Ethnicity is
excluded from predictors and retained separately only for offline subgroup auditing.

The selected release's actual results are in [the generated model card](reports/MODEL_CARD.md),
[32 validation comparisons](reports/model_comparison.csv), and
[test metrics, uncertainty and subgroup checks](reports/test_metrics.json).
Previous-version reports remain under `reports/previous_version/`. Better results on
some metrics do not establish clinical suitability or transfer to Saudi populations.
See [the complete version comparison](reports/VERSION_COMPARISON.csv), including metrics
that decreased. Run `python scripts/export_dataset.py` to reproduce the processed CSV;
the prepared delivery includes CSV and a convenient Excel copy under `data/processed/`.

## Structure

```text
DATA_SET/                  40 original XPORT files, unchanged
src/nhanes_ai/
  schema.py                Eight-input / eleven-feature contract and thresholds
  data.py                  Validated joins, family history, original cohort and targets
  features.py              Shared derivation, fixed family dummies, imputation and scaling
  train.py                 Four algorithms, calibration, selection and versioned export
  inference.py             Eight-input validation, model integrity and raw-input SHAP
app/
  main.py                  Bilingual Streamlit dashboard
  i18n.py                  English/Arabic copy and measurement definitions
  ui.py / style.css        Escaped cards, clickable help and responsive visual design
scripts/run_windows.ps1   Environment/model checks and Windows startup
START_WINDOWS.bat         Double-click launcher
models/                   Generated models and atomic current pointer (ignored by Git)
reports/                  Actual metrics, model card, audits and previous-version reports
tests/                    Clinical-label, input, SHAP, integrity and bilingual UI checks
docs/                     Technical methodology, data dictionary and operation guides
notebooks/                Reproducible exploration walkthrough
```

## Verification and deployment

```bash
ruff check src app tests
ruff format --check src app tests
pytest -q
docker build -t mizan-ai:2.0 .
docker run --rm -p 8501:8501 --memory=2g --cpus=2 mizan-ai:2.0
```

Train before testing/building a source-only checkout. Integration tests require a real
compatible release. The schema version prevents silently loading old ten-input models.
Artifacts are SHA256-checked and restricted to expected paths and exact runtime versions;
only load trusted joblib files. Model releases activate atomically after successful training.
See [methodology](docs/METHODOLOGY.md), [data dictionary](docs/DATA_DICTIONARY.md),
[deployment](docs/DEPLOYMENT.md) and [validation evidence](reports/VALIDATION.md).
