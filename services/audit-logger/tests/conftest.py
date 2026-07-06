from __future__ import annotations

import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "docs" / "fixtures"


@pytest.fixture()
def synthetic_audit_lines() -> list[dict]:
    path = FIXTURES_DIR / "synthetic-audit-lines.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def tmp_sink_path(tmp_path: Path) -> Path:
    return tmp_path / "audit.log"
