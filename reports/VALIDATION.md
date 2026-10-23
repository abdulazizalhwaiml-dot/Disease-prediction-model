# MIZAN v2 delivery validation — 2026-10-23

These are engineering/research checks actually executed in the cloud, not clinical validation.
Previous-version evidence is preserved in `reports/previous_version/VALIDATION.md`.

## Data and training

- All 40 supplied XPORT files read and one-to-one joins/participant IDs checked.
- Original source files unchanged; all forty source hashes match the active release.
- Cohort preserved: 39,156 → **10,623**, ages 20–59, original pregnancy/exam exclusions.
- Eight entered inputs and eleven raw predictors. No ethnicity or BMC model inputs.
- Family diabetes yes/no/unknown: **4422 / 6031 / 170**.
- Early family cardiac yes/no/unknown: **1174 / 9222 / 227**.
- Family definitions/codes verified against official codebooks in all four cycles;
  URLs, hashes and exact excerpts are in `docs/family_history_provenance.json`.
- Cholesterol OR threshold **190 mg/dL** retained: **3,122** positives. Other labels unchanged.
- Shared BMI/fat mass/FFM derivation matches training, inference, UI and SHAP.
- Ran all **32** comparisons (four actual algorithms × eight outcomes), class weighting,
  separate sigmoid calibration, validation selection/thresholds and temporal evaluation.
- Current complete schema-2 release: **`20261023T131025Z-6012cdf9`**.
- All training-code hashes still match the release manifest after formatting.
- The test cycle was previously inspected in v1: these are version comparisons, not
  new independent external validation. No test score was used to retune this run.

## Software and UI

- `ruff check src app tests scripts`: passed.
- `ruff format --check src app tests scripts`: fifteen Python files formatted.
- Full suite: **34 passed**; after replacing dropdowns with explicit radio choices,
  both bilingual UI tests were rerun and passed. No model-dependent skips.
- Real predictions and all eight SHAP explanations are finite and additive; the eight
  original inputs are explained while derived values are recalculated inside SHAP.
- Invalid/missing inputs, unknown-family coding, corruption/path traversal, older schema
  rejection and stale results are checked.
- Actual Chromium desktop **1440px** and touch/mobile **390px** interactions passed:
  eight inputs, explicit family selections, actual eight predictions, clickable help,
  no horizontal overflow and no browser JavaScript errors.
- English/Arabic rendering and real SHAP chart rendering were checked in Chromium.
- Notebook executed successfully; output saved outside the source checkout.
- CSV and Excel copies read back successfully: 10,623 rows, 25 columns. Unknown labels
  and family answers remain blank; protected audit attribute excluded from downloads.

## Container

- Final image **`mizan-ai:2.0`** built successfully using verified cached dependency layers.
- Image ID: `sha256:9c9041c3e5db955bf08233eec0b4429d2effa0077628adecabb864550cb8ee29`.
- Final image checked with external networking disabled: UID **10001**, schema 2,
  eight real predictions, additive eight-input SHAP, `/_stcore/health = ok`, page HTTP 200.
- A daemon smoke run also reached Docker's **healthy** state. Only task smoke containers
  were removed; the host Streamlit process remains available internally on port 8502.

## Limits and platforms

- Experimental, not clinically validated; rare cardiac outcomes still show low recall
  and/or precision. Inspect `MODEL_CARD.md`, `test_metrics.json` and `VERSION_COMPARISON.csv`.
- BIA smart-scale transfer, Saudi population validity and future-risk prediction are unproven.
- The cohort remains selected for complete DXA measurements; no national prevalence inference.
- Python runtime dependencies and locks did not change. Windows startup scripts were prepared
  and reviewed; **actual Windows execution was not available** in this Linux environment.
- A version-1 clean install/container was verified earlier; this record does not claim a
  second fresh installation. Latest source and models were tested in the existing pinned runtime.
- Source changes are local/reviewable. No new GitHub push, hosted deployment or publication
  was performed during this rebuild.
