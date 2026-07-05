# Retry Backoff

`RetryPolicy.nextDelay` returns exponential delays based on attempt number:
`baseDelayMs * 2^attempt`. It returns `null` when attempts are exhausted. The
`Dispatcher` currently uses the policy as a retry counter but does not sleep,
which keeps tests fast and deterministic.

The important behavior is how many times the client is called before returning
`sent` or `failed`. Tests should assert call counts and status values rather
than elapsed time.

Coverage priorities:

- first, middle, and exhausted attempts
- custom `maxAttempts` and `baseDelayMs`
- success on first attempt
- success after one or more failures
- permanent failure after retries are exhausted
