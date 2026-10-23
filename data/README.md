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

`processed/` is reserved for local, ignored exploration outputs. Training works in memory
and does not create a participant-level processed dataset or alter source files.
See [the data dictionary](../docs/DATA_DICTIONARY.md) for variable mappings and units.
