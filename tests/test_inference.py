"""Input, encoding, serialization-integrity and real prediction/explanation checks."""

import json
import shutil

import numpy as np
import pandas as pd
import pytest

from nhanes_ai.features import FeatureEncoder, preprocessing
from nhanes_ai.inference import InputError, ModelRegistry, validate_record
from nhanes_ai.schema import DISEASES, FEATURES
from nhanes_ai.train import choose_threshold, metrics


def test_ten_inputs_automatic_bmi_no_id(record):
    assert len(record) == 10
    frame = validate_record(record)
    assert list(frame) == FEATURES
    assert frame.bmi.iloc[0] == pytest.approx(80 / 1.75**2)
    with pytest.raises(InputError):
        validate_record({**record, "bmi": 20})
    with pytest.raises(InputError):
        validate_record({**record, "id": "do-not-learn-id"})


@pytest.mark.parametrize(
    "field,value",
    [
        ("age", 60),
        ("age", 19),
        ("age", 30.5),
        ("weight_kg", np.nan),
        ("height_cm", np.inf),
        ("bone_mass_kg", 3000),
        ("fat_mass_kg", True),
        ("gender", 9),
        ("ethnicity", 5),
        ("lean_mass_kg", None),
    ],
)
def test_input_rejects_bad_values(record, field, value):
    with pytest.raises(InputError):
        validate_record({**record, field: value})


def test_inconsistent_composition(record):
    with pytest.raises(InputError, match="composition_weight"):
        validate_record({**record, "weight_kg": 120})
    with pytest.raises(InputError, match="composition_fat"):
        validate_record({**record, "body_fat_pct": 55})


def test_explicit_unknown_background_and_stable_dummies(record):
    train = validate_record(record)
    unknown = validate_record({**record, "ethnicity": None})
    encoder = FeatureEncoder().fit(train.assign(SEQN=123456, LBXTC=999))
    encoded = encoder.transform(unknown)
    names = encoder.get_feature_names_out().tolist()
    assert encoded[0, names.index("ethnicity_unknown")] == 1
    assert "ethnicity_6" in names  # category absent in fitting rows still has a fixed column
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


def test_real_release_predicts_eight_targets_and_exact_shap(model_root, record):
    registry = ModelRegistry(model_root)
    first = registry.predict(record)
    second = registry.predict(record)
    assert first["id"] != second["id"]
    assert first["predictions"] == second["predictions"]
    assert {p["disease"] for p in first["predictions"]} == set(DISEASES)
    for prediction in first["predictions"]:
        assert 0 <= prediction["probability"] <= 1
        explanation = registry.explain(record, prediction["disease"])
        assert explanation["probability"] == pytest.approx(prediction["probability"])
        assert explanation["baseline"] + sum(
            explanation["contributions"].values()
        ) == pytest.approx(prediction["probability"], abs=1e-6)
    assert registry.manifest["cohort"]["remaining_records"] == 10623
    assert registry.manifest["clinical_validation"] is False


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
    assert registry.manifest["models"]["angina"]["quality_flags"]


def test_path_traversal_is_rejected(tmp_path):
    (tmp_path / "current.json").write_text(json.dumps({"run_id": "../escape"}))
    with pytest.raises(ValueError, match="release ID"):
        ModelRegistry(tmp_path)
