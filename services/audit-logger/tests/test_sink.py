from __future__ import annotations

import pytest

from audit_logger.sink import FileAuditSink


def test_write_creates_missing_parent_directory(sink_path):
    assert not sink_path.parent.exists()

    FileAuditSink(sink_path).write("line-1")

    assert sink_path.parent.is_dir()
    assert sink_path.read_text(encoding="utf-8") == "line-1\n"


def test_write_appends_across_multiple_calls(sink_path):
    sink = FileAuditSink(sink_path)

    sink.write("line-1")
    sink.write("line-2")

    assert sink_path.read_text(encoding="utf-8") == "line-1\nline-2\n"


def test_each_line_is_newline_terminated(sink_path):
    FileAuditSink(sink_path).write("only")

    contents = sink_path.read_text(encoding="utf-8")
    assert contents.endswith("\n")
    assert contents.count("\n") == 1


def test_write_raises_when_parent_path_is_a_file(tmp_path):
    # A regular file stands where the sink expects a directory, so mkdir fails.
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("occupied", encoding="utf-8")
    sink = FileAuditSink(blocker / "audit.log")

    with pytest.raises((NotADirectoryError, FileExistsError)):
        sink.write("line")
