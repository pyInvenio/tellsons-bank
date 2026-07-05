package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class AmountValidatorTest {
    private final AmountValidator validator = new AmountValidator();

    @Test
    void acceptsWholeDollarAmount() {
        assertEquals(new BigDecimal("42.00"), validator.validate("42", "USD"));
    }
}
