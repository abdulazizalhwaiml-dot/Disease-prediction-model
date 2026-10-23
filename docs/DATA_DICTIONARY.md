# Data dictionary

Variable names and embedded labels were inspected in all supplied SAS XPORT files.
The attached files are the source actually used by this implementation.

## Predictors

| Feature | Source | Meaning / conversion |
|---|---|---|
| ID | `SEQN` for joins; random UUID in app | Metadata only, never a predictor |
| Recorded sex | DEMO `RIAGENDR` | 1 male / 2 female, as recorded by NHANES |
| Background | DEMO `RIDRETH3` | Fixed pandas dummy schema, categories below |
| Age | DEMO `RIDAGEYR` | Completed years, supported ages 20–59 |
| Waist | BMX `BMXWAIST` | cm |
| Weight | BMX `BMXWT` | kg |
| Height | BMX `BMXHT` | cm |
| BMI | Weight / height | `weight_kg / (height_cm / 100)^2` |
| Bone | DXX `DXDTOBMC` | Total bone mineral content in grams ÷ 1000 |
| Fat % | DXX `DXDTOPF` | Total DXA percent fat |
| Fat mass | DXX `DXDTOFAT` | Total fat in grams ÷ 1000 |
| Lean mass | DXX `DXDTOLE` | Total lean soft tissue **excluding** bone mineral content, grams ÷ 1000 |

Bone mineral content is not the total anatomical weight of bones. Use DXA measurements;
consumer-scale outputs are not validated substitutes. Bone + fat + lean approximately
equal total DXA mass, which can differ from scale weight. Source fat percentage is
approximately `100 × fat / (bone + fat + lean)`.

The app checks mass discrepancy against max(10 kg, 15% of weight) and fat discrepancy
against 5 percentage points. These detect likely unit/input mistakes; they are not clinical
cutoffs. Numeric inputs are also checked for finite values and plausible bounds.

### Ethnicity schema

`RIDRETH3`: 1 Mexican American; 2 Other Hispanic; 3 Non-Hispanic White;
4 Non-Hispanic Black; 6 Non-Hispanic Asian; 7 Other, including multiracial.
There is no category 5 in this classification.

`pd.get_dummies()` creates six fixed columns plus unknown. Missing/not-represented values
never become “Other”. No nationality, country, name or language is used to infer a group.
There is no dedicated Arab category, and unknown-background estimates are extrapolations
without explicit representation in the training data.

## Disease evidence

- BPQ `BPQ080`: ever told high cholesterol. Non-HDL = TCHOL `LBXTC` minus HDL `LBDHDD`,
  in mg/dL. Default positive threshold: 190. Non-HDL is not LDL. Implausible lab values
  (nonpositive or total below HDL) are treated as unknown.
- BPQ `BPQ020`: ever told high pressure. Clinical means use available nonzero
  BPX `BPXSY1..4` and `BPXDI1..4` separately. Default positives: systolic ≥140 or diastolic ≥90.
  This declared study mean rule does not confirm hypertension across repeat visits.
- DIQ `DIQ010`: doctor told diabetes. GHB `LBXGH`: HbA1c percentage, default positive ≥6.5.
  Borderline response code 3 remains unknown unless lab evidence is positive.
- MCQ `MCQ160C`: coronary heart disease, the available self-reported proxy for requested CAD.
  The source does not contain angiographic adjudication.
- MCQ `MCQ160E`, `MCQ160D`, `MCQ160B`, `MCQ160F`: heart attack, angina, congestive heart
  failure and stroke, respectively. These are lifetime self-reported diagnoses.

Questionnaire 1=yes / 2=no; refused, don't know and missing are unknown. For composite
outcomes, any positive establishes a positive, all sources observed negative establish
a negative, and all other combinations remain unknown. Unknown rows are excluded **per
target**, not globally labelled healthy. No lab or diagnosis fields enter the predictors.

## Filtering and audit

| Sequential exclusion | Removed in initial run |
|---|---:|
| Outside ages 20–59 | 24,222 |
| Pregnant / indeterminate pregnancy | 608 |
| Missing or incomplete clinical/body/DXA exam | 2,340 |
| Missing or nonpositive core measurements | 1,363 |
| Unknown recorded sex | 0 |
| **Remaining from 39,156** | **10,623** |

Require DEMO `RIDSTATR=2`, BMX `BMDSTATS=1`, DXX `DXAEXSTS=1`, and available positive
waist, weight, height, bone mineral content, fat percentage, fat mass and lean mass.
Exclude `RIDEXPRG=1` at any age. In women 20–44, require `RIDEXPRG=2` (not pregnant),
excluding indeterminate/missing. Missing status outside that released age range is common
and not automatically excluded; DXA eligibility itself excludes pregnancy. The app is
intended only for non-pregnant adults. Complete body exams do not imply observed disease labs.

Age restriction combines adult heart-question eligibility (20+) and DXA availability
(8–59). Models do not cover older adults, a major exclusion for cardiovascular disease.

## Design metadata and provenance

`WTMEC2YR`, `SDMVSTRA` and `SDMVPSU` are retained, never model inputs.
`mec_weight_8yr = WTMEC2YR / 4` for four equal two-year cycles. These weights are not
used to claim design-adjusted performance or national prevalence. Further survey-aware
analysis is needed for clustering, strata, nonresponse and representativeness.

All 40 files are fingerprinted in each manifest; training writes no merged person-level
table and does not alter `DATA_SET/`. `reports/cohort.json` records aggregate counts.

Further official documentation:
[NHANES portal](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx),
[DXA](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DXX_J.htm),
[demographics](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm),
[medical conditions](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/MCQ_J.htm).
After network access became available, the 2017–2018 DXX, DEMO, MCQ, BPQ, BPX and DIQ
codebooks were retrieved and checked on 2026-10-23. They confirm DXA ages 8–59,
exam-status code 1, pregnancy-status eligibility, background codes, and adult cardiac
questions starting at age 20. File-embedded variable labels were checked across all four
supplied cycles. See [source provenance](source_provenance.json) for URLs and response hashes.
