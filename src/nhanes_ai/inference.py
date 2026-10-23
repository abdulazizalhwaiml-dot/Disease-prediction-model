"""Validated inputs, integrity-checked model releases, and calibrated probability SHAP.

Only load artifacts produced by a trusted training process. SHA256 detects corruption;
it is not a signature and does not make untrusted pickle files safe to deserialize.
"""

import hashlib
import io
import json
import math
import platform
import re
import uuid
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from nhanes_ai.schema import DISEASES, ETHNICITY, FEATURES

LIMITS = {
    "age": (20, 59),
    "waist_cm": (40, 200),
    "weight_kg": (25, 205),
    "height_cm": (120, 220),
    "bone_mass_kg": (0.5, 7),
    "body_fat_pct": (3, 65),
    "fat_mass_kg": (1, 150),
    "lean_mass_kg": (10, 150),
}
USER_FIELDS = ["gender", "ethnicity", *LIMITS]


class InputError(ValueError):
    """An invalid measurement, unsupported age, or internally inconsistent DXA input."""


def validate_record(record: dict) -> pd.DataFrame:
    """Validate ten user fields and calculate BMI on the server as well as the UI."""
    if set(record) != set(USER_FIELDS):
        raise InputError(f"Expected exactly these ten inputs: {USER_FIELDS}")
    clean = {}
    for key, (low, high) in LIMITS.items():
        try:
            value = float(record[key])
        except (TypeError, ValueError) as error:
            raise InputError(f"{key}: a measured number is required") from error
        if isinstance(record[key], bool) or not math.isfinite(value) or not low <= value <= high:
            raise InputError(f"{key}: expected a finite value from {low} to {high}")
        clean[key] = value
    if clean["age"] != int(clean["age"]):
        raise InputError("age: enter completed years")
    if isinstance(record["gender"], bool) or record["gender"] not in (1, 2):
        raise InputError("gender: use NHANES recorded sex code 1 or 2")
    if record["ethnicity"] is not None and (
        isinstance(record["ethnicity"], bool) or record["ethnicity"] not in ETHNICITY
    ):
        raise InputError("ethnicity: use a supported self-identified category or None")
    clean["gender"] = record["gender"]
    clean["ethnicity"] = record["ethnicity"]
    clean["bmi"] = clean["weight_kg"] / (clean["height_cm"] / 100) ** 2
    dxa_total = clean["bone_mass_kg"] + clean["fat_mass_kg"] + clean["lean_mass_kg"]
    if abs(dxa_total - clean["weight_kg"]) > max(10, 0.15 * clean["weight_kg"]):
        raise InputError(
            "composition_weight: bone + fat + lean mass disagree with weight; check kg units"
        )
    expected_fat = 100 * clean["fat_mass_kg"] / dxa_total
    if abs(expected_fat - clean["body_fat_pct"]) > 5:
        raise InputError(
            "composition_fat: fat percentage disagrees with DXA masses by over 5 points"
        )
    return pd.DataFrame([clean])[FEATURES]


def release_fingerprint(root: Path) -> str:
    """A Streamlit resource-cache key changes after atomic model release activation."""
    return hashlib.sha256((root / "current.json").read_bytes()).hexdigest()


class ModelRegistry:
    """Read-only registry; construction fails closed on missing or corrupt artifacts."""

    def __init__(self, root: Path):
        pointer = json.loads((root / "current.json").read_text())
        run_id = pointer["run_id"]
        if not isinstance(run_id, str) or not re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{8}", run_id):
            raise ValueError("Invalid model release ID")
        release = root / run_id
        if release.resolve().parent != root.resolve():
            raise ValueError("Model release escapes the configured model directory")
        manifest_path = release / "manifest.json"
        manifest_bytes = manifest_path.read_bytes()
        if hashlib.sha256(manifest_bytes).hexdigest() != pointer["manifest_sha256"]:
            raise ValueError("Manifest checksum failed")
        self.manifest = json.loads(manifest_bytes)
        if self.manifest["schema_version"] != 1 or self.manifest["run_id"] != run_id:
            raise ValueError("Unsupported model schema or inconsistent release")
        if platform.python_version_tuple()[:2] != tuple(self.manifest["python"].split(".")[:2]):
            raise ValueError("Python major/minor differs from the training runtime")
        for package, expected in self.manifest["versions"].items():
            actual = __import__("xgboost").__version__ if package == "xgboost" else version(package)
            if actual != expected:
                raise ValueError(
                    f"Model dependency mismatch: {package}; expected {expected}, got {actual}"
                )
        if set(self.manifest["models"]) != set(DISEASES):
            raise ValueError("A release must contain all eight diseases")
        self.bundles = {}
        for disease, entry in self.manifest["models"].items():
            if entry["filename"] != f"{disease}.joblib":
                raise ValueError("Unexpected artifact filename")
            path = release / entry["filename"]
            if path.resolve().parent != release.resolve():
                raise ValueError("Artifact path escapes release directory")
            artifact_bytes = path.read_bytes()
            if hashlib.sha256(artifact_bytes).hexdigest() != entry["sha256"]:
                raise ValueError(f"Model checksum failed: {disease}")
            bundle = joblib.load(io.BytesIO(artifact_bytes))
            if bundle["schema_version"] != 1 or bundle["disease"] != disease:
                raise ValueError("Inconsistent artifact schema")
            self.bundles[disease] = bundle

    def predict(self, record: dict):
        frame = validate_record(record)
        predictions = []
        for disease, bundle in self.bundles.items():
            probability = float(bundle["pipeline"].predict_proba(frame)[0, 1])
            if not math.isfinite(probability) or not 0 <= probability <= 1:
                raise ValueError("Invalid model output")
            predictions.append(
                {
                    "disease": disease,
                    "probability": probability,
                    "threshold": bundle["threshold"],
                    "above_threshold": probability >= bundle["threshold"],
                    "algorithm": bundle["algorithm"],
                }
            )
        outside_training = [
            name
            for name, bounds in self.manifest.get("training_reference_ranges", {}).items()
            if not bounds["min"] <= float(frame[name].iloc[0]) <= bounds["max"]
        ]
        return {
            "id": str(uuid.uuid4()),
            "bmi": float(frame.bmi.iloc[0]),
            "predictions": predictions,
            "run_id": self.manifest["run_id"],
            "outside_training_range": outside_training,
        }

    def explain(self, record: dict, disease: str):
        """Permutation SHAP on the actual calibrated probability, with additive validation.

        The numeric masker uses transformed training-background rows. Ethnicity dummy
        contributions are summed for display. Correlated measurements can share credit;
        these are associations within a model, not causal or treatment effects.
        """
        import shap

        if disease not in self.bundles:
            raise ValueError("Unknown disease")
        frame = validate_record(record)
        bundle = self.bundles[disease]
        pipeline = bundle["pipeline"]
        encoded = pipeline.named_steps["preprocess"].transform(frame)
        estimator = pipeline.named_steps["classifier"]
        explainer = shap.PermutationExplainer(
            lambda rows: estimator.predict_proba(rows)[:, 1],
            shap.maskers.Independent(bundle["background"], max_samples=32),
            feature_names=bundle["feature_names"],
            seed=bundle["seed"],
        )
        explanation = explainer(encoded, max_evals=3 * (2 * encoded.shape[1] + 1), silent=True)
        values = explanation.values[0]
        baseline = float(np.asarray(explanation.base_values).ravel()[0])
        probability = float(estimator.predict_proba(encoded)[0, 1])
        if not np.isclose(baseline + values.sum(), probability, atol=1e-6):
            raise ValueError("SHAP explanation does not reconstruct the predicted probability")
        grouped = {}
        for name, value in zip(bundle["feature_names"], values):
            key = "ethnicity" if name.startswith("ethnicity_") else name
            grouped[key] = grouped.get(key, 0.0) + float(value)
        return {
            "baseline": baseline,
            "probability": probability,
            "contributions": grouped,
            "method": "permutation SHAP, calibrated probability",
        }
