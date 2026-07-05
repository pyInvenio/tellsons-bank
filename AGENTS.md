# Agent Instructions

This is a synthetic public repository. Never introduce real customer data, real
secrets, real bank identifiers, or external network calls in tests.

## Testing rule

Compliance-path tasks may add or modify tests, fixtures, mocks, CI wiring, and coverage
scripts. They must not change production code unless the prompt explicitly asks for a bug
fix after coverage remediation.

## Synthetic data rule

Use only fixture values under `docs/fixtures` or values that are obviously fake, such as
`000-00-0000`, `4111111111111111`, or `acct_test_0001`.
