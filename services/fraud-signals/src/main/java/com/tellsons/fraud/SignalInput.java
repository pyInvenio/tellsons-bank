package com.tellsons.fraud;

import java.math.BigDecimal;

public record SignalInput(
        String customerId,
        BigDecimal amount,
        String currency,
        int velocityCount,
        boolean newDevice,
        boolean crossBorder) {
}
