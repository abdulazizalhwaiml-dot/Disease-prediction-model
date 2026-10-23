# Deployment and operations

## Development and training

Use Python 3.12 and install `requirements-dev.lock` with `--require-hashes`, followed by
`pip install --no-deps -e .`. Run from the repository root with `python -m streamlit run
app/main.py`, not `python app/main.py`. The data are already under `DATA_SET/`.

Training CLI defaults: `--data DATA_SET --output models --reports reports --jobs 2`.
Define labels with `--non-hdl 190 --systolic 140 --diastolic 90 --hba1c 6.5`; changing
definitions requires retraining and interpreting a different study outcome. Algorithms
run sequentially, with two threads per model; additionally bound BLAS/OpenMP if needed:
`OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2`.

## Model lifecycle

Each training run produces eight joblib files plus `manifest.json` under a unique
`models/<run-id>/`. The pointer activates only a complete successful run. An interrupted
run can leave an inactive partial directory, but cannot replace the working release.
Keep previous complete releases for rollback.

Reports and model card should be reviewed for actual utility, not merely a successful fit
or high ROC-AUC. Distribute the complete release and matching pointer through controlled
GitHub Releases/CI artifacts; binaries are intentionally ignored by Git. The manifest alone
cannot reconstruct a model. Keep artifact storage trusted and read-only.

`NHANES_MODELS_DIR` can point the app at an alternate trusted directory. The default is
the repository's `models/`. A new pointer changes the cache fingerprint; input/model changes
invalidate session estimates. Exact package versions are checked against the manifest.
Dependency upgrades require lock regeneration, retraining and revalidation; never manually
edit checksums to bypass a failed load.

## Container and hosting

Train before building:

```bash
docker build -t nhanes-ai:1.0 .
docker run --rm -p 8501:8501 --memory=2g --cpus=2 nhanes-ai:1.0
```

The image installs CPU dependencies with hashes, includes OpenMP, copies source/models,
excludes raw data and runs as UID 10001. `/_stcore/health` checks server liveness; actual
model correctness is covered separately by integration tests. Container binding to all
interfaces supports proxy routing.

If your network uses an HTTPS inspection proxy, supply its trusted CA bundle as a
temporary BuildKit secret and forward the existing proxy bindings by name:

```bash
docker build --build-arg HTTP_PROXY --build-arg HTTPS_PROXY \
  --secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t nhanes-ai:1.0 .
```

Use your administrator-provided trusted CA path on other systems. The optional bundle
is mounted only during apt/pip steps and is not copied into the image. TLS, Debian package
signatures and Python artifact hashes remain verified. Never disable certificate checks.

For exposed hosting, supply a TLS/authentication reverse proxy with websocket support,
request limits and session policy. Streamlit has no clinical user-authorization system.
Keep CORS/XSRF enabled. Hosting logs must not record health measurements or websocket
payloads. Limit concurrent SHAP requests and worker resources. See `SECURITY.md`.

## Validation and CI

```bash
ruff check src app tests
ruff format --check src app tests
python -m nhanes_ai.train --jobs 2
pytest -q
```

Model-dependent tests skip explicitly if no release is present. CI trains on the supplied
data before testing, uploads complete artifacts/reports, then builds the container.
The suite covers labels, filtering, encoding, imputation, unit/consistency validation,
artifact corruption, eight real predictions/explanations and bilingual widget execution.
Passing tests do not imply good disease discrimination or clinical effectiveness.

## Dependency updates

Direct versions live in `.txt`; transitive versions/hashes live in `.lock`. After deliberate
pin updates, use a verified `uv` installation to regenerate:

```bash
uv pip compile requirements.txt --python-version 3.12 --only-binary :all: --generate-hashes -o requirements.lock
uv pip compile requirements-dev.txt --python-version 3.12 --only-binary :all: --generate-hashes -o requirements-dev.lock
```

Install into a clean environment, retrain and rerun checks. Preserve TLS and artifact
verification. Never accept patient-uploaded pickle/joblib files.

The actual delivery commands/outcomes are in `reports/VALIDATION.md`. Docker builds and
remote GitHub CI runs are separate from local Python validation; configuration files alone
do not establish that either ran successfully.
