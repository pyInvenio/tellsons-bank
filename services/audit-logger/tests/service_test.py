from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from audit_logger.formatter import AuditFormatter
from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService
from audit_logger.sink import FileAuditSink


def test_service_records_redacted_message_to_real_components(tmp_path: Path) -> None:
    sink_path = tmp_path / "audit" / "service.log"
    chain = LogChain()
    service = AuditLoggerService(chain, Redactor(), FileAuditSink(sink_path))

    message = "cust_test_0001 sent 000-00-0000 from acct_test_0001"
    record_hash = service.record(message)

    assert chain.verify() is True
    assert record_hash == chain._records[-1].hash
    assert sink_path.exists()

    line = sink_path.read_text(encoding="utf-8").strip()
    assert "***-**-****" in line
    assert "acct_***" in line
    assert "000-00-0000" not in line
    assert "acct_test_0001" not in line


def test_service_writes_formatted_redacted_line_to_sink_mock() -> None:
    chain = LogChain()
    sink = Mock()
    service = AuditLoggerService(chain, Redactor(), sink)

    message = "cust_test_0001 sent 000-00-0000 from acct_test_0001"
    record_hash = service.record(message)

    assert record_hash == chain._records[-1].hash
    sink.write.assert_called_once_with(AuditFormatter().format(chain._records[-1]))
