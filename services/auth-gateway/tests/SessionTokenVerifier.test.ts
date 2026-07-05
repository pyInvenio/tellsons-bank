import { SessionTokenVerifier } from '../src/SessionTokenVerifier';
import {
  generateSyntheticKeyPair,
  makeUnsignedToken,
  signSynthetic,
  SYNTHETIC_NOW
} from './fixtures/jwt';

describe('SessionTokenVerifier', () => {
  const { publicKey, privateKey } = generateSyntheticKeyPair();
  const fixedNow = () => SYNTHETIC_NOW;

  const verifier = (skew = 30, now: () => number = fixedNow) =>
    new SessionTokenVerifier(publicKey, now, skew);

  describe('token shape validation', () => {
    it('rejects an empty token', () => {
      expect(() => verifier().verify('')).toThrow('malformed token');
    });

    it('rejects a token with fewer than three segments', () => {
      expect(() => verifier().verify('only.two')).toThrow('malformed token');
    });

    it('rejects a token with more than three segments', () => {
      expect(() => verifier().verify('a.b.c.d')).toThrow('malformed token');
    });

    it('rejects a header that is not valid base64url JSON', () => {
      // Three segments so it passes the shape check, but the header will not
      // decode to JSON, exercising the parse-failure path at the boundary.
      expect(() => verifier().verify('!!!.payload.sig')).toThrow();
    });
  });

  describe('algorithm enforcement', () => {
    it('rejects unsigned (alg: none) tokens before signature verification', () => {
      const token = makeUnsignedToken({ sub: 'user_test_alg', exp: SYNTHETIC_NOW + 60 });
      expect(() => verifier().verify(token)).toThrow('unsigned tokens are not accepted');
    });

    it('rejects tokens signed with a different key', () => {
      const other = generateSyntheticKeyPair();
      const token = signSynthetic(other.privateKey, {
        sub: 'user_test_wrongkey',
        exp: SYNTHETIC_NOW + 60
      });
      expect(() => verifier().verify(token)).toThrow();
    });
  });

  describe('claim validation', () => {
    it('rejects a token without a subject', () => {
      // exp must be in the real-clock future so jsonwebtoken accepts the token
      // and control reaches the explicit subject check.
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, { exp: realFutureExp });
      expect(() => verifier(30, () => realFutureExp).verify(token)).toThrow('subject required');
    });

    it('rejects a token without a numeric expiration', () => {
      const token = signSynthetic(privateKey, { sub: 'user_test_noexp' });
      expect(() => verifier().verify(token)).toThrow('expiration required');
    });
  });

  describe('expiration and clock skew', () => {
    it('accepts a token whose expiration is within the configured skew', () => {
      // exp is in the real-clock future so jsonwebtoken accepts it; the injected
      // clock sits exactly on the skew boundary (exp + skew), which is allowed.
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, { sub: 'user_test_skew', exp: realFutureExp });
      const now = () => realFutureExp + 30;
      const result = verifier(30, now).verify(token);
      expect(result.subject).toBe('user_test_skew');
    });

    it('rejects a token just outside the skew window', () => {
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, { sub: 'user_test_skew', exp: realFutureExp });
      const now = () => realFutureExp + 31;
      expect(() => verifier(30, now).verify(token)).toThrow('token expired');
    });

    it('rejects immediately past expiration when skew is zero', () => {
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, { sub: 'user_test_zeroskew', exp: realFutureExp });
      const now = () => realFutureExp + 1;
      expect(() => verifier(0, now).verify(token)).toThrow('token expired');
    });
  });

  describe('scope normalization', () => {
    it('parses a space-delimited scope string', () => {
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, {
        sub: 'user_test_scopes',
        exp: realFutureExp,
        scope: 'accounts:read transfers:write'
      });
      const result = verifier(30, () => realFutureExp).verify(token);
      expect(result.scopes).toEqual(['accounts:read', 'transfers:write']);
    });

    it('parses an array scope claim', () => {
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, {
        sub: 'user_test_scopes',
        exp: realFutureExp,
        scope: ['accounts:read', 'transfers:write']
      });
      const result = verifier(30, () => realFutureExp).verify(token);
      expect(result.scopes).toEqual(['accounts:read', 'transfers:write']);
    });

    it('returns an empty scope list when the claim is absent', () => {
      const realFutureExp = Math.floor(Date.now() / 1000) + 3600;
      const token = signSynthetic(privateKey, { sub: 'user_test_noscope', exp: realFutureExp });
      const result = verifier(30, () => realFutureExp).verify(token);
      expect(result.scopes).toEqual([]);
      expect(result.expiresAt).toBe(realFutureExp);
    });
  });
});
