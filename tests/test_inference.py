"""Input, encoding, serialization-integrity and real prediction checks."""

import json
import shutil

import numpy as np
import pandas as pd
import pytest

from nhanes_ai.features import FeatureEncoder, preprocessing
from nhanes_ai.inference import InputError, ModelRegistry, validate_record
from nhanes_ai.schema import DISEASES, FEATURES
from nhanes_ai.train import choose_threshold, metrics


def test_eight_inputs_automatic_composition_no_id(record):
    assert len(record) == 8
    frame = validate_record(record)
    assert list(frame) == FEATURES
    assert frame.bmi.iloc[0] == pytest.approx(80 / 1.75**2)
    assert frame.fat_mass_kg.iloc[0] == 24
    assert frame.fat_free_mass_kg.iloc[0] == 56
    with pytest.raises(InputError):
        validate_record({**record, "bmi": 20})
    with pytest.raises(InputError):
        validate_record({**record, "id": "do-not-learn-id"})


@pytest.mark.parametrize(
    "field,value",
    [
        ("age", 80),
        ("age", 19),
        ("age", 30.5),
        ("weight_kg", np.nan),
        ("height_cm", np.inf),
        ("body_fat_pct", 3000),
        ("body_fat_pct", True),
        ("gender", 9),
        ("family_diabetes", 9),
        ("family_diabetes", None),
        ("family_heart_early", 2),
    ],
)
def test_input_rejects_bad_values(record, field, value):
    with pytest.raises(InputError):
        validate_record({**record, field: value})


def test_composition_is_recomputed_and_cannot_be_injected(record):
    result = validate_record({**record, "weight_kg": 120})
    assert result.fat_mass_kg.iloc[0] == 36
    assert result.fat_free_mass_kg.iloc[0] == 84
    with pytest.raises(InputError):
        validate_record({**record, "fat_free_mass_kg": 84})


def test_explicit_unknown_family_and_stable_dummies(record):
    train = validate_record(record)
    unknown = train.copy()
    unknown.loc[0, "family_diabetes"] = np.nan
    encoder = FeatureEncoder().fit(train.assign(SEQN=123456, LBXTC=999, ethnicity=3))
    encoded = encoder.transform(unknown)
    names = encoder.get_feature_names_out().tolist()
    assert encoded[0, names.index("family_diabetes_unknown")] == 1
    assert encoded[0, names.index("family_diabetes_no")] == 0
    assert "family_heart_early_yes" in names
    assert not any("ethnicity" in name for name in names)
    assert "SEQN" not in names and "LBXTC" not in names
    assert encoder.transform(train).shape == encoded.shape


def test_imputation_is_fitted_only_on_training_rows(record):
    fit = pd.concat(
        [validate_record(record), validate_record({**record, "age": 35})], ignore_index=True
    )
    pre = preprocessing().fit(fit)
    before = pre.named_steps["impute"].statistics_.copy()
    inference = fit.copy()
    inference.loc[0, "age"] = np.nan
    assert np.isfinite(pre.transform(inference)).all()
    np.testing.assert_array_equal(before, pre.named_steps["impute"].statistics_)


def test_threshold_optimizes_validation_f2():
    y = np.array([0, 1, 0, 1, 1])
    p = np.array([0.05, 0.2, 0.3, 0.6, 0.7])
    threshold = choose_threshold(y, p)
    assert metrics(y, p, threshold)["f2"] == max(metrics(y, p, t)["f2"] for t in p)


def test_real_release_predicts_eight_targets_and_expanded_ages(model_root, record):
    registry = ModelRegistry(model_root)
    for age in [20, 45, 60, 79]:
        first = registry.predict({**record, "age": age})
        second = registry.predict({**record, "age": age})
        assert first["id"] != second["id"]
        assert first["predictions"] == second["predictions"]
        assert {p["disease"] for p in first["predictions"]} == set(DISEASES)
        assert all(0 <= p["probability"] <= 1 for p in first["predictions"])
    assert registry.manifest["cohort"]["remaining_records"] == 21117
    assert registry.manifest["cohort"]["age_groups"]["60-79"] == 2789
    assert registry.manifest["clinical_validation"] is False
    assert registry.manifest["age_limits"] == [20, 79]
    assert not hasattr(registry, "explain")


def test_corruption_fails_before_unpickling(model_root, tmp_path):
    pointer = json.loads((model_root / "current.json").read_text())
    release = tmp_path / pointer["run_id"]
    shutil.copytree(model_root / pointer["run_id"], release)
    shutil.copy(model_root / "current.json", tmp_path / "current.json")
    (release / "angina.joblib").write_bytes(b"corrupt artifact")
    with pytest.raises(ValueError, match="checksum"):
        ModelRegistry(tmp_path)


def test_development_range_extrapolation_is_explicit(model_root, record):
    registry = ModelRegistry(model_root)
    result = registry.predict({**record, "height_cm": 220})
    assert "height_cm" in result["outside_training_range"]
    assert any(entry["quality_flags"] for entry in registry.manifest["models"].values())


def test_path_traversal_is_rejected(tmp_path):
    (tmp_path / "current.json").write_text(json.dumps({"run_id": "../escape"}))
    with pytest.raises(ValueError, match="release ID"):
        ModelRegistry(tmp_path)


def test_old_input_schema_is_rejected_before_artifact_loading(model_root, tmp_path):
    import hashlib

    pointer = json.loads((model_root / "current.json").read_text())
    manifest = json.loads((model_root / pointer["run_id"] / "manifest.json").read_text())
    manifest["schema_version"] = 1
    release = tmp_path / pointer["run_id"]
    release.mkdir()
    manifest_bytes = json.dumps(manifest).encode()
    (release / "manifest.json").write_bytes(manifest_bytes)
    pointer["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    (tmp_path / "current.json").write_text(json.dumps(pointer))
    with pytest.raises(ValueError, match="Unsupported model schema"):
        ModelRegistry(tmp_path)
