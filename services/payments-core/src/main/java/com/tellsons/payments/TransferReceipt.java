package com.tellsons.payments;

import java.time.Instant;

public record TransferReceipt(String transferId, String status, Instant postedAt) {
}
