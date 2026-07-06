from __future__ import annotations

from datetime import datetime, timezone

from audit_logger.formatter import AuditFormatter
from audit_logger.log_chain import AuditRecord, LogChain


def test_formatter_outputs_pipe_delimited_fields_in_expected_order() -> None:
    occurred_at = datetime(2024, 1, 1, 12, 30, 45, tzinfo=timezone.utc)
    record = AuditRecord(
        sequence=7,
        previous_hash="prev-hash",
        message="synthetic audit payload",
        occurred_at=occurred_at,
        hash=LogChain._hash(7, "prev-hash", "synthetic audit payload", occurred_at.isoformat()),
    )

    assert AuditFormatter().format(record) == (
        "7|prev-hash|"
        f"{record.hash}|"
        "2024-01-01T12:30:45+00:00|synthetic audit payload"
    )
