package com.tellsons.fraud;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class FraudSignalEvaluator {
    public SignalDecision evaluate(SignalInput input) {
        if (input.customerId() == null || input.customerId().isBlank()) {
            throw new IllegalArgumentException("customer id required");
        }
        if (input.amount().signum() < 0) {
            throw new IllegalArgumentException("amount cannot be negative");
        }

        int score = 0;
        List<String> reasons = new ArrayList<>();
        if (input.amount().compareTo(new BigDecimal("5000.00")) > 0) {
            score += 35;
            reasons.add("large_amount");
        }
        if (input.velocityCount() > 4) {
            score += 30;
            reasons.add("high_velocity");
        }
        if (input.newDevice()) {
            score += 20;
            reasons.add("new_device");
        }
        if (input.crossBorder()) {
            score += 15;
            reasons.add("cross_border");
        }

        String disposition = score >= 70 ? "HOLD" : score >= 40 ? "REVIEW" : "ALLOW";
        return new SignalDecision(disposition, score, reasons);
    }
}
