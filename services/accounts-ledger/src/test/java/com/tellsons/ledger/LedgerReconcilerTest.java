package com.tellsons.ledger;

import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

class LedgerReconcilerTest {
    @Test
    void acceptsBalancedSyntheticLedger() {
        LedgerEntry debit = new LedgerEntry("entry_test_1", "acct_test_source",
                new BigDecimal("10.00"), BigDecimal.ZERO, "USD", Instant.EPOCH, "payments-core");
        LedgerEntry credit = new LedgerEntry("entry_test_2", "acct_test_source",
                BigDecimal.ZERO, new BigDecimal("10.00"), "USD", Instant.EPOCH, "payments-core");

        assertTrue(new LedgerReconciler().reconcile(List.of(debit, credit)).isEmpty());
    }
}
