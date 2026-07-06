import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_0001')).toBe(false);
  });

  it('locks once failures strictly exceed the threshold', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_0001')).toBe(false); // 1
    expect(counter.recordFailure('cust_test_0001')).toBe(false); // 2
    expect(counter.recordFailure('cust_test_0001')).toBe(false); // 3 == threshold, not locked
    expect(counter.recordFailure('cust_test_0001')).toBe(true); // 4 > threshold
  });

  // FINDING (see docs/findings/auth-gateway-lockout-off-by-one.md): with the
  // default threshold of five, the fifth failure is NOT locked because the
  // implementation uses `next > threshold`. This test documents the CURRENT
  // behavior for reviewer visibility; production code is intentionally unchanged.
  it('does not lock on the fifth failure with the default threshold (documented off-by-one)', () => {
    const counter = new LockoutCounter();
    let locked = false;
    for (let i = 0; i < 5; i += 1) {
      locked = counter.recordFailure('cust_test_0002');
    }
    expect(locked).toBe(false); // fifth failure remains unlocked
    expect(counter.recordFailure('cust_test_0002')).toBe(true); // sixth locks
  });

  it('locks immediately past a threshold of one', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure('cust_test_0003')).toBe(false); // 1 == threshold
    expect(counter.recordFailure('cust_test_0003')).toBe(true); // 2 > threshold
  });

  it('locks on the first failure when the threshold is zero', () => {
    const counter = new LockoutCounter(0);
    expect(counter.recordFailure('cust_test_0004')).toBe(true); // 1 > 0
  });

  it('tracks separate counters per user', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure('cust_test_0005')).toBe(false);
    // A different user is unaffected by the first user's failure.
    expect(counter.recordFailure('cust_test_0006')).toBe(false);
  });

  it('resets a user counter after previous failures', () => {
    const counter = new LockoutCounter(1);
    counter.recordFailure('cust_test_0007');
    counter.recordFailure('cust_test_0007'); // would be locked
    counter.reset('cust_test_0007');
    expect(counter.recordFailure('cust_test_0007')).toBe(false); // starts from zero again
  });

  it('handles a blank user id if callers do not validate upstream', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure('')).toBe(false);
    expect(counter.recordFailure('')).toBe(true);
  });
});
