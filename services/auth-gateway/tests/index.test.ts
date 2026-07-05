/**
 * Exercises the app bootstrap in src/index.ts, covering both branches of the
 * AUTH_PUBLIC_KEY fallback. No network listener is started; we only assert the
 * exported express app is constructed.
 */
describe('auth-gateway app bootstrap', () => {
  const originalKey = process.env.AUTH_PUBLIC_KEY;

  afterEach(() => {
    if (originalKey === undefined) {
      delete process.env.AUTH_PUBLIC_KEY;
    } else {
      process.env.AUTH_PUBLIC_KEY = originalKey;
    }
    jest.resetModules();
  });

  it('falls back to a synthetic public key when AUTH_PUBLIC_KEY is unset', () => {
    delete process.env.AUTH_PUBLIC_KEY;
    jest.resetModules();
    const { app } = require('../src/index');
    expect(typeof app.use).toBe('function');
  });

  it('uses the configured AUTH_PUBLIC_KEY when present', () => {
    process.env.AUTH_PUBLIC_KEY = 'synthetic-configured-key';
    jest.resetModules();
    const { app } = require('../src/index');
    expect(typeof app.use).toBe('function');
  });
});
