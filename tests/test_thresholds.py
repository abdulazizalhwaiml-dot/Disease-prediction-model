"""Check threshold trade-offs, ties, invalid inputs and validation-only boundaries."""

from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from nhanes_ai.rethreshold import plan_thresholds
from nhanes_ai.schema import FEATURES
from nhanes_ai.thresholds import choose_threshold
from nhanes_ai.train import metrics


def test_recall_guard_prevents_the_unconstrained_f1_sensitivity_drop():
    y = np.array([1, 0, 0, 0, 1, 1, 1, 0])
    p = np.linspace(0.05, 0.95, len(y))
    baseline = metrics(y, p, choose_threshold(y, p, policy="recall"))
    unguarded = metrics(y, p, choose_threshold(y, p, policy="f1"))
    guarded = metrics(y, p, choose_threshold(y, p))
    assert baseline["recall"] == 1
    assert unguarded["recall"] == 0.75
    assert unguarded["precision"] == 0.75
    assert guarded["recall"] >= baseline["recall"] - 0.10
    assert guarded["f1"] >= baseline["f1"]
    # A consciously relaxed research guard permits the alternative operating point.
    relaxed = metrics(y, p, choose_threshold(y, p, max_recall_drop=0.25))
    assert relaxed["f1"] == unguarded["f1"]


def test_identical_probabilities_are_never_split_at_a_threshold():
    y = np.array([0, 1, 0, 1])
    p = np.repeat(0.2, len(y))
    assert choose_threshold(y, p) == 0.2
    assert metrics(y, p, 0.2)["confusion_matrix"] == {"tn": 0, "fp": 2, "fn": 0, "tp": 2}


@pytest.mark.parametrize(
    "y,p",
    [
        ([], []),
        ([0, 0], [0.1, 0.2]),
        ([0, 1], [0.2]),
        ([0, 2], [0.1, 0.2]),
        ([0, 1], [0.1, np.nan]),
        ([0, 1], [0.1, np.inf]),
        ([0, 1], [0.1, 1.1]),
        ([0, 1], [-0.1, 0.5]),
        ([[0], [1]], [0.1, 0.5]),
    ],
)
def test_invalid_threshold_inputs_fail(y, p):
    with pytest.raises(ValueError, match="binary labels"):
        choose_threshold(y, p)


@pytest.mark.parametrize("drop", [-0.1, 1.1, np.nan])
def test_invalid_recall_drop_fails(drop):
    with pytest.raises(ValueError, match="Recall-drop"):
        choose_threshold([0, 1], [0.1, 0.9], max_recall_drop=drop)


class FakePipeline:
    def predict_proba(self, frame):
        p = frame.age.to_numpy(dtype=float) / 100
        return np.column_stack([1 - p, p])


def validation_fixture():
    frame = pd.DataFrame({name: np.zeros(8) for name in FEATURES})
    frame["age"] = np.linspace(5, 95, 8)
    frame["diabetes"] = [1, 0, 0, 0, 1, 1, 1, 0]
    frame["stroke"] = frame.diabetes
    frame["partition"] = "validation"
    frame["cycle"] = "2015-2016"
    return frame


def test_plan_uses_validation_only_and_keeps_rare_target_points():
    frame = validation_fixture()
    bundle = {"threshold": 0.05, "pipeline": FakePipeline()}
    # No manifest/test scores are provided: selection only needs fitted pipelines and validation.
    registry = SimpleNamespace(bundles={"diabetes": bundle, "stroke": bundle})
    plan = plan_thresholds(registry, frame, max_recall_drop=0.25)
    assert plan["targets"]["diabetes"]["threshold"] > 0.5
    assert plan["targets"]["stroke"]["threshold"] == 0.05
    assert plan["targets"]["stroke"]["deployment_scope"] == "retain_previous"
    assert plan["policy"]["test_used_for_selection"] is False


@pytest.mark.parametrize("partition", ["test", "development", None])
def test_plan_rejects_any_non_validation_row(partition):
    frame = validation_fixture()
    frame.loc[0, "partition"] = partition
    with pytest.raises(ValueError, match="validation rows only"):
        plan_thresholds(SimpleNamespace(bundles={}), frame)


def test_accuracy_is_reported_with_imbalance_baseline_and_sensitivity():
    y = np.array([0] * 99 + [1])
    result = metrics(y, np.repeat(0.01, 100), 0.5)
    assert result["accuracy"] == result["majority_baseline_accuracy"] == 0.99
    assert result["recall"] == 0
    assert result["balanced_accuracy"] == 0.5
