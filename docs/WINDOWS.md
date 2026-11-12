# Run Mizanak on Windows

## Quick start

1. Install [64-bit Python 3.12](https://www.python.org/downloads/) with the Python Launcher.
2. Extract the project and open the folder containing README.md and START_WINDOWS.bat.
3. Double-click START_WINDOWS.bat and wait for installation to finish.
4. Open **http://localhost:8501** when the launch URL appears.

The ready package includes current models. If they are missing or incompatible, the launcher downloads and verifies historical data, then retrains. Initial installation may take several minutes; keep the window open. No GPU, API key, or PowerShell execution-policy change is required.

## Manual setup

Type `powershell` into the project folder's address bar and press Enter. Run **one command at a time**, waiting for the `PS` prompt to return:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements-windows.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

To retrain, run these before starting the app:

```powershell
.\.venv\Scripts\python.exe scripts/download_data.py
.\.venv\Scripts\python.exe -m nhanes_ai.train --jobs 2
.\.venv\Scripts\python.exe scripts/export_dataset.py
```

## Later sessions

Double-click START_WINDOWS.bat or run only the final launch command. Keep the window open; Ctrl+C stops the application.

## Common errors

- Missing requirements-windows.lock: open PowerShell in the correct project folder.
- Unrecognized `py`: install Python 3.12 with the Python Launcher and reopen the terminal.
- LightGBM DLL/WinError126: install [Microsoft Visual C++ x64](https://aka.ms/vs/17/release/vc_redist.x64.exe).
- Missing historical training files: complete scripts/download_data.py with internet access.
- Incompatible models: retrain with the locked package versions; do not change manifests or hashes.

Supported ages are **20–79**, excluding pregnancy. The project is experimental and does not diagnose disease or certify health. Automated Windows checks passed for model loading, the interface, and encoding; PowerShell launcher syntax was checked. Interactive double-click use on a physical device was not tested.

## Upgrade from an earlier release

If MODEL_CARD.md writing raises UnicodeEncodeError, use the complete updated package. Text reading and report writing now explicitly use UTF-8, and the Windows launcher enables the same encoding. Retraining is unnecessary when bundled models load successfully; if needed, the launcher first displays the reason.

Automatic Git line-ending conversion on Windows can invalidate the model-manifest hash. The new .gitattributes preserves model bytes without bypassing integrity checks.

The package includes portable exports of both XGBoost models instead of the historical memory format rejected by Windows. Stop the earlier instance with Ctrl+C before launching the new one on localhost:8501.
