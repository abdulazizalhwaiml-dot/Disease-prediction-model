"""Build a ready ZIP from tracked source plus verified original older XPORT files.

Developer command from a Git checkout: python scripts/package_project.py
No environment, credentials, previous model releases or previous datasets are included.
"""

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root.parent / "MIZANAK_v4_1.zip")
    args = parser.parse_args()
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    sources = json.loads((root / "data/older_sources.json").read_text(encoding="utf-8"))
    files = {root / name for name in tracked if name and (root / name).is_file()}
    files.update(root / "DATA_SET" / source["cycle"] / source["filename"] for source in sources)
    pointer = json.loads((root / "models/current.json").read_text(encoding="utf-8"))
    release = root / "models" / pointer["run_id"]
    manifest = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    for relative, digest in manifest["sources_sha256"].items():
        if hashlib.sha256((root / "DATA_SET" / relative).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Source checksum mismatch: {relative}")
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(files):
            archive.write(path, f"{args.output.stem}/{path.relative_to(root).as_posix()}")
    with zipfile.ZipFile(args.output) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC verification failed")
        names = archive.namelist()
        assert sum(name.endswith(".joblib") for name in names) == 8
        assert sum(name.lower().endswith(".xpt") for name in names) == 77
        assert not any(".venv/" in name or "/.git/" in name for name in names)
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    args.output.with_suffix(".zip.sha256").write_text(
        f"{digest}  {args.output.name}\n", encoding="utf-8"
    )
    print(
        f"Verified ZIP: {len(files)} files, {args.output.stat().st_size:,} bytes; SHA256 {digest}"
    )


if __name__ == "__main__":
    main()
