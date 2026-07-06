describe('auth-gateway app', () => {
  it('exports a configured express app', () => {
    const { app } = require('../src/index');
    expect(app).toBeDefined();
    expect(typeof app).toBe('function');
  });
});
