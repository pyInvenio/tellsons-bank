import { LockoutCounter } from '../src/LockoutCounter';

const USER = 'cust_test_001';
const OTHER = 'cust_test_002';

describe('LockoutCounter', () => {
  it('does not lock while failures are below the threshold', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure(USER)).toBe(false);
    expect(counter.recordFailure(USER)).toBe(false);
  });

  // FINDING (documented, not a bug fix): recordFailure returns `next > threshold`,
  // so the Nth failure is NOT locked when the threshold is N. Locking happens only
  // on failure N+1. This matches docs/lockout-policy.md and is surfaced here for
  // human review rather than changed in production code.
  it('does not lock on the failure that exactly equals the threshold (off-by-one boundary)', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure(USER); // 1
    counter.recordFailure(USER); // 2
    expect(counter.recordFailure(USER)).toBe(false); // 3 == threshold -> not locked
  });

  it('locks on the first failure that exceeds the threshold', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure(USER); // 1
    counter.recordFailure(USER); // 2
    counter.recordFailure(USER); // 3
    expect(counter.recordFailure(USER)).toBe(true); // 4 > threshold -> locked
  });

  it('uses a default threshold of five', () => {
    const counter = new LockoutCounter();
    for (let i = 0; i < 5; i++) {
      expect(counter.recordFailure(USER)).toBe(false);
    }
    expect(counter.recordFailure(USER)).toBe(true); // 6th failure
  });

  it('locks immediately after the first failure when threshold is zero', () => {
    const counter = new LockoutCounter(0);
    expect(counter.recordFailure(USER)).toBe(true); // 1 > 0
  });

  it('locks on the second failure when threshold is one', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure(USER)).toBe(false); // 1 == threshold
    expect(counter.recordFailure(USER)).toBe(true); // 2 > threshold
  });

  it('clears the counter on reset', () => {
    const counter = new LockoutCounter(1);
    counter.recordFailure(USER);
    counter.recordFailure(USER); // would lock
    counter.reset(USER);
    expect(counter.recordFailure(USER)).toBe(false); // back to first failure
  });

  it('tracks failures per user independently', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure(USER)).toBe(false);
    expect(counter.recordFailure(USER)).toBe(true);
    // OTHER is unaffected by USER's failures.
    expect(counter.recordFailure(OTHER)).toBe(false);
  });
});
