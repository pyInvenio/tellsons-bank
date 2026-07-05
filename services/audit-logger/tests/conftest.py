from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import audit_logger.log_chain as log_chain_module
from audit_logger.log_chain import AuditRecord, LogChain
from audit_logger.redactor import Redactor

REPO_ROOT = Path(__file__).resolve().parents[3]
SYNTHETIC_AUDIT_LINES = REPO_ROOT / "docs" / "fixtures" / "synthetic-audit-lines.json"

# Fixed, obviously-synthetic timestamps. No wall-clock dependence anywhere.
BASE_TIME = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


class FixedClock:
    """Deterministic time source used to replace ``datetime.now`` in LogChain."""

    def __init__(self, start: datetime) -> None:
        self._current = start

    def now(self, tz=None):  # noqa: ANN001 - mirrors datetime.now signature
        value = self._current
        return value.astimezone(tz) if tz is not None else value

    def advance(self, seconds: int) -> None:
        self._current = self._current.fromtimestamp(
            self._current.timestamp() + seconds, tz=timezone.utc
        )


@pytest.fixture
def fixed_clock(monkeypatch):
    """Patch the module-level ``datetime`` so appends use a fixed time source."""
    clock = FixedClock(BASE_TIME)

    class _PatchedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return clock.now(tz)

    monkeypatch.setattr(log_chain_module, "datetime", _PatchedDateTime)
    return clock


@pytest.fixture
def chain(fixed_clock):
    return LogChain()


@pytest.fixture
def redactor():
    return Redactor()


@pytest.fixture
def sink_path(tmp_path):
    return tmp_path / "nested" / "audit.log"


@pytest.fixture
def synthetic_audit_lines():
    return json.loads(SYNTHETIC_AUDIT_LINES.read_text(encoding="utf-8"))


def make_record(sequence, previous_hash, message, occurred_at=BASE_TIME):
    """Build a self-consistent AuditRecord for verify() success cases."""
    digest = LogChain._hash(sequence, previous_hash, message, occurred_at.isoformat())
    return AuditRecord(sequence, previous_hash, message, occurred_at, digest)
