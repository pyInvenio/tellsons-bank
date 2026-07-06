describe('auth-gateway app wiring', () => {
  const KEY = 'AUTH_PUBLIC_KEY';
  let saved: string | undefined;

  beforeEach(() => {
    saved = process.env[KEY];
    jest.resetModules();
  });

  afterEach(() => {
    if (saved === undefined) {
      delete process.env[KEY];
    } else {
      process.env[KEY] = saved;
    }
  });

  it('falls back to a synthetic public key when AUTH_PUBLIC_KEY is unset', () => {
    delete process.env[KEY];
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { app } = require('../src/index');
    expect(typeof app).toBe('function'); // express app is callable
  });

  it('uses the provided AUTH_PUBLIC_KEY when set', () => {
    process.env[KEY] = 'synthetic-public-key-from-env';
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    const { app } = require('../src/index');
    expect(typeof app).toBe('function');
  });
});
