from __future__ import annotations

from datetime import datetime, timezone

from audit_logger.formatter import AuditFormatter
from audit_logger.log_chain import AuditRecord


class TestAuditFormatter:
    def test_field_order(self) -> None:
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=1,
            previous_hash="GENESIS",
            message="cust_test_001 logged in",
            occurred_at=ts,
            hash="abc123def456",
        )
        formatter = AuditFormatter()
        result = formatter.format(record)
        parts = result.split("|")
        assert parts[0] == "1"
        assert parts[1] == "GENESIS"
        assert parts[2] == "abc123def456"
        assert parts[3] == ts.isoformat()
        assert parts[4] == "cust_test_001 logged in"

    def test_pipe_separated_output(self) -> None:
        ts = datetime(2025, 6, 1, 8, 30, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=42,
            previous_hash="prev_hash_value",
            message="txn_test_001 processed",
            occurred_at=ts,
            hash="current_hash_value",
        )
        formatter = AuditFormatter()
        result = formatter.format(record)
        assert result.count("|") == 4

    def test_message_with_pipe_characters(self) -> None:
        ts = datetime(2025, 1, 1, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=1,
            previous_hash="GENESIS",
            message="msg|with|pipes",
            occurred_at=ts,
            hash="hashval",
        )
        formatter = AuditFormatter()
        result = formatter.format(record)
        assert "msg|with|pipes" in result
