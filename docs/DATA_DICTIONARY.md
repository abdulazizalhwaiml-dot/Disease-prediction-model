# Version 2 data dictionary

## Eight entered inputs

| App / feature field | Source | Meaning |
|---|---|---|
| `age` | DEMO `RIDAGEYR` | Completed years, 20–59 |
| `gender` | DEMO `RIAGENDR` | 1 male / 2 female |
| `height_cm` | BMX `BMXHT` | Standing height, cm |
| `weight_kg` | BMX `BMXWT` | Body weight, kg |
| `waist_cm` | BMX `BMXWAIST` | Circumference at upper right iliac border, cm |
| `body_fat_pct` | DXX `DXDTOPF` | DXA body-fat percentage; BIA transfer is unvalidated |
| `family_diabetes` | MCQ `MCQ300C` | A biological father/mother/sister/brother, living or deceased, ever told by a health professional they had diabetes; no age condition |
| `family_heart_early` | MCQ `MCQ300A` | The same biological relatives ever told they had a heart attack or angina **before age 50**, for either sex |

Original family-history codes: **1 yes, 2 no, 7 refused, 9 don't know, blank missing**.
Training maps 1→1 and 2→0; all others stay unknown and receive a distinct dummy category.
The app offers only yes/no and requires an explicit selection. Unknown history is not no.
The definition is not the alternative clinical family-history cutoff of 55/65 years.
Nor does it include every cardiac disorder, hypertension or stroke.

The official codebooks use case variants `MCQ300a`/`MCQ300c`; supplied XPORT columns
are uppercase. Definitions and codes were checked across all four cycles. Saved URLs,
retrieval hashes and exact definitions: [family-history provenance](family_history_provenance.json).

## Three derived model features

| Field | Shared formula |
|---|---|
| `bmi` | `weight_kg / (height_cm / 100)^2` |
| `fat_mass_kg` | `weight_kg * body_fat_pct / 100` |
| `fat_free_mass_kg` | `weight_kg - fat_mass_kg` |

Training, UI, validation and SHAP call `derive_features()`. FFM includes minerals and
all nonfat tissues; it is not pure muscle. The new masses are derived from BMX weight
and DXA percentage to reproduce the app's exact measurement contract. They are not
the previous dataset's `DXDTOLE + DXDTOBMC` reference FFM or independent DXA fat mass.
These derived quantities do not add three independent biological measurements.

There are **eleven raw predictors**, expanded to fifteen preprocessing columns: nine
numeric columns and three fixed no/yes/unknown dummy columns per family question.
No ethnicity, BMC, ID, clinical labs, own diagnosis questions or cycle enter the model.

## Disease labels

- Cholesterol: BPQ `BPQ080=1` OR non-HDL `LBXTC−LBDHDD ≥190 mg/dL`.
  Require positive TC/HDL and TC≥HDL for valid laboratory evidence. Non-HDL is not LDL.
  The threshold is an explicitly user-selected study definition, not a universal desirable goal.
- Blood pressure: BPQ `BPQ020=1` OR mean nonzero systolic `BPXSY1–4 ≥140`
  OR mean nonzero diastolic `BPXDI1–4 ≥90 mmHg`.
- Diabetes: DIQ `DIQ010=1` OR positive GHB `LBXGH ≥6.5%`.
- CAD proxy / heart attack / angina / CHF / stroke: yes to `MCQ160C/E/D/B/F` respectively.

Questionnaire yes=1/no=2. Borderline, refused, uncertain and missing stay unknown.
For OR outcomes: any positive wins; negative requires every source known negative;
otherwise unknown. Unknown outcomes are excluded per target, never globally imputed healthy.
Single-visit BP or one HbA1c does not establish a confirmed clinical diagnosis.

## Cohort — preserved from version 1

| Exclusion | Removed |
|---|---:|
| Outside ages 20–59 | 24,222 |
| Pregnant or indeterminate pregnancy | 608 |
| Incomplete body/clinical/DXA examination | 2,340 |
| Missing/nonpositive required measurements | 1,363 |
| Unknown recorded sex | 0 |
| **Remaining from 39,156** | **10,623** |

Require `RIDSTATR=2`, `BMDSTATS=1`, `DXAEXSTS=1`, and positive waist/weight/height,
DXA BMC/fat percentage/fat mass/lean mass. Although some are no longer predictors,
the original cohort restriction remains for version comparability. Exclude pregnancy
`RIDEXPRG=1`, and require known nonpregnancy `RIDEXPRG=2` for women 20–44.

Family history is not an exclusion: diabetes yes/no/unknown **4422/6031/170**;
early cardiac yes/no/unknown **1174/9222/227**. Counts are sample descriptions,
not weighted national prevalence. Target positive counts remain unchanged.

## Metadata, not prediction inputs

`SEQN` is the public participant join key. `cycle` identifies the sampling period, not
a longitudinal follow-up. `WTMEC2YR` is the two-year MEC survey weight.
`mec_weight_8yr=WTMEC2YR/4` combines four equal cycles; the two weights are not multiplied.
`SDMVSTRA` and `SDMVPSU` are masked variance strata/primary units for survey-aware uncertainty.
Weights alone do not correct the selection induced by the complete-DXA cohort.

`ethnicity_audit` retains `RIDRETH3` solely for offline subgroup auditing. It is excluded
from FEATURES, the UI and processed training-data downloads. It is never inferred from
nationality. Original files and all forty source hashes remain unchanged.

Sources: [MCQ 2011–2012](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2011/DataFiles/MCQ_G.htm),
[MCQ 2017–2018](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/MCQ_J.htm),
[body measures](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm),
[DXA](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm).
