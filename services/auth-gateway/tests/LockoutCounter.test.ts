import { LockoutCounter } from '../src/LockoutCounter';

describe('LockoutCounter', () => {
  it('allows early failures', () => {
    const counter = new LockoutCounter(3);
    expect(counter.recordFailure('user_test')).toBe(false);
  });
});
