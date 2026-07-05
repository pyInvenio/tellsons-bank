from pathlib import Path


class FileAuditSink:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(self, line: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
