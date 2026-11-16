from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture(autouse=True)
def _clear_promptdiff_cache() -> None:
    import shutil

    cache = ROOT / ".promptdiff"
    if cache.exists():
        shutil.rmtree(cache)
    yield
    if cache.exists():
        shutil.rmtree(cache)


ROOT = Path(__file__).resolve().parents[1]


def write_recording(path: Path, mapping: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mapping), encoding="utf-8")
    return path
