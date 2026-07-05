import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('user_test')).toBe(false);
  });

  describe('default threshold boundary (5)', () => {
    it('does not lock on the first through fifth failures and locks on the sixth', () => {
      const counter = new LockoutCounter();
      const results = Array.from({ length: 6 }, () => counter.recordFailure('user_test_default'));
      // Documents the current `failures > threshold` behavior: the fifth failure
      // is NOT locked even though the threshold is five. See docs/lockout-policy.md.
      expect(results).toEqual([false, false, false, false, false, true]);
    });
  });

  describe('custom thresholds', () => {
    it('locks on the second failure when threshold is one', () => {
      const counter = new LockoutCounter(1);
      expect(counter.recordFailure('user_test_one')).toBe(false);
      expect(counter.recordFailure('user_test_one')).toBe(true);
    });

    it('locks on the first failure when threshold is zero', () => {
      const counter = new LockoutCounter(0);
      expect(counter.recordFailure('user_test_zero')).toBe(true);
    });
  });

  describe('reset behavior', () => {
    it('clears the counter so a subsequent failure starts over', () => {
      const counter = new LockoutCounter(2);
      counter.recordFailure('user_test_reset');
      counter.recordFailure('user_test_reset');
      expect(counter.recordFailure('user_test_reset')).toBe(true);
      counter.reset('user_test_reset');
      expect(counter.recordFailure('user_test_reset')).toBe(false);
    });

    it('is a no-op when resetting an unknown user', () => {
      const counter = new LockoutCounter(2);
      expect(() => counter.reset('user_test_unknown')).not.toThrow();
    });
  });

  describe('isolation and edge inputs', () => {
    it('tracks separate counters for separate users', () => {
      const counter = new LockoutCounter(1);
      expect(counter.recordFailure('user_test_a')).toBe(false);
      expect(counter.recordFailure('user_test_b')).toBe(false);
      expect(counter.recordFailure('user_test_a')).toBe(true);
    });

    it('tracks a blank user id as its own counter', () => {
      const counter = new LockoutCounter(1);
      expect(counter.recordFailure('')).toBe(false);
      expect(counter.recordFailure('')).toBe(true);
    });
  });
});
