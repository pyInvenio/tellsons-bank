from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskSignal:
    name: str
    weight: int
    active: bool


class RiskScorecard:
    def score(self, signals: list[RiskSignal]) -> tuple[int, str]:
        total = sum(signal.weight for signal in signals if signal.active)
        if total >= 80:
            return total, "BLOCK"
        if total >= 45:
            return total, "STEP_UP"
        return total, "ALLOW"
