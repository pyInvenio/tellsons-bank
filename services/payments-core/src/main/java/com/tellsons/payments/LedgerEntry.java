package com.tellsons.payments;

import java.math.BigDecimal;
import java.time.Instant;

public record LedgerEntry(
        String entryId,
        String sourceAccountId,
        String destinationAccountId,
        BigDecimal amount,
        String currency,
        Instant occurredAt) {
}
