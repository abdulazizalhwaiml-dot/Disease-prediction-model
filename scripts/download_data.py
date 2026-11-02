"""Download public older NHANES files with pinned SHA256 verification.

Run once before retraining: python scripts/download_data.py
Existing valid files are reused. A failed download never replaces a valid local file.
"""

import argparse
import hashlib
import json
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def fetch(source, destination):
    path = destination / source["cycle"] / source["filename"]
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]:
        return f"Verified {source['cycle']}/{path.name}"
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(source["url"], timeout=120) as response:
        data = response.read()
    if (
        not data.startswith(b"HEADER RECORD")
        or hashlib.sha256(data).hexdigest() != source["sha256"]
    ):
        raise ValueError(f"Unexpected file or checksum: {source['url']}")
    temporary = path.with_suffix(".download")
    temporary.write_bytes(data)
    os.replace(temporary, path)
    return f"Downloaded {source['cycle']}/{path.name}"


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=root / "DATA_SET")
    args = parser.parse_args()
    sources = json.loads((root / "data/older_sources.json").read_text())
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(lambda source: fetch(source, args.data), sources):
            print(result, flush=True)
    print(f"Ready: {len(sources)} verified older source files.")


if __name__ == "__main__":
    main()
