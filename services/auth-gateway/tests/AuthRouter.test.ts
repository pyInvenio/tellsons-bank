import express from 'express';
import type { AddressInfo } from 'net';
import type { Server } from 'http';
import { buildAuthRouter } from '../src/AuthRouter';
import type { SessionTokenVerifier, VerificationResult } from '../src/SessionTokenVerifier';

/**
 * Narrow fake for SessionTokenVerifier. The router contract only depends on
 * `verify` either returning a result or throwing, so we avoid real JWT signing
 * here per docs/routing.md. No downstream or network dependency is involved
 * beyond the ephemeral localhost test server.
 */
function fakeVerifier(impl: (token: string) => VerificationResult): SessionTokenVerifier {
  return { verify: impl } as unknown as SessionTokenVerifier;
}

async function withServer(
  verifier: SessionTokenVerifier,
  run: (baseUrl: string) => Promise<void>
): Promise<void> {
  const app = express();
  app.use('/auth', buildAuthRouter(verifier));
  const server: Server = await new Promise((resolve) => {
    const s = app.listen(0, () => resolve(s));
  });
  try {
    const { port } = server.address() as AddressInfo;
    await run(`http://127.0.0.1:${port}`);
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
}

describe('AuthRouter GET /auth/session', () => {
  it('returns the verifier result for a valid bearer token', async () => {
    const verifier = fakeVerifier((token) => {
      expect(token).toBe('good-token');
      return { subject: 'user_test_router', scopes: ['accounts:read'], expiresAt: 1_700_000_000 };
    });
    await withServer(verifier, async (baseUrl) => {
      const res = await fetch(`${baseUrl}/auth/session`, {
        headers: { authorization: 'Bearer good-token' }
      });
      expect(res.status).toBe(200);
      expect(await res.json()).toEqual({
        subject: 'user_test_router',
        scopes: ['accounts:read'],
        expiresAt: 1_700_000_000
      });
    });
  });

  it('strips a mixed-case bearer prefix with extra whitespace', async () => {
    let seen = '';
    const verifier = fakeVerifier((token) => {
      seen = token;
      return { subject: 'user_test_router', scopes: [], expiresAt: 1_700_000_000 };
    });
    await withServer(verifier, async (baseUrl) => {
      const res = await fetch(`${baseUrl}/auth/session`, {
        headers: { authorization: 'bEaReR    spaced-token' }
      });
      expect(res.status).toBe(200);
      expect(seen).toBe('spaced-token');
    });
  });

  it('passes an empty token through when the authorization header is missing', async () => {
    let seen = 'unset';
    const verifier = fakeVerifier((token) => {
      seen = token;
      throw new Error('malformed token');
    });
    await withServer(verifier, async (baseUrl) => {
      const res = await fetch(`${baseUrl}/auth/session`);
      expect(res.status).toBe(401);
      expect(seen).toBe('');
    });
  });

  it('maps a verifier error to a generic 401 without leaking the message', async () => {
    const verifier = fakeVerifier(() => {
      throw new Error('token expired: internal detail user_test_router');
    });
    await withServer(verifier, async (baseUrl) => {
      const res = await fetch(`${baseUrl}/auth/session`, {
        headers: { authorization: 'Bearer bad-token' }
      });
      expect(res.status).toBe(401);
      const body = await res.text();
      expect(JSON.parse(body)).toEqual({ error: 'invalid_session' });
      expect(body).not.toContain('internal detail');
    });
  });
});
