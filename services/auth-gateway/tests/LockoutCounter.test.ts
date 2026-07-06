import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures below threshold', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('user_test_01')).toBe(false);
    expect(counter.recordFailure('user_test_01')).toBe(false);
    expect(counter.recordFailure('user_test_01')).toBe(false);
  });

  it('locks out after exceeding threshold', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('user_test_02');
    counter.recordFailure('user_test_02');
    expect(counter.recordFailure('user_test_02')).toBe(true);
  });

  it('tracks users independently', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('user_test_03');
    counter.recordFailure('user_test_03');
    expect(counter.recordFailure('user_test_04')).toBe(false);
  });

  it('resets failure count for a user', () => {
    const counter = new LockoutCounter(2);
    counter.recordFailure('user_test_05');
    counter.recordFailure('user_test_05');
    counter.reset('user_test_05');
    expect(counter.recordFailure('user_test_05')).toBe(false);
  });
});
