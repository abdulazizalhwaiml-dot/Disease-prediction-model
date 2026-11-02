"""Join original NHANES files, harmonize cycles and create nullable study labels."""

from pathlib import Path

import numpy as np
import pandas as pd

from nhanes_ai.features import derive_features
from nhanes_ai.schema import (
    AGE_MAX,
    AGE_MIN,
    CARDIAC_LABELS,
    DISEASES,
    FEATURES,
    PARTITIONS,
    LabelConfig,
)

CYCLES = {
    "1999-2000": "",
    "2001-2002": "B",
    "2003-2004": "C",
    "2005-2006": "D",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J",
}
COMPONENTS = {
    "DEMO": ["RIAGENDR", "RIDAGEYR", "RIDEXPRG", "RIDSTATR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"],
    "BMX": ["BMDSTATS", "BMXWAIST", "BMXWT", "BMXHT"],
    "DXX": ["DXAEXSTS", "DXDTOBMC", "DXDTOPF", "DXDTOFAT", "DXDTOLE"],
    "BPQ": ["BPQ020", "BPQ080"],
    "DIQ": ["DIQ010"],
    "MCQ": [*CARDIAC_LABELS.values(), "MCQ300A", "MCQ300C"],
    "TCHOL": ["LBXTC"],
    "HDL": ["LBDHDD"],
    "GHB": ["LBXGH"],
    "BPX": [f"BPX{kind}{n}" for kind in ["SY", "DI"] for n in range(1, 5)],
}
DXA_MEASURES = ["DXDTOBMC", "DXDTOPF", "DXDTOFAT", "DXDTOLE"]
OLD_FAMILY = ["MCQ250A", "MCQ250G"] + [
    f"MCQ260{condition}{relative}" for condition in ["A", "G"] for relative in "ABCDEFGHI"
]


def read_xport(path: Path) -> pd.DataFrame:
    """Normalize the IBM floating-point zero encoding seen in older XPORT files."""
    frame = pd.read_sas(path, format="xport")
    numeric = frame.select_dtypes(include="number").columns
    frame[numeric] = frame[numeric].mask(frame[numeric].abs().lt(1e-70), 0.0)
    if frame.SEQN.isna().any():
        raise ValueError(f"{path}: missing participant ID")
    return frame


def collapse_observed_dxa(table: pd.DataFrame) -> pd.DataFrame:
    """Keep one record per person; later exclude every partially imputed scan.

    Five imputation versions are not five people. Fully observed measurements must
    agree across versions. We never train using an arbitrarily selected imputation.
    """
    if "_MULT_" not in table:
        result = table.copy()
        result["dxa_observed"] = True
        result["dxa_flag_conflict"] = False
    else:
        groups = table.groupby("SEQN")
        if not (groups.size().eq(5).all() and groups._MULT_.nunique().eq(5).all()):
            raise ValueError("Older DXA must contain exactly five versions per participant")
        if not table._MULT_.isin([1, 2, 3, 4, 5]).all():
            raise ValueError("Unexpected DXA imputation version")
        flags = ["DXITOT"] if "DXITOT" in table else ["DXITOTBN", "DXITOTST"]
        if groups[flags].nunique(dropna=False).gt(1).any().any():
            raise ValueError("Imputation status differs between versions")
        declared_observed = table[flags].eq(0).all(axis=1)
        varying = groups[DXA_MEASURES].nunique(dropna=False).gt(1).any(axis=1)
        invalid_columns = [c for c in table if c.startswith("DXA") and c.endswith(("BV", "TV"))]
        valid_regions = table[invalid_columns].eq(0).all(axis=1)
        consistent = ~table.SEQN.map(varying)
        table = table.copy()
        table["dxa_flag_conflict"] = declared_observed & ~(consistent & valid_regions)
        table["dxa_observed"] = declared_observed & consistent & valid_regions
        result = table.loc[table._MULT_.eq(1)].copy()
    if not result.SEQN.is_unique:
        raise ValueError("Duplicate participant IDs after DXA normalization")
    return result[["SEQN", *COMPONENTS["DXX"], "dxa_observed", "dxa_flag_conflict"]]


def old_family_history(frame: pd.DataFrame, condition: str) -> pd.Series:
    """Rebuild parents/siblings only; old general questions also included grandparents.

    Code-all-that-apply: a blank checkbox is unselected only after a valid kin answer.
    Refusal, unknown, and general yes without kin details remain unknown.
    """
    general = frame[f"MCQ250{condition}"]
    details = frame[[f"MCQ260{condition}{suffix}" for suffix in "ABCDEFGHI"]]
    # A mother, father, brother or sister is a first-degree biological relative.
    first_degree = pd.concat(
        [
            details[f"MCQ260{condition}{suffix}"].eq(code)
            for suffix, code in [("A", 1), ("B", 2), ("G", 7), ("H", 8)]
        ],
        axis=1,
    ).any(axis=1)
    valid_kin = pd.concat(
        [
            details[f"MCQ260{condition}{suffix}"].eq(code)
            for code, suffix in enumerate("ABCDEFGHI", start=1)
        ],
        axis=1,
    ).any(axis=1)
    refused_or_unknown = details.isin([77, 99]).any(axis=1)
    result = pd.Series(pd.NA, index=frame.index, dtype="Float64")
    result.loc[general.eq(2) & ~first_degree] = 0
    result.loc[general.eq(1) & valid_kin & ~first_degree & ~refused_or_unknown] = 0
    result.loc[first_degree] = 1
    return result


def read_cycles(root: Path) -> pd.DataFrame:
    """Read eight cycles with explicit file/column mappings and one-to-one joins."""
    frames = []
    for cycle, suffix in CYCLES.items():
        older = cycle < "2011"
        old_family = cycle < "2005"
        folder = root / cycle
        label = f"_{suffix}" if suffix else ""
        specs = {name: (f"{name}{label}", columns) for name, columns in COMPONENTS.items()}
        if cycle in ["1999-2000", "2001-2002", "2003-2004"]:
            lipid = "LAB13" if not suffix else f"L13{label}"
            ghb = "LAB10" if not suffix else f"L10{label}"
            hdl = "LBXHDD" if suffix == "C" else "LBDHDL"
            specs["TCHOL"] = (lipid, ["LBXTC", hdl])
            specs.pop("HDL")
            specs["GHB"] = (ghb, ["LBXGH"])
            specs["MCQ"] = (f"MCQ{label}", [*CARDIAC_LABELS.values(), *OLD_FAMILY])
        merged = None
        for component, (filename, columns) in specs.items():
            path = folder / f"{filename}.xpt"
            if not path.is_file():
                raise FileNotFoundError(f"Missing {path}. Run python scripts/download_data.py")
            table = read_xport(path)
            if component == "DXX":
                table = collapse_observed_dxa(table)
                columns = [*columns, "dxa_observed", "dxa_flag_conflict"]
            elif not table.SEQN.is_unique:
                raise ValueError(f"{path}: duplicate participant IDs")
            if component == "BMX" and cycle in ["1999-2000", "2001-2002"]:
                # BMDSTATS was not released. Positive observed BMX measures are checked below.
                columns = [c for c in columns if c != "BMDSTATS"]
            if component == "DEMO":
                columns = [*columns, "WTMEC4YR"] if cycle < "2003" else columns
            missing = set(["SEQN", *columns]) - set(table)
            if missing:
                raise ValueError(f"{path}: missing columns {sorted(missing)}")
            table = table[["SEQN", *columns]]
            if component == "TCHOL" and old_family:
                table = table.rename(columns={hdl: "LBDHDD"})
            merged = (
                table
                if merged is None
                else merged.merge(table, on="SEQN", how="left", validate="one_to_one")
            )
        merged["cycle"] = cycle
        merged["source_era"] = "1999-2006" if older else "2011-2018"
        if old_family:
            merged["family_diabetes"] = old_family_history(merged, "A")
            merged["family_heart_early"] = old_family_history(merged, "G")
        else:
            merged["family_diabetes"] = yes_no(merged.MCQ300C)
            merged["family_heart_early"] = yes_no(merged.MCQ300A)
        frames.append(merged)
    pooled = pd.concat(frames, ignore_index=True)
    if not pooled.SEQN.is_unique:
        raise ValueError("Participant IDs overlap between survey cycles")
    return pooled


def yes_no(values: pd.Series) -> pd.Series:
    """1=yes, 2=no; refused, uncertain, borderline and missing remain unknown."""
    return values.map({1: 1.0, 2: 0.0}).astype("Float64")


def observed_threshold(values: pd.Series, threshold: float) -> pd.Series:
    return (values >= threshold).astype("Float64").mask(values.isna())


def nullable_or(*sources: pd.Series) -> pd.Series:
    """A positive wins; a negative requires every source to be observed negative."""
    frame = pd.concat(sources, axis=1)
    result = pd.Series(pd.NA, index=frame.index, dtype="Float64")
    result.loc[frame.eq(1).any(axis=1)] = 1
    result.loc[frame.eq(0).all(axis=1) & frame.notna().all(axis=1)] = 0
    return result


def make_labels(frame: pd.DataFrame, config: LabelConfig) -> pd.DataFrame:
    """Non-HDL is total minus HDL, not LDL. Labs create labels, never predictors."""
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
    """Complete observed exams, no pregnancy, ages 20–79, then shared derived features."""
    frame = raw.copy()
    audit = {
        "initial_records": len(frame),
        "exclusions": {},
        "dxa_flag_conflicts_in_sources": int(frame.dxa_flag_conflict.fillna(False).sum()),
    }

    def keep(mask, reason):
        nonlocal frame
        before = len(frame)
        frame = frame.loc[mask].copy()
        audit["exclusions"][reason] = before - len(frame)

    keep(frame.RIDAGEYR.between(AGE_MIN, AGE_MAX), "outside_age_20_79")
    uncertain = frame.RIAGENDR.eq(2) & frame.RIDAGEYR.between(20, 44) & ~frame.RIDEXPRG.eq(2)
    keep(~frame.RIDEXPRG.eq(1) & ~uncertain, "pregnant_or_indeterminate_pregnancy")
    bmx = frame.BMDSTATS.eq(1) | frame.cycle.isin(["1999-2000", "2001-2002"])
    keep(frame.RIDSTATR.eq(2) & bmx & frame.DXAEXSTS.eq(1), "missing_or_incomplete_clinical_exam")
    keep(frame.dxa_observed.eq(True), "imputed_or_unknown_dxa")
    required = ["BMXWAIST", "BMXWT", "BMXHT", *DXA_MEASURES]
    keep(
        frame[required].notna().all(axis=1) & frame[required].gt(0).all(axis=1),
        "missing_or_nonpositive_measurements",
    )
    keep(frame.RIAGENDR.isin([1, 2]), "unknown_recorded_sex")
    labels = make_labels(frame, config)
    features = derive_features(
        pd.DataFrame(
            {
                "gender": frame.RIAGENDR,
                "age": frame.RIDAGEYR,
                "waist_cm": frame.BMXWAIST,
                "weight_kg": frame.BMXWT,
                "height_cm": frame.BMXHT,
                "body_fat_pct": frame.DXDTOPF,
                "family_diabetes": frame.family_diabetes,
                "family_heart_early": frame.family_heart_early,
            },
            index=frame.index,
        )
    )
    metadata = ["SEQN", "cycle", "WTMEC2YR", "WTMEC4YR", "SDMVSTRA", "SDMVPSU"]
    result = pd.concat([frame[metadata], features[FEATURES], labels], axis=1).reset_index(drop=True)
    partition_map = {
        cycle: partition for partition, cycles in PARTITIONS.items() for cycle in cycles
    }
    result["partition"] = result.cycle.map(partition_map)
    if result.partition.isna().any():
        raise ValueError("A cycle has no declared evaluation partition")
    result["source_era"] = frame.source_era.to_numpy()
    result["age_group"] = pd.cut(
        result.age, bins=[19, 39, 59, 79], labels=["20-39", "40-59", "60-79"]
    ).astype(str)
    audit["remaining_records"] = len(result)
    audit["cycles"] = result.groupby("cycle").size().to_dict()
    audit["age_groups"] = result.groupby("age_group").size().to_dict()
    audit["era_age_groups"] = (
        result.groupby(["source_era", "age_group"])
        .size()
        .unstack(fill_value=0)
        .to_dict(orient="index")
    )
    audit["partitions"] = result.groupby("partition").size().to_dict()
    audit["family_history"] = {
        name: {
            "yes": int(result[name].eq(1).sum()),
            "no": int(result[name].eq(0).sum()),
            "unknown": int(result[name].isna().sum()),
        }
        for name in ["family_diabetes", "family_heart_early"]
    }
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
