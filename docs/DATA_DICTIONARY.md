# Mizanak data dictionary

## Model inputs

| Column | Meaning | NHANES source |
|---|---|---|
| age | Completed age, 20–79 | RIDAGEYR |
| gender | 1 male, 2 female | RIAGENDR |
| height_cm | Height in cm | BMXHT |
| weight_kg | Weight in kg | BMXWT |
| waist_cm | Waist circumference in cm | BMXWAIST |
| body_fat_pct | Body-fat percentage, e.g. 25 rather than 0.25 | DXDTOPF |
| family_diabetes | Diabetes in parents or siblings | Harmonized MCQ questions |
| family_heart_early | Heart attack or angina before age 50 in the same relatives | Harmonized MCQ questions |
| bmi | Weight divided by squared height in meters | Calculated |
| fat_mass_kg | Weight × body-fat percentage / 100 | Calculated |
| fat_free_mass_kg | Weight − fat mass | Calculated |

There are eight entered inputs and three derived features; the derived features are not additional independent measurements. FFM includes water, organs, muscle, and minerals.
Exported family history uses **1 yes, 0 no, empty unknown**. Original responses use 1 yes, 2 no, 7 refused, and 9 unknown. An individual's family history is not inferred from age, sex, or personal disease status.

For 2005–2006 and 2011–2018, MCQ300C supplies diabetes history and MCQ300A supplies heart history. In 1999–2004, MCQ250A/G also include grandparents; only parents and siblings were extracted from MCQ260AA/AB/AG/AH and MCQ260GA/GB/GG/GH. Relative codes are 1 mother, 2 father, 7 brother, and 8 sister. A general “Yes” with unknown relative details remains unknown. Grandparents alone do not meet this definition.

## Eight targets

| Column | Positive label |
|---|---|
| high_cholesterol | BPQ080=1 or LBXTC−HDL ≥190 mg/dL |
| high_blood_pressure | BPQ020=1 or mean BPXSY1–4 ≥140 or BPXDI1–4 ≥90 |
| diabetes | DIQ010=1 or LBXGH ≥6.5% |
| coronary_artery_disease | MCQ160C=1; self-reported prior coronary disease |
| heart_attack | MCQ160E=1 |
| angina | MCQ160D=1 |
| heart_failure | MCQ160B=1 |
| stroke | MCQ160F=1 |

Exports use **1 positive, 0 known negative, empty unknown**. Any positive source makes the target positive; a negative label requires all sources to be negative. Refusal, missing values, and borderline diabetes are not converted to negative labels. Zero blood-pressure readings are excluded from means. Non-HDL is not LDL; the 190 cutoff is a project-owner-selected definition. A single-visit blood-pressure measurement or isolated HbA1c result does not establish a clinical diagnosis.

HDL uses LBDHDL in 1999–2002, LBXHDD in 2003–2004, and LBDHDD in later cycles. These are published public-release values; no additional undocumented corrections were applied. Historical LAB13/L13 and LAB10/L10 laboratory files correspond to newer lipid and HbA1c files.

## Identifiers and survey design — not model inputs

| Column | Purpose |
|---|---|
| SEQN | Participant record linkage; excluded from prediction |
| cycle | Data-collection cycle |
| source_era | 1999–2006 or 2011–2018, for separate evaluation |
| age_group | 20–39, 40–59, or 60–79, for auditing only |
| partition | development, validation, or test, assigned by cycle |
| WTMEC2YR | Original two-year examination survey weight |
| WTMEC4YR | Original four-year weight, available only for 1999–2002 |
| SDMVSTRA | Sampling stratum |
| SDMVPSU | Primary sampling unit |

Survey weights are not used for model training, and no national-prevalence representativeness is claimed. No pooled weight was created by simply dividing all weights by the number of cycles; historical cycles have different weighting requirements. Race and bone mineral measurements are absent from the export.

## Filtering

Of **80,630** participants across eight cycles, **21,117** remain:

- Ages 20–79; younger participants and ages 80 or above are unsupported.
- Documented pregnancy is excluded; women aged 20–44 require evidence of non-pregnancy.
- Complete MEC and DXA examinations, with BMDSTATS=1 when available. That variable is absent in 1999–2002, so complete observed body-composition measurements are required instead.
- Complete positive waist, weight, height, and body-fat measurements, together with original DXA completeness for minerals, fat, and lean mass. Minerals are not model features.
- Historical DXA checks require non-imputation flags, valid regions, and consistent values across all five copies. Only one record per participant is retained.
- Unknown family history does not exclude a participant; an unknown target excludes that record only for that condition.

Detailed checks found 80 participants in the 2003–2004 file whose overall completeness flag suggested non-imputation despite inconsistent measurements or regional validity. Of these, 34 would have entered the initial age-20–79 cohort and are now excluded. The final historical cohort is therefore **10,494**, rather than 10,528; the modern cohort remains **10,623**.
Correcting SAS zero-value parsing changed three modern-cycle blood-pressure targets from negative to unknown; the positive count remains 2,944. See [cohort.json](../reports/cohort.json) for exact counts and exclusions.
