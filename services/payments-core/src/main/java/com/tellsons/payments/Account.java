package com.tellsons.payments;

import java.math.BigDecimal;

public record Account(String accountId, BigDecimal availableBalance, String currency) {
}
