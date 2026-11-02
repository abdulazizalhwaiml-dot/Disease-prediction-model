"""Validated inputs, integrity-checked model releases, and calibrated probabilities.

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
import pandas as pd

from nhanes_ai.features import derive_features
from nhanes_ai.schema import (
    AGE_MAX,
    AGE_MIN,
    DISEASES,
    FAMILY_FIELDS,
    FEATURES,
    SCHEMA_VERSION,
    USER_FIELDS,
)

LIMITS = {
    "age": (AGE_MIN, AGE_MAX),
    "waist_cm": (40, 200),
    "weight_kg": (25, 205),
    "height_cm": (120, 220),
    "body_fat_pct": (3, 65),
}


class InputError(ValueError):
    """An invalid measurement, unsupported age, or missing family-history answer."""


def validate_record(record: dict) -> pd.DataFrame:
    """Validate exactly eight inputs and derive BMI, fat mass and fat-free mass."""
    if set(record) != set(USER_FIELDS):
        raise InputError(f"Expected exactly these eight inputs: {USER_FIELDS}")
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
    clean["gender"] = record["gender"]
    for name in FAMILY_FIELDS:
        if isinstance(record[name], bool) or record[name] not in (0, 1):
            raise InputError(f"{name}: choose yes (1) or no (0)")
        clean[name] = int(record[name])
    return derive_features(pd.DataFrame([clean]))


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
        if self.manifest["schema_version"] != SCHEMA_VERSION or self.manifest["run_id"] != run_id:
            raise ValueError("Unsupported model schema or inconsistent release")
        if (
            self.manifest.get("user_fields") != USER_FIELDS
            or self.manifest.get("features") != FEATURES
        ):
            raise ValueError("Model input contract does not match the eight-input app")
        if self.manifest.get("age_limits") != [AGE_MIN, AGE_MAX]:
            raise ValueError("Model age scope does not match the application")
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
            if bundle["schema_version"] != SCHEMA_VERSION or bundle["disease"] != disease:
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
            "fat_mass_kg": float(frame.fat_mass_kg.iloc[0]),
            "fat_free_mass_kg": float(frame.fat_free_mass_kg.iloc[0]),
            "predictions": predictions,
            "run_id": self.manifest["run_id"],
            "outside_training_range": outside_training,
        }
