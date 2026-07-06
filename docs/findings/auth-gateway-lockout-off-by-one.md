# Finding: LockoutCounter off-by-one at the configured threshold

**Service:** `services/auth-gateway`
**Path family:** auth
**Component:** `src/LockoutCounter.ts`
**Status:** Reported for human review. No production code changed.
**Severity:** Medium (weakens brute-force lockout by one attempt).

## Summary

`LockoutCounter.recordFailure` signals a lockout only when the running failure
count is **strictly greater than** the threshold:

```ts
recordFailure(userId: string): boolean {
  const next = (this.failures.get(userId) ?? 0) + 1;
  this.failures.set(userId, next);
  return next > this.threshold; // <-- off-by-one
}
```

With the default `threshold = 5`, the account is not locked on the fifth failed
attempt; lockout is signalled only on the sixth. Callers that expect "lock on
the Nth failure" get "lock on the (N+1)th failure". This matches the note in
`services/auth-gateway/docs/lockout-policy.md`.

## Reproduction

Deterministic unit reproduction (synthetic IDs, no network, no sleeps):

```
cd services/auth-gateway
npm test -- LockoutCounter
```

The test `does not lock on the fifth failure with the default threshold`
in `tests/LockoutCounter.test.ts` records five failures for `cust_test_0002`
and asserts the current (unlocked) behavior, then asserts the sixth failure
locks. This documents the boundary explicitly for reviewer visibility.

Minimal manual repro:

```ts
const counter = new LockoutCounter(); // threshold = 5
[1,2,3,4,5].forEach(() => counter.recordFailure('cust_test_0002'));
// returns false on the 5th call; true only on the 6th
```

## Impact

An attacker gets one extra password attempt per lockout window than the policy
intends. Whether this is a defect depends on the intended contract of
`threshold` ("max allowed failures" vs. "failures before lock").

## Human decision needed

Confirm the intended semantics of `threshold`:

- If `threshold` is "lock on the Nth failure", change the comparison to
  `next >= this.threshold` (production-code change, out of scope for this
  test-coverage task).
- If `threshold` is "allowed failures before locking", the current behavior is
  correct and only the documentation/tests need to encode it.

Per the compliance-tests workflow, remediation is intentionally **not** applied
here. The current behavior is captured by tests so it cannot regress silently.
