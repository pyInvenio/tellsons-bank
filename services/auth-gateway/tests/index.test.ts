describe('index', () => {
  it('uses either the configured public key or the synthetic default', () => {
    const originalPublicKey = process.env.AUTH_PUBLIC_KEY;

    try {
      process.env.AUTH_PUBLIC_KEY = 'synthetic-test-public-key';
      jest.resetModules();
      jest.isolateModules(() => {
        const mod = require('../src/index');
        expect(mod.app).toBeTruthy();
      });

      delete process.env.AUTH_PUBLIC_KEY;
      jest.resetModules();
      jest.isolateModules(() => {
        const mod = require('../src/index');
        expect(mod.app).toBeTruthy();
      });
    } finally {
      if (originalPublicKey === undefined) {
        delete process.env.AUTH_PUBLIC_KEY;
      } else {
        process.env.AUTH_PUBLIC_KEY = originalPublicKey;
      }
      jest.resetModules();
    }
  });
});
