"""Re-select research alert levels on validation rows without refitting models.

python -m nhanes_ai.rethreshold --data DATA_SET --models models --reports reports
All validation decisions are frozen before the historical test set is evaluated.
"""

import argparse
import copy
import hashlib
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from nhanes_ai.data import prepare_cohort, read_cycles
from nhanes_ai.inference import ModelRegistry
from nhanes_ai.schema import FEATURES, LabelConfig
from nhanes_ai.thresholds import (
    BALANCED_TARGETS,
    DEFAULT_MAX_RECALL_DROP,
    choose_threshold,
    threshold_policy,
)
from nhanes_ai.train import (
    bootstrap_intervals,
    metrics,
    save_json,
    subgroup_metrics,
    write_model_card,
)


def plan_thresholds(registry, validation, max_recall_drop=DEFAULT_MAX_RECALL_DROP):
    """Only validation rows are accepted; the complete decision plan precedes test evaluation."""
    if validation.empty or not validation.partition.eq("validation").fillna(False).all():
        raise ValueError("Threshold selection accepts validation rows only")
    plan = {"policy": threshold_policy(max_recall_drop), "targets": {}}
    for disease, bundle in registry.bundles.items():
        known = validation.loc[validation[disease].notna()]
        y = known[disease].to_numpy(dtype=int)
        probability = bundle["pipeline"].predict_proba(known[FEATURES])[:, 1]
        candidate = choose_threshold(y, probability, max_recall_drop=max_recall_drop)
        selected = candidate if disease in BALANCED_TARGETS else bundle["threshold"]
        candidates = {
            "previous": bundle["threshold"],
            "recall_f2": choose_threshold(y, probability, policy="recall"),
            "unconstrained_f1": choose_threshold(y, probability, policy="f1"),
            "balanced_candidate": candidate,
            "adopted": selected,
        }
        plan["targets"][disease] = {
            "threshold": selected,
            "changed": selected != bundle["threshold"],
            "deployment_scope": "balanced" if disease in BALANCED_TARGETS else "retain_previous",
            "validation_cycles": sorted(known.cycle.unique()),
            "comparison": {
                name: metrics(y, probability, value) for name, value in candidates.items()
            },
        }
        scores = plan["targets"][disease]["comparison"]
        if disease in BALANCED_TARGETS:
            if (
                scores["adopted"]["recall"]
                < scores["recall_f2"]["recall"] - max_recall_drop - 1e-12
            ):
                raise ValueError("Selected validation sensitivity violates the research guard")
            if scores["adopted"]["f1"] < scores["recall_f2"]["f1"] - 1e-12:
                raise ValueError("Selected validation F1 is below the eligible F2 baseline")
    return plan


def comparison_row(disease, partition, before, after):
    keys = [
        "threshold",
        "accuracy",
        "recall",
        "precision",
        "specificity",
        "balanced_accuracy",
        "f1",
        "f2",
        "roc_auc",
        "pr_auc",
        "alert_rate",
        "majority_baseline_accuracy",
    ]
    return {
        "disease": disease,
        "partition": partition,
        "n": after["n"],
        "positive": after["positive"],
        **{
            f"{side}_{key}": score[key]
            for side, score in [("before", before), ("after", after)]
            for key in keys
        },
        **{
            f"{side}_{key}": value
            for side, score in [("before", before), ("after", after)]
            for key, value in score["confusion_matrix"].items()
        },
    }


def rethreshold(data_root, model_root, reports, max_recall_drop=DEFAULT_MAX_RECALL_DROP):
    registry = ModelRegistry(model_root)
    original = registry.manifest
    for name, digest in original["sources_sha256"].items():
        if hashlib.sha256((data_root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Original source checksum mismatch: {name}")
    cohort, audit = prepare_cohort(read_cycles(data_root), LabelConfig(**original["label_config"]))
    if audit != original["cohort"]:
        raise ValueError("Cohort reconstruction differs from the original trained release")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    report_dir = reports / "runs" / run_id
    report_dir.mkdir(parents=True, exist_ok=False)
    plan = plan_thresholds(registry, cohort.loc[cohort.partition.eq("validation")], max_recall_drop)
    plan.update(source_release=original["run_id"], selected_before_test_evaluation=True)
    # Freeze every target's operating point before reading any test labels/probabilities.
    save_json(report_dir / "threshold_selection.json", plan)
    plan_digest = hashlib.sha256((report_dir / "threshold_selection.json").read_bytes()).hexdigest()
    print("Frozen validation-only threshold plan:", plan_digest, flush=True)

    release = model_root / run_id
    release.mkdir(exist_ok=False)
    manifest = copy.deepcopy(original)
    comparisons, evaluations, age_rows = [], {}, []
    for disease, bundle in registry.bundles.items():
        threshold = plan["targets"][disease]["threshold"]
        test = cohort.loc[cohort.partition.eq("test") & cohort[disease].notna()]
        y = test[disease].to_numpy(dtype=int)
        probability = bundle["pipeline"].predict_proba(test[FEATURES])[:, 1]
        before = metrics(y, probability, bundle["threshold"])
        # Verify that the old artifact/test reconstruction matches the published baseline.
        if before["confusion_matrix"] != original["models"][disease]["test"]["confusion_matrix"]:
            raise ValueError(f"Published baseline no longer reproduces for {disease}")
        after = metrics(y, probability, threshold)
        for key in ["roc_auc", "pr_auc", "brier"]:
            if before[key] != after[key]:
                raise ValueError("Threshold-only changes must preserve probability-based scores")
        evaluation = {
            **after,
            "algorithm": bundle["algorithm"],
            "bootstrap_95_ci": bootstrap_intervals(y, probability, threshold, original["seed"]),
            "subgroups": subgroup_metrics(test, y, probability, threshold),
            "splits": original["models"][disease]["test"]["splits"],
        }
        evaluations[disease] = evaluation
        comparisons.append(comparison_row(disease, "test", before, after))
        validation = plan["targets"][disease]["comparison"]
        comparisons.append(
            comparison_row(disease, "validation", validation["previous"], validation["adopted"])
        )
        for group, score in evaluation["subgroups"]["age_group"].items():
            age_rows.append(
                {
                    "disease": disease,
                    "age_group": group,
                    **{key: value for key, value in score.items() if key != "confusion_matrix"},
                }
            )

        # Re-export the same fitted/calibrated pipeline with only a changed alert level.
        bundle = {**bundle, "threshold": threshold}
        filename = original["models"][disease]["filename"]
        path = release / filename
        expected = bundle["pipeline"].predict_proba(cohort[FEATURES])
        if disease in BALANCED_TARGETS:
            joblib.dump(bundle, path, compress=3)
        else:
            shutil.copyfile(model_root / original["run_id"] / filename, path)
        restored = joblib.load(path)
        np.testing.assert_array_equal(
            restored["pipeline"].predict_proba(cohort[FEATURES]), expected
        )
        flags = []
        if after["recall"] < 0.5:
            flags.append("low_heldout_recall")
        if after["precision"] < 0.1:
            flags.append("low_heldout_precision")
        if after["positive"] < 30:
            flags.append("few_positive_test_cases")
        if after["accuracy"] < after["majority_baseline_accuracy"]:
            flags.append("accuracy_below_majority_baseline")
        manifest["models"][disease].update(
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            threshold=threshold,
            validation=validation["adopted"],
            test=evaluation,
            quality_flags=flags,
        )
        print(
            f"{disease}: F1 {before['f1']:.3f}->{after['f1']:.3f}, "
            f"recall {before['recall']:.3f}->{after['recall']:.3f}, "
            f"precision {before['precision']:.3f}->{after['precision']:.3f}, "
            f"false positives {before['confusion_matrix']['fp']}->{after['confusion_matrix']['fp']}",
            flush=True,
        )
    manifest.update(
        run_id=run_id,
        threshold_policy=plan["policy"],
        threshold_selection="maximum validation F1 with a validation-F2 recall guard; no test-set tuning",
        threshold_update={
            "source_release": original["run_id"],
            "source_manifest_sha256": hashlib.sha256(
                (model_root / original["run_id"] / "manifest.json").read_bytes()
            ).hexdigest(),
            "pipelines_refitted": False,
            "calibration_refitted": False,
            "validation_plan_sha256": plan_digest,
            "probability_roundtrip_verified_rows": len(cohort),
            "maximum_probability_change": 0,
            "historical_test_reused": True,
            "fresh_external_validation": False,
            "changed_targets": list(BALANCED_TARGETS),
            "other_targets": "previous operating points and artifact bytes retained",
        },
        threshold_update_code_sha256={
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(__file__).parent.glob("*.py")
        },
    )
    save_json(release / "manifest.json", manifest)
    pointer = {
        "run_id": run_id,
        "manifest_sha256": hashlib.sha256((release / "manifest.json").read_bytes()).hexdigest(),
    }
    with tempfile.TemporaryDirectory(prefix="mizanak-threshold-check-") as directory:
        check = Path(directory)
        save_json(check / "current.json", pointer)
        shutil.copytree(release, check / run_id)
        ModelRegistry(check)
    save_json(report_dir / "test_metrics.json", evaluations)
    pd.DataFrame(comparisons).to_csv(report_dir / "threshold_comparison.csv", index=False)
    pd.DataFrame(age_rows).to_csv(report_dir / "age_validation.csv", index=False)
    write_model_card(report_dir / "MODEL_CARD.md", manifest)
    reports.mkdir(parents=True, exist_ok=True)
    for filename in [
        "threshold_selection.json",
        "threshold_comparison.csv",
        "test_metrics.json",
        "age_validation.csv",
        "MODEL_CARD.md",
    ]:
        shutil.copyfile(report_dir / filename, reports / filename)
    temporary = model_root / f".threshold-{uuid.uuid4().hex}.json"
    save_json(temporary, pointer)
    os.replace(temporary, model_root / "current.json")
    print(f"Activated integrity-checked research release {run_id}", flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("DATA_SET"))
    parser.add_argument("--models", type=Path, default=Path("models"))
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    parser.add_argument("--max-recall-drop", type=float, default=DEFAULT_MAX_RECALL_DROP)
    args = parser.parse_args()
    if not np.isfinite(args.max_recall_drop) or not 0 <= args.max_recall_drop <= 1:
        parser.error("Recall-drop allowance must be between 0 and 1")
    rethreshold(args.data, args.models, args.reports, args.max_recall_drop)


if __name__ == "__main__":
    main()
