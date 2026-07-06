package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import org.mockito.ArgumentCaptor;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class TransferServiceTest {
    private static final Instant FIXED_INSTANT = Instant.parse("2026-01-01T00:00:00Z");
    private static final Clock FIXED_CLOCK = Clock.fixed(FIXED_INSTANT, ZoneOffset.UTC);

    @Mock AccountRepository accounts;
    @Mock LedgerClient ledger;

    private TransferService service() {
        return new TransferService(new AmountValidator(), accounts, ledger, new IdempotencyStore(), FIXED_CLOCK);
    }

    private static TransferRequest request(String source, String destination, String amount, String currency, String key) {
        return new TransferRequest(source, destination, amount, currency, key);
    }

    @Test
    void postsHappyPathTransfer() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "USD")));

        TransferReceipt receipt = service().transfer(request(
                "acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_1"));

        assertEquals("POSTED", receipt.status());
        verify(ledger).post(any(LedgerEntry.class));
    }

    @Test
    void rejectsNullRequest() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class, () -> service().transfer(null));

        assertEquals("request required", exception.getMessage());
    }

    @Test
    void rejectsNullIdempotencyKey() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", null)));

        assertEquals("idempotency key required", exception.getMessage());
    }

    @Test
    void rejectsBlankIdempotencyKey() {
        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "  ")));

        assertEquals("idempotency key required", exception.getMessage());
    }

    @Test
    void rejectsMissingSourceAccount() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.empty());

        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_2")));

        assertEquals("source account not found", exception.getMessage());
    }

    @Test
    void rejectsMissingDestinationAccount() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.empty());

        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_3")));

        assertEquals("destination account not found", exception.getMessage());
    }

    @Test
    void rejectsCurrencyMismatch() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "EUR")));

        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_4")));

        assertEquals("currency mismatch", exception.getMessage());
    }

    @Test
    void rejectsInsufficientFunds() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("9.99"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "USD")));

        InvalidTransferException exception = assertThrows(
                InvalidTransferException.class,
                () -> service().transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_5")));

        assertEquals("insufficient funds", exception.getMessage());
    }

    @Test
    void acceptsTransferAtExactBalance() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("10.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "USD")));

        TransferReceipt receipt = service().transfer(request(
                "acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_6"));

        assertEquals("POSTED", receipt.status());
    }

    @Test
    void returnsCachedReceiptOnIdempotencyCollision() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "USD")));

        TransferService service = service();
        TransferRequest transferRequest = request(
                "acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_collision");

        TransferReceipt first = service.transfer(transferRequest);
        TransferReceipt second = service.transfer(transferRequest);

        assertSame(first, second);
        verify(ledger, times(1)).post(any(LedgerEntry.class));
    }

    @Test
    void postedEntryUsesInjectedClock() {
        when(accounts.find("acct_demo_source")).thenReturn(Optional.of(
                new Account("acct_demo_source", new BigDecimal("100.00"), "USD")));
        when(accounts.find("acct_demo_dest")).thenReturn(Optional.of(
                new Account("acct_demo_dest", new BigDecimal("5.00"), "USD")));

        TransferService service = service();
        ArgumentCaptor<LedgerEntry> captor = ArgumentCaptor.forClass(LedgerEntry.class);

        service.transfer(request("acct_demo_source", "acct_demo_dest", "10.00", "USD", "txn_demo_idem_7"));

        verify(ledger).post(captor.capture());
        assertEquals(FIXED_INSTANT, captor.getValue().occurredAt());
    }
}
