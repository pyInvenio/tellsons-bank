import { RetryPolicy } from '../src/RetryPolicy';

describe('RetryPolicy', () => {
  it('backs off exponentially', () => {
    const policy = new RetryPolicy(3, 50);
    expect(policy.nextDelay(0)).toBe(50);
    expect(policy.nextDelay(1)).toBe(100);
  });
});
