"""Shared synthetic inputs; tests never require patient-entered data."""

from pathlib import Path

import pytest


@pytest.fixture
def record():
    return dict(
        age=45,
        gender=1,
        ethnicity=3,
        waist_cm=95,
        weight_kg=80,
        height_cm=175,
        bone_mass_kg=3,
        body_fat_pct=30,
        fat_mass_kg=24,
        lean_mass_kg=53,
    )


@pytest.fixture(scope="session")
def model_root():
    root = Path(__file__).resolve().parents[1] / "models"
    if not (root / "current.json").is_file():
        pytest.skip("Integration test requires an actual trained release; run nhanes-train")
    return root
