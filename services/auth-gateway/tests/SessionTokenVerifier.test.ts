import crypto from 'crypto';
import jwt from 'jsonwebtoken';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
});

const FAR_FUTURE = Math.floor(Date.now() / 1000) + 3600;

function signToken(payload: object): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

describe('SessionTokenVerifier', () => {
  const realNow = () => Math.floor(Date.now() / 1000);
  const verifier = new SessionTokenVerifier(publicKey, realNow, 30);

  describe('malformed tokens', () => {
    it('rejects empty string', () => {
      expect(() => verifier.verify('')).toThrow('malformed token');
    });

    it('rejects token with fewer than 3 parts', () => {
      expect(() => verifier.verify('abc.def')).toThrow('malformed token');
    });
  });

  describe('unsigned tokens', () => {
    it('rejects alg:none tokens', () => {
      const header = Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url');
      const payload = Buffer.from(JSON.stringify({ sub: 'cust_test_0001', exp: FAR_FUTURE })).toString('base64url');
      const fakeToken = `${header}.${payload}.`;
      expect(() => verifier.verify(fakeToken)).toThrow('unsigned tokens are not accepted');
    });
  });

  describe('valid token verification', () => {
    it('returns subject, scopes array, and expiresAt for a valid token', () => {
      const token = signToken({
        sub: 'cust_test_0001',
        exp: FAR_FUTURE,
        scope: ['read', 'write'],
      });
      const result = verifier.verify(token);
      expect(result.subject).toBe('cust_test_0001');
      expect(result.scopes).toEqual(['read', 'write']);
      expect(result.expiresAt).toBe(FAR_FUTURE);
    });

    it('parses space-delimited scope string', () => {
      const token = signToken({
        sub: 'cust_test_0002',
        exp: FAR_FUTURE,
        scope: 'read write admin',
      });
      const result = verifier.verify(token);
      expect(result.scopes).toEqual(['read', 'write', 'admin']);
    });

    it('handles missing scope as empty array', () => {
      const token = signToken({
        sub: 'cust_test_0003',
        exp: FAR_FUTURE,
      });
      const result = verifier.verify(token);
      expect(result.scopes).toEqual([]);
    });
  });

  describe('missing required claims', () => {
    it('rejects token without sub claim', () => {
      const token = signToken({ exp: FAR_FUTURE, scope: 'read' });
      expect(() => verifier.verify(token)).toThrow('subject required');
    });

    it('rejects token without exp claim', () => {
      const tokenNoExp = jwt.sign(
        { sub: 'cust_test_0001', iat: Math.floor(Date.now() / 1000) },
        privateKey,
        { algorithm: 'RS256', noTimestamp: true }
      );
      expect(() => verifier.verify(tokenNoExp)).toThrow('expiration required');
    });
  });

  describe('expiration', () => {
    it('rejects token that has expired beyond clock skew', () => {
      // Use a nowSeconds that is far past the token's exp
      const expiredExp = FAR_FUTURE;
      const futureNow = () => expiredExp + 100; // 100 seconds past exp
      const strictVerifier = new SessionTokenVerifier(publicKey, futureNow, 30);
      const token = signToken({
        sub: 'cust_test_0001',
        exp: expiredExp,
      });
      expect(() => strictVerifier.verify(token)).toThrow();
    });

    it('accepts token within clock skew tolerance', () => {
      const token = signToken({
        sub: 'cust_test_0001',
        exp: FAR_FUTURE,
      });
      const result = verifier.verify(token);
      expect(result.subject).toBe('cust_test_0001');
    });
  });
});
