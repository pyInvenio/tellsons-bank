# Transfer Wire Format

The transfer boundary is represented by `TransferRequest`, a simple record with
`sourceAccountId`, `destinationAccountId`, `amount`, `currency`, and
`idempotencyKey`. Amount is intentionally a string at the boundary so callers can
send the exact decimal representation they received from forms or upstream
systems.

`TransferReceipt` returns the ledger entry ID, final status, and posted
timestamp. Tests should verify the service response through this public contract
instead of depending on internal UUID format or repository implementation
details.

Coverage priorities:

- null request rejection
- missing source or destination account IDs through repository lookups
- malformed amount strings from the boundary
- receipt status for successful posts
- deterministic timestamps through injected `Clock`
