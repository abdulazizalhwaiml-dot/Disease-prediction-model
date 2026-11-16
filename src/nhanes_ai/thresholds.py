"""Validation-only operating points; research trade-offs, not clinical cutoffs."""

import numpy as np
from sklearn.metrics import precision_recall_curve

DEFAULT_MAX_RECALL_DROP = 0.10
BALANCED_TARGETS = ("high_cholesterol", "high_blood_pressure", "diabetes")


def threshold_policy(max_recall_drop=DEFAULT_MAX_RECALL_DROP):
    return {
        "name": "validation_f1_with_recall_guard",
        "balanced_targets": list(BALANCED_TARGETS),
        "other_targets": "retain previous validation-F2 operating points",
        "objective": "maximum validation F1",
        "baseline": "maximum validation F2",
        "max_validation_recall_drop": max_recall_drop,
        "tie_break": "highest threshold within absolute score tolerance 1e-12",
        "clinical_cutoff": False,
        "test_used_for_selection": False,
    }


def choose_threshold(
    y, probabilities, *, policy="balanced", max_recall_drop=DEFAULT_MAX_RECALL_DROP
):
    """Maximise F1 with a validation recall guard, or reproduce the F2 objective.

    The guard is relative to the same pipeline's maximum-F2 validation point.
    It is an explicit research preference, not a minimum clinical sensitivity or
    a guarantee on unseen data. Selection has no access to test-set outcomes.
    """
    y = np.asarray(y)
    probabilities = np.asarray(probabilities, dtype=float)
    if (
        y.ndim != 1
        or probabilities.ndim != 1
        or y.shape != probabilities.shape
        or set(np.unique(y)) != {0, 1}
        or not np.isfinite(probabilities).all()
        or np.any((probabilities < 0) | (probabilities > 1))
    ):
        raise ValueError("Expected matching binary labels and finite probabilities in [0, 1]")
    if policy not in {"balanced", "recall", "f1"}:
        raise ValueError("Unknown threshold policy")
    if not np.isfinite(max_recall_drop) or not 0 <= max_recall_drop <= 1:
        raise ValueError("Recall-drop allowance must be between 0 and 1")
    precision, recall, thresholds = precision_recall_curve(y, probabilities)
    precision, recall = precision[:-1], recall[:-1]
    f2 = 5 * precision * recall / np.maximum(4 * precision + recall, 1e-12)
    previous = np.flatnonzero(np.isclose(f2, f2.max(), rtol=0, atol=1e-12))[-1]
    if policy == "recall":
        return float(thresholds[previous])
    f1 = 2 * precision * recall / np.maximum(precision + recall, 1e-12)
    eligible = (
        recall >= recall[previous] - max_recall_drop - 1e-12
        if policy == "balanced"
        else np.ones(len(thresholds), dtype=bool)
    )
    best_score = f1[eligible].max()
    best = np.flatnonzero(eligible & np.isclose(f1, best_score, rtol=0, atol=1e-12))[-1]
    return float(thresholds[best])
