package com.tellsons.payments;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.util.UUID;

public class TransferService {
    private final AmountValidator amountValidator;
    private final AccountRepository accountRepository;
    private final LedgerClient ledgerClient;
    private final IdempotencyStore idempotencyStore;
    private final Clock clock;

    public TransferService(
            AmountValidator amountValidator,
            AccountRepository accountRepository,
            LedgerClient ledgerClient,
            IdempotencyStore idempotencyStore,
            Clock clock) {
        this.amountValidator = amountValidator;
        this.accountRepository = accountRepository;
        this.ledgerClient = ledgerClient;
        this.idempotencyStore = idempotencyStore;
        this.clock = clock;
    }

    public TransferReceipt transfer(TransferRequest request) {
        if (request == null) {
            throw new InvalidTransferException("request required");
        }
        if (request.idempotencyKey() == null || request.idempotencyKey().isBlank()) {
            throw new InvalidTransferException("idempotency key required");
        }

        return idempotencyStore.getOrCreate(request.idempotencyKey(), () -> {
            BigDecimal amount = amountValidator.validate(request.amount(), request.currency());
            Account source = accountRepository.find(request.sourceAccountId())
                    .orElseThrow(() -> new InvalidTransferException("source account not found"));
            Account destination = accountRepository.find(request.destinationAccountId())
                    .orElseThrow(() -> new InvalidTransferException("destination account not found"));

            if (!source.currency().equals(destination.currency())) {
                throw new InvalidTransferException("currency mismatch");
            }
            if (source.availableBalance().compareTo(amount) < 0) {
                throw new InvalidTransferException("insufficient funds");
            }

            LedgerEntry entry = new LedgerEntry(
                    UUID.randomUUID().toString(),
                    source.accountId(),
                    destination.accountId(),
                    amount,
                    request.currency(),
                    Instant.now(clock));
            ledgerClient.post(entry);
            return new TransferReceipt(entry.entryId(), "POSTED", entry.occurredAt());
        });
    }
}
