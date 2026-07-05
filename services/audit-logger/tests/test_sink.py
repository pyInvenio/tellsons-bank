from __future__ import annotations

from pathlib import Path
from unittest.mock import mock_open, patch

from audit_logger.sink import FileAuditSink


class TestFileAuditSink:
    def test_creates_parent_directory(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("1|GENESIS|hash|2025-01-15T12:00:00+00:00|login failed for cust_test_001")
        assert tmp_sink_path.parent.exists()

    def test_writes_line_with_newline(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("line for cust_test_001")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert content == "line for cust_test_001\n"

    def test_appends_multiple_lines(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("first for cust_test_001")
        sink.write("second for acct_test_source")
        lines = tmp_sink_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        assert lines[0] == "first for cust_test_001"
        assert lines[1] == "second for acct_test_source"

    def test_handles_empty_line(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert content == "\n"

    def test_utf8_encoding(self, tmp_sink_path: Path) -> None:
        sink = FileAuditSink(tmp_sink_path)
        sink.write("withdrawal for cust_test_002 \u00e9\u00e0\u00fc\u00f1")
        content = tmp_sink_path.read_text(encoding="utf-8")
        assert "\u00e9\u00e0\u00fc\u00f1" in content

    def test_parent_already_exists(self, tmp_path: Path) -> None:
        sink_path = tmp_path / "test.log"
        sink = FileAuditSink(sink_path)
        sink.write("line for cust_test_001")
        content = sink_path.read_text(encoding="utf-8")
        assert content == "line for cust_test_001\n"

    def test_deeply_nested_path(self, tmp_path: Path) -> None:
        sink_path = tmp_path / "a" / "b" / "c" / "test.log"
        sink = FileAuditSink(sink_path)
        sink.write("deep write for cust_test_001")
        assert sink_path.exists()
        assert "deep write" in sink_path.read_text(encoding="utf-8")

    def test_unwritable_path_raises(self, tmp_path: Path) -> None:
        import os
        import stat

        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        os.chmod(read_only_dir, stat.S_IRUSR | stat.S_IXUSR)
        sink_path = read_only_dir / "subdir" / "test.log"
        sink = FileAuditSink(sink_path)
        try:
            sink.write("should fail")
            assert False, "Expected an OSError"
        except OSError:
            pass
        finally:
            os.chmod(read_only_dir, stat.S_IRWXU)
