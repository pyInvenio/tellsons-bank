import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_001')).toBe(false);
  });

  it('returns false up to threshold count', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_001')).toBe(false); // 1
    expect(counter.recordFailure('cust_test_001')).toBe(false); // 2
    expect(counter.recordFailure('cust_test_001')).toBe(false); // 3
  });

  it('returns true once threshold is exceeded', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure('cust_test_002'); // 1
    counter.recordFailure('cust_test_002'); // 2
    counter.recordFailure('cust_test_002'); // 3
    expect(counter.recordFailure('cust_test_002')).toBe(true); // 4 > 3
  });

  it('tracks users independently', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('cust_test_001'); // 1
    counter.recordFailure('cust_test_001'); // 2
    expect(counter.recordFailure('cust_test_001')).toBe(true); // 3 > 2
    expect(counter.recordFailure('cust_test_002')).toBe(false); // 1
  });

  it('resets a user counter', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('cust_test_001');
    counter.recordFailure('cust_test_001');
    counter.reset('cust_test_001');
    expect(counter.recordFailure('cust_test_001')).toBe(false); // 1
  });

  it('uses default threshold of 5', () => {
    const counter = new LockoutCounter();
    for (let i = 0; i < 5; i++) {
      expect(counter.recordFailure('cust_test_003')).toBe(false);
    }
    expect(counter.recordFailure('cust_test_003')).toBe(true); // 6 > 5
  });
});
