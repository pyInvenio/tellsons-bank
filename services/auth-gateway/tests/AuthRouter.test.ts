import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import express from 'express';
import http from 'http';
import { buildAuthRouter } from '../src/AuthRouter';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

/* ── Synthetic key pair ─────────────────────────────────────────── */
const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

function realNow(): number {
  return Math.floor(Date.now() / 1000);
}

function signToken(payload: Record<string, unknown>): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

/* ── Minimal HTTP helper (no real network; uses Node test server) ─ */
function request(
  app: express.Express,
  path: string,
  headers: Record<string, string> = {}
): Promise<{ status: number; body: Record<string, unknown> }> {
  return new Promise((resolve, reject) => {
    const server = app.listen(0, () => {
      const addr = server.address();
      if (!addr || typeof addr === 'string') {
        server.close();
        return reject(new Error('unexpected address format'));
      }
      const req = http.request(
        { hostname: '127.0.0.1', port: addr.port, path, headers },
        (res) => {
          let data = '';
          res.on('data', (chunk: Buffer) => { data += chunk.toString(); });
          res.on('end', () => {
            server.close();
            resolve({ status: res.statusCode ?? 0, body: JSON.parse(data) });
          });
        }
      );
      req.on('error', (err) => { server.close(); reject(err); });
      req.end();
    });
  });
}

describe('AuthRouter /session endpoint', () => {
  const verifier = new SessionTokenVerifier(publicKey);
  const app = express();
  app.use('/auth', buildAuthRouter(verifier));

  it('returns 200 with session data for a valid Bearer token', async () => {
    const token = signToken({
      sub: 'cust_test_010',
      scope: 'read write',
      exp: realNow() + 3600
    });
    const { status, body } = await request(app, '/auth/session', {
      authorization: `Bearer ${token}`
    });
    expect(status).toBe(200);
    expect(body).toMatchObject({
      subject: 'cust_test_010',
      scopes: ['read', 'write']
    });
  });

  it('returns 401 when no Authorization header is present', async () => {
    const { status, body } = await request(app, '/auth/session');
    expect(status).toBe(401);
    expect(body).toEqual({ error: 'invalid_session' });
  });

  it('returns 401 for a malformed token', async () => {
    const { status, body } = await request(app, '/auth/session', {
      authorization: 'Bearer not-a-jwt'
    });
    expect(status).toBe(401);
    expect(body).toEqual({ error: 'invalid_session' });
  });

  it('returns 401 for an expired token', async () => {
    const token = signToken({
      sub: 'cust_test_011',
      scope: 'read',
      exp: realNow() - 300
    });
    const { status, body } = await request(app, '/auth/session', {
      authorization: `Bearer ${token}`
    });
    expect(status).toBe(401);
    expect(body).toEqual({ error: 'invalid_session' });
  });

  it('handles Authorization header without Bearer prefix', async () => {
    const token = signToken({
      sub: 'cust_test_012',
      scope: 'read',
      exp: realNow() + 3600
    });
    const { status } = await request(app, '/auth/session', {
      authorization: token
    });
    expect(status).toBe(200);
  });
});
