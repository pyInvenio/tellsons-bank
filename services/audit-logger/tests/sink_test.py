"""Branch coverage for FileAuditSink temp-file writes and error paths."""
from __future__ import annotations

import pytest

from audit_logger.sink import FileAuditSink


def test_write_creates_missing_parent_directory(tmp_sink_path):
    assert not tmp_sink_path.parent.exists()

    FileAuditSink(tmp_sink_path).write("1|GENESIS|deadbeef|t|line one")

    assert tmp_sink_path.parent.is_dir()
    assert tmp_sink_path.read_text(encoding="utf-8") == "1|GENESIS|deadbeef|t|line one\n"


def test_write_appends_across_multiple_writes_with_newlines(tmp_sink_path):
    sink = FileAuditSink(tmp_sink_path)

    sink.write("line one")
    sink.write("line two")

    assert tmp_sink_path.read_text(encoding="utf-8") == "line one\nline two\n"


def test_write_raises_when_parent_path_is_a_file(tmp_path):
    # A regular file blocks directory creation, simulating an unwritable sink.
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    sink = FileAuditSink(blocker / "nested" / "chain.log")

    with pytest.raises((NotADirectoryError, FileExistsError, OSError)):
        sink.write("should fail")
