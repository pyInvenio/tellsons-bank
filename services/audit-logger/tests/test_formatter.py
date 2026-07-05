from __future__ import annotations

from audit_logger.formatter import AuditFormatter

from conftest import BASE_TIME, make_record


def test_format_uses_pipe_separated_field_order():
    record = make_record(7, "prev-hash", "audit body", BASE_TIME)

    line = AuditFormatter().format(record)

    assert line == (
        f"7|prev-hash|{record.hash}|{BASE_TIME.isoformat()}|audit body"
    )


def test_format_preserves_message_verbatim():
    record = make_record(1, "GENESIS", "acct_*** redacted", BASE_TIME)

    assert AuditFormatter().format(record).endswith("|acct_*** redacted")
