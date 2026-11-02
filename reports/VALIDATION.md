# Mizanak v4 — validation, 2026-11-02

## Scope of this update

- New bilingual interface and brand: ميزانك / Mizanak, square scale/pulse logo and matching favicon.
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

Two regression tests emulate cp1256 as the default Path text encoding, then exercise
real model-card generation and Arabic/symbol JSON output. Both pass. This addresses the
reported failure; actual Windows execution is unavailable in the Linux environment.

## Data and model provenance

The active trained release remains **20261102T140111Z-4ba2271e**, schema3, ages20–79.
The8 pipelines, thresholds and21,117-row cohort are unchanged. No retraining or tuning is
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
  sha256:e6e48646828c39a2c9a25a74166d4d19aa62fef121676bbfd6bb01f062afd05a.
- Offline container smoke: UID10001, all3 artwork files, original active release,8 predictions
  at age79. Server health=ok, HTTP200. Smoke container removed after checking.

The repository deployment branch and ready ZIP are distribution artifacts. Local validation
does not establish the status of a running Streamlit Cloud site.
