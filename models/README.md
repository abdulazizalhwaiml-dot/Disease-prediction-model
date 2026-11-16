# Trusted model release

`current.json` selects the active directory containing eight calibrated joblib pipelines and
`manifest.json`. The manifest records exact sources, schema3, ages20–79, runtime versions,
selection rules, evaluation results and artifact checksums.

The ready application includes a complete trusted release. Rebuild with:

```bash
python scripts/download_data.py
python -m nhanes_ai.train --jobs 2
```

Activation is atomic: a failed run does not replace the working release. Do not edit checksums
or load user-uploaded pickle/joblib files. Keep code and model storage trusted and read-only.

Version4.2 retains fitted/calibrated pipelines and re-selects only the three cardiometabolic
alert levels on validation rows. Run `python -m nhanes_ai.rethreshold` to reproduce the policy
from a compatible trusted source release. It verifies raw source hashes/cohort reconstruction,
freezes validation decisions before test evaluation, checks unchanged probabilities after export,
and verifies the new registry before activating. See docs/THRESHOLD_REVIEW.md for trade-offs.
