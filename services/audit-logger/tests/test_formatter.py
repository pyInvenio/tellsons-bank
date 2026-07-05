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
            message="login failed for cust_test_001",
            occurred_at=ts,
            hash="abc123def456",
        )
        fmt = AuditFormatter()
        result = fmt.format(record)
        parts = result.split("|")
        assert parts[0] == "1"
        assert parts[1] == "GENESIS"
        assert parts[2] == "abc123def456"
        assert parts[3] == "2025-01-15T12:00:00+00:00"
        assert parts[4] == "login failed for cust_test_001"

    def test_pipe_count(self) -> None:
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=1,
            previous_hash="GENESIS",
            message="transfer denied for acct_test_source",
            occurred_at=ts,
            hash="deadbeef",
        )
        fmt = AuditFormatter()
        result = fmt.format(record)
        assert result.count("|") == 4

    def test_message_with_pipe_character(self) -> None:
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=1,
            previous_hash="GENESIS",
            message="action|detail for cust_test_001",
            occurred_at=ts,
            hash="hash_val",
        )
        fmt = AuditFormatter()
        result = fmt.format(record)
        assert result.endswith("action|detail for cust_test_001")

    def test_empty_message(self) -> None:
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=1,
            previous_hash="GENESIS",
            message="",
            occurred_at=ts,
            hash="hash_val",
        )
        fmt = AuditFormatter()
        result = fmt.format(record)
        assert result.endswith("|")

    def test_high_sequence_number(self) -> None:
        ts = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        record = AuditRecord(
            sequence=999999,
            previous_hash="prev",
            message="event for cust_test_001",
            occurred_at=ts,
            hash="hash_val",
        )
        fmt = AuditFormatter()
        result = fmt.format(record)
        assert result.startswith("999999|")

    def test_format_with_genesis_record_fixture(
        self, genesis_record: AuditRecord
    ) -> None:
        fmt = AuditFormatter()
        result = fmt.format(genesis_record)
        parts = result.split("|")
        assert parts[0] == "1"
        assert parts[1] == "GENESIS"
        assert parts[2] == genesis_record.hash
        assert parts[4] == genesis_record.message
