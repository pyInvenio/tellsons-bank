# Tellson's Bank Compliance-Critical Paths

Internal memo, synthetic copy.

Tellson's Bank currently tracks four examination-prep path families. The
coverage problem is not uniform across the estate: broad smoke coverage exists
in several support services, but the regulatory paths below have the weakest
branch coverage and the most consequential error-handling gaps.

| Family | Primary services | Supporting services | Primary risk | Current test posture |
| --- | --- | --- | --- | --- |
| Transaction processing | `services/payments-core` | `accounts-ledger`, `fraud-signals`, `risk-scoring`, `notification-dispatch` | Incorrect money movement, rounding, ledger imbalance, idempotency races, notification retry failures | JUnit/Jest and JaCoCo exist; targeted branch coverage is sparse |
| Authentication | `services/auth-gateway` | `loan-origination` | Expired or malformed tokens, unsigned JWTs, lockout mistakes, unauthenticated loan decisions | Jest exists; only shallow lockout tests |
| PII handling | `services/pii-vault` | `statements-api`, `customer-profile` | Bad redaction, unsafe tokenization, unicode and boundary mishandling, statement leakage | Java and TS tests exist; masking and statement edge cases are thin |
| Audit logging | `services/audit-logger` | `dispute-resolution` | Broken hash-chain integrity and PII leaking into immutable logs | Audit logger has no pytest, no coverage config, no CI job, and no mocks |

Examiner focus: error handling and data validation edge cases.
Generated tests must use synthetic fixtures only.

## Priority Targets

1. `payments-core/AmountValidator` and `payments-core/TransferService`
2. `auth-gateway/SessionTokenVerifier` and `auth-gateway/LockoutCounter`
3. `pii-vault/MaskingService` and `statements-api/StatementAssembler`
4. `audit-logger/LogChain` and `audit-logger/Redactor`

## Known Gaps

- Transaction processing lacks tests for negative amounts, null currency,
  rounding boundaries, mixed currency ledgers, and duplicate idempotency keys.
- Authentication lacks tests for expired tokens, malformed JWTs, missing claims,
  clock skew, unsigned-token rejection, and lockout threshold boundaries.
- PII handling lacks tests for unicode names, oversized values, short account
  numbers, statement-line classification, and token namespace validation.
- Audit logging lacks all test infrastructure. It needs pytest, coverage, mocks
  for sinks, CI wiring, hash-chain tamper tests, and redaction tests.
