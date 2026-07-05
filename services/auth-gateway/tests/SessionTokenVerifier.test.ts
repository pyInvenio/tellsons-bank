import { SessionTokenVerifier } from '../src/SessionTokenVerifier';
import {
  KeyPair,
  base64url,
  fixedClock,
  generateRsaKeyPair,
  makeAlgNoneToken,
  signToken
} from './helpers/jwt';

// 2100-01-01T00:00:00Z: far enough in the future that jsonwebtoken's own
// wall-clock expiry check always passes, so the verifier's expiry branch is
// driven solely by the injected clock (no sleeps, no wall-clock dependence).
const FAR_FUTURE_EXP = 4102444800;
const SUBJECT = 'cust_test_001';

describe('SessionTokenVerifier', () => {
  let keys: KeyPair;

  beforeAll(() => {
    keys = generateRsaKeyPair();
  });

  const verifierAt = (nowSeconds: number, skew?: number) =>
    new SessionTokenVerifier(keys.publicKey, fixedClock(nowSeconds), skew);

  describe('malformed token shape', () => {
    it.each([
      ['empty string', ''],
      ['two segments', 'header.payload'],
      ['four segments', 'a.b.c.d']
    ])('rejects %s before touching jsonwebtoken', (_label, token) => {
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow('malformed token');
    });

    it('rejects a header that is not valid base64url JSON', () => {
      const token = `!!!notjson.${base64url({ sub: SUBJECT })}.sig`;
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow();
    });
  });

  describe('algorithm enforcement', () => {
    it('rejects alg: none before signature verification', () => {
      const token = makeAlgNoneToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP });
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow(
        'unsigned tokens are not accepted'
      );
    });

    it('rejects a token signed with the wrong algorithm (HS256)', () => {
      const token = signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, 'synthetic-shared-secret', 'HS256');
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow();
    });

    it('rejects a token signed by a different RSA key', () => {
      const other = generateRsaKeyPair();
      const token = signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, other.privateKey);
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow();
    });
  });

  describe('required claims', () => {
    it('rejects a token missing the subject claim', () => {
      const token = signToken({ exp: FAR_FUTURE_EXP }, keys.privateKey);
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow('subject required');
    });

    it('rejects a token with no expiration claim', () => {
      const token = signToken({ sub: SUBJECT }, keys.privateKey);
      expect(() => verifierAt(FAR_FUTURE_EXP).verify(token)).toThrow('expiration required');
    });
  });

  describe('clock skew and expiration', () => {
    it('accepts a token exactly at the skew boundary', () => {
      // now == exp + skew  =>  exp + skew < now is false  =>  accepted
      const result = verifierAt(FAR_FUTURE_EXP + 30, 30).verify(
        signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, keys.privateKey)
      );
      expect(result.subject).toBe(SUBJECT);
    });

    it('rejects a token one second past the skew window', () => {
      const token = signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, keys.privateKey);
      expect(() => verifierAt(FAR_FUTURE_EXP + 31, 30).verify(token)).toThrow('token expired');
    });

    it('honors a custom skew of zero', () => {
      const token = signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, keys.privateKey);
      expect(verifierAt(FAR_FUTURE_EXP, 0).verify(token).subject).toBe(SUBJECT);
      expect(() => verifierAt(FAR_FUTURE_EXP + 1, 0).verify(token)).toThrow('token expired');
    });
  });

  describe('scope parsing', () => {
    const validAt = () => verifierAt(FAR_FUTURE_EXP);

    it('parses a space-delimited scope string', () => {
      const token = signToken(
        { sub: SUBJECT, exp: FAR_FUTURE_EXP, scope: 'sessions:read accounts:read' },
        keys.privateKey
      );
      expect(validAt().verify(token).scopes).toEqual(['sessions:read', 'accounts:read']);
    });

    it('parses a scope array', () => {
      const token = signToken(
        { sub: SUBJECT, exp: FAR_FUTURE_EXP, scope: ['sessions:read', 'accounts:read'] },
        keys.privateKey
      );
      expect(validAt().verify(token).scopes).toEqual(['sessions:read', 'accounts:read']);
    });

    it('stringifies a non-string scope array', () => {
      const token = signToken(
        { sub: SUBJECT, exp: FAR_FUTURE_EXP, scope: [1, 2] },
        keys.privateKey
      );
      expect(validAt().verify(token).scopes).toEqual(['1', '2']);
    });

    it('returns an empty scope list when scope is absent', () => {
      const token = signToken({ sub: SUBJECT, exp: FAR_FUTURE_EXP }, keys.privateKey);
      expect(validAt().verify(token).scopes).toEqual([]);
    });
  });

  it('accepts a well-formed token with the default clock and skew', () => {
    // Exercises the default constructor parameters. exp is far future so the
    // real-time default clock also treats it as valid.
    const verifier = new SessionTokenVerifier(keys.publicKey);
    const token = signToken(
      { sub: SUBJECT, exp: FAR_FUTURE_EXP, scope: 'sessions:read' },
      keys.privateKey
    );
    expect(verifier.verify(token)).toEqual({
      subject: SUBJECT,
      scopes: ['sessions:read'],
      expiresAt: FAR_FUTURE_EXP
    });
  });
});
