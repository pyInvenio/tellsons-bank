# Lockout Policy

`LockoutCounter` tracks failures in memory by user ID. The default threshold is
five failures. `recordFailure` returns whether the account should be locked, and
`reset` clears the counter after successful authentication or manual unlock.

The implementation currently returns `true` only when failures are greater than
the threshold. That means the fifth failure is not locked when the threshold is
five. Tests should document this boundary explicitly so the product decision is
visible during review.

Coverage priorities:

- first through fifth failures with the default threshold
- custom thresholds such as one and zero
- reset after previous failures
- separate counters for separate users
- blank user IDs if callers do not validate upstream
