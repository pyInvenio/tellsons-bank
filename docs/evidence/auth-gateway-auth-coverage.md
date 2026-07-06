# Evidence: auth-gateway auth-path coverage

**Path family:** auth
**Service:** `services/auth-gateway`
**Trigger:** Change event on [PR #18](https://github.com/pyInvenio/tellsons-bank/pull/18)
(`services/auth-gateway/src/AuthRouter.ts` gained an optional `x-tellsons-client-id`
enforcement branch with no accompanying tests).
**Scope:** Tests, fixtures, mocks, and evidence only. No production code changed.

## Commands run

```bash
cd services/auth-gateway
npm install
npm test          # jest --coverage
npm run typecheck # tsc --noEmit
# repo-level ratchet
python3 .github/scripts/coverage_gate.py --paths auth --min 80
```

## Coverage before / after (targeted files, branch %)

Source: `services/auth-gateway/coverage/coverage-summary.json`.

| File | Branch before | Branch after |
| --- | --- | --- |
| `src/AuthRouter.ts` | 0.00% | 100% |
| `src/SessionTokenVerifier.ts` | 0.00% | 100% |
| `src/LockoutCounter.ts` | 66.66% | 100% |
| `src/Clock.ts` | (unused) | 100% |
| `src/index.ts` | 0.00% | 100% |
| **Service total (branches)** | **7.14%** | **100%** |

Auth ratchet target is 80% branch (`tellsons.service.json`). Result:
`below_threshold=false` for the auth path.

## Edge cases covered

`SessionTokenVerifier` (trust-boundary input validation):
- empty token; tokens with fewer/more than three segments (malformed shape)
- invalid base64url header (parse error propagates)
- `alg: none` rejected before signature verification
- signature mismatch (token signed by a different synthetic key)
- missing `sub` claim; missing / non-numeric `exp` claim
- expiry via the injected-clock skew branch (default 30s and custom 0s)
- acceptance exactly inside a custom skew window
- default system clock path (no injected clock)
- scope as array, as space-delimited string, and absent (empty list)

`AuthRouter` (`GET /auth/session`):
- verifier success shape; `clientId` omitted when enforcement is off
- mixed-case `Bearer` prefix + surrounding whitespace stripped
- missing `Authorization` header forwards an empty token
- verifier error maps to `401 invalid_session` with no internal-detail leak
- `requireClientId`: missing id and whitespace-only id -> `400 client_id_required`
  (short-circuits before the verifier)
- `requireClientId`: valid id echoed for downstream audit correlation
- client id echoed even when enforcement is disabled
- default-options branch of `buildAuthRouter`

`LockoutCounter`:
- strictly-greater-than lockout, custom thresholds (1 and 0), per-user isolation,
  reset, blank user id
- documented off-by-one boundary at the default threshold
  (see `docs/findings/auth-gateway-lockout-off-by-one.md`)

## Synthetic fixtures used

- `tests/fixtures/synthetic-auth.ts`: demo identifiers only
  (`cust_demo_0001`, `client_demo_web_0001`), RFC 5737 documentation IP
  `203.0.113.7`, `example.test` email domain.
- Synthetic RS256 key pairs generated per test run in-memory
  (`tests/helpers/tokens.ts`); no keys or tokens are stored on disk.
- Router tests use a narrow in-memory fake verifier; no real JWT signing.
- Lockout tests use `cust_test_*` identifiers.

## Flaky-risk notes

- No sleeps or wall-clock waits. Token expiry is exercised through the injected
  `nowSeconds` clock. `jsonwebtoken` still validates `exp` against the real
  clock, so tokens are signed with far-future / near-now `exp` values that stay
  valid across a normal CI run; the verifier's own skew branch is what the
  assertions target.
- Router tests bind to an ephemeral port (`listen(0)`) and close the server in
  `afterEach`, avoiding port collisions.
- `Clock` test brackets the reading between two real-clock samples rather than
  asserting an exact value.
- No external network calls; downstream verification is faked in-process.

## Finding

`LockoutCounter` has an off-by-one at the configured threshold. Reported for
human review with reproduction steps in
`docs/findings/auth-gateway-lockout-off-by-one.md`. Production code was left
unchanged per the compliance-tests no-production-code-change rule.

## Reviewer checklist

- [x] Tests cover error handling and data validation for the auth path.
- [x] Fixtures are synthetic and contain no realistic customer data.
- [x] No real network calls are made.
- [x] No production files changed.
- [x] Coverage report / CI evidence is linked.
