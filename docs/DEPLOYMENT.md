# Running and deploying

Use Python3.12. Install `requirements.lock` (or the Windows lock) with `--require-hashes`,
then `pip install --no-deps -e .`. The ready project includes the current schema3 models.

```bash
python -m streamlit run streamlit_app.py
```

## Retraining

```bash
python scripts/download_data.py
python -m nhanes_ai.train --jobs 2
python scripts/export_dataset.py
pytest -q
```

Older raw data are fetched from official CDC URLs and verified against pinned hashes.
Training defaults: non-HDL190, systolic140, diastolic90, HbA1c6.5, seed42, two threads.
A successful run creates `models/<run-id>/` and activates `current.json` atomically.
The app checks schema3, age limits20–79, eight-input contract, versions and checksums.
Do not bypass these checks; retrain after changing model-runtime dependencies.

`NHANES_MODELS_DIR` selects an alternate trusted model directory. Input or model changes
clear session results. Keep models/code read-only. Do not accept uploaded pickle/joblib files.

## Docker

Train first or use the prepared trusted model release:

```bash
docker build -t mizan-ai:3.0 .
docker run --rm -p 8501:8501 --memory=2g --cpus=2 mizan-ai:3.0
```

The container excludes raw data and runs as UID10001. For an HTTPS inspection proxy,
pass the administrator's trusted CA as a temporary BuildKit secret:

```bash
docker build --build-arg HTTP_PROXY --build-arg HTTPS_PROXY \
  --secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t mizan-ai:3.0 .
```

No certificate/hash verification is disabled. A reverse proxy must support WebSockets;
keep CORS/XSRF enabled and avoid recording health inputs in logs. See SECURITY.md.
`/_stcore/health` proves server liveness; integration tests check actual prediction.

## Checks and dependency updates

```bash
ruff check src app tests scripts
ruff format --check src app tests scripts
pytest -q
```

CI downloads original older files, trains, tests and builds a container. Model-dependent
tests skip if no release exists; delivery verification requires no such skips.
Actual executed checks are recorded in reports/VALIDATION.md.

After intentional dependency changes, regenerate all four locks using verified `uv`:

```bash
uv pip compile requirements.txt --python-version 3.12 --generate-hashes -o requirements.lock
uv pip compile requirements-dev.txt --python-version 3.12 --generate-hashes -o requirements-dev.lock
uv pip compile requirements.txt --python-version 3.12 --python-platform windows --generate-hashes -o requirements-windows.lock
uv pip compile requirements-dev.txt --python-version 3.12 --python-platform windows --generate-hashes -o requirements-windows-dev.lock
```

Use a clean environment and retrain before distributing new runtime versions.

The Windows CI job loads the committed release, tests the bilingual app and cp1256 regression,
and parses the launcher using Windows PowerShell. It uses requirements-windows-dev.lock.
