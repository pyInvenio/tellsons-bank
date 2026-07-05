"""Shared fixtures for audit-logger compliance tests.

All data here is synthetic. Identifiers use the mandatory ``test_``/``demo_``
prefixes and SSN-like values use the reserved ``000-00-0000`` documentation
pattern. No real customer data, secrets, or network calls are used.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from audit_logger.log_chain import AuditRecord, LogChain


FIXED_TIME = datetime(2020, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def fixed_time() -> datetime:
    """A deterministic, wall-clock-independent timestamp for record fixtures."""
    return FIXED_TIME


@pytest.fixture
def tmp_sink_path(tmp_path: Path) -> Path:
    """A temp-file path for FileAuditSink writes (never a shared location)."""
    return tmp_path / "audit" / "chain.log"


def build_chain(messages: list[str], start: datetime = FIXED_TIME) -> list[AuditRecord]:
    """Build a valid hash-linked record list with fixed, monotonic timestamps.

    Uses ``LogChain._hash`` so records are internally consistent, but assigns
    deterministic timestamps instead of ``datetime.now`` so tests never depend
    on wall-clock time.
    """
    records: list[AuditRecord] = []
    previous_hash = "GENESIS"
    for index, message in enumerate(messages):
        sequence = index + 1
        occurred_at = start + timedelta(seconds=index)
        digest = LogChain._hash(sequence, previous_hash, message, occurred_at.isoformat())
        records.append(AuditRecord(sequence, previous_hash, message, occurred_at, digest))
        previous_hash = digest
    return records


@pytest.fixture
def make_records():
    """Factory fixture exposing :func:`build_chain` without cross-module imports."""
    return build_chain


@pytest.fixture
def valid_records() -> list[AuditRecord]:
    return build_chain([
        "login ok for cust_test_001",
        "transfer queued txn_test_0001",
        "statement exported for cust_demo_002",
    ])
