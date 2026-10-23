"""Shared synthetic inputs; tests never require patient-entered data."""

from pathlib import Path

import pytest


@pytest.fixture
def record():
    return dict(
        age=45,
        gender=1,
        waist_cm=95,
        weight_kg=80,
        height_cm=175,
        body_fat_pct=30,
        family_diabetes=1,
        family_heart_early=0,
    )


@pytest.fixture(scope="session")
def model_root():
    root = Path(__file__).resolve().parents[1] / "models"
    if not (root / "current.json").is_file():
        pytest.skip("Integration test requires an actual trained release; run nhanes-train")
    return root
