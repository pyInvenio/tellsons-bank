from __future__ import annotations

from pathlib import Path

from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService
from audit_logger.sink import FileAuditSink


class TestAuditLoggerService:
    def _make_service(self, sink_path: Path) -> AuditLoggerService:
        return AuditLoggerService(LogChain(), Redactor(), FileAuditSink(sink_path))

    def test_record_returns_hash(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        result = svc.record("cust_test_001 logged in")
        assert isinstance(result, str) and len(result) == 64

    def test_record_redacts_ssn(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("SSN 000-00-0000 detected")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "000-00-0000" not in content
        assert "***-**-****" in content

    def test_record_redacts_account_id(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("transfer from acct_test_source_01")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "acct_test_source_01" not in content
        assert "acct_***" in content

    def test_chain_integrity_after_multiple_records(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("cust_test_001 event one")
        svc.record("cust_test_002 event two")
        svc.record("txn_test_001 event three")
        assert svc.chain.verify() is True

    def test_sink_receives_formatted_output(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("cust_test_001 logged in")
        lines = tmp_sink_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        parts = lines[0].split("|")
        assert parts[0] == "1"
        assert parts[1] == "GENESIS"

    def test_uses_synthetic_fixture_messages(
        self, tmp_sink_path: Path, synthetic_audit_lines: list[dict]
    ) -> None:
        svc = self._make_service(tmp_sink_path)
        for entry in synthetic_audit_lines:
            svc.record(entry["message"])
        assert svc.chain.verify() is True
        lines = tmp_sink_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == len(synthetic_audit_lines)
