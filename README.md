# Tellson's Bank

Tellson's Bank is a synthetic banking monorepo used to exercise service
ownership, compliance-path test coverage, and CI-driven quality gates. It
contains no real customer data, secrets, or production integrations.

The repo has 12 microservices across Java, TypeScript, and Python. Existing
coverage is deliberately uneven: support services have a few smoke tests, while
the four compliance-critical paths have sparse branch coverage and many
uncovered edge cases around validation and error handling.

## Compliance-Critical Paths

- Transaction processing: `payments-core`, `accounts-ledger`, `fraud-signals`, `notification-dispatch`
- Authentication: `auth-gateway`, `loan-origination`
- PII handling: `pii-vault`, `statements-api`, `customer-profile`
- Audit logging: `audit-logger`, `dispute-resolution`

`audit-logger` is deliberately under-instrumented: no pytest configuration, no
CI job, and no mocks. It is the primary bootstrap target for audit-path test
infrastructure.
`dispute-resolution` is another Python service with no test harness, but it is
lower priority than the immutable audit log path.

## Service Families

Java services:

- `payments-core`
- `pii-vault`
- `accounts-ledger`
- `fraud-signals`

TypeScript services:

- `auth-gateway`
- `notification-dispatch`
- `statements-api`
- `loan-origination`

Python services:

- `audit-logger`
- `customer-profile`
- `risk-scoring`
- `dispute-resolution`

## Operating Model

The repo is organized around a repeatable testing workflow:

1. Map service ownership and compliance paths.
2. Encode service-specific testing conventions.
3. Add focused tests for uncovered validation and error-handling branches.
4. Review evidence in PRs.
5. Preserve coverage reports through CI.
6. Ratchet compliance-path coverage when it falls below threshold.
