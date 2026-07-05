from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    previous_hash: str
    message: str
    occurred_at: datetime
    hash: str


class LogChain:
    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def append(self, message: str) -> AuditRecord:
        previous_hash = self._records[-1].hash if self._records else "GENESIS"
        sequence = len(self._records) + 1
        occurred_at = datetime.now(timezone.utc)
        digest = self._hash(sequence, previous_hash, message, occurred_at.isoformat())
        record = AuditRecord(sequence, previous_hash, message, occurred_at, digest)
        self._records.append(record)
        return record

    def verify(self, records: list[AuditRecord] | None = None) -> bool:
        candidate = records if records is not None else self._records
        previous = "GENESIS"
        for expected_sequence, record in enumerate(candidate, start=1):
            if record.sequence != expected_sequence:
                return False
            if record.previous_hash != previous:
                return False
            expected_hash = self._hash(
                record.sequence,
                record.previous_hash,
                record.message,
                record.occurred_at.isoformat(),
            )
            if expected_hash != record.hash:
                return False
            previous = record.hash
        return True

    @staticmethod
    def _hash(sequence: int, previous_hash: str, message: str, occurred_at: str) -> str:
        payload = f"{sequence}|{previous_hash}|{message}|{occurred_at}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()
