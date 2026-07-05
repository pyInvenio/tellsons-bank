from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import audit_logger.log_chain as log_chain_module

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class FrozenClock:
    """Deterministic replacement for ``datetime.now`` used by ``LogChain``.

    Injecting a fixed time source keeps hashes reproducible and avoids any
    wall-clock or sleep dependence in the audit chain tests.
    """

    def __init__(self, instants: list[datetime]) -> None:
        self._instants = list(instants)
        self._index = 0

    def now(self, tz=None):
        instant = self._instants[min(self._index, len(self._instants) - 1)]
        self._index += 1
        if tz is not None and instant.tzinfo is None:
            instant = instant.replace(tzinfo=tz)
        return instant


@pytest.fixture
def fixed_instant() -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def frozen_clock(monkeypatch, fixed_instant):
    """Patch the clock used inside ``LogChain.append`` to a fixed sequence."""

    instants = [
        fixed_instant.replace(second=second) for second in range(0, 60)
    ]
    clock = FrozenClock(instants)

    class _FrozenDatetime:
        @staticmethod
        def now(tz=None):
            return clock.now(tz)

    monkeypatch.setattr(log_chain_module, "datetime", _FrozenDatetime)
    return clock


@pytest.fixture
def redaction_fixtures() -> list[dict]:
    path = FIXTURES_DIR / "synthetic_redaction_cases.json"
    return json.loads(path.read_text(encoding="utf-8"))
