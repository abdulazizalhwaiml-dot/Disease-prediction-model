# Trusted model releases

Run `python -m nhanes_ai.train` from the project root. Training writes eight calibrated
`.joblib` pipelines to a versioned release directory, plus `manifest.json` containing
SHA256 checksums, runtime versions, label definitions, cohort counts and test results.
`current.json` is atomically updated only after the complete run succeeds.

The app checks all eight models, manifest integrity and dependency versions before use.
Do not edit the pointer or checksums manually. Only load locally trained or independently
trusted artifacts: joblib/pickle can execute code, and a checksum is not a digital signature.

Model binaries are generated artifacts, excluded from Git. Publish a complete release
directory **and** its `current.json` as a GitHub release/CI artifact or bake them into the
container. Keep the directory read-only in deployment. Retain the previous release for
rollback. The current training runtime and source data are recorded in the manifest.
