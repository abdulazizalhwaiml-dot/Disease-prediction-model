"""Export the merged, unscaled cohort and a machine-readable column dictionary.

Run from the project folder: python scripts/export_dataset.py
Unknown labels/history stay blank. ID, design and partition columns are never predictors.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from nhanes_ai.data import prepare_cohort, read_cycles
from nhanes_ai.schema import DISEASES, FEATURES, USER_FIELDS, LabelConfig


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=root / "DATA_SET")
    parser.add_argument("--output", type=Path, default=root / "data/processed")
    args = parser.parse_args()
    config = LabelConfig()
    frame, audit = prepare_cohort(read_cycles(args.data), config)
    for name in [
        "SEQN",
        "age",
        "gender",
        "SDMVSTRA",
        "SDMVPSU",
        *DISEASES,
        "family_diabetes",
        "family_heart_early",
    ]:
        frame[name] = frame[name].astype("Int64")
    args.output.mkdir(parents=True, exist_ok=True)
    path = args.output / "NHANES_MIZAN.csv"
    frame.to_csv(path, index=False, encoding="utf-8-sig")
    pd.testing.assert_frame_equal(pd.read_csv(path), frame, check_dtype=False)
    metadata = {
        "rows": len(frame),
        "columns": len(frame.columns),
        "column_names": frame.columns.tolist(),
        "user_inputs": USER_FIELDS,
        "model_features": FEATURES,
        "targets": list(DISEASES),
        "metadata_columns": [c for c in frame if c not in FEATURES + list(DISEASES)],
        "label_config": config.to_dict(),
        "cohort": audit,
        "derived_formulas": {
            "bmi": "weight_kg / (height_cm / 100)^2",
            "fat_mass_kg": "weight_kg * body_fat_pct / 100",
            "fat_free_mass_kg": "weight_kg - fat_mass_kg",
        },
        "family_codes": {"1": "yes", "0": "no", "blank": "unknown; not negative"},
        "target_codes": {"1": "positive", "0": "known negative", "blank": "unknown"},
        "scaled": False,
        "imputed": False,
        "pooled_survey_weight": None,
    }
    (args.output / "dataset_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Exported and verified {len(frame):,} rows / {len(frame.columns)} columns: {path}")


if __name__ == "__main__":
    main()
