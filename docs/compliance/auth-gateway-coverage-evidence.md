# auth-gateway — Auth Path Coverage Evidence

Compliance path: **auth**. Service: `services/auth-gateway` (TypeScript, Jest).
Synthetic-only. No production-code files were changed.

## Commands run

```bash
cd services/auth-gateway
npm install
npm test          # jest --coverage
npm run typecheck # tsc --noEmit
python3 ../../.github/scripts/coverage_gate.py --paths auth --min 80
```

## Branch coverage before / after (targeted modules)

| Module | Before | After |
| --- | --- | --- |
| `src/SessionTokenVerifier.ts` | 0.00% (0/13) | 100% (13/13) |
| `src/LockoutCounter.ts` | 66.66% (2/3) | 100% (3/3) |
| `src/AuthRouter.ts` | 0.00% (0/2) | 100% (2/2) |
| **auth-gateway total (Jest branches)** | **10.00% (2/20)** | **90.00% (18/20)** |

`src/index.ts` (process bootstrap, 2 branches) is intentionally left uncovered;
it wires env config to the app and is out of scope for the auth trust-boundary
logic. Total branch coverage (90%) clears the compliance ratchet minimum (80%),
and `coverage_gate.py --paths auth --min 80` reports `below_threshold=false`.

## Edge cases covered

- **SessionTokenVerifier**: empty token, <3 and >3 segments, invalid base64url/JSON
  header, `alg:none` rejection, signature mismatch (unrelated key), missing `sub`,
  missing `exp`, expiry at the skew boundary vs. one second past it, custom
  zero-skew clock, and scope normalization (array, space-delimited string, absent).
- **LockoutCounter**: default-threshold boundary (locks on the sixth failure —
  documented in `docs/lockout-policy.md`), threshold of one, threshold of zero,
  reset behavior, reset of an unknown user, per-user isolation, and blank user id.
- **AuthRouter**: valid bearer token, mixed-case bearer prefix with extra
  whitespace, missing `Authorization` header → 401, and verifier failure → 401
  with no internal error detail leaked in the response body.

## Synthetic fixtures used

- `devin-workspace/fixtures/synthetic/auth-gateway.json` — synthetic subjects
  (`cust_test_*`, `cust_demo_*`), scopes, `example.test` domain, and a
  `203.0.113.0/24` documentation IP.
- RSA keypairs are generated at test runtime (`crypto.generateKeyPairSync`); no
  real or stored keys/tokens are used.

## Flaky-risk notes

- JWT expiry tests use a far-future `exp` (real clock) so `jsonwebtoken`'s own
  expiry check always passes, while the custom skew logic is exercised solely via
  the injected `nowSeconds` clock — no sleeps or wall-clock dependence.
- `AuthRouter` tests bind an ephemeral loopback port (`127.0.0.1:0`) on an
  in-process Express app; there are no external/downstream network calls. The
  server is closed in `afterAll`.

## Finding (no code changed)

`LockoutCounter.recordFailure` returns `true` only when the failure count is
strictly greater than the threshold (`next > threshold`), so with the default
threshold of five the account is not locked until the **sixth** failure. This
matches `docs/lockout-policy.md`, which flags it as a boundary requiring a
product decision. Per the no-production-code-change rule this is recorded as a
finding for human review and documented via a characterization test rather than
"fixed".

## Reviewer checklist

- [x] Tests cover error handling and data validation for the auth path.
- [x] Fixtures are synthetic and contain no realistic customer data.
- [x] No real network calls are made (loopback in-process Express only).
- [x] No production files changed.
- [x] Coverage report / gate evidence is linked.
