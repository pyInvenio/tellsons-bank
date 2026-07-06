from __future__ import annotations

from pathlib import Path

import pytest

from audit_logger.sink import FileAuditSink


def test_sink_creates_missing_parent_directory(sink_path: Path) -> None:
    sink = FileAuditSink(sink_path)

    sink.write("first line")

    assert sink_path.exists()
    assert sink_path.read_text(encoding="utf-8") == "first line\n"


def test_sink_appends_multiple_lines_and_preserves_newlines(sink_path: Path) -> None:
    sink = FileAuditSink(sink_path)

    sink.write("first line")
    sink.write("second line")

    content = sink_path.read_text(encoding="utf-8")
    assert content == "first line\nsecond line\n"
    assert content.splitlines() == ["first line", "second line"]


def test_sink_write_raises_when_parent_is_a_file(tmp_path: Path) -> None:
    parent_file = tmp_path / "parent-file"
    parent_file.write_text("not a directory", encoding="utf-8")
    sink = FileAuditSink(parent_file / "child.log")

    with pytest.raises((NotADirectoryError, FileExistsError)):
        sink.write("line")
