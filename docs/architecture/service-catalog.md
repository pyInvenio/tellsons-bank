# Service Catalog

Tellson's Bank is intentionally shaped like a small but realistic bank platform:
12 microservices, three implementation languages, uneven testing maturity, and
several cross-service compliance paths.

| Service | Language | Path family | Test infrastructure | Coverage role |
| --- | --- | --- | --- | --- |
| `payments-core` | Java | Transaction | JUnit, Mockito, JaCoCo | Primary transaction remediation target |
| `accounts-ledger` | Java | Transaction | JUnit, JaCoCo | Ledger support path |
| `fraud-signals` | Java | Transaction | JUnit, JaCoCo | Risk-adjacent transaction branch coverage |
| `auth-gateway` | TypeScript | Authentication | Jest coverage | Primary auth remediation target |
| `loan-origination` | TypeScript | Authentication | Jest coverage | Auth-dependent downstream service |
| `pii-vault` | Java | PII | JUnit, JaCoCo | PII masking/tokenization target |
| `statements-api` | TypeScript | PII | Jest coverage | PII leakage through generated statements |
| `customer-profile` | Python | PII | `unittest` CI smoke tests | Support service with unicode input handling |
| `audit-logger` | Python | Audit | None | Bootstrap target |
| `dispute-resolution` | Python | Audit | None | Secondary no-infra Python service |
| `risk-scoring` | Python | Transaction | `unittest` CI smoke tests | Cross-path scoring support |
| `notification-dispatch` | TypeScript | Transaction support | Jest coverage | Retry/backoff support target |

## Dependency Story

- `payments-core` emits ledger entries and audit-worthy transfer outcomes.
- `accounts-ledger` reconciles transaction entries from `payments-core`.
- `fraud-signals` and `risk-scoring` classify high-risk transfers.
- `notification-dispatch` sends transfer and dispute notifications with retry/backoff logic.
- `auth-gateway` verifies session tokens used by loan and statement workflows.
- `pii-vault`, `customer-profile`, and `statements-api` form the PII handling
  path from profile input to redacted statement output.
- `audit-logger` records immutable evidence for transfer, auth, PII, and
  dispute events.
- `dispute-resolution` consumes transaction identifiers and audit reasons, but
  intentionally has no test harness yet.

## Why This Looks Like A Real Coverage Problem

The repo is not just missing tests. It has inconsistent test patterns:

- Java services use JUnit and JaCoCo, but only a few happy-path tests exist.
- TypeScript services use Jest, but coverage is concentrated in trivial branches.
- Python support services use basic `unittest`, while audit-critical Python code
  has no pytest, coverage config, or CI lane.
- CI covers several services, but the ratchet separately watches named
  compliance paths because repo-level coverage can hide low branch coverage in
  critical modules.
