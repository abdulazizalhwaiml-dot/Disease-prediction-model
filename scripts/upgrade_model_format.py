"""Re-export trusted existing models in a portable format, without retraining.

Run only for a trusted local release: python scripts/upgrade_model_format.py
All predictions are checked on the full exported cohort before atomic activation.
"""

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from nhanes_ai.inference import ModelRegistry
from nhanes_ai.schema import FEATURES
from nhanes_ai.serialization import make_portable
from nhanes_ai.train import save_json, write_model_card


def main():
    root = Path(__file__).resolve().parents[1]
    models = root / "models"
    registry = ModelRegistry(models)  # Validate every source artifact before conversion.
    source_id = registry.manifest["run_id"]
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    destination = models / run_id
    destination.mkdir()
    frame = pd.read_csv(root / "data/processed/NHANES_MIZAN.csv")[FEATURES]
    manifest = json.loads(json.dumps(registry.manifest))
    for disease, bundle in registry.bundles.items():
        filename = manifest["models"][disease]["filename"]
        path = destination / filename
        if bundle["algorithm"] == "xgboost":
            expected = bundle["pipeline"].predict_proba(frame)
            make_portable(bundle["pipeline"])
            joblib.dump(bundle, path, compress=3)
            restored = joblib.load(path)
            actual = restored["pipeline"].predict_proba(frame)
            np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)
            print(
                f"{disease}: portable re-export verified on all {len(frame):,} rows; max delta {np.abs(actual - expected).max():.3g}",
                flush=True,
            )
        else:
            shutil.copyfile(models / source_id / filename, path)
        manifest["models"][disease]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest["run_id"] = run_id
    manifest["format_conversion"] = {
        "source_release": source_id,
        "retrained": False,
        "xgboost_format": "UBJSON model; runtime CPU/two-thread setting",
        "verified_rows": len(frame),
        "prediction_tolerance": 1e-12,
    }
    manifest["export_code_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (root / "src/nhanes_ai").glob("*.py")
    }
    save_json(destination / "manifest.json", manifest)
    temporary = models / ".current-portable.json"
    save_json(
        temporary,
        {
            "run_id": run_id,
            "manifest_sha256": hashlib.sha256(
                (destination / "manifest.json").read_bytes()
            ).hexdigest(),
        },
    )
    # Verify the complete new release using a temporary isolated pointer before activation.
    check = root / ".portable-check"
    check.mkdir(exist_ok=False)
    try:
        shutil.copyfile(temporary, check / "current.json")
        shutil.copytree(destination, check / run_id)
        ModelRegistry(check)
    finally:
        shutil.rmtree(check)
    os.replace(temporary, models / "current.json")
    write_model_card(root / "reports/MODEL_CARD.md", manifest)
    print(f"Activated portable release: {run_id}")


if __name__ == "__main__":
    main()
