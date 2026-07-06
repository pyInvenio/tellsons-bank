import { systemClock } from '../src/Clock';

describe('systemClock', () => {
  it('returns current epoch seconds as an integer', () => {
    const before = Math.floor(Date.now() / 1000);
    const result = systemClock.epochSeconds();
    const after = Math.floor(Date.now() / 1000);
    expect(result).toBeGreaterThanOrEqual(before);
    expect(result).toBeLessThanOrEqual(after);
    expect(Number.isInteger(result)).toBe(true);
  });
});
