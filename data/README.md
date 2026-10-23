# Data layout

Original public NHANES SAS XPORT files remain unchanged in `../DATA_SET/`:

```
DATA_SET/
  2011-2012/   # suffix G
  2013-2014/   # suffix H
  2015-2016/   # suffix I
  2017-2018/   # suffix J
```

Each cycle has DEMO, BMX, DXX, BPQ, BPX, DIQ, MCQ, TCHOL, HDL and GHB files.
`read_cycles()` checks required variables and one-to-one participant joins. No downloads
are required. Files are fingerprinted in every model manifest.

`processed/` holds local ignored exports. Run `python scripts/export_dataset.py` to save
`NHANES_MIZAN_v2.csv` and metadata JSON: 10,623 rows with eight entered inputs, three
derived features, eight targets and six metadata columns (25 total). Family yes/no are
1/0; unknown histories/outcomes stay blank. The offline-only ethnicity audit column is
excluded from exports. Training works in memory and never alters the source files.
See [the data dictionary](../docs/DATA_DICTIONARY.md) for variable mappings and units.
