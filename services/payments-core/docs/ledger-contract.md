# Ledger Contract

`TransferService` posts a `LedgerEntry` after amount validation, account lookup,
currency comparison, and balance checks succeed. The ledger payload contains a
generated entry ID, source account ID, destination account ID, normalized amount,
currency, and `occurredAt` from the injected `Clock`.

Tests should mock `LedgerClient` and assert the posted entry, not call an
external ledger. The service should not post when validation fails, accounts are
missing, currencies differ, or funds are insufficient.

Coverage priorities:

- ledger post contains the normalized amount, not the raw amount string
- fixed-clock timestamp is propagated to the entry and receipt
- no ledger post occurs for invalid requests
- downstream `LedgerClient.post` exceptions are surfaced consistently
- source and destination account IDs are not swapped
