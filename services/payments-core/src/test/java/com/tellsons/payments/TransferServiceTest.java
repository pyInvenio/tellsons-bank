package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class TransferServiceTest {
    @Mock AccountRepository accounts;
    @Mock LedgerClient ledger;

    @Test
    void postsHappyPathTransfer() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(
                new Account("acct_test_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(
                new Account("acct_test_dest", new BigDecimal("5.00"), "USD")));
        TransferService service = new TransferService(
                new AmountValidator(),
                accounts,
                ledger,
                new IdempotencyStore(),
                Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC));

        TransferReceipt receipt = service.transfer(new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "idem-1"));

        assertEquals("POSTED", receipt.status());
        verify(ledger).post(any(LedgerEntry.class));
    }
}
