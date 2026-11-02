"""Reproducible temporal model comparison, calibration, thresholding and export.

Usage: python -m nhanes_ai.train --data DATA_SET --output models
No holdout rows are used to fit preprocessing, calibration or decision thresholds.
"""

import argparse
import hashlib
import json
import os
import platform
import uuid
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.frozen import FrozenEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from nhanes_ai.data import prepare_cohort, read_cycles
from nhanes_ai.features import preprocessing
from nhanes_ai.schema import (
    AGE_MAX,
    AGE_MIN,
    DISEASES,
    FEATURES,
    NUMERIC,
    PARTITIONS,
    SCHEMA_VERSION,
    USER_FIELDS,
    LabelConfig,
)


def classifiers(y, seed, jobs):
    """Bounded CPU algorithms; weighting is learned only from the fitting partition."""
    imbalance = float((y == 0).sum() / (y == 1).sum())
    return {
        "logistic_regression": LogisticRegression(
            C=0.5, class_weight="balanced", max_iter=2000, random_state=seed
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=160,
            max_depth=9,
            min_samples_leaf=12,
            max_features="sqrt",
            class_weight="balanced_subsample",
            n_jobs=jobs,
            random_state=seed,
        ),
        "xgboost": XGBClassifier(
            n_estimators=160,
            max_depth=3,
            learning_rate=0.04,
            subsample=0.85,
            colsample_bytree=0.85,
            reg_lambda=5,
            min_child_weight=8,
            scale_pos_weight=imbalance,
            tree_method="hist",
            device="cpu",
            eval_metric="logloss",
            n_jobs=jobs,
            random_state=seed,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=160,
            max_depth=4,
            num_leaves=12,
            learning_rate=0.04,
            min_child_samples=30,
            reg_lambda=5,
            class_weight="balanced",
            n_jobs=jobs,
            random_state=seed,
            verbosity=-1,
            deterministic=True,
            force_col_wise=True,
        ),
    }


def choose_threshold(y, probabilities):
    """Maximise validation F2 (recall weighted twice), never the test score."""
    precision, recall, thresholds = precision_recall_curve(y, probabilities)
    f2 = 5 * precision[:-1] * recall[:-1] / np.maximum(4 * precision[:-1] + recall[:-1], 1e-12)
    best = np.flatnonzero(np.isclose(f2, f2.max()))[-1]
    return float(thresholds[best])


def metrics(y, probabilities, threshold):
    prediction = probabilities >= threshold
    tn, fp, fn, tp = confusion_matrix(y, prediction, labels=[0, 1]).ravel()
    return {
        "n": len(y),
        "positive": int(np.sum(y)),
        "prevalence": float(np.mean(y)),
        "recall": float(recall_score(y, prediction, zero_division=0)),
        "precision": float(precision_score(y, prediction, zero_division=0)),
        "f1": float(f1_score(y, prediction, zero_division=0)),
        "f2": float(fbeta_score(y, prediction, beta=2, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, probabilities)),
        "pr_auc": float(average_precision_score(y, probabilities)),
        "brier": float(brier_score_loss(y, probabilities)),
        "threshold": float(threshold),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def bootstrap_intervals(y, probabilities, threshold, seed, repeats=300):
    """Unweighted participant bootstrap; not survey-design confidence intervals."""
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(repeats):
        index = rng.integers(0, len(y), size=len(y))
        if len(np.unique(y[index])) != 2:
            continue
        result = metrics(y[index], probabilities[index], threshold)
        rows.append([result[key] for key in ["recall", "f1", "roc_auc", "pr_auc"]])
    low, high = np.quantile(rows, [0.025, 0.975], axis=0)
    return {
        key: [float(lo), float(hi)]
        for key, lo, hi in zip(["recall", "f1", "roc_auc", "pr_auc"], low, high)
    }


def subgroup_metrics(frame, y, probabilities, threshold):
    """Report small-group limitations instead of treating sparse estimates as reliable."""
    result = {}
    for attribute in [
        "age_group",
        "source_era",
        "cycle",
        "gender",
        "family_diabetes",
        "family_heart_early",
    ]:
        result[attribute] = {}
        for group in sorted(frame[attribute].dropna().unique()):
            mask = frame[attribute].eq(group).fillna(False).to_numpy(dtype=bool)
            n, positive = int(mask.sum()), int(y[mask].sum())
            entry = {"n": n, "positive": positive, "sparse": positive < 20 or n - positive < 20}
            if len(np.unique(y[mask])) == 2:
                entry.update(metrics(y[mask], probabilities[mask], threshold))
            result[attribute][str(group)] = entry
    return result


def save_json(path, value):
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )


def write_model_card(path, manifest):
    """Write a short model card directly from the exported release."""
    lines = [
        "# MIZAN — trained models",
        "",
        f"Release: `{manifest['run_id']}`; seed {manifest['seed']}; schema {SCHEMA_VERSION}.",
        "",
        "Research only: cross-sectional NHANES disease labels, not future risk or diagnosis.",
        "Non-pregnant adults aged 20–79; ages 60–79 come only from 1999–2006.",
        "There is no contemporary external validation for older adults or home scales.",
        "",
        f"Cohort: {manifest['cohort']['initial_records']:,} → **{manifest['cohort']['remaining_records']:,}** participants.",
        "Older DXA: retain fully observed scans only; count each participant once.",
        "",
        "## Fixed evaluation partitions",
        "",
        "- Development: 1999–2000 and 2011–2014; 80% fit / 20% sigmoid calibration per target.",
        "- Validation: 2001–2002 and 2015–2016; select the mean AP across age groups",
        "  20–39, 40–59 and 60–79; ties use overall AP then ROC-AUC. Threshold maximizes F2.",
        "- Test: 2003–2006 and 2017–2018; no refitting or threshold tuning after evaluation.",
        "",
        "The 2017–2018 cycle was examined in earlier software; it is not a fresh external test.",
        "Older test cycles provide historical validation, not evidence of current clinical utility.",
        "",
        "## Combined test results",
        "",
        "| Disease | Algorithm | Positive / N | Recall | Precision | F1 | ROC-AUC | AP | Brier |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for disease, entry in manifest["models"].items():
        score = entry["test"]
        lines.append(
            f"| {DISEASES[disease]} | {entry['algorithm']} | {score['positive']} / {score['n']} | "
            + " | ".join(
                f"{score[key]:.3f}"
                for key in ["recall", "precision", "f1", "roc_auc", "pr_auc", "brier"]
            )
            + " |"
        )
    lines += [
        "",
        "Four real algorithms per disease: Logistic Regression, Random Forest, XGBoost, LightGBM.",
        "Class weights address imbalance; calibration uses separate natural-prevalence rows.",
        "`model_comparison.csv` contains validation comparisons. `age_validation.csv` and",
        "`test_metrics.json` report performance by age, cycle and era, with sparse-cell flags.",
        "The latter includes 300 participant-bootstrap intervals, not survey-design intervals.",
        "Low precision and false negatives remain possible, especially for rare cardiac labels.",
        "No national prevalence claim: survey weights are metadata, not model-fitting weights.",
        "",
        "## Inputs and use",
        "",
        "Eight inputs; BMI, fat mass and FFM use the same formulas in training and inference.",
        "No ethnicity, ID, bone mineral, disease labs or own-diagnosis variables are predictors.",
        "Historical family history is reconstructed for parents/siblings; unknown is not no.",
        "All diagnostic thresholds remain unchanged (non-HDL ≥190; BP ≥140/90; HbA1c ≥6.5%).",
        "",
        "The app displays fixed general wellness messages according to model thresholds.",
        "They are not personalized treatment or proof of health. No explanation module is used.",
        "",
        "Sources, hashes, runtime versions and selected pipeline checksums are in manifest.json.",
        "Historical assay/device changes, complete-case selection and population transfer limit use.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def train(data_root: Path, output: Path, reports: Path, config=LabelConfig(), seed=42, jobs=2):
    raw = read_cycles(data_root)
    cohort, audit = prepare_cohort(raw, config)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    release = output / run_id
    release.mkdir(parents=True, exist_ok=False)
    report_dir = reports / "runs" / run_id
    report_dir.mkdir(parents=True, exist_ok=False)
    comparisons, evaluations, entries = [], {}, {}
    versions = {
        pkg: version(pkg)
        for pkg in ["numpy", "pandas", "scikit-learn", "scipy", "lightgbm", "joblib"]
    }
    versions["xgboost"] = __import__("xgboost").__version__
    for disease in DISEASES:
        known = cohort.loc[cohort[disease].notna()].copy()
        development = known.loc[known.partition.eq("development")]
        validation = known.loc[known.partition.eq("validation")]
        test = known.loc[known.partition.eq("test")]
        for name, partition in [
            ("development", development),
            ("validation", validation),
            ("test", test),
        ]:
            if partition[disease].value_counts().min() < 5 or partition[disease].nunique() != 2:
                raise ValueError(f"{disease}: insufficient positive/negative cases in {name}")
        fitting, calibration = train_test_split(
            development, test_size=0.2, random_state=seed, stratify=development[disease].astype(int)
        )
        y_fit = fitting[disease].to_numpy(dtype=int)
        y_cal = calibration[disease].to_numpy(dtype=int)
        y_val = validation[disease].to_numpy(dtype=int)
        y_test = test[disease].to_numpy(dtype=int)
        candidates = []
        for algorithm, classifier in classifiers(y_fit, seed, jobs).items():
            # Preprocessor sees fitting rows only. Calibrator sees separate, natural prevalence rows.
            pre = preprocessing().fit(fitting[FEATURES])
            z_fit = pre.transform(fitting[FEATURES])
            classifier.fit(z_fit, y_fit)
            calibrated = CalibratedClassifierCV(FrozenEstimator(classifier), method="sigmoid")
            calibrated.fit(pre.transform(calibration[FEATURES]), y_cal)
            pipeline = Pipeline([("preprocess", pre), ("classifier", calibrated)])
            probability = pipeline.predict_proba(validation[FEATURES])[:, 1]
            threshold = choose_threshold(y_val, probability)
            score = metrics(y_val, probability, threshold)
            age_scores = []
            for group in sorted(validation.age_group.unique()):
                mask = validation.age_group.eq(group).to_numpy()
                if len(np.unique(y_val[mask])) == 2:
                    age_scores.append(average_precision_score(y_val[mask], probability[mask]))
            score["age_macro_ap"] = float(np.mean(age_scores))
            comparisons.append(
                {
                    "disease": disease,
                    "algorithm": algorithm,
                    **{key: value for key, value in score.items() if key != "confusion_matrix"},
                }
            )
            candidates.append(
                (
                    score["age_macro_ap"],
                    score["pr_auc"],
                    score["roc_auc"],
                    algorithm,
                    pipeline,
                    threshold,
                )
            )
            print(
                f"{disease} / {algorithm}: age-macro AP={score['age_macro_ap']:.3f}, AP={score['pr_auc']:.3f}, "
                f"recall={score['recall']:.3f}, F1={score['f1']:.3f}",
                flush=True,
            )
        # The test set is evaluated only after validation selects algorithm and operating point.
        _, _, _, algorithm, pipeline, threshold = max(candidates, key=lambda item: item[:3])
        probabilities = pipeline.predict_proba(test[FEATURES])[:, 1]
        evaluation = metrics(y_test, probabilities, threshold)
        evaluation.update(
            {
                "algorithm": algorithm,
                "bootstrap_95_ci": bootstrap_intervals(y_test, probabilities, threshold, seed),
                "subgroups": subgroup_metrics(test, y_test, probabilities, threshold),
                "splits": {
                    name: {"n": len(part), "positive": int(part[disease].sum())}
                    for name, part in [
                        ("fitting", fitting),
                        ("calibration", calibration),
                        ("validation", validation),
                        ("test", test),
                    ]
                },
            }
        )
        evaluations[disease] = evaluation
        quality_flags = []
        if evaluation["recall"] < 0.5:
            quality_flags.append("low_heldout_recall")
        if evaluation["precision"] < 0.1:
            quality_flags.append("low_heldout_precision")
        if evaluation["positive"] < 30:
            quality_flags.append("few_positive_test_cases")
        bundle = {
            "schema_version": SCHEMA_VERSION,
            "disease": disease,
            "algorithm": algorithm,
            "pipeline": pipeline,
            "threshold": threshold,
            "encoded_feature_names": pipeline.named_steps["preprocess"]
            .get_feature_names_out()
            .tolist(),
            "seed": seed,
        }
        path = release / f"{disease}.joblib"
        joblib.dump(bundle, path, compress=3)
        entries[disease] = {
            "filename": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "algorithm": algorithm,
            "threshold": threshold,
            "test": evaluation,
            "quality_flags": quality_flags,
        }
    # Fingerprint exact input files without serializing raw participant data into reports.
    sources = {
        str(path.relative_to(data_root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(data_root.glob("*/*.xpt"))
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "user_fields": USER_FIELDS,
        "features": FEATURES,
        "feature_engineering": {
            "bmi": "weight_kg / (height_cm/100)^2",
            "fat_mass_kg": "weight_kg * body_fat_pct / 100",
            "fat_free_mass_kg": "weight_kg - fat_mass_kg",
        },
        "run_id": run_id,
        "python": platform.python_version(),
        "versions": versions,
        "seed": seed,
        "label_config": config.to_dict(),
        "selection": "validation mean age-group average precision, then overall AP, then ROC-AUC",
        "partitions": PARTITIONS,
        "age_limits": [AGE_MIN, AGE_MAX],
        "threshold_selection": "maximum validation F2; no test-set tuning",
        "scope": "Non-pregnant US NHANES participants aged 20-79 with observed complete DXA exams",
        "clinical_validation": False,
        "cohort": audit,
        "sources_sha256": sources,
        "code_sha256": {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(Path(__file__).parent.glob("*.py"))
        },
        "training_reference_ranges": {
            name: {
                "min": float(cohort.loc[cohort.partition.eq("development"), name].min()),
                "max": float(cohort.loc[cohort.partition.eq("development"), name].max()),
            }
            for name in NUMERIC
        },
        "models": entries,
    }
    save_json(release / "manifest.json", manifest)
    pd.DataFrame(comparisons).to_csv(report_dir / "model_comparison.csv", index=False)
    age_rows = []
    for disease, evaluation in evaluations.items():
        for group, score in evaluation["subgroups"]["age_group"].items():
            age_rows.append(
                {
                    "disease": disease,
                    "age_group": group,
                    **{key: value for key, value in score.items() if key != "confusion_matrix"},
                }
            )
    pd.DataFrame(age_rows).to_csv(report_dir / "age_validation.csv", index=False)
    save_json(report_dir / "test_metrics.json", evaluations)
    save_json(report_dir / "cohort.json", audit)
    save_json(report_dir / "manifest.json", manifest)
    write_model_card(report_dir / "MODEL_CARD.md", manifest)
    reports.mkdir(parents=True, exist_ok=True)
    for filename in [
        "model_comparison.csv",
        "age_validation.csv",
        "test_metrics.json",
        "cohort.json",
        "MODEL_CARD.md",
    ]:
        (reports / filename).write_bytes((report_dir / filename).read_bytes())
    # Atomic pointer activation: a failed run never replaces the previously working release.
    pointer = {
        "run_id": run_id,
        "manifest_sha256": hashlib.sha256((release / "manifest.json").read_bytes()).hexdigest(),
    }
    temp = output / f".current-{uuid.uuid4().hex}.json"
    save_json(temp, pointer)
    os.replace(temp, output / "current.json")
    print(f"Exported eight calibrated pipelines to {release}", flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("DATA_SET"))
    parser.add_argument("--output", type=Path, default=Path("models"))
    parser.add_argument("--reports", type=Path, default=Path("reports"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--non-hdl", type=float, default=190.0)
    parser.add_argument("--systolic", type=float, default=140.0)
    parser.add_argument("--diastolic", type=float, default=90.0)
    parser.add_argument("--hba1c", type=float, default=6.5)
    args = parser.parse_args()
    thresholds = [args.non_hdl, args.systolic, args.diastolic, args.hba1c]
    if args.jobs < 1 or any(not np.isfinite(value) or value <= 0 for value in thresholds):
        parser.error("Thread count and finite label thresholds must be positive")
    train(args.data, args.output, args.reports, LabelConfig(*thresholds), args.seed, args.jobs)


if __name__ == "__main__":
    main()
