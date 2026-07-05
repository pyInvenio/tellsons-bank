package com.tellsons.payments;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class TransferServiceTest {
    private static final Clock FIXED_CLOCK =
            Clock.fixed(Instant.parse("2026-01-01T00:00:00Z"), ZoneOffset.UTC);
    private static final Account SOURCE_ACCOUNT =
            new Account("acct_test_source", new BigDecimal("100.00"), "USD");
    private static final Account DEST_ACCOUNT =
            new Account("acct_test_dest", new BigDecimal("5.00"), "USD");

    @Mock AccountRepository accounts;
    @Mock LedgerClient ledger;

    private IdempotencyStore idempotencyStore;
    private TransferService service;

    @BeforeEach
    void setUp() {
        idempotencyStore = new IdempotencyStore();
        service = new TransferService(
                new AmountValidator(), accounts, ledger, idempotencyStore, FIXED_CLOCK);
    }

    @Test
    void postsHappyPathTransfer() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));

        TransferReceipt receipt = service.transfer(new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "idem-1"));

        assertEquals("POSTED", receipt.status());
        verify(ledger).post(any(LedgerEntry.class));
    }

    // --- null / blank request ---

    @Test
    void rejectsNullRequest() {
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(null));
        assertEquals("request required", ex.getMessage());
    }

    @Test
    void rejectsNullIdempotencyKey() {
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", null);
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("idempotency key required", ex.getMessage());
    }

    @Test
    void rejectsBlankIdempotencyKey() {
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "   ");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("idempotency key required", ex.getMessage());
    }

    @Test
    void rejectsEmptyIdempotencyKey() {
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("idempotency key required", ex.getMessage());
    }

    // --- account lookups ---

    @Test
    void rejectsWhenSourceAccountNotFound() {
        when(accounts.find("acct_test_missing")).thenReturn(Optional.empty());
        TransferRequest request = new TransferRequest(
                "acct_test_missing", "acct_test_dest", "10.00", "USD", "idem-src-missing");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("source account not found", ex.getMessage());
    }

    @Test
    void rejectsWhenDestinationAccountNotFound() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_missing")).thenReturn(Optional.empty());
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_missing", "10.00", "USD", "idem-dest-missing");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("destination account not found", ex.getMessage());
    }

    // --- currency mismatch ---

    @Test
    void rejectsCurrencyMismatch() {
        Account eurDest = new Account("acct_test_dest_eur", new BigDecimal("500.00"), "EUR");
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest_eur")).thenReturn(Optional.of(eurDest));

        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest_eur", "10.00", "USD", "idem-mismatch");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("currency mismatch", ex.getMessage());
        verify(ledger, never()).post(any());
    }

    // --- insufficient funds ---

    @Test
    void rejectsInsufficientFunds() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));

        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "100.01", "USD", "idem-nsf");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("insufficient funds", ex.getMessage());
        verify(ledger, never()).post(any());
    }

    @Test
    void acceptsTransferExactlyEqualToBalance() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));

        TransferReceipt receipt = service.transfer(new TransferRequest(
                "acct_test_source", "acct_test_dest", "100.00", "USD", "idem-exact"));
        assertEquals("POSTED", receipt.status());
        verify(ledger).post(any(LedgerEntry.class));
    }

    // --- downstream LedgerClient failure ---

    @Test
    void propagatesLedgerClientFailure() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));
        doThrow(new RuntimeException("ledger unavailable")).when(ledger).post(any());

        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "idem-ledger-fail");
        RuntimeException ex = assertThrows(RuntimeException.class,
                () -> service.transfer(request));
        assertEquals("ledger unavailable", ex.getMessage());
    }

    // --- idempotency-key reuse ---

    @Test
    void idempotencyKeyReturnsOriginalReceipt() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));

        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "10.00", "USD", "idem-dup");
        TransferReceipt first = service.transfer(request);
        TransferReceipt second = service.transfer(request);

        assertSame(first, second);
    }

    // --- AmountValidator failure propagation ---

    @Test
    void propagatesAmountValidatorNegativeAmount() {
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "-5.00", "USD", "idem-neg");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("negative transfer amount", ex.getMessage());
        verify(ledger, never()).post(any());
    }

    @Test
    void propagatesAmountValidatorOverflow() {
        TransferRequest request = new TransferRequest(
                "acct_test_source", "acct_test_dest", "999999.99", "USD", "idem-overflow");
        InvalidTransferException ex = assertThrows(InvalidTransferException.class,
                () -> service.transfer(request));
        assertEquals("transfer exceeds limit", ex.getMessage());
        verify(ledger, never()).post(any());
    }

    // --- receipt fields ---

    @Test
    void receiptContainsFixedTimestamp() {
        when(accounts.find("acct_test_source")).thenReturn(Optional.of(SOURCE_ACCOUNT));
        when(accounts.find("acct_test_dest")).thenReturn(Optional.of(DEST_ACCOUNT));

        TransferReceipt receipt = service.transfer(new TransferRequest(
                "acct_test_source", "acct_test_dest", "1.00", "USD", "idem-ts"));
        assertEquals(Instant.parse("2026-01-01T00:00:00Z"), receipt.postedAt());
    }
}
