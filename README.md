# Mizanak

**Live website: [https://mizanak.streamlit.app/](https://mizanak.streamlit.app/)** — hosted on Streamlit Community Cloud.

[Ready-to-run download](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/releases/latest) · [Hosting guide](docs/STREAMLIT_CLOUD.md) · [Repository guide](docs/README.md) · [CI checks](https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/actions)

Mizanak is an experimental Arabic/English research application that estimates eight health conditions from **eight entered inputs**.
The merged NHANES **1999–2006 and 2011–2018** dataset contains **21,117 participants aged 20–79**, including **2,789 aged 60–79**.

**Experimental project; not clinically validated.** Results reflect associations with study conditions, not diagnoses or predictions of future disease. A low estimate does not establish absence of disease. Older-adult data are historical and require validation in a contemporary cohort.

## Run on Windows

1. Install **64-bit Python 3.12** with the Python Launcher.
2. Extract the project and open the folder containing this file.
3. Double-click **START_WINDOWS.bat**.
4. Open **http://localhost:8501** and keep the launcher window open.

The ready package includes trained models. If models are missing or incompatible, the launcher downloads historical CDC data, verifies their hashes, and retrains. Internet access is needed for installation and downloads. See [Windows setup and troubleshooting](docs/WINDOWS.md).

## Interface — version 4.1.1

Inputs appear above the report, with automatic scrolling after submission. The language selector is at the top, without a sidebar. Help controls beside each field open explanations; height and waist help include illustrations. Expandable report cards provide condition definitions. Three calculated values appear below the inputs and update before submission.

The approved logo and favicon use a hollow rounded rectangular display on a transparent background. A separate welcome illustration combines a measurement card, measuring tape, and small heart in the site's colors. Internal scrolling in the header and all eight field-heading/help rows has been fixed.

The interface retains the version 3 trained models, data, disease definitions, and probabilities. XGBoost models were exported in a format portable between Windows and Linux without retraining or changing results. Explicit UTF-8 fixes Windows report-writing errors; the launcher explains model incompatibility before fallback training.

## User inputs

Age, sex, height in cm, weight in kg, waist in cm, body-fat percentage, family history of diabetes, and family history of early heart disease.
Help is available for every field. Family history refers to **parents and siblings**. Early heart disease means a heart attack or angina **before age 50**, for either sex. An unknown answer is not treated as “No.”

The interface and training use the same calculations:

```text
BMI = weight_kg / (height_cm / 100)²
Fat mass = weight_kg × body_fat_pct / 100
Fat-free mass = weight_kg − fat_mass_kg
```

Race, bone mineral measurements, and participant identifiers are not model inputs. Fat-free mass is not muscle mass alone. Study body-fat measurements use DXA; performance on users' devices or the Saudi population has not been validated.

[Desktop preview](docs/previews/desktop-ar.png) · [Mobile preview](docs/previews/mobile-ar.png) · [Report cards](docs/previews/report-ar.png)

## Results

Eight cards cover high cholesterol, high blood pressure, diabetes, coronary artery disease, heart attack, angina, heart failure, and stroke. Colors follow research alert levels, not clinical risk categories.

- If any estimate reaches its alert level, a common message encourages activity, a balanced diet, and appropriate tests with a healthcare professional.
- If all estimates remain below their alert levels, a common message encourages continued healthy habits and screening without certifying health.

Session inputs are not saved to a database. Results can be downloaded and are cleared when inputs change.

## Data and training

| Condition | Positive-label definition |
|---|---|
| High cholesterol | Self-report **or** non-HDL = total cholesterol − HDL ≥ **190 mg/dL** |
| High blood pressure | Self-report **or** mean systolic ≥140 or diastolic ≥90 |
| Diabetes | Self-report **or** HbA1c ≥6.5% |
| Other five targets | Condition-specific prior-diagnosis questions; see the data dictionary |

Any positive source overrides a missing source. A negative label requires every source to be negative; otherwise the label remains unknown. Pregnancy and incomplete examinations are excluded. Only observed, non-imputed DXA measurements are accepted, with one record per participant. Historical family-history responses were reconstructed to exclude grandparents and harmonize definitions.

Four algorithms were compared for each target: Logistic Regression, Random Forest, XGBoost, and LightGBM, using class weights and separate calibration. Algorithm selection uses mean AP across ages 20–39, 40–59, and 60–79. Decision thresholds maximize F2 on selection data only. Test data are excluded from training and threshold tuning.

| Purpose | Cycles |
|---|---|
| Training and calibration | 1999–2000 and 2011–2014; 80%/20% split per target |
| Model and threshold selection | 2001–2002 and 2015–2016 |
| Testing | 2003–2006 and 2017–2018 |

Recall, Precision, F1, ROC-AUC, AP, and Brier results are published as measured, including weak performance on some rare cardiac outcomes. The 2017–2018 cycle was examined in earlier releases; this is not a new external validation study.

- [Actual performance](reports/MODEL_CARD.md) · [Evaluation by age](reports/age_validation.csv)
- [Merged CSV](data/processed/NHANES_MIZAN.csv) · [Filtering and column metadata](data/processed/dataset_metadata.json)
- [Data dictionary](docs/DATA_DICTIONARY.md) · [Harmonization and methodology](docs/METHODOLOGY.md)
- [Validation record](reports/VALIDATION.md)

## Developer setup and retraining

Use Python 3.12 from the project directory:

```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-deps -e .
python scripts/download_data.py
python -m nhanes_ai.train --jobs 2
python scripts/export_dataset.py
pytest -q
python -m streamlit run streamlit_app.py
```

On Windows, use `requirements-windows.lock` for runtime dependencies and the environment-specific commands in the [Windows guide](docs/WINDOWS.md). Original 2011–2018 files are included; the download script retrieves 37 historical files with pinned hashes. Source data remain unchanged. The exported CSV preserves original units and represents unknown values as empty cells, without scaling or imputation.

```text
app/                 Interface, translations, and styling
src/nhanes_ai/       Data loading, features, training, and inference
scripts/             Downloads, exports, and Windows launchers
DATA_SET/            Original NHANES files, grouped by cycle
data/processed/      Merged dataset and metadata
models/              Active models and release manifest
reports/             Filtering, comparisons, and test results
notebooks/           Short analysis example
docs/                Data dictionary, methodology, and setup
tests/               Data, model, and interface tests
```

## Hosting

The website is hosted on **Streamlit Community Cloud** at **[https://mizanak.streamlit.app/](https://mizanak.streamlit.app/)**.
GitHub stores the source and model files. The canonical development and deployment branch is **`main`**, containing both the source and active models. Deployment uses Python **3.12** and **`streamlit_app.py`**; `packages.txt` supplies OpenMP.
See the [Streamlit hosting guide](docs/STREAMLIT_CLOUD.md) or [container deployment guide](docs/DEPLOYMENT.md).

No prospective-risk, clinical-readiness, national-representativeness, or device-transfer claim is made. See the methodology and generated model card for fixed splits and actual performance.
