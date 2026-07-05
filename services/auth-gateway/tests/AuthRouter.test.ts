import express from 'express';
import http from 'http';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { buildAuthRouter } from '../src/AuthRouter';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

const REAL_NOW = Math.floor(Date.now() / 1000);

function signToken(payload: Record<string, unknown>): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

function request(
  server: http.Server,
  path: string,
  headers: Record<string, string> = {}
): Promise<{ status: number; body: Record<string, unknown> }> {
  return new Promise((resolve, reject) => {
    const addr = server.address();
    if (!addr || typeof addr === 'string') return reject(new Error('no address'));
    const req = http.request(
      { hostname: '127.0.0.1', port: addr.port, path, headers, method: 'GET' },
      (res) => {
        let data = '';
        res.on('data', (chunk: string) => (data += chunk));
        res.on('end', () =>
          resolve({ status: res.statusCode ?? 0, body: JSON.parse(data) })
        );
      }
    );
    req.on('error', reject);
    req.end();
  });
}

describe('AuthRouter /session', () => {
  let server: http.Server;

  beforeAll(() => {
    return new Promise<void>((resolve) => {
      const verifier = new SessionTokenVerifier(publicKey, () => REAL_NOW);
      const app = express();
      app.use('/auth', buildAuthRouter(verifier));
      server = app.listen(0, () => resolve());
    });
  });

  afterAll(() => new Promise<void>((resolve) => {
    server.close(() => resolve());
  }));

  it('returns 200 with session data for a valid Bearer token', async () => {
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW + 600,
      scope: 'read write'
    });
    const resp = await request(server, '/auth/session', {
      authorization: `Bearer ${token}`
    });
    expect(resp.status).toBe(200);
    expect(resp.body.subject).toBe('cust_test_001');
    expect(resp.body.scopes).toEqual(['read', 'write']);
  });

  it('returns 401 for missing Authorization header', async () => {
    const resp = await request(server, '/auth/session');
    expect(resp.status).toBe(401);
    expect(resp.body.error).toBe('invalid_session');
  });

  it('returns 401 for malformed token', async () => {
    const resp = await request(server, '/auth/session', {
      authorization: 'Bearer not-a-jwt'
    });
    expect(resp.status).toBe(401);
    expect(resp.body.error).toBe('invalid_session');
  });

  it('returns 401 for expired token', async () => {
    const futureVerifier = new SessionTokenVerifier(publicKey, () => REAL_NOW + 10000);
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW + 600,
      scope: 'read'
    });
    expect(() => futureVerifier.verify(token)).toThrow('token expired');
  });

  it('handles case-insensitive Bearer prefix', async () => {
    const token = signToken({
      sub: 'cust_test_002',
      exp: REAL_NOW + 600,
      scope: 'admin'
    });
    const resp = await request(server, '/auth/session', {
      authorization: `bearer ${token}`
    });
    expect(resp.status).toBe(200);
    expect(resp.body.subject).toBe('cust_test_002');
  });
});
