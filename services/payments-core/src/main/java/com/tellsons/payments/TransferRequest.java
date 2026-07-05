package com.tellsons.payments;

public record TransferRequest(
        String sourceAccountId,
        String destinationAccountId,
        String amount,
        String currency,
        String idempotencyKey) {
}
