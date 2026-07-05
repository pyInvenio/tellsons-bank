---
name: compliance-tests
description: Use when adding or reviewing Tellson's Bank compliance-path tests for transaction, auth, PII, or audit services. Applies the no-production-code-change rule, synthetic fixture policy, and targeted coverage evidence requirements.
---

# Tellson's Bank Compliance Tests

Use this workflow for `!compliance-tests` tasks.

## Rules

- Change tests, fixtures, mocks, CI config, or evidence docs only.
- Do not change production code. If product behavior appears defective, write a finding and stop.
- Use synthetic IDs only: `cust_test_*`, `cust_demo_*`, `acct_test_*`, `acct_demo_*`, `txn_test_*`, `txn_demo_*`.
- Do not make real network calls.
- Prefer injected clocks or fixed timestamps; do not use sleeps.
- Report targeted branch coverage for the classes/modules touched. Do not claim repo-level remediation.

## Path Targets

- Transaction: `payments-core`, `accounts-ledger`, `fraud-signals`, `risk-scoring`, `notification-dispatch`
- Auth: `auth-gateway`, `loan-origination`
- PII: `pii-vault`, `statements-api`, `customer-profile`
- Audit: `audit-logger`, `dispute-resolution`

## Evidence

Every PR should include:

- commands run
- coverage before/after for targeted files
- edge cases covered
- synthetic fixtures used
- flaky-risk notes
- reviewer checklist
