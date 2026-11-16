# Changelog

## Unreleased

- Translate repository documentation into English.
- Document the live website at https://mizanak.streamlit.app/, hosted on Streamlit Community Cloud.

## 4.2.0 — November 16, 2026

- Re-select cholesterol, blood-pressure and diabetes alert levels on validation data, maximizing F1 with a research guard allowing at most a 10-percentage-point validation recall loss relative to validation F2.
- Reduce false positives on the historical test set while also increasing missed cases; publish the complete trade-off, not an accuracy-only claim.
- Retain the other five operating points. Publish the exploratory eight-target comparison, including candidate regressions and persistent weak rare-outcome performance.
- Preserve fitted/calibrated pipelines, probabilities, source data, labels and the eight-input/eleven-feature contract. Verify unchanged predictions on all 21,117 rows and preserve the five retained artifact bytes.
- Add reproducible validation-only threshold re-selection, imbalance-aware metrics, selection provenance, research-policy tests and current model reports. This is not new external or clinical validation.

## 4.1.1 — November 3, 2026

- Fix internal scrolling in all eight field-heading/help rows; container height follows content and labels wrap on narrow screens.
- Add browser checks covering the header and all fields in Arabic and English, six viewport sizes, four zoom levels, and keyboard-operated help dialogs. Include the checks in GitHub Actions.
- Use “Male or female.” for sex help; remove “biological” from both family-history explanations.
- Use `main` for source, runtime, and deployment; add a repository guide, free-hosting instructions, and a GitHub Releases package.
- Models, data, calculations, and alert levels are unchanged.

## 4.1 — November 2, 2026

- Fix scrolling in the logo/language row and use question-mark/arrow icons for help controls.
- Place automatic calculations below the inputs; add brief condition definitions, a medical limitation, and clearer “alert level” wording.
- Use the approved hollow-display logo and a separate welcome illustration with a measurement card, measuring tape, and small heart.
