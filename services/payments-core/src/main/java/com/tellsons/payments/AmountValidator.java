package com.tellsons.payments;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.Currency;
import java.util.Objects;

public class AmountValidator {
    private static final BigDecimal MAX_TRANSFER = new BigDecimal("250000.00");

    public BigDecimal validate(String rawAmount, String currencyCode) {
        Objects.requireNonNull(rawAmount, "rawAmount");
        Currency currency = Currency.getInstance(currencyCode);
        BigDecimal amount = new BigDecimal(rawAmount).setScale(2, RoundingMode.HALF_EVEN);

        if (amount.signum() < 0) {
            throw new InvalidTransferException("negative transfer amount");
        }
        if (amount.compareTo(MAX_TRANSFER) > 0) {
            throw new InvalidTransferException("transfer exceeds limit");
        }
        if (currency.getDefaultFractionDigits() > 2) {
            throw new InvalidTransferException("unsupported currency scale");
        }
        return amount;
    }
}
