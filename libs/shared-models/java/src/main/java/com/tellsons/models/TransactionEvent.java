package com.tellsons.models;

import java.time.Instant;
import java.util.Map;

public record TransactionEvent(
        String eventId,
        String accountId,
        String amount,
        String currency,
        Instant occurredAt,
        Map<String, String> metadata) {
}
