import jwt from 'jsonwebtoken';
import crypto from 'crypto';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

const REAL_NOW = Math.floor(Date.now() / 1000);

function signToken(
  payload: Record<string, unknown>,
  opts?: jwt.SignOptions
): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256', ...opts });
}

describe('SessionTokenVerifier', () => {
  const verifier = new SessionTokenVerifier(publicKey, () => REAL_NOW);

  // --- malformed-token branch ---

  it('rejects empty string', () => {
    expect(() => verifier.verify('')).toThrow('malformed token');
  });

  it('rejects token with fewer than three parts', () => {
    expect(() => verifier.verify('a.b')).toThrow('malformed token');
  });

  it('rejects token with more than three parts', () => {
    expect(() => verifier.verify('a.b.c.d')).toThrow('malformed token');
  });

  // --- unsigned-token branch ---

  it('rejects tokens with alg=none', () => {
    const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify({ sub: 'cust_test_001' })).toString('base64url');
    const fakeToken = `${header}.${payload}.nosig`;
    expect(() => verifier.verify(fakeToken)).toThrow('unsigned tokens are not accepted');
  });

  // --- missing subject branch ---

  it('rejects token without sub claim', () => {
    const token = signToken({ exp: REAL_NOW + 600, scope: 'read' });
    expect(() => verifier.verify(token)).toThrow('subject required');
  });

  // --- missing expiration branch ---

  it('rejects token without exp claim', () => {
    const token = jwt.sign(
      { sub: 'cust_test_001', scope: 'read' },
      privateKey,
      { algorithm: 'RS256' }
    );
    expect(() => verifier.verify(token)).toThrow('expiration required');
  });

  // --- expired-token branch (custom clock far in future) ---

  it('rejects token whose exp + skew is before now', () => {
    const futureVerifier = new SessionTokenVerifier(publicKey, () => REAL_NOW + 10000);
    const token = signToken({
      sub: 'cust_test_002',
      exp: REAL_NOW + 600,
      scope: 'read'
    });
    expect(() => futureVerifier.verify(token)).toThrow('token expired');
  });

  // --- scope parsing: string ---

  it('parses space-delimited scope string', () => {
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW + 600,
      scope: 'read write'
    });
    const result = verifier.verify(token);
    expect(result.subject).toBe('cust_test_001');
    expect(result.scopes).toEqual(['read', 'write']);
    expect(result.expiresAt).toBe(REAL_NOW + 600);
  });

  // --- scope parsing: array ---

  it('parses scope provided as an array', () => {
    const token = signToken({
      sub: 'cust_test_002',
      exp: REAL_NOW + 600,
      scope: ['admin', 'transfer']
    });
    const result = verifier.verify(token);
    expect(result.scopes).toEqual(['admin', 'transfer']);
  });

  // --- scope parsing: undefined / empty ---

  it('returns empty scopes when scope claim is absent', () => {
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW + 600
    });
    const result = verifier.verify(token);
    expect(result.scopes).toEqual([]);
  });

  // --- wrong algorithm ---

  it('rejects token signed with HS256', () => {
    const token = jwt.sign(
      { sub: 'cust_test_001', exp: REAL_NOW + 600, scope: 'read' },
      'some-secret',
      { algorithm: 'HS256' }
    );
    expect(() => verifier.verify(token)).toThrow();
  });

  // --- clock-skew boundary: token within skew window ---

  it('accepts token within clock-skew window', () => {
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW - 10,
      scope: 'read'
    });
    const result = verifier.verify(token);
    expect(result.subject).toBe('cust_test_001');
  });

  // --- clock-skew boundary: token exactly at skew boundary ---

  it('accepts token near skew boundary', () => {
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW - 28,
      scope: 'read'
    });
    const result = verifier.verify(token);
    expect(result.subject).toBe('cust_test_001');
  });

  // --- custom skew ---

  it('respects custom clock skew setting', () => {
    const strictVerifier = new SessionTokenVerifier(publicKey, () => REAL_NOW + 10000, 0);
    const token = signToken({
      sub: 'cust_test_001',
      exp: REAL_NOW + 600,
      scope: 'read'
    });
    expect(() => strictVerifier.verify(token)).toThrow('token expired');
  });

  // --- default clock (coverage for default parameter) ---

  it('uses system clock when none provided', () => {
    const sysVerifier = new SessionTokenVerifier(publicKey);
    const token = signToken({
      sub: 'cust_test_001',
      exp: Math.floor(Date.now() / 1000) + 600,
      scope: 'read'
    });
    const result = sysVerifier.verify(token);
    expect(result.subject).toBe('cust_test_001');
  });
});
