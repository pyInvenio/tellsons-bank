"""End-to-end branch coverage for AuditLoggerService redaction + chaining."""
from __future__ import annotations

from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService
from audit_logger.sink import FileAuditSink


def test_record_redacts_appends_and_writes(tmp_sink_path):
    chain = LogChain()
    service = AuditLoggerService(chain, Redactor(), FileAuditSink(tmp_sink_path))

    returned_hash = service.record("payout 000-00-0000 to acct_test_source")

    written = tmp_sink_path.read_text(encoding="utf-8").strip()
    # Raw PII must never reach the sink.
    assert "000-00-0000" not in written
    assert "acct_test_source" not in written
    assert "***-**-****" in written and "acct_***" in written
    # Returned hash is the one persisted to the sink line (3rd pipe field).
    assert written.split("|")[2] == returned_hash
    assert chain.verify() is True


def test_record_produces_verifiable_multi_entry_chain(tmp_sink_path):
    chain = LogChain()
    service = AuditLoggerService(chain, Redactor(), FileAuditSink(tmp_sink_path))

    service.record("login ok for cust_test_001")
    service.record("statement export for cust_demo_002")

    assert len(tmp_sink_path.read_text(encoding="utf-8").splitlines()) == 2
    assert chain.verify() is True
