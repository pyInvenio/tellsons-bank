# Idempotency

`TransferService` requires every transfer request to carry an idempotency key.
The key is passed to `IdempotencyStore.getOrCreate`, which returns a previous
receipt when the same key has already been seen.

The current store is deliberately simple. It performs a `get`, invokes the
supplier, then performs a `put`. That is adequate for single-threaded smoke
tests, but it is not atomic under concurrent requests. A compliance-path test
suite should prove this race with a controlled supplier rather than sleeping or
depending on wall-clock timing.

Coverage priorities:

- missing, blank, and duplicate idempotency keys
- supplier not called when a receipt already exists
- concurrent calls with the same key producing multiple ledger posts
- supplier exception behavior and whether failed attempts are cached
- stable receipt reuse across retried client requests
