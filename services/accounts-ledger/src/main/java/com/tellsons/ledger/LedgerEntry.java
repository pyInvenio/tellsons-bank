package com.tellsons.ledger;

import java.math.BigDecimal;
import java.time.Instant;

public record LedgerEntry(
        String entryId,
        String accountId,
        BigDecimal debit,
        BigDecimal credit,
        String currency,
        Instant postedAt,
        String sourceSystem) {
}
