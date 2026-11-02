# Development checks

Use Python 3.12 and the platform-specific development lock described in
[DEPLOYMENT.md](DEPLOYMENT.md). Run from the repository root:

```bash
ruff check src app tests scripts
ruff format --check src app tests scripts
pytest -q
```

## Browser layout regression

The browser check covers all eight field-heading/help rows and the topbar, rather than
only the topbar. It checks real overflow, clipping, accessible help, keyboard operation,
both languages, six viewport widths and four CSS scales. It preserves normal page scrolling.

Install Node.js and the optional browser tooling, then start the app in another terminal:

```bash
npm install --no-save --package-lock=false playwright@1.62.1
npx playwright install chromium
python -m streamlit run streamlit_app.py
```

Run the browser check:

```bash
node scripts/check_ui_layout.cjs
```

Optional environment variables: `MIZANAK_TEST_URL` selects a different local app URL,
`MIZANAK_UI_OUTPUT` writes screenshots and JSON evidence, and
`PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` selects a system Chromium executable.
The application itself has no Node.js or Playwright dependency.

## Ready releases

The **Package ready Mizanak release** workflow runs manually on `main`. Supply the
application version from `pyproject.toml`. It tests the shipped models, verifies the
original source downloads, builds the complete ZIP with its checksum, and publishes
both files to GitHub Releases. It does not train replacement models.
