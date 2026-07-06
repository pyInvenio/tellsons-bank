package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class AmountValidatorTest {
    private final AmountValidator validator = new AmountValidator();

    @Test
    void acceptsWholeDollarAmount() {
        assertEquals(new BigDecimal("42.00"), validator.validate("42", "USD"));
    }

    @Test
    void rejectsNullAmount() {
        assertThrows(NullPointerException.class, () -> validator.validate(null, "USD"));
    }

    @Test
    void rejectsUnknownCurrencyCode() {
        assertThrows(IllegalArgumentException.class, () -> validator.validate("10", "ZZZ"));
    }

    @Test
    void rejectsNegativeAmount() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class, () -> validator.validate("-1.00", "USD"));

        assertEquals("negative transfer amount", exception.getMessage());
    }

    @Test
    void acceptsZeroAmount() {
        assertEquals(new BigDecimal("0.00"), validator.validate("0", "USD"));
    }

    @Test
    void acceptsMaxTransferBoundary() {
        assertEquals(new BigDecimal("250000.00"), validator.validate("250000.00", "USD"));
    }

    @Test
    void rejectsAboveMaxTransfer() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class, () -> validator.validate("250000.01", "USD"));

        assertEquals("transfer exceeds limit", exception.getMessage());
    }

    @Test
    void rejectsUnsupportedCurrencyScale() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class, () -> validator.validate("10", "BHD"));

        assertEquals("unsupported currency scale", exception.getMessage());
    }

    @Test
    void roundsHalfEven() {
        assertEquals(new BigDecimal("1.00"), validator.validate("1.005", "USD"));
        assertEquals(new BigDecimal("1.02"), validator.validate("1.015", "USD"));
    }
}
