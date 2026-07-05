package com.tellsons.fraud;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class FraudSignalEvaluatorTest {
    @Test
    void allowsLowRiskSyntheticTransfer() {
        SignalDecision decision = new FraudSignalEvaluator().evaluate(
                new SignalInput("cust_test_001", new BigDecimal("42.00"), "USD", 1, false, false));

        assertEquals("ALLOW", decision.disposition());
    }
}
