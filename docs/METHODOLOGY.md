# Methodology and cycle harmonization

## Scope

Eight cross-sectional disease-label models, ages 20–79, non-pregnant adults with complete
observed DXA/body measurements. These are neither prospective forecasts nor diagnoses.
The final cohort is 21,117: 10,494 from 1999–2006 and 10,623 from 2011–2018.
All 2,789 participants aged 60–79 come from the older era. This selection is not nationally representative.

## Harmonization before joining

- Read 77 original SAS XPORT files; require unique SEQN in each ordinary module and one-to-one joins.
- Older DXA contains five imputation versions per person. Check all five, then retain one
  record only where overall imputation flags are zero, released regional invalidity codes
  are zero, and original DXA measurements agree across versions. Never select an arbitrary
  imputation for training. In 2005 use both DXITOTBN and DXITOTST.
- The 2003 DXA file has 80 cases whose zero summary flag conflicts with invalid regional
  data and/or varying measurements; exclude them. Of these, 34 would otherwise pass the
  20–79 project filters. This corrects the earlier feasibility count of 10,528 older records.
- Normalize the SAS IBM-zero decoding artifact (~5.3976e-79) to numeric zero, preserving missing values.
- Apply zero normalization to all cycles. It also corrects three recent BP labels from
  negative to unknown where a zero reading had previously looked like a tiny positive number.
  The number of BP-positive recent participants remains2,944; recent cohort size is unchanged.
- Map older LAB13/L13 cholesterol and LAB10/L10 HbA1c files to common label columns.
  HDL uses published LBDHDL (1999–2002), LBXHDD (2003–2004), LBDHDD thereafter.
  Published assay corrections are not applied twice. HDL method changes remain a limitation.
- Reconstruct older family history for parents/siblings only from MCQ260 detail fields.
  MCQ250 alone includes grandparents and cannot be substituted directly. Valid grandparent-only
  answers become no first-degree history; missing/refused kin details remain unknown.
- Retain original survey weights/design metadata; do not invent one pooled weight for
  these eras. Current modeling and intervals are unweighted research benchmarks.

Source download URLs, byte counts and SHA256 hashes are pinned in `data/older_sources.json`.
The training manifest fingerprints all 77 files. Original 2011–2018 source files are unchanged.
Official sources:
[DXA index](https://wwwn.cdc.gov/nchs/nhanes/dxa/dxa.aspx),
[2003 DXA](https://wwwn.cdc.gov/nchs/data/nhanes/public/2003/datafiles/dxx_c.pdf),
[2005 DXA](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/DXX_D.htm),
[2003 MCQ](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/MCQ_C.htm),
[2003 cholesterol assay notes](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/L13_C.htm).

## Features and labels

Eight original inputs produce BMI, fat mass and FFM using `derive_features()` in training,
UI and inference. These are correlated derived values, not three new independent measurements.
Eleven predictors become fifteen encoded columns: nine numeric and six fixed family-history
no/yes/unknown dummies, using `pd.get_dummies()`. Imputation medians and scaling are fitted
only on fitting rows. Unknown history is never encoded as no.

Labels use self-reported diagnoses OR valid clinical evidence for cholesterol, BP and diabetes.
Thresholds remain non-HDL190, BP140/90, HbA1c6.5. Unknown is not healthy. Details are in the data dictionary.
ID, cycle, age-group labels, design variables, ethnicity, bone mineral, diagnostic labs and
own-diagnosis answers never enter predictors. Age is the participant's current measurement age.

## Algorithms and fixed selection

| Candidate | Configuration |
|---|---|
| Logistic Regression | L2, C=.5, balanced classes, max_iter2000 |
| Random Forest | 160 trees, depth9, minimum leaf12, balanced subsample |
| XGBoost | 160 depth3 trees, learning rate.04, subsample/column sample.85, L2=5, minimum child weight8, fit-set negative/positive ratio |
| LightGBM | 160 trees, depth4, 12 leaves, learning rate.04, minimum leaf30, L2=5, balanced classes |

1. **Development:** 1999–2000 and2011–2014, stratified80% fitting/20% calibration separately per disease, seed42.
2. **Validation:** 2001–2002 and2015–2016. Select the highest unweighted mean average precision
   across ages20–39,40–59,60–79, then overall AP and ROC-AUC for ties. Each age band contributes
   equally so the larger younger cohort does not dominate selection. Choose threshold by maximum
   validationF2. No model is selected using accuracy alone.
3. **Test:** 2003–2006 and2017–2018, after algorithm/threshold selection, without refitting.

Each class-weighted candidate receives independent sigmoid calibration on natural-prevalence
calibration rows. Report Recall, Precision, F1, F2, ROC-AUC, AP, Brier and confusion matrices.
AP is sklearn average precision, not trapezoidal area. Calibration is measured, not presumed perfect.
Three hundred participant-bootstrap resamples supply descriptive95% intervals, not survey-aware intervals.

Age/cycle/era/sex/family subgroup results flag fewer than20 positives or negatives as sparse.
The 2017–2018 cycle was already examined in previous versions. Historical elder holdouts are
useful but do not establish contemporary older-adult or clinical validity. Smart-scale and
Saudi population performance remain unvalidated. Poor rare-outcome results are reported honestly.

## Simple app and trusted artifacts

The interface has eight inputs, three automatic values, eight disease cards and one fixed
wellness message. If any estimate crosses its own model threshold, show the attention message;
otherwise show the maintain-habits message. Neither branch diagnoses disease or certifies health.
No disease-specific advice or feature-attribution module is used. Colors follow research thresholds.

Schema3 records age limits20–79. Loading checks schema, input contract, Python/package versions,
paths and SHA256 hashes before trusted joblib deserialization. The active pointer changes atomically
only when all eight pipelines and reports are written. Hashes detect corruption, not malicious
replacement of both manifest and model. Inputs remain session-local; changes clear old results.

## Cross-platform export

The original XGBoost pickle memory snapshot failed in the native Windows library.
`PortableBooster` serializes the official UBJSON model plus JSON configuration instead.
The active export preserves all trees, calibration and thresholds. Before activation,
`upgrade_model_format.py` round-tripped both selected XGBoost pipelines on all21,117
exported feature rows, with maximum probability difference0. No models were refit.
Training now uses the same portable export for future selected XGBoost models.
