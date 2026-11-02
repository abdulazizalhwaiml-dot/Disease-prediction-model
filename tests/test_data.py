"""Guard label semantics and cohort exclusions against clinically material regressions."""

import numpy as np
import pandas as pd
import pytest

from nhanes_ai.data import COMPONENTS, make_labels, nullable_or, prepare_cohort, yes_no
from nhanes_ai.schema import LabelConfig


def raw_rows(n=1):
    frame = pd.DataFrame(
        {name: np.full(n, np.nan) for columns in COMPONENTS.values() for name in columns}
    )
    defaults = dict(
        SEQN=1,
        cycle="2011-2012",
        source_era="2011-2018",
        WTMEC4YR=np.nan,
        dxa_observed=True,
        dxa_flag_conflict=False,
        family_diabetes=0,
        family_heart_early=0,
        RIAGENDR=1,
        RIDAGEYR=45,
        RIDSTATR=2,
        BMDSTATS=1,
        DXAEXSTS=1,
        BMXWAIST=95,
        BMXWT=80,
        BMXHT=175,
        DXDTOBMC=3000,
        DXDTOPF=30,
        DXDTOFAT=24000,
        DXDTOLE=53000,
        BPQ020=2,
        BPQ080=2,
        DIQ010=2,
        LBXTC=200,
        LBDHDD=50,
        LBXGH=5.5,
        BPXSY1=120,
        BPXDI1=80,
        WTMEC2YR=4,
        SDMVSTRA=1,
        SDMVPSU=1,
    )
    for name, value in defaults.items():
        frame[name] = value
    frame.SEQN = np.arange(n) + 1
    return frame


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (1, pd.NA, 1),
        (pd.NA, 1, 1),
        (0, 0, 0),
        (0, pd.NA, None),
        (pd.NA, 0, None),
        (pd.NA, pd.NA, None),
    ],
)
def test_nullable_or_does_not_turn_unknown_into_healthy(left, right, expected):
    result = nullable_or(
        pd.Series([left], dtype="Float64"), pd.Series([right], dtype="Float64")
    ).iloc[0]
    assert pd.isna(result) if expected is None else result == expected


def test_refused_borderline_and_unknown_are_not_negative():
    result = yes_no(pd.Series([1, 2, 3, 7, 9, np.nan]))
    assert result.iloc[:2].tolist() == [1, 0]
    assert result.iloc[2:].isna().all()


def test_label_thresholds_self_reports_and_non_hdl():
    frame = raw_rows(5)
    frame.loc[0, ["LBXTC", "LBDHDD"]] = [240, 50]  # exactly 190 non-HDL
    frame.loc[1, "BPQ080"] = 1
    frame.loc[1, "LBXTC"] = np.nan
    frame.loc[2, ["BPXSY1", "BPXSY2"]] = [130, 150]  # average exactly 140
    frame.loc[3, "LBXGH"] = 6.5
    frame.loc[4, ["DIQ010", "LBXGH", "BPXDI1"]] = [9, np.nan, 0]
    labels = make_labels(frame, LabelConfig())
    assert labels.high_cholesterol.iloc[:2].tolist() == [1, 1]
    assert labels.high_blood_pressure.iloc[2] == 1
    assert labels.diabetes.iloc[3] == 1
    assert pd.isna(labels.diabetes.iloc[4])
    assert pd.isna(labels.high_blood_pressure.iloc[4])  # missing diastolic is not negative
    assert labels.heart_attack.isna().all()


def test_positive_blood_pressure_overrides_other_missing_readings():
    frame = raw_rows()
    frame.loc[0, ["BPXDI1", "BPXSY1"]] = [0, 150]
    assert make_labels(frame, LabelConfig()).high_blood_pressure.iloc[0] == 1


def test_cohort_age_pregnancy_exam_missing_units_and_id_exclusion():
    frame = raw_rows(7)
    frame.loc[1, ["RIAGENDR", "RIDAGEYR", "RIDEXPRG"]] = [2, 30, 1]
    frame.loc[2, "DXAEXSTS"] = 6
    frame.loc[3, "BMXWAIST"] = np.nan
    frame.loc[4, "RIDAGEYR"] = 80
    frame.loc[5, ["RIAGENDR", "RIDAGEYR", "RIDEXPRG"]] = [2, 35, 3]
    frame.loc[6, ["RIAGENDR", "RIDAGEYR", "RIDEXPRG"]] = [2, 35, 2]
    cohort, audit = prepare_cohort(frame, LabelConfig())
    assert len(cohort) == audit["remaining_records"] == 2
    assert cohort.SEQN.tolist() == [1, 7]
    assert cohort.fat_mass_kg.iloc[0] == 24
    assert cohort.fat_free_mass_kg.iloc[0] == 56
    assert "bone_mass_kg" not in cohort and "lean_mass_kg" not in cohort
    assert cohort.bmi.iloc[0] == pytest.approx(80 / 1.75**2)
    assert cohort.WTMEC2YR.iloc[0] == 4
    assert "mec_weight_8yr" not in cohort


def test_family_history_codes_and_unknowns_are_not_negative():
    frame = raw_rows(6)
    frame["MCQ300A"] = [1, 2, 7, 9, np.nan, 2]
    frame["MCQ300C"] = [2, 1, 9, 7, np.nan, 1]
    frame["family_diabetes"] = yes_no(frame.MCQ300C)
    frame["family_heart_early"] = yes_no(frame.MCQ300A)
    cohort, audit = prepare_cohort(frame, LabelConfig())
    assert cohort.family_heart_early.iloc[:2].tolist() == [1, 0]
    assert cohort.family_diabetes.iloc[:2].tolist() == [0, 1]
    assert cohort[["family_diabetes", "family_heart_early"]].iloc[2:5].isna().all().all()
    assert audit["family_history"]["family_diabetes"] == {"yes": 2, "no": 1, "unknown": 3}


def test_old_family_history_excludes_grandparents_and_preserves_unknown():
    from nhanes_ai.data import OLD_FAMILY, old_family_history

    f = pd.DataFrame(np.nan, index=range(7), columns=OLD_FAMILY)
    f["MCQ250A"] = [2, 1, 1, 1, 9, 1, 1]
    f.loc[1, "MCQ260AA"] = 1  # Mother.
    f.loc[2, "MCQ260AC"] = 3  # Grandmother only: no first-degree history.
    f.loc[3, "MCQ260AA"] = 99  # Kin unknown: not a negative.
    f.loc[5, "MCQ260AG"] = 7  # Brother code, not questionnaire refusal.
    result = old_family_history(f, "A")
    assert result.iloc[:3].tolist() == [0, 1, 0]
    assert result.iloc[3:5].isna().all()
    assert result.iloc[5] == 1
    assert pd.isna(result.iloc[6])  # General yes, all kin details missing.


def test_old_dxa_is_not_duplicated_or_arbitrarily_imputed():
    from nhanes_ai.data import DXA_MEASURES, collapse_observed_dxa

    f = pd.concat([raw_rows(1)] * 5, ignore_index=True)
    f["_MULT_"] = range(1, 6)
    f["DXITOT"] = 0
    assert len(collapse_observed_dxa(f)) == 1
    assert collapse_observed_dxa(f).dxa_observed.iloc[0]
    f.loc[1, DXA_MEASURES[1]] += 1
    collapsed = collapse_observed_dxa(f)
    assert not collapsed.dxa_observed.iloc[0]
    assert collapsed.dxa_flag_conflict.iloc[0]
    with pytest.raises(ValueError, match="five versions"):
        collapse_observed_dxa(f.iloc[:4])


def test_old_dxa_invalid_regions_override_a_zero_summary_flag():
    from nhanes_ai.data import collapse_observed_dxa

    f = pd.concat([raw_rows(1)] * 5, ignore_index=True)
    f["_MULT_"] = range(1, 6)
    f["DXITOT"] = 0
    f["DXARATV"] = 4
    collapsed = collapse_observed_dxa(f)
    assert not collapsed.dxa_observed.iloc[0]
    assert collapsed.dxa_flag_conflict.iloc[0]


def test_sas_ibm_zero_decoding_is_normalized(monkeypatch):
    from pathlib import Path

    from nhanes_ai.data import read_xport

    monkeypatch.setattr(
        pd,
        "read_sas",
        lambda *a, **kw: pd.DataFrame(
            {"SEQN": [1, 2, 3], "flag": [5.397605346934028e-79, 1, np.nan]}
        ),
    )
    f = read_xport(Path("unused.xpt"))
    assert f.flag.iloc[0] == 0
    assert f.flag.iloc[1] == 1
    assert pd.isna(f.flag.iloc[2])
