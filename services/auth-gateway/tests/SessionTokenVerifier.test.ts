import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

/* ── Synthetic RSA key pair (generated at test time, never stored) ── */
const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

function realNow(): number {
  return Math.floor(Date.now() / 1000);
}

function signToken(
  payload: Record<string, unknown>,
  opts?: jwt.SignOptions
): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256', ...opts });
}

describe('SessionTokenVerifier', () => {
  /* Use real clock for most tests so jwt.verify's internal check passes. */
  const verifier = new SessionTokenVerifier(publicKey);

  /* ── Malformed-token branch ───────────────────────────────────── */
  it('rejects an empty string', () => {
    expect(() => verifier.verify('')).toThrow('malformed token');
  });

  it('rejects a token with fewer than three segments', () => {
    expect(() => verifier.verify('header.payload')).toThrow('malformed token');
  });

  it('rejects a token with more than three segments', () => {
    expect(() => verifier.verify('a.b.c.d')).toThrow('malformed token');
  });

  /* ── Algorithm-none guard ─────────────────────────────────────── */
  it('rejects alg:none tokens', () => {
    const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify({ sub: 'cust_test_001' })).toString('base64url');
    const unsignedToken = `${header}.${payload}.`;
    expect(() => verifier.verify(unsignedToken)).toThrow('unsigned tokens are not accepted');
  });

  /* ── Missing subject ──────────────────────────────────────────── */
  it('rejects a token without sub claim', () => {
    const token = signToken({ scope: 'read', exp: realNow() + 3600 });
    expect(() => verifier.verify(token)).toThrow('subject required');
  });

  /* ── Missing expiration ───────────────────────────────────────── */
  it('rejects a token without exp claim', () => {
    const token = signToken(
      { sub: 'cust_test_002', scope: 'read' },
      { noTimestamp: true }
    );
    expect(() => verifier.verify(token)).toThrow('expiration required');
  });

  /* ── Expired-token branch (custom nowSeconds check) ───────────── */
  it('rejects a token expired beyond clock-skew via injected clock', () => {
    const now = realNow();
    const exp = now + 100;
    // Injected clock returns a time far past exp + skew
    const futureVerifier = new SessionTokenVerifier(publicKey, () => exp + 200, 30);
    const token = signToken(
      { sub: 'cust_test_003', scope: 'read', exp },
      { noTimestamp: true }
    );
    expect(() => futureVerifier.verify(token)).toThrow('token expired');
  });

  /* ── Scope parsing: space-separated string ────────────────────── */
  it('parses a space-separated scope string', () => {
    const token = signToken({ sub: 'cust_test_004', scope: 'read write', exp: realNow() + 3600 });
    const result = verifier.verify(token);
    expect(result.scopes).toEqual(['read', 'write']);
  });

  /* ── Scope parsing: array ─────────────────────────────────────── */
  it('parses a scope array', () => {
    const token = signToken({ sub: 'cust_test_005', scope: ['admin', 'audit'], exp: realNow() + 3600 });
    const result = verifier.verify(token);
    expect(result.scopes).toEqual(['admin', 'audit']);
  });

  /* ── Scope absent → empty array ───────────────────────────────── */
  it('returns empty scopes when scope claim is absent', () => {
    const token = signToken({ sub: 'cust_test_006', exp: realNow() + 3600 });
    const result = verifier.verify(token);
    expect(result.scopes).toEqual([]);
  });

  /* ── Happy path ───────────────────────────────────────────────── */
  it('returns subject, scopes, and expiresAt for a valid token', () => {
    const exp = realNow() + 7200;
    const token = signToken({ sub: 'cust_test_007', scope: 'transfer', exp });
    const result = verifier.verify(token);
    expect(result).toEqual({
      subject: 'cust_test_007',
      scopes: ['transfer'],
      expiresAt: exp
    });
  });

  /* ── Clock-skew tolerance (within window) ─────────────────────── */
  it('accepts a token within clock-skew tolerance', () => {
    const now = realNow();
    const barelyExpired = now - 10; // 10s past, within 30s skew
    const token = signToken({ sub: 'cust_test_008', scope: 'read', exp: barelyExpired });
    const result = verifier.verify(token);
    expect(result.subject).toBe('cust_test_008');
  });

  /* ── Wrong signing algorithm ──────────────────────────────────── */
  it('rejects a token signed with an unsupported algorithm', () => {
    const hmacToken = jwt.sign(
      { sub: 'cust_test_009', scope: 'read', exp: realNow() + 3600 },
      'some-secret',
      { algorithm: 'HS256' }
    );
    expect(() => verifier.verify(hmacToken)).toThrow();
  });

  /* ── Custom clock-skew constructor param ──────────────────────── */
  it('respects a custom allowedClockSkewSeconds of zero', () => {
    const now = realNow();
    const exp = now + 100;
    // Injected clock is 101s past exp; with skew=0, exp + 0 < now → expired
    const strictVerifier = new SessionTokenVerifier(publicKey, () => exp + 101, 0);
    const token = signToken({ sub: 'cust_test_010', scope: 'read', exp });
    expect(() => strictVerifier.verify(token)).toThrow('token expired');
  });
});
