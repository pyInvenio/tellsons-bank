from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class DisputeCase:
    case_id: str
    transaction_id: str
    status: str
    audit_reason: str
    updated_at: datetime


class DisputeWorkflow:
    def open_case(self, case_id: str, transaction_id: str, reason: str) -> DisputeCase:
        if not case_id.startswith("case_test_"):
            raise ValueError("synthetic case id required")
        if not transaction_id:
            raise ValueError("transaction id required")
        return DisputeCase(case_id, transaction_id, "OPEN", reason, datetime.now(timezone.utc))

    def resolve(self, case: DisputeCase, approved: bool) -> DisputeCase:
        status = "CUSTOMER_CREDITED" if approved else "DENIED"
        return DisputeCase(case.case_id, case.transaction_id, status, case.audit_reason, datetime.now(timezone.utc))
