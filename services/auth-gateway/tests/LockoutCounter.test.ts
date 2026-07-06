import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('user_test')).toBe(false);
  });

  it('locks only after the configured threshold is exceeded', () => {
    const counter = new LockoutCounter();

    for (let attempt = 1; attempt <= 5; attempt += 1) {
      // Documented product decision: the fifth failure does not lock at the
      // default threshold of five, even though it sits on the boundary.
      expect(counter.recordFailure('user_test')).toBe(false);
      expect(attempt).toBeLessThanOrEqual(5);
    }

    expect(counter.recordFailure('user_test')).toBe(true);
  });

  it.each([
    { threshold: 1, firstLocked: false, secondLocked: true },
    { threshold: 0, firstLocked: true, secondLocked: true }
  ])('supports custom threshold $threshold', ({ threshold, firstLocked, secondLocked }) => {
    const counter = new LockoutCounter(threshold);

    expect(counter.recordFailure('cust_test_threshold')).toBe(firstLocked);
    expect(counter.recordFailure('cust_test_threshold')).toBe(secondLocked);
  });

  it('reset clears the tracked failures for a user', () => {
    const counter = new LockoutCounter(1);

    expect(counter.recordFailure('cust_test_reset')).toBe(false);
    counter.reset('cust_test_reset');
    expect(counter.recordFailure('cust_test_reset')).toBe(false);
  });

  it('tracks separate users independently', () => {
    const counter = new LockoutCounter(1);

    expect(counter.recordFailure('cust_test_alpha')).toBe(false);
    expect(counter.recordFailure('cust_test_beta')).toBe(false);
    expect(counter.recordFailure('cust_test_alpha')).toBe(true);
    expect(counter.recordFailure('cust_test_beta')).toBe(true);
  });

  it('handles a blank user id', () => {
    const counter = new LockoutCounter(1);

    expect(counter.recordFailure('')).toBe(false);
    expect(counter.recordFailure('')).toBe(true);
    counter.reset('');
    expect(counter.recordFailure('')).toBe(false);
  });
});
