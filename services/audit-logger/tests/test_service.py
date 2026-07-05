from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from audit_logger.log_chain import LogChain
from audit_logger.redactor import Redactor
from audit_logger.service import AuditLoggerService
from audit_logger.sink import FileAuditSink


class TestAuditLoggerService:
    def _make_service(self, sink_path: Path) -> AuditLoggerService:
        return AuditLoggerService(
            chain=LogChain(),
            redactor=Redactor(),
            sink=FileAuditSink(sink_path),
        )

    def test_record_returns_hash(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        result = svc.record("login failed for cust_test_001")
        assert isinstance(result, str)
        assert len(result) == 64

    def test_record_writes_to_sink(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("login failed for cust_test_001")
        assert tmp_sink_path.exists()
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "login failed for cust_test_001" in content

    def test_record_redacts_ssn(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("customer 000-00-0000 accessed system")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "000-00-0000" not in content
        assert "***-**-****" in content

    def test_record_redacts_account_id(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("transfer from acct_test_source")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "acct_test_source" not in content
        assert "acct_***" in content

    def test_record_preserves_chain_integrity(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("event 1 for cust_test_001")
        svc.record("event 2 for cust_test_002")
        svc.record("event 3 for acct_test_source")
        assert svc.chain.verify() is True

    def test_multiple_records_appended_to_sink(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("event 1 for cust_test_001")
        svc.record("event 2 for cust_test_002")
        lines = tmp_sink_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 2

    def test_record_with_mock_sink(self) -> None:
        mock_sink = MagicMock(spec=FileAuditSink)
        svc = AuditLoggerService(
            chain=LogChain(),
            redactor=Redactor(),
            sink=mock_sink,
        )
        svc.record("login failed for cust_test_001")
        mock_sink.write.assert_called_once()
        written_line = mock_sink.write.call_args[0][0]
        assert "login failed for cust_test_001" in written_line

    def test_record_with_combined_pii(self, tmp_sink_path: Path) -> None:
        svc = self._make_service(tmp_sink_path)
        svc.record("customer 000-00-0000 transferred from acct_test_source")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "000-00-0000" not in content
        assert "acct_test_source" not in content

    def test_sink_exception_propagates(self) -> None:
        mock_sink = MagicMock(spec=FileAuditSink)
        mock_sink.write.side_effect = OSError("disk full")
        svc = AuditLoggerService(
            chain=LogChain(),
            redactor=Redactor(),
            sink=mock_sink,
        )
        try:
            svc.record("event for cust_test_001")
            assert False, "Expected OSError"
        except OSError:
            pass

    def test_record_with_synthetic_fixture_messages(
        self,
        tmp_sink_path: Path,
        synthetic_audit_lines: list[dict[str, str]],
    ) -> None:
        svc = self._make_service(tmp_sink_path)
        for line in synthetic_audit_lines:
            svc.record(line["message"])
        assert svc.chain.verify() is True
        content = tmp_sink_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(content) == len(synthetic_audit_lines)

    def test_idempotency_collision_produces_unique_hashes(
        self, tmp_sink_path: Path
    ) -> None:
        svc = self._make_service(tmp_sink_path)
        h1 = svc.record("duplicate event for cust_test_001")
        h2 = svc.record("duplicate event for cust_test_001")
        assert h1 != h2
