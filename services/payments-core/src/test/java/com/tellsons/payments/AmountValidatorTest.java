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
    void rejectsNegativeAmount() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("-1.00", "USD"));
        assertEquals("negative transfer amount", ex.getMessage());
    }

    @Test
    void rejectsNegativeFractionalAmount() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("-0.01", "USD"));
        assertEquals("negative transfer amount", ex.getMessage());
    }

    @Test
    void rejectsAmountExceedingLimit() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("250000.01", "USD"));
        assertEquals("transfer exceeds limit", ex.getMessage());
    }

    @Test
    void acceptsExactMaxTransfer() {
        assertEquals(new BigDecimal("250000.00"), validator.validate("250000.00", "USD"));
    }

    @Test
    void rejectsUnsupportedCurrencyScale() {
        // BHD (Bahraini Dinar) has 3 default fraction digits
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("10.00", "BHD"));
        assertEquals("unsupported currency scale", ex.getMessage());
    }

    @Test
    void throwsOnNullRawAmount() {
        assertThrows(NullPointerException.class,
                () -> validator.validate(null, "USD"));
    }

    @Test
    void throwsOnNullCurrencyCode() {
        assertThrows(NullPointerException.class,
                () -> validator.validate("10.00", null));
    }

    @Test
    void throwsOnInvalidCurrencyCode() {
        assertThrows(IllegalArgumentException.class,
                () -> validator.validate("10.00", "INVALID"));
    }

    @Test
    void throwsOnMalformedAmountString() {
        assertThrows(NumberFormatException.class,
                () -> validator.validate("not_a_number", "USD"));
    }

    @Test
    void acceptsZeroAmount() {
        assertEquals(new BigDecimal("0.00"), validator.validate("0", "USD"));
    }

    @Test
    void roundsHalfEvenBankersRounding() {
        // "42.005" rounds to "42.00" with HALF_EVEN (bankers rounding)
        assertEquals(new BigDecimal("42.00"), validator.validate("42.005", "USD"));
    }

    @Test
    void roundsHalfEvenUp() {
        // "42.015" rounds to "42.02" with HALF_EVEN
        assertEquals(new BigDecimal("42.02"), validator.validate("42.015", "USD"));
    }

    @Test
    void setsScaleToTwoDecimalPlaces() {
        assertEquals(new BigDecimal("99.99"), validator.validate("99.99", "USD"));
    }

    @Test
    void acceptsAmountJustBelowLimit() {
        assertEquals(new BigDecimal("249999.99"), validator.validate("249999.99", "USD"));
    }

    @Test
    void acceptsAmountWithExtraScale() {
        assertEquals(new BigDecimal("100.00"), validator.validate("100.000", "USD"));
    }

    @Test
    void acceptsGbpCurrency() {
        assertEquals(new BigDecimal("50.00"), validator.validate("50", "GBP"));
    }

    @Test
    void acceptsEurCurrency() {
        assertEquals(new BigDecimal("75.50"), validator.validate("75.50", "EUR"));
    }

    @Test
    void rejectsLargeNegativeAmount() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("-999999.99", "USD"));
        assertEquals("negative transfer amount", ex.getMessage());
    }

    @Test
    void rejectsLargeOverflowAmount() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> validator.validate("9999999.99", "USD"));
        assertEquals("transfer exceeds limit", ex.getMessage());
    }
}
