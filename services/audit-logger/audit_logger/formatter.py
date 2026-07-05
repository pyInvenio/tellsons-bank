from .log_chain import AuditRecord


class AuditFormatter:
    def format(self, record: AuditRecord) -> str:
        return (
            f"{record.sequence}|{record.previous_hash}|"
            f"{record.hash}|{record.occurred_at.isoformat()}|{record.message}"
        )
