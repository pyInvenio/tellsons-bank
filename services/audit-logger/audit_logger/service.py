from .formatter import AuditFormatter
from .log_chain import LogChain
from .redactor import Redactor
from .sink import FileAuditSink


class AuditLoggerService:
    def __init__(self, chain: LogChain, redactor: Redactor, sink: FileAuditSink) -> None:
        self.chain = chain
        self.redactor = redactor
        self.sink = sink
        self.formatter = AuditFormatter()

    def record(self, message: str) -> str:
        safe_message = self.redactor.redact(message)
        record = self.chain.append(safe_message)
        line = self.formatter.format(record)
        self.sink.write(line)
        return record.hash
