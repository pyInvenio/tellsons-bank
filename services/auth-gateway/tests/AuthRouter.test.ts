import { startAuthRouter, RunningRouter } from './helpers/router';
import type { SessionTokenVerifier, VerificationResult } from '../src/SessionTokenVerifier';
import { SYNTHETIC } from './fixtures/synthetic-auth';

/**
 * Narrow fake verifier per routing.md guidance: records the token the router
 * forwarded and returns a canned synthetic result or throws. No real JWT
 * signing and no downstream network calls happen in router tests.
 */
class FakeVerifier implements Pick<SessionTokenVerifier, 'verify'> {
  lastToken: string | undefined;
  constructor(private readonly behavior: (token: string) => VerificationResult) {}
  verify(token: string): VerificationResult {
    this.lastToken = token;
    return this.behavior(token);
  }
}

const okResult: VerificationResult = {
  subject: SYNTHETIC.subject,
  scopes: SYNTHETIC.scopesArray,
  expiresAt: 2_000_000_000
};

describe('AuthRouter GET /auth/session', () => {
  let running: RunningRouter | undefined;

  afterEach(async () => {
    if (running) {
      await running.close();
      running = undefined;
    }
  });

  const get = (headers: Record<string, string> = {}): Promise<Response> => {
    if (!running) throw new Error('router not started');
    return fetch(`${running.baseUrl}/auth/session`, { headers });
  };

  it('returns the verifier result and omits clientId when not required', async () => {
    const verifier = new FakeVerifier(() => okResult);
    running = await startAuthRouter(verifier);

    const res = await get({ authorization: `Bearer synthetic.jwt.token` });
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body).toEqual({ subject: SYNTHETIC.subject, scopes: SYNTHETIC.scopesArray, expiresAt: 2_000_000_000 });
    expect(body).not.toHaveProperty('clientId');
  });

  it('strips a mixed-case Bearer prefix and surrounding whitespace', async () => {
    const verifier = new FakeVerifier(() => okResult);
    running = await startAuthRouter(verifier);

    await get({ authorization: 'bEaReR   synthetic.jwt.token' });
    expect(verifier.lastToken).toBe('synthetic.jwt.token');
  });

  it('forwards an empty token when the authorization header is missing', async () => {
    const verifier = new FakeVerifier(() => okResult);
    running = await startAuthRouter(verifier);

    await get();
    expect(verifier.lastToken).toBe('');
  });

  it('maps any verifier error to 401 without leaking internal detail', async () => {
    const verifier = new FakeVerifier(() => {
      throw new Error('token expired: internal detail that must not leak');
    });
    running = await startAuthRouter(verifier);

    const res = await get({ authorization: 'Bearer synthetic.jwt.token' });
    const body = await res.json();

    expect(res.status).toBe(401);
    expect(body).toEqual({ error: 'invalid_session' });
    expect(JSON.stringify(body)).not.toContain('internal detail');
  });

  describe('with requireClientId enabled', () => {
    it('rejects a missing client id with 400 client_id_required', async () => {
      const verifier = new FakeVerifier(() => okResult);
      running = await startAuthRouter(verifier, { requireClientId: true });

      const res = await get({ authorization: 'Bearer synthetic.jwt.token' });
      const body = await res.json();

      expect(res.status).toBe(400);
      expect(body).toEqual({ error: 'client_id_required' });
      // Short-circuits before the verifier is ever consulted.
      expect(verifier.lastToken).toBeUndefined();
    });

    it('rejects a whitespace-only client id (trimmed to empty) with 400', async () => {
      const verifier = new FakeVerifier(() => okResult);
      running = await startAuthRouter(verifier, { requireClientId: true });

      const res = await get({ authorization: 'Bearer synthetic.jwt.token', 'x-tellsons-client-id': '   ' });
      expect(res.status).toBe(400);
    });

    it('echoes the client id on success for downstream audit correlation', async () => {
      const verifier = new FakeVerifier(() => okResult);
      running = await startAuthRouter(verifier, { requireClientId: true });

      const res = await get({
        authorization: 'Bearer synthetic.jwt.token',
        'x-tellsons-client-id': SYNTHETIC.clientId
      });
      const body = await res.json();

      expect(res.status).toBe(200);
      expect(body.clientId).toBe(SYNTHETIC.clientId);
    });
  });

  it('echoes a provided client id even when enforcement is disabled', async () => {
    const verifier = new FakeVerifier(() => okResult);
    running = await startAuthRouter(verifier, { requireClientId: false });

    const res = await get({
      authorization: 'Bearer synthetic.jwt.token',
      'x-tellsons-client-id': SYNTHETIC.clientId
    });
    const body = await res.json();

    expect(res.status).toBe(200);
    expect(body.clientId).toBe(SYNTHETIC.clientId);
  });
});
