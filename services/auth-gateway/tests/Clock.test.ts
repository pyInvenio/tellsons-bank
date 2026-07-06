import { systemClock } from '../src/Clock';

describe('systemClock', () => {
  it('returns the current time as integer epoch seconds', () => {
    const before = Math.floor(Date.now() / 1000);
    const value = systemClock.epochSeconds();
    const after = Math.floor(Date.now() / 1000);

    expect(Number.isInteger(value)).toBe(true);
    expect(value).toBeGreaterThanOrEqual(before);
    expect(value).toBeLessThanOrEqual(after);
  });
});
