from dataclasses import dataclass, field


@dataclass(frozen=True)
class TransactionEvent:
    event_id: str
    account_id: str
    amount: str
    currency: str
    occurred_at: str
    metadata: dict[str, str] = field(default_factory=dict)
