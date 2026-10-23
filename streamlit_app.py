"""Cloud entry point: load the local src package without an editable pip install.

Run locally with: python -m streamlit run streamlit_app.py
Community Cloud uses this same entry point and the checked-in trusted model release.
"""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for directory in [ROOT, ROOT / "src"]:
    path = str(directory)
    if path not in sys.path:
        sys.path.insert(0, path)

runpy.run_path(str(ROOT / "app" / "main.py"), run_name="__main__")
