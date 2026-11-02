"""Reproduce the user's cp1256 report failure without requiring a Windows machine."""

import json
from pathlib import Path

import pytest

from nhanes_ai.train import save_json, write_model_card


@pytest.fixture
def windows_text_default(monkeypatch):
    original = Path.open

    def open_with_cp1256(self, mode="r", buffering=-1, encoding=None, errors=None, newline=None):
        if "b" not in mode and encoding in (None, "locale"):
            encoding = "cp1256"
        return original(self, mode, buffering, encoding, errors, newline)

    monkeypatch.setattr(Path, "open", open_with_cp1256)


def test_model_card_writes_utf8_under_windows_default(model_root, tmp_path, windows_text_default):
    pointer = json.loads((model_root / "current.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (model_root / pointer["run_id"] / "manifest.json").read_text(encoding="utf-8")
    )
    report = tmp_path / "MODEL_CARD.md"
    write_model_card(report, manifest)
    text = report.read_bytes().decode("utf-8")
    assert "→" in text
    assert "≥" in text
    assert "21,117" in text


def test_json_writes_arabic_and_symbols_under_windows_default(tmp_path, windows_text_default):
    path = tmp_path / "metadata.json"
    payload = {"project": "ميزانك", "rule": "non-HDL ≥190 → positive"}
    save_json(path, payload)
    assert json.loads(path.read_bytes().decode("utf-8")) == payload
