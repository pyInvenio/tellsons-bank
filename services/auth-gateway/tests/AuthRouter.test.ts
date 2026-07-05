import type { AddressInfo } from 'net';
import type { Server } from 'http';
import express from 'express';
import { buildAuthRouter } from '../src/AuthRouter';
import type { SessionTokenVerifier, VerificationResult } from '../src/SessionTokenVerifier';

const SESSION = {
  subject: 'cust_test_0001',
  scopes: ['accounts:read'],
  expiresAt: 1700000000
} satisfies VerificationResult;

const INTERNAL_ERROR_MESSAGE = 'stack-trace-with-secret-should-not-leak';

// Narrow fake standing in for SessionTokenVerifier. It records the raw token it
// received so the router's Bearer-prefix stripping can be asserted, and it fails
// for any token that is not the expected synthetic value.
function fakeVerifier(): { verifier: SessionTokenVerifier; lastToken: () => string | undefined } {
  let seen: string | undefined;
  const verifier = {
    verify(token: string): VerificationResult {
      seen = token;
      if (token !== 'good-token') {
        throw new Error(INTERNAL_ERROR_MESSAGE);
      }
      return SESSION;
    }
  } as unknown as SessionTokenVerifier;
  return { verifier, lastToken: () => seen };
}

describe('AuthRouter GET /auth/session', () => {
  let server: Server;
  let baseUrl: string;
  let harness: ReturnType<typeof fakeVerifier>;

  beforeAll(async () => {
    harness = fakeVerifier();
    const app = express();
    app.use('/auth', buildAuthRouter(harness.verifier));
    await new Promise<void>((resolve) => {
      server = app.listen(0, '127.0.0.1', resolve);
    });
    const { port } = server.address() as AddressInfo;
    baseUrl = `http://127.0.0.1:${port}`;
  });

  afterAll(async () => {
    await new Promise<void>((resolve, reject) =>
      server.close((err) => (err ? reject(err) : resolve()))
    );
  });

  it('returns the verifier result for a valid bearer token', async () => {
    const res = await fetch(`${baseUrl}/auth/session`, {
      headers: { authorization: 'Bearer good-token' }
    });
    expect(res.status).toBe(200);
    await expect(res.json()).resolves.toEqual(SESSION);
  });

  it('strips a mixed-case bearer prefix with extra whitespace', async () => {
    const res = await fetch(`${baseUrl}/auth/session`, {
      headers: { authorization: 'bEaRer   good-token' }
    });
    expect(res.status).toBe(200);
    expect(harness.lastToken()).toBe('good-token');
  });

  it('maps a missing authorization header to a generic 401', async () => {
    const res = await fetch(`${baseUrl}/auth/session`);
    expect(res.status).toBe(401);
    await expect(res.json()).resolves.toEqual({ error: 'invalid_session' });
  });

  it('maps verifier failures to 401 without leaking internal error detail', async () => {
    const res = await fetch(`${baseUrl}/auth/session`, {
      headers: { authorization: 'Bearer bad-token' }
    });
    expect(res.status).toBe(401);
    const body = await res.text();
    expect(JSON.parse(body)).toEqual({ error: 'invalid_session' });
    expect(body).not.toContain(INTERNAL_ERROR_MESSAGE);
  });
});
