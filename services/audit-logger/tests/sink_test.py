from __future__ import annotations

import pytest

from audit_logger.sink import FileAuditSink


def test_write_creates_missing_parent_directory(tmp_path):
    target = tmp_path / "nested" / "dir" / "audit.log"
    assert not target.parent.exists()

    FileAuditSink(target).write("1|GENESIS|hash|ts|msg")

    assert target.exists()
    assert target.read_text(encoding="utf-8") == "1|GENESIS|hash|ts|msg\n"


def test_write_appends_across_multiple_calls(tmp_path):
    target = tmp_path / "audit.log"
    sink = FileAuditSink(target)

    sink.write("first")
    sink.write("second")

    assert target.read_text(encoding="utf-8") == "first\nsecond\n"


def test_write_terminates_each_line_with_newline(tmp_path):
    target = tmp_path / "audit.log"
    FileAuditSink(target).write("only")

    assert target.read_text(encoding="utf-8").endswith("\n")


def test_write_raises_when_path_is_unwritable(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("not a directory", encoding="utf-8")
    target = blocker / "audit.log"

    with pytest.raises((NotADirectoryError, FileExistsError, OSError)):
        FileAuditSink(target).write("line")
