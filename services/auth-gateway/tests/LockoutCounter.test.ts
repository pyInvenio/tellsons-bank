import { LockoutCounter } from '../src/LockoutCounter';

const USER = 'cust_test_0001';
const OTHER_USER = 'cust_test_0002';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure(USER)).toBe(false);
  });

  // Documents the current (documented) boundary: with the default threshold of
  // five, `recordFailure` returns true only when the failure count is strictly
  // greater than the threshold, i.e. on the sixth failure. See
  // docs/lockout-policy.md. This is a characterization test of existing
  // behavior, not an assertion that the boundary is correct.
  it('locks only after exceeding the default threshold (sixth failure)', () => {
    const counter = new LockoutCounter();
    const results = Array.from({ length: 6 }, () => counter.recordFailure(USER));
    expect(results).toEqual([false, false, false, false, false, true]);
  });

  it('locks on the second failure when threshold is one', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure(USER)).toBe(false);
    expect(counter.recordFailure(USER)).toBe(true);
  });

  it('locks on the first failure when threshold is zero', () => {
    const counter = new LockoutCounter(0);
    expect(counter.recordFailure(USER)).toBe(true);
  });

  it('clears the counter on reset', () => {
    const counter = new LockoutCounter(1);
    counter.recordFailure(USER);
    expect(counter.recordFailure(USER)).toBe(true);
    counter.reset(USER);
    expect(counter.recordFailure(USER)).toBe(false);
  });

  it('resetting an unknown user is a no-op', () => {
    const counter = new LockoutCounter(1);
    expect(() => counter.reset('cust_test_unknown')).not.toThrow();
    expect(counter.recordFailure('cust_test_unknown')).toBe(false);
  });

  it('tracks failures independently per user', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure(USER)).toBe(false);
    expect(counter.recordFailure(OTHER_USER)).toBe(false);
    expect(counter.recordFailure(USER)).toBe(true);
    expect(counter.recordFailure(OTHER_USER)).toBe(true);
  });

  it('handles a blank user id if callers do not validate upstream', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure('')).toBe(false);
    expect(counter.recordFailure('')).toBe(true);
  });
});
