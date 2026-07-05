"""Branch coverage for AuditFormatter deterministic field ordering."""
from __future__ import annotations

from audit_logger.formatter import AuditFormatter


def test_format_uses_pipe_separated_field_order(fixed_time, make_records):
    (record,) = make_records(["transfer queued txn_test_0001"], start=fixed_time)

    line = AuditFormatter().format(record)

    expected = (
        f"{record.sequence}|{record.previous_hash}|{record.hash}|"
        f"{fixed_time.isoformat()}|transfer queued txn_test_0001"
    )
    assert line == expected
    assert line.split("|")[0] == "1"
    assert line.split("|")[1] == "GENESIS"
