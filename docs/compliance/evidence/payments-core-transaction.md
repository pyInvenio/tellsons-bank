# Evidence: payments-core (transaction path) branch coverage

Scope: add compliance-path tests for the transaction path in `services/payments-core`.
Test-only change. No production code was modified. Synthetic fixtures only.

## Commands run

```bash
# Baseline and after (payments-core targeted)
gradle :services:payments-core:test :services:payments-core:jacocoTestReport

# Full Java service suite (as CI runs it)
gradle :services:payments-core:test :services:pii-vault:test \
       :services:accounts-ledger:test :services:fraud-signals:test
```

JaCoCo XML: `services/payments-core/build/reports/jacoco/test/jacocoTestReport.xml`
JaCoCo HTML: `services/payments-core/build/reports/jacoco/test/html/index.html`

## Branch coverage before/after (targeted classes)

| Scope / Class | Before (missed/covered) | Before % | After (missed/covered) | After % |
|---|---:|---:|---:|---:|
| payments-core report-level | 11 / 9 | 45.00% | 0 / 20 | 100.00% |
| `AmountValidator` | 3 / 3 | 50.00% | 0 / 6 | 100.00% |
| `TransferService` | 5 / 5 | 50.00% | 0 / 10 | 100.00% |
| `IdempotencyStore` | 1 / 1 | 50.00% | 0 / 2 | 100.00% |
| `GlobalTransferExceptionHandler` | 2 / 0 | 0.00% | 0 / 2 | 100.00% |

## Edge cases covered

- **AmountValidator**: null amount (NPE), unknown currency code, negative amount,
  zero amount (non-negative boundary), max-transfer boundary (`250000.00` allowed vs
  `250000.01` rejected), unsupported currency scale (`BHD`, 3 fraction digits),
  HALF_EVEN rounding (`1.005 -> 1.00`, `1.015 -> 1.02`).
- **TransferService**: null request, null idempotency key, blank idempotency key,
  missing source account, missing destination account, currency mismatch,
  insufficient funds, exact-balance boundary (`compareTo == 0` accepted),
  idempotency collision (cached receipt returned, ledger posted once),
  injected-clock timestamp on posted ledger entry.
- **GlobalTransferExceptionHandler**: `InvalidTransferException` mapping and generic
  exception flattening.

## Synthetic fixtures used

Inline synthetic accounts/requests with obviously-fake identifiers:
`acct_demo_source`, `acct_demo_dest`, `txn_demo_idem_*`. No real account numbers,
no PII, no network calls. `TransferService` tests inject `Clock.fixed(...)`; no sleeps.

## Findings (recorded, NOT remediated — awaiting human review)

Per the no-production-code-change rule, the following seeded weaknesses were
observed while writing tests. They are documented here for human review; no
production code was changed and no test asserts the (arguably incorrect) safe
behavior.

1. **`IdempotencyStore.getOrCreate` is not atomic (duplicate-post risk).**
   It does a `get` then a separate `put` around `supplier.get()`. Under concurrent
   requests with the same key, two threads can both observe `existing == null`,
   both invoke the supplier, and both post to the ledger — breaking the
   idempotency guarantee for transaction replays.
   - Reproduction sketch: two threads call `transfer(...)` with the same
     `idempotencyKey` before either completes; `ledger.post` runs twice.
   - Not covered by an automated test here because a threaded race test would be
     flaky/wall-clock dependent (see flaky-risk notes). The single-threaded
     collision test only proves the cache short-circuit on the second call.
   - Suggested fix (needs human decision): use `computeIfAbsent` / atomic
     compute so the supplier runs at most once per key.

2. **`GlobalTransferExceptionHandler` flattens all non-`InvalidTransferException`
   errors into `TEMPORARY_FAILURE` with a fixed message.** The original exception
   type/message is discarded, which reduces auditability/observability of the
   failure signal. Tests assert the current behavior; whether to preserve more
   detail is a human decision.

## Flaky-risk notes

- No sleeps, no wall-clock reads: `TransferService` uses `Clock.fixed(...)`.
- No real network/downstreams: `AccountRepository` and `LedgerClient` are Mockito mocks.
- The idempotency-collision test is single-threaded and deterministic; it does
  **not** attempt to reproduce the concurrency race in finding (1) to avoid
  introducing a flaky/timing-dependent test.
- Currency-scale test relies on JDK `Currency` fraction digits for `BHD` (3),
  which is stable across JDK versions.

## Reviewer checklist

- [x] Tests cover error handling and data validation for the transaction path.
- [x] Fixtures are synthetic and contain no realistic customer data.
- [x] No real network calls are made.
- [x] No production files changed.
- [x] Coverage report / CI evidence is linked (JaCoCo paths above).
