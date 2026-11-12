# Mizanak v4.1.1 — field-heading scrollbar fix, 2026-11-03

- Reproduced the reported scrollbar in all eight field-heading/help rows on the previous
  commit5e79387. At320px the row clientHeight was37px while scrollHeight was48px;
  the nowrap Streamlit row had automatic internal scrolling. The earlier fix covered
  only the topbar, not these field-heading rows.
- Field rows now use keyed content-height wrapping containers and native HTML labels.
  Scoped styles keep content visible and allow long labels to wrap, including long
  English words at2x CSS scaling. Normal main-page scrolling remains enabled.
- The browser regression fails on the previous release with eight internal scrollers.
  It passes48 combinations of viewport320/390/768/1100/1285/1440, Arabic/English and
  CSS scale1/1.25/1.5/2. All eight help dialogs support Enter/Escape in both languages.
  Evidence: ui_layout_checks.json and updated docs/previews screenshots.
- The existing43 Python tests passed with no skips; Ruff lint/format checks passed.
- Gender help is exactly “Male or female.” in both interface languages; simplified family-history
  wording keeps the parent/sibling scope. Model artifacts, data and decision limits are unchanged.
- Main is the canonical source/deployment branch. A ready ZIP and checksum accompany
  the GitHub release; historical download branches remain available.
- scripts/check_ui_layout.cjs is also part of the Linux CI workflow.

Native Windows/Linux CI, browser regression, full training check and Docker build:
https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/actions/runs/41526302085 (success).
Verified ready-archive packaging and publication:
https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/actions/runs/41526754721 (success).

Earlier validation follows; linked native CI runs below refer to their respective versions.

# Mizanak v4.1 — interface maintenance

- Corrected the top-row internal scrollbar. The previous wrap=False Streamlit columns
  became a scrolling flex container; a Markdown-measured49px child contained a65px brand.
  With RTL layout, the internal vertical scrollbar appeared on the left beside Language.
- Header now uses a content-sized keyed container, normally flowing columns, scoped
  overflow:visible and a native HTML brand block. No global scrollbar hiding was added.
- Chromium regression:40 combinations of viewport320/390/768/1285/1440, Arabic/English,
  and CSS scaling1/1.25/1.5/2. No internal header scroller or clipped brand; normal page
  scrolling remained enabled. Eight icon-only help controls retain accessible names and
  keyboard operation.
- BMI, fat mass and FFM are read-only under the inputs, before submit. Actual editing of
  height175→180 updates displayed BMI26.1→24.7 without submitting; still only eight inputs.
- Disease cards use short condition definitions plus one common medical limitation.
  User-facing “model threshold” is now “alert level” in both interface languages, defined as a research
  calculation. Comparison operators and all model operating points are unchanged.
- The original waist illustration is retained at the user's request. The user-approved
  hollow-display logo replaces the shared header and browser-icon asset. The hero uses
  a separate decorative measurement-card/tape/heart SVG instead of repeating the logo. Earlier
  numbered/leaf/filled-display logo drafts are excluded from the application and archive.
- Approved-logo/hero follow-up: the four existing application tests passed. Real Chromium
  checks at390/768/1285px in both languages verified the exact approved header/favicon
  bytes, the separate SVG illustration, responsive visibility, and no header scroller.
- Existing43-test suite passed locally and in both native Windows/Linux CI jobs. Real Chromium desktop/mobile report and help
  interactions, both languages and first/repeated auto-scroll passed.
- Same trusted portable model release20261102T184611Z-ebdefc95; no refit or data changes.

v4.1 CI evidence: https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/actions/runs/41512837483

Earlier v4 validation and native Windows portability evidence follows.

# Mizanak v4 — validation, 2026-11-02

## Scope of this update

- New bilingual interface and brand: Mizanak (Arabic and English), square scale/pulse logo and matching favicon.
- Input panel precedes the report in both DOM and visual order; no sidebar or reserved sidebar width.
- Eight accessible native help popovers; local height and corrected NHANES waist illustrations.
- Four report columns on desktop, two on mobile; one visible percentage per card.
  Tap to read a fixed condition definition. Derived values are in a collapsed section.
- After submission, a session-specific script scrolls/focuses the report. Its unique token
  also supports repeated submissions. Reduced-motion preference is respected.
- Two fixed wellness messages retained; neither diagnoses disease nor certifies health.

## Windows failure fixed

The supplied Windows screenshot failed in write_model_card with UnicodeEncodeError for
U+2192 under cp1256. Python text file operations now specify UTF-8 explicitly. The Windows
launcher sets PYTHONUTF8/PYTHONIOENCODING and the console encoding, and prints a model
compatibility failure before any fallback training. No model checksums are bypassed.

The first native Windows CI run additionally exposed Git CRLF conversion of manifest.json,
causing checksum rejection and disabled prediction. .gitattributes now preserves all model
bytes and original XPORT/PNG bytes; Python source uses LF. The fix does not normalize or
accept a changed manifest after the integrity check.

Two regression tests emulate cp1256 as the default Path text encoding, then exercise
real model-card generation and Arabic/symbol JSON output. Both pass. This addresses the
reported failure; the native Windows CI job subsequently passed the complete suite and PowerShell syntax check (see below).

## Data and model provenance

Training origin: **20261102T140111Z-4ba2271e**. Active portable export:
**20261102T184611Z-ebdefc95**, schema3, ages20–79.
The trained model parameters, thresholds and21,117-row cohort are unchanged.
The native Windows check also rejected XGBoost pickle memory snapshots with input-stream
corruption despite correct artifact hashes. The two XGBoost pipelines now use official
UBJSON model serialization only, with a CPU/two-thread runtime setting. Linux round-trip checks on all21,117
rows gave maximum probability difference0 for both. Platform-specific training
configuration is intentionally not restored; it also failed to load on Windows. The other six artifact bytes are unchanged. No retraining or tuning is
needed for this interface/text-I/O update. The manifest code fingerprints describe the
code used to generate that model release, rather than the later UI/encoding maintenance.
Original model and data integrity checks remain active. No manifest is edited to pretend
that the historical training source is identical to the current source.

See MODEL_CARD.md, age_validation.csv and VERSION_COMPARISON.csv for actual performance.
Some rare cardiac outcomes remain weak; historical older-adult evaluation does not establish
contemporary, Saudi-population, home-device or clinical validity.

## Checks actually run

- Ruff lint and formatting; git whitespace checks.
- **43 tests passed**, no skips, using the existing clean Python3.12 verification environment.
- Both app entrypoints, languages, eight inputs, family answers, automatic calculations,
  eight predictions, input boundaries, stale-result clearing and both wellness branches.
- Real Chromium:1440px desktop and390px touch. Height/waist help images, interactive cards,
  original8 predictions, page title, first/repeated auto-scroll, report ordering, no sidebar,
  no horizontal overflow and no browser JavaScript errors. English also verified.
- Artwork bundled locally; model/runtime remains offline-capable.
- Container mizanak-ai:4.0 built successfully, image:
  sha256:bc68c957b4e84eba1990b2f6e718698efb3b73e4f2c54d30bb3be338492d4df5.
- Offline container smoke: UID10001, all3 artwork files, original active release,8 predictions
  at age79. Server health=ok, HTTP200. Smoke container removed after checking.

The repository deployment branch and ready ZIP are distribution artifacts. Local validation
does not establish the status of a running Streamlit Cloud site.

## Native Windows confirmation

On source commit5f4dd4673fe4c1be7ef0c351287fca78746f8412, the windows-app CI job completed
successfully: the full43-test suite, loading the Linux-trained portable models on Windows,
and Windows PowerShell launcher parsing. This includes the cp1256 regression, actual8-target
inference and both bilingual entrypoints. Interactive double-click use on a physical Windows
device was not performed; browser layout checks used Chromium in the cloud.

CI evidence: https://github.com/abdulazizalhwaiml-dot/Disease-prediction-model/actions/runs/41503936273

The final portable image was rebuilt and passed offline8-target inference with release
20261102T184611Z-ebdefc95. Original data hashes remain unchanged.
