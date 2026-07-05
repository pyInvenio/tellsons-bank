# Evidence: auth-gateway (auth path) coverage remediation

Compliance path: **auth**. Targeted classes: `SessionTokenVerifier`, `LockoutCounter`.
Task: add error-handling and data-validation tests; no production-code changes.

## Commands run

```bash
cd services/auth-gateway
npm test          # jest --coverage
npm run typecheck # tsc --noEmit
```

## Targeted branch coverage (before → after)

| Module | Branch before | Branch after |
| --- | --- | --- |
| `src/SessionTokenVerifier.ts` | 0% | 92.3% |
| `src/LockoutCounter.ts` | 66.66% | 100% |

Service-level (jest, all `src/**`): 10% → 75% branch. Repo-level remediation is
**not** claimed; support files (`AuthRouter.ts`, `index.ts`, `Clock.ts`) remain
uncovered and are outside the requested auth targets.

The one remaining uncovered branch in `SessionTokenVerifier` is the default
`nowSeconds` parameter (line 12), which is bypassed because tests inject a fixed
clock — the intended, deterministic behavior.

## Edge cases covered

`SessionTokenVerifier`:
- malformed token (empty, and non-three-segment)
- unsigned `alg=none` header rejected
- signature from an untrusted key rejected
- missing `sub` (subject required)
- missing/non-numeric `exp` (expiration required)
- expired beyond allowed clock skew (injected future clock)
- accepted at the clock-skew boundary (not yet expired)
- scope normalization: array, space-delimited string, and absent

`LockoutCounter`:
- failures below threshold do not lock out
- exactly-at-threshold returns false (observed off-by-one; see finding)
- exceeding threshold locks out
- reset clears count (nullish-coalescing branch re-exercised)
- default threshold (5) path
- users tracked independently

## Synthetic fixtures used

No stored token/key fixtures. RS256 key material is generated per test run via
Node `crypto.generateKeyPairSync` (synthetic, ephemeral). Synthetic identifiers
use `cust_test_*` / `user_test`. No real network calls; `jwt.verify` runs
in-process against the generated public key.

## Flaky-risk notes

- Token `exp` values are anchored to a single `Date.now()` read at module load
  because `jwt.verify` validates `exp` against the real wall clock and cannot be
  injected. No `sleep`s and no per-test wall-clock reads, so runs are stable.
- The verifier's own expiry check uses an injected clock pinned to the same
  reference, keeping the boundary/expired tests deterministic.
- RSA keygen adds a small per-run cost but no timing dependence.

## Finding raised

`docs/compliance/findings/auth-gateway-lockout-off-by-one.md` — LockoutCounter
off-by-one, left for human review. Production code intentionally unchanged.

## Reviewer checklist

- [ ] Tests cover error handling and data validation for the auth path.
- [ ] Fixtures are synthetic and contain no realistic customer data.
- [ ] No real network calls are made.
- [ ] No production files changed.
- [ ] Coverage report / CI evidence is linked.
