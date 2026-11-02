# MIZAN v3 validation — 2026-11-02

Executed engineering/research checks; none establishes clinical validity.

## Data and training

- Downloaded and verified 37 official older files; all 40 supplied recent files remain unchanged.
- Read 77 source files; validated joins/IDs and all source/code SHA256 hashes in the final manifest.
- Eight cycles: 80,630 participants → **21,117** after filtering, including **2,789 ages60–79**.
- Older cohort10,494; recent cohort10,623. No BIA files are used.
- Older DXA records checked across all five versions; imputed or inconsistent records excluded.
  Regional/version checks found80 conflicts in the2003 source,34 otherwise-eligible records removed.
- SAS-zero normalization changes three recent BP labels from negative to unknown; recent BP
  positives2,944 and cholesterol positives3,122 remain unchanged. Threshold definitions did not change.
- Family history reconstructed for parents/siblings; refused/missing details remain unknown.
- Exactly eight entered inputs, eleven predictors; no ethnicity, mineral, ID or diagnostic leakage.
- All32 candidate comparisons executed. Fixed era-specific chronological partitions, independent
  calibration, age-macro AP selection and validationF2 thresholds. No test-score tuning.
- Final release **20261102T140111Z-4ba2271e**, schema3, ages20–79. Bundles contain no explanation backgrounds.
- Model-generation code was rerun after finalizing package version metadata with the same fixed
  settings. Selection settings and thresholds were not adjusted after viewing test results.
- CSV round-trip passed:21,117 rows,28 columns; original units, no imputed DXA or unknown-as-no labels.
- VERSION_COMPARISON.csv compares v2/v3 on the same2017–2018 cycle with equal N/positive counts.
  AP improves for five outcomes and decreases for three; improvements are not universal.

## Software, installation and interface

- Clean Python3.12 environment installed from the new hashed development lock.
- **41 tests passed**, no skips, including actual model predictions at ages20,45,60,79.
- Tests cover source-zero decoding, old family skip logic, duplicate/imputed/inconsistent DXA,
  nullable labels, boundaries, encoding, checksums, traversal and old-schema rejection.
- Both Streamlit entrypoints tested in Arabic/English: eight inputs, eight results, derived values,
  explicit family choices, clickable help, language switching and stale-result clearing.
- Both fixed-message branches tested; actual low-estimate UI profile shows maintenance text
  with no statement certifying health. No feature-attribution action/API remains.
- Ruff lint/format and git whitespace checks passed.
- Real Chromium:1440px desktop and390px touch; age70, actual predictions, help interactions,
  eight cards, fixed message, no horizontal overflow and no JavaScript errors. English also checked.
- Screenshots in docs/previews; details in browser_checks.json.
- Updated notebook executed successfully using exported data/reports.
- Removed the unused attribution/chart dependencies and regenerated Linux,development,Windows locks.

## Container

- Image mizan-ai:3.0 built from the current source and the active release only.
- ID: sha256:d7bd2bc4541c27d6c77c7dac5da7963a6841fb2630cd8f97c7fc43bcdb14c8ca.
- Offline smoke: UID10001, eight predictions at age79, active release integrity/runtime verified.
- Offline server: health=ok, page HTTP200. Smoke container removed afterward.

## Practical limits

- Rare cardiac labels still have low precision/recall; see MODEL_CARD.md and age_validation.csv.
- Elder test results are historical. No contemporary external validation or reliable extrapolation
  below20/above79, no home-device or Saudi-population validation, no prospective-risk claims.
- Bootstrap intervals are participant-based and unweighted, not NHANES survey-design intervals.
- Windows lock/launcher prepared; actual Windows execution unavailable in this Linux environment.
- Streamlit account deployment/live-site availability is distinct from these local checks.
