from __future__ import annotations

from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService


class RecordingSink:
    """Test double capturing writes instead of touching the filesystem."""

    def __init__(self) -> None:
        self.lines: list[str] = []

    def write(self, line: str) -> None:
        self.lines.append(line)


def _service(sink: RecordingSink) -> AuditLoggerService:
    return AuditLoggerService(LogChain(), Redactor(), sink)


def test_record_redacts_pii_before_writing(frozen_clock):
    sink = RecordingSink()
    service = _service(sink)

    service.record("cust 000-00-0000 owns acct_test_777001")

    assert len(sink.lines) == 1
    written = sink.lines[0]
    assert "000-00-0000" not in written
    assert "acct_test_777001" not in written
    assert "***-**-****" in written
    assert "acct_***" in written


def test_record_returns_chain_hash_and_keeps_chain_verifiable(frozen_clock):
    sink = RecordingSink()
    service = _service(sink)

    first = service.record("login for cust_test_001")
    second = service.record("logout for cust_test_001")

    assert first != second
    assert service.chain.verify() is True
    trailing_hash = sink.lines[-1].split("|")[2]
    assert trailing_hash == second


def test_record_writes_one_line_per_event(frozen_clock):
    sink = RecordingSink()
    service = _service(sink)

    service.record("event one")
    service.record("event two")

    assert len(sink.lines) == 2
