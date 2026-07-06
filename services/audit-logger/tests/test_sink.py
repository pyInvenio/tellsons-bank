from __future__ import annotations

from pathlib import Path

import pytest

from audit_logger.sink import FileAuditSink


class TestFileAuditSink:
    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "audit.log"
        sink = FileAuditSink(nested)
        sink.write("cust_test_001 event")
        assert nested.parent.exists()

    def test_writes_line_with_newline(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("cust_test_001 event")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert content == "cust_test_001 event\n"

    def test_appends_multiple_lines(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("line one")
        sink.write("line two")
        lines = tmp_sink_path.read_text(encoding="utf-8").splitlines()
        assert lines == ["line one", "line two"]

    def test_utf8_content(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("cust_test_001 \u00e9v\u00e9nement")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "\u00e9v\u00e9nement" in content

    def test_unwritable_path_raises(self, tmp_path: Path) -> None:
        bad_path = Path("/proc/nonexistent/audit.log")
        sink = FileAuditSink(bad_path)
        with pytest.raises(OSError):
            sink.write("should fail")
