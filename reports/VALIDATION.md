# Delivery validation — 2026-10-23

This records work actually executed in the cloud environment, separate from remote CI,
publication or clinical validation.

## Data and training: passed

- Read and checked all 40 original SAS XPORT files; joined modules one-to-one by SEQN.
- Initial records: **39,156**. Remaining after filtering: **10,623**.
- Ran all **32** target/algorithm comparisons, using Logistic Regression, Random Forest,
  CPU XGBoost and LightGBM for every target.
- Used 2011–2014 fitting/calibration, 2015–2016 selection/thresholds, 2017–2018 testing.
- Exported eight real, calibrated `.joblib` pipelines with checksums, runtime metadata,
  source/data fingerprints, thresholds and results.
- Active release: `20261023T052300Z-6e2717eb`.
- A second metadata/report-producing training run reproduced the initial selected models
  and reported metrics. No test-driven threshold or label tuning was performed.

Command: `OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python -m nhanes_ai.train --jobs 2`.

## Clean installation and software tests: passed

A fresh Python **3.12.14** virtual environment was created outside the checkout. All
dependencies were installed from `requirements-dev.lock` with `--require-hashes`, and the
project was installed editable with no dependency re-resolution.

| Check | Outcome |
|---|---|
| `uv pip check` in clean environment | Compatible dependencies |
| `ruff check src app tests` | Passed |
| `ruff format --check src app tests` | 13 files already formatted |
| `pytest -q` in clean environment | **30 passed**, no skipped tests |
| Eight exported model predictions | Finite probabilities, stable results |
| All eight SHAP explanations | Baseline + contributions matched actual calibrated probability |
| English/Arabic Streamlit AppTest | Passed real widgets, submission, explanations and translated content |
| Input/unit/range/consistency errors | Rejected as expected |
| Corrupted artifacts and traversal paths | Rejected before unpickling |
| Changed inputs / model release | Stale-result invalidation covered |

## Notebook and actual web startup: passed

Executed all code cells in `notebooks/01_data_and_evaluation.ipynb` using the registered
Python 3.12 kernel. Aggregate outputs, the data audit and comparison tables completed.
Executed output is retained outside the source checkout in the cloud setup directory.

Started the actual Streamlit server using `python -m streamlit run app/main.py
--server.address=127.0.0.1`. Internal requests returned `ok` from `/_stcore/health`
and HTTP 200 from the page. Bilingual prediction interactions were independently exercised
by AppTest; a health endpoint alone was not treated as functional model validation.

## Container: passed

Built the pinned Python 3.12 slim image using the supplied Dockerfile. This network's
HTTPS inspection required forwarding existing proxy bindings and mounting the machine's
trusted CA bundle as an optional BuildKit secret, as documented. The initial HTTP route,
missing container trust and secret permissions were diagnosed and corrected. At no point
were TLS verification, Debian signatures or Python artifact hashes disabled.

The final built image passed:

- UID **10001** execution and read-only source/artifact permissions.
- Eight real model predictions and an additive calibrated-probability SHAP explanation.
- Successful inference with external networking disabled.
- Actual Streamlit startup, HTTP page response and a **healthy** Docker health status.
- Container runtime limits of two CPUs and 2 GiB in the server smoke run.

Only smoke containers started by this task were stopped. The host application process
was left running; processes must be restarted after a new cloud machine is created.

## Source and environment preservation

Original `DATA_SET/` files remain unchanged. New source, tests, documentation, notebooks,
dependency locks and deployment configuration are reviewable repository changes. Generated
model binaries and historical run outputs are ignored by Git but included in the delivery
archive for the active release. No patient-entered data are stored in that archive.

Reusable cloud `install_script` and `start_skill` were updated and saved. The installer
was executed successfully and verified all eight models. Draft saving is not environment
publication. A future published-snapshot restore has not been independently tested.

## Remaining limitations

- **Not clinically production-ready.** Rare-target performance is weak. In particular,
  test angina recall/F1 were zero and heart-failure recall was 0.059. See `MODEL_CARD.md`.
- No independent clinical, non-US, prospective or external cohort validation was performed.
- No survey-design-adjusted performance inference or clinical threshold optimization.
- No older-adult coverage: source DXA limits the application to ages 20–59.
- Country-to-ethnicity inference is deliberately replaced by direct optional self-identification.
- Remote GitHub Actions outcomes are separate from the local validation recorded here;
  consult the repository's Actions page for current remote results. No hosted clinical
  deployment or environment publication was performed by these validation commands.

## Windows startup follow-up

The runtime dependencies were resolved for Windows x64 / Python 3.12 using binary-only
packages and verified hashes, saved as `requirements-windows.lock`. Windows PowerShell
instructions are in `docs/WINDOWS.md`; they do not require activating scripts or changing
execution policy. Actual Windows execution was not available in this cloud environment.
