# Data

`DATA_SET/` contains the original XPORT files, one folder per two-year cycle.

- 2011–2018: 40 supplied files, tracked unchanged.
- 1999–2006: 37 public CDC files, downloaded with `python scripts/download_data.py`.
  URLs, hashes and sizes are in `older_sources.json`; large older raw files are not tracked.

Run `python scripts/export_dataset.py` to reproduce:

- `processed/NHANES_MIZAN.csv`: 21,117 rows, 28 columns; UTF-8 BOM for Excel.
- `processed/dataset_metadata.json`: exact columns, formulas, label definitions and filter counts.

Columns: 11 predictors, eight nullable targets and nine metadata columns. Metadata never enters
prediction. Values use original units; unknown history/targets stay blank. The export has no
ethnicity or bone-mineral field. It contains only one row per participant and observed DXA data.
See [the dictionary](../docs/DATA_DICTIONARY.md) for mappings and the historical-DXA quality correction.
