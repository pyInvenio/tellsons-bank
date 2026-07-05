from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from audit_logger.log_chain import AuditRecord, LogChain

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "docs" / "fixtures"


@pytest.fixture()
def synthetic_audit_lines() -> list[dict[str, str]]:
    path = FIXTURES_DIR / "synthetic-audit-lines.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def synthetic_customers() -> list[dict[str, str]]:
    path = FIXTURES_DIR / "synthetic-customers.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def synthetic_accounts() -> list[dict[str, str]]:
    path = FIXTURES_DIR / "synthetic-accounts.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture()
def fixed_timestamp() -> datetime:
    return datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture()
def genesis_record(fixed_timestamp: datetime) -> AuditRecord:
    chain = LogChain()
    msg = "login failed for cust_test_001"
    digest = chain._hash(1, "GENESIS", msg, fixed_timestamp.isoformat())
    return AuditRecord(
        sequence=1,
        previous_hash="GENESIS",
        message=msg,
        occurred_at=fixed_timestamp,
        hash=digest,
    )


@pytest.fixture()
def tmp_sink_path(tmp_path: Path) -> Path:
    return tmp_path / "audit" / "test.log"
