import { generateKeyPairSync } from 'crypto';
import jwt from 'jsonwebtoken';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

// Synthetic RS256 key material is generated per test run. No real keys or tokens
// are stored in fixtures, and no network calls are made.
const { privateKey, publicKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

const { privateKey: otherPrivateKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

// The library `jwt.verify` validates `exp` against the real wall clock and cannot
// be injected, so token `exp` values are anchored to a single reference read at
// module load (no sleeps, no per-test wall-clock reads). The verifier's explicit
// expiry check uses the injected `fixedClock`, pinned to the same reference.
const REF_NOW = Math.floor(Date.now() / 1000);
const fixedClock = () => REF_NOW;

function sign(payload: Record<string, unknown>): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

function unsignedToken(payload: Record<string, unknown>): string {
  const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
  const body = Buffer.from(JSON.stringify(payload)).toString('base64url');
  return `${header}.${body}.`;
}

describe('SessionTokenVerifier', () => {
  const verifier = new SessionTokenVerifier(publicKey, fixedClock);

  it('verifies a well-formed synthetic token and normalizes array scopes', () => {
    const token = sign({ sub: 'cust_test_0001', exp: REF_NOW + 300, scope: ['read', 'write'] });
    const result = verifier.verify(token);
    expect(result).toEqual({
      subject: 'cust_test_0001',
      scopes: ['read', 'write'],
      expiresAt: REF_NOW + 300
    });
  });

  it('splits a space-delimited scope string', () => {
    const token = sign({ sub: 'cust_test_0002', exp: REF_NOW + 300, scope: 'read write admin' });
    expect(verifier.verify(token).scopes).toEqual(['read', 'write', 'admin']);
  });

  it('returns an empty scope list when scope is absent', () => {
    const token = sign({ sub: 'cust_test_0003', exp: REF_NOW + 300 });
    expect(verifier.verify(token).scopes).toEqual([]);
  });

  it('rejects an empty token as malformed', () => {
    expect(() => verifier.verify('')).toThrow('malformed token');
  });

  it('rejects a token that does not have three segments', () => {
    expect(() => verifier.verify('a.b')).toThrow('malformed token');
  });

  it('rejects unsigned (alg=none) tokens', () => {
    const token = unsignedToken({ sub: 'cust_test_0004', exp: REF_NOW + 300 });
    expect(() => verifier.verify(token)).toThrow('unsigned tokens are not accepted');
  });

  it('rejects a token signed by an untrusted key', () => {
    const token = jwt.sign({ sub: 'cust_test_0005', exp: REF_NOW + 300 }, otherPrivateKey, {
      algorithm: 'RS256'
    });
    expect(() => verifier.verify(token)).toThrow();
  });

  it('rejects a token without a subject', () => {
    const token = sign({ exp: REF_NOW + 300 });
    expect(() => verifier.verify(token)).toThrow('subject required');
  });

  it('rejects a token without a numeric expiration', () => {
    const token = sign({ sub: 'cust_test_0006', noExp: true });
    expect(() => verifier.verify(token)).toThrow('expiration required');
  });

  it('rejects a token expired beyond the allowed clock skew', () => {
    // exp is valid against the real jwt.verify clock, but the injected clock is
    // far in the future so the explicit expiry check trips.
    const realExp = Math.floor(Date.now() / 1000) + 300;
    const token = sign({ sub: 'cust_test_0007', exp: realExp });
    const futureVerifier = new SessionTokenVerifier(publicKey, () => realExp + 100000);
    expect(() => futureVerifier.verify(token)).toThrow('token expired');
  });

  it('accepts a token at the clock-skew boundary (not yet expired)', () => {
    const realNow = Math.floor(Date.now() / 1000);
    const token = sign({ sub: 'cust_test_0008', exp: realNow + 5 });
    // Injected clock is exactly at exp + allowedClockSkew, so exp + skew < now is false.
    const boundaryVerifier = new SessionTokenVerifier(publicKey, () => realNow + 5 + 30);
    expect(boundaryVerifier.verify(token).subject).toBe('cust_test_0008');
  });
});
