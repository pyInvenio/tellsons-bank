from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pytest

from audit_logger.log_chain import AuditRecord


@pytest.fixture
def sink_path(tmp_path: Path) -> Path:
    return tmp_path / "audit" / "log.jsonl"


@pytest.fixture
def fixed_record() -> Callable[..., AuditRecord]:
    def _make(
        *,
        sequence: int = 1,
        previous_hash: str = "GENESIS",
        message: str = "synthetic audit event",
        occurred_at: datetime | None = None,
        hash_value: str = "fixed-hash",
    ) -> AuditRecord:
        return AuditRecord(
            sequence=sequence,
            previous_hash=previous_hash,
            message=message,
            occurred_at=occurred_at or datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
            hash=hash_value,
        )

    return _make


@pytest.fixture
def redaction_fixtures() -> list[dict[str, str]]:
    fixture_path = (
        Path(__file__).resolve().parents[3]
        / "docs"
        / "fixtures"
        / "audit-logger-redaction.json"
    )
    return json.loads(fixture_path.read_text(encoding="utf-8"))
