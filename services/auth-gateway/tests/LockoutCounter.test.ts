import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('user_test')).toBe(false);
  });

  it('does not lock out on failures below the threshold', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_0001')).toBe(false); // 1
    expect(counter.recordFailure('cust_test_0001')).toBe(false); // 2
  });

  // NOTE: Documents *observed* behavior, not necessarily correct behavior.
  // With threshold=3, the 3rd failure still returns false and lockout only trips
  // on the 4th failure (next > threshold). See docs/findings for the off-by-one
  // finding raised for human review; production code is intentionally unchanged.
  it('returns false at exactly the threshold (observed off-by-one)', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure('cust_test_0002'); // 1
    counter.recordFailure('cust_test_0002'); // 2
    expect(counter.recordFailure('cust_test_0002')).toBe(false); // 3 == threshold
  });

  it('locks out only after the threshold is exceeded', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure('cust_test_0003'); // 1
    counter.recordFailure('cust_test_0003'); // 2
    counter.recordFailure('cust_test_0003'); // 3
    expect(counter.recordFailure('cust_test_0003')).toBe(true); // 4 > threshold
  });

  it('resets the failure count for a user', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('cust_test_0004'); // 1
    counter.recordFailure('cust_test_0004'); // 2
    counter.reset('cust_test_0004');
    // After reset the nullish-coalescing branch (undefined -> 0) is exercised again.
    expect(counter.recordFailure('cust_test_0004')).toBe(false); // back to 1
  });

  it('applies the default threshold of 5 when none is provided', () => {
    const counter = new LockoutCounter();
    for (let i = 0; i < 5; i += 1) {
      expect(counter.recordFailure('cust_test_0005')).toBe(false);
    }
    expect(counter.recordFailure('cust_test_0005')).toBe(true); // 6th > 5
  });

  it('tracks users independently', () => {
    const counter = new LockoutCounter(1);
    expect(counter.recordFailure('cust_test_0006')).toBe(false); // user A: 1
    expect(counter.recordFailure('cust_test_0007')).toBe(false); // user B: 1
    expect(counter.recordFailure('cust_test_0006')).toBe(true); // user A: 2 > 1
  });
});
