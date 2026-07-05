from __future__ import annotations

from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService
from audit_logger.sink import FileAuditSink


def test_record_redacts_appends_and_writes(fixed_clock, sink_path, synthetic_audit_lines):
    chain = LogChain()
    service = AuditLoggerService(chain, Redactor(), FileAuditSink(sink_path))

    returned_hash = service.record("login failed for 000-00-0000 on acct_test_0001")

    # Returned hash matches the single appended record.
    assert len(chain._records) == 1
    assert returned_hash == chain._records[0].hash

    line = sink_path.read_text(encoding="utf-8").strip()
    # PII is redacted before it reaches the sink.
    assert "000-00-0000" not in line
    assert "acct_test_0001" not in line
    assert "***-**-****" in line
    assert "acct_***" in line
    assert line.endswith("login failed for ***-**-**** on acct_***")


def test_record_multiple_synthetic_lines_keeps_chain_verifiable(
    fixed_clock, sink_path, synthetic_audit_lines
):
    chain = LogChain()
    service = AuditLoggerService(chain, Redactor(), FileAuditSink(sink_path))

    for entry in synthetic_audit_lines:
        service.record(entry["message"])

    assert len(chain._records) == len(synthetic_audit_lines)
    assert chain.verify() is True
    written = sink_path.read_text(encoding="utf-8").splitlines()
    assert len(written) == len(synthetic_audit_lines)
