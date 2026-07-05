from __future__ import annotations

from datetime import datetime, timezone

from audit_logger.formatter import AuditFormatter
from audit_logger.log_chain import AuditRecord


def test_format_preserves_field_order_and_separators():
    occurred_at = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    record = AuditRecord(
        sequence=2,
        previous_hash="prevhash",
        message="login for cust_test_001",
        occurred_at=occurred_at,
        hash="currenthash",
    )

    line = AuditFormatter().format(record)

    assert line == (
        "2|prevhash|currenthash|2024-01-01T12:00:00+00:00|login for cust_test_001"
    )
    assert line.split("|") == [
        "2",
        "prevhash",
        "currenthash",
        "2024-01-01T12:00:00+00:00",
        "login for cust_test_001",
    ]
