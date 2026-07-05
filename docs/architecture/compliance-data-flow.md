# Compliance Data Flow

This document exists so repo-comprehension tools can connect the four OCC examination
paths to concrete code instead of only reading service names.

## Transaction Processing

1. `payments-core/TransferService` validates transfer requests and posts ledger
   entries through a `LedgerClient`.
2. `payments-core/AmountValidator` normalizes amounts and currency.
3. `accounts-ledger/LedgerReconciler` compares debits and credits by account.
4. `fraud-signals/FraudSignalEvaluator` assigns hold/review/allow decisions for
   high-risk transfer patterns.
5. `risk-scoring/RiskScorecard` combines fraud and profile signals into a final
   action.

Priority edge cases:

- negative and oversized amounts
- scale and rounding boundaries
- mixed currency ledger entries
- duplicate idempotency keys
- missing accounts and downstream exceptions

## Authentication

1. `auth-gateway/SessionTokenVerifier` parses and verifies JWT claims.
2. `auth-gateway/LockoutCounter` tracks failed login attempts.
3. `loan-origination/ApplicationPolicy` depends on an authenticated session
   before approving synthetic loan applications.

Priority edge cases:

- malformed JWTs
- unsigned-token headers
- expired tokens and clock skew
- missing subject or expiration claims
- off-by-one lockout thresholds

## PII Handling

1. `customer-profile/ProfileNormalizer` normalizes display names and email
   domains from synthetic profile records.
2. `pii-vault/MaskingService` masks SSNs, account identifiers, and display names.
3. `pii-vault/TokenizationService` creates deterministic synthetic tokens.
4. `statements-api/StatementAssembler` rejects unredacted statement lines.

Priority edge cases:

- unicode names
- short account numbers
- oversized SSNs or account identifiers
- empty and null inputs
- statement lines incorrectly marked `PUBLIC`

## Audit Logging

1. `audit-logger/LogChain` builds tamper-evident hash chains.
2. `audit-logger/Redactor` redacts SSNs and account IDs before immutable writes.
3. `audit-logger/FileAuditSink` writes formatted records.
4. `dispute-resolution/DisputeWorkflow` produces audit reasons but currently has
   no tests.

Priority edge cases:

- missing sequence numbers
- changed previous hashes
- tampered messages
- PII leakage into immutable lines
- sink failures and formatter boundaries
