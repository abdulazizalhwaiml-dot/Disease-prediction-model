"""Validated SAS ingestion, conservative cohort filtering, and nullable disease labels.

Clinical variables create targets only. None of these columns reach the model features.
Unknown questionnaire responses and missing laboratory values never become healthy labels.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from nhanes_ai.schema import CARDIAC_LABELS, DISEASES, FEATURES, LabelConfig

CYCLES = {"2011-2012": "G", "2013-2014": "H", "2015-2016": "I", "2017-2018": "J"}
COMPONENTS = {
    "DEMO": [
        "RIAGENDR",
        "RIDAGEYR",
        "RIDRETH3",
        "RIDEXPRG",
        "RIDSTATR",
        "WTMEC2YR",
        "SDMVSTRA",
        "SDMVPSU",
    ],
    "BMX": ["BMDSTATS", "BMXWAIST", "BMXWT", "BMXHT"],
    "DXX": ["DXAEXSTS", "DXDTOBMC", "DXDTOPF", "DXDTOFAT", "DXDTOLE"],
    "BPQ": ["BPQ020", "BPQ080"],
    "DIQ": ["DIQ010"],
    "MCQ": list(CARDIAC_LABELS.values()),
    "TCHOL": ["LBXTC"],
    "HDL": ["LBDHDD"],
    "GHB": ["LBXGH"],
    "BPX": [f"BPX{kind}{n}" for kind in ["SY", "DI"] for n in range(1, 5)],
}


def read_cycles(root: Path) -> pd.DataFrame:
    """Left-join each module onto demographics with cardinality/schema checks."""
    frames = []
    for cycle, suffix in CYCLES.items():
        merged = None
        for component, columns in COMPONENTS.items():
            path = root / cycle / f"{component}_{suffix}.xpt"
            table = pd.read_sas(path, format="xport")
            missing = set(["SEQN", *columns]) - set(table.columns)
            if missing:
                raise ValueError(f"{path}: missing columns {sorted(missing)}")
            if table.SEQN.isna().any() or not table.SEQN.is_unique:
                raise ValueError(f"{path}: invalid or duplicate participant IDs")
            table = table[["SEQN", *columns]]
            merged = (
                table
                if merged is None
                else merged.merge(table, on="SEQN", how="left", validate="one_to_one")
            )
        merged["cycle"] = cycle
        frames.append(merged)
    pooled = pd.concat(frames, ignore_index=True)
    if not pooled.SEQN.is_unique:
        raise ValueError("Participant IDs overlap between survey cycles")
    return pooled


def yes_no(values: pd.Series) -> pd.Series:
    """NHANES 1=yes, 2=no; refused, uncertain, borderline and missing remain unknown."""
    return values.map({1: 1.0, 2: 0.0}).astype("Float64")


def observed_threshold(values: pd.Series, threshold: float) -> pd.Series:
    result = (values >= threshold).astype("Float64")
    return result.mask(values.isna())


def nullable_or(*sources: pd.Series) -> pd.Series:
    """A positive overrides unknown; negative requires every component to be observed negative."""
    frame = pd.concat(sources, axis=1)
    result = pd.Series(pd.NA, index=frame.index, dtype="Float64")
    result.loc[frame.eq(1).any(axis=1)] = 1
    result.loc[frame.eq(0).all(axis=1) & frame.notna().all(axis=1)] = 0
    return result


def make_labels(frame: pd.DataFrame, config: LabelConfig) -> pd.DataFrame:
    """Composite study labels; non-HDL is total cholesterol minus HDL, not LDL."""
    non_hdl = (frame.LBXTC - frame.LBDHDD).where(
        frame.LBXTC.gt(0) & frame.LBDHDD.gt(0) & frame.LBXTC.ge(frame.LBDHDD)
    )
    systolic = frame[[f"BPXSY{n}" for n in range(1, 5)]].replace(0, np.nan).mean(axis=1)
    diastolic = frame[[f"BPXDI{n}" for n in range(1, 5)]].replace(0, np.nan).mean(axis=1)
    hba1c = frame.LBXGH.where(frame.LBXGH.gt(0))
    labels = pd.DataFrame(index=frame.index)
    labels["high_cholesterol"] = nullable_or(
        yes_no(frame.BPQ080), observed_threshold(non_hdl, config.non_hdl_mg_dl)
    )
    labels["high_blood_pressure"] = nullable_or(
        yes_no(frame.BPQ020),
        observed_threshold(systolic, config.systolic_mm_hg),
        observed_threshold(diastolic, config.diastolic_mm_hg),
    )
    labels["diabetes"] = nullable_or(
        yes_no(frame.DIQ010), observed_threshold(hba1c, config.hba1c_pct)
    )
    for target, column in CARDIAC_LABELS.items():
        labels[target] = yes_no(frame[column])
    return labels[list(DISEASES)]


def prepare_cohort(raw: pd.DataFrame, config: LabelConfig):
    """Return feature/label data and an auditable, sequential exclusion report.

    Require an actual completed body exam and DXA with all requested measurements.
    Pregnancy status is only released for a limited age range: conservatively exclude
    women 20–44 whose status is unknown as well as every confirmed pregnant participant.
    """
    frame = raw.copy()
    audit = {"initial_records": len(frame), "exclusions": {}}

    def keep(mask, reason):
        nonlocal frame
        before = len(frame)
        frame = frame.loc[mask].copy()
        audit["exclusions"][reason] = before - len(frame)

    keep(frame.RIDAGEYR.between(20, 59), "outside_age_20_59")
    uncertain = frame.RIAGENDR.eq(2) & frame.RIDAGEYR.between(20, 44) & ~frame.RIDEXPRG.eq(2)
    keep(~frame.RIDEXPRG.eq(1) & ~uncertain, "pregnant_or_indeterminate_pregnancy")
    keep(
        frame.RIDSTATR.eq(2) & frame.BMDSTATS.eq(1) & frame.DXAEXSTS.eq(1),
        "missing_or_incomplete_clinical_exam",
    )
    required = ["BMXWAIST", "BMXWT", "BMXHT", "DXDTOBMC", "DXDTOPF", "DXDTOFAT", "DXDTOLE"]
    keep(
        frame[required].notna().all(axis=1) & frame[required].gt(0).all(axis=1),
        "missing_or_nonpositive_measurements",
    )
    keep(frame.RIAGENDR.isin([1, 2]), "unknown_recorded_sex")
    labels = make_labels(frame, config)
    # Bone mineral content and soft tissue mass are in grams in the source XPORT files.
    features = pd.DataFrame(
        {
            "gender": frame.RIAGENDR,
            "age": frame.RIDAGEYR,
            "ethnicity": frame.RIDRETH3,
            "waist_cm": frame.BMXWAIST,
            "weight_kg": frame.BMXWT,
            "height_cm": frame.BMXHT,
            "bmi": frame.BMXWT / (frame.BMXHT / 100).pow(2),
            "bone_mass_kg": frame.DXDTOBMC / 1000,
            "body_fat_pct": frame.DXDTOPF,
            "fat_mass_kg": frame.DXDTOFAT / 1000,
            "lean_mass_kg": frame.DXDTOLE / 1000,
        },
        index=frame.index,
    )
    result = pd.concat(
        [frame[["SEQN", "cycle", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"]], features[FEATURES], labels],
        axis=1,
    ).reset_index(drop=True)
    # Four equal two-year cycles; retained for optional descriptive, not design-based inference.
    result["mec_weight_8yr"] = result.WTMEC2YR / 4
    audit["remaining_records"] = len(result)
    audit["cycles"] = result.groupby("cycle").size().to_dict()
    audit["targets"] = {
        name: {
            "known": int(result[name].notna().sum()),
            "positive": int(result[name].sum()),
            "unknown": int(result[name].isna().sum()),
        }
        for name in DISEASES
    }
    print(f"Total records remaining after filtering: {len(result):,}", flush=True)
    return result, audit
