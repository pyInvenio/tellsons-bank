# Finding: LockoutCounter off-by-one (auth path)

- Service: `auth-gateway`
- Component: `src/LockoutCounter.ts`
- Compliance path: auth
- Status: OPEN — awaiting human decision (production code intentionally unchanged)

## What was observed

`LockoutCounter.recordFailure` returns the lockout decision as:

```ts
return next > this.threshold;
```

With `threshold = N`, the counter reports "locked out" only on the `(N+1)`th
failed attempt, not the `N`th. For the default `threshold = 5`, lockout trips on
the 6th failure. The source already flags this with a `// Seeded off-by-one target.`
comment.

## Why it matters

The auth compliance path asks whether "sessions/accounts lock after N failed
attempts." If the intended policy is "lock out on the Nth failure," the current
`>` comparison permits one extra credential-guessing attempt per window than the
policy allows. Whether this is a defect depends on the intended semantics of
`threshold` (max allowed failures vs. attempt count that triggers lockout), which
is ambiguous from the code alone.

## How it was reproduced

Synthetic unit tests in `tests/LockoutCounter.test.ts` document the observed
behavior without asserting a "correct" value:

- `returns false at exactly the threshold (observed off-by-one)` — the Nth
  failure returns `false`.
- `locks out only after the threshold is exceeded` — the (N+1)th failure returns
  `true`.

These tests assert the current implementation so CI stays green; they do not
encode a fix.

## Human decision needed

Confirm the intended lockout policy:

1. If lockout should occur **on** the Nth failure, change the comparison to
   `next >= this.threshold` and update the affected tests. (Production-code change
   — out of scope for this compliance-test pass.)
2. If the current `> threshold` behavior is intentional, keep the code and adjust
   the documented policy/tests accordingly.

No production code was changed in this PR.
