import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('cust_test_020')).toBe(false);
  });

  it('returns false at exactly the threshold', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure('cust_test_021');
    counter.recordFailure('cust_test_021');
    expect(counter.recordFailure('cust_test_021')).toBe(false);
  });

  it('returns true when failures exceed the threshold', () => {
    const counter = new LockoutCounter(3);
    counter.recordFailure('cust_test_022');
    counter.recordFailure('cust_test_022');
    counter.recordFailure('cust_test_022');
    expect(counter.recordFailure('cust_test_022')).toBe(true);
  });

  it('resets the counter for a user', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('cust_test_023');
    counter.recordFailure('cust_test_023');
    counter.reset('cust_test_023');
    expect(counter.recordFailure('cust_test_023')).toBe(false);
  });

  it('tracks users independently', () => {
    const counter = new LockoutCounter(1);
    counter.recordFailure('cust_test_024');
    expect(counter.recordFailure('cust_test_024')).toBe(true);
    expect(counter.recordFailure('cust_test_025')).toBe(false);
  });

  it('uses default threshold of 5 when none provided', () => {
    const counter = new LockoutCounter();
    for (let i = 0; i < 5; i++) counter.recordFailure('cust_test_026');
    expect(counter.recordFailure('cust_test_026')).toBe(true);
  });
});
