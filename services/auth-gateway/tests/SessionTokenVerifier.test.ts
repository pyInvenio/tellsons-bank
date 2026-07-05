import { generateKeyPairSync } from 'crypto';
import { readFileSync } from 'fs';
import { join } from 'path';
import jwt from 'jsonwebtoken';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

const fixtures = JSON.parse(
  readFileSync(
    join(__dirname, '../../../devin-workspace/fixtures/synthetic/auth-gateway.json'),
    'utf8'
  )
) as {
  subjects: { primary: string; secondary: string; demo: string; blank: string };
  scopes: { array: string[]; spaceDelimited: string; single: string };
  clock: { fixedEpochSeconds: number; defaultSkewSeconds: number };
};

const { publicKey, privateKey } = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

// A second, unrelated keypair to exercise signature-mismatch rejection.
const otherKey = generateKeyPairSync('rsa', {
  modulusLength: 2048,
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});

// Far-future expiry (relative to the real clock) so that jsonwebtoken's own
// expiry check always passes; our custom skew logic is exercised purely through
// the injected `nowSeconds` clock, keeping the tests wall-clock independent.
const REAL_NOW = Math.floor(Date.now() / 1000);
const FUTURE_EXP = REAL_NOW + 3600;

function sign(payload: Record<string, unknown>, key: string = privateKey): string {
  return jwt.sign(payload, key, { algorithm: 'RS256' });
}

function base64url(value: object): string {
  return Buffer.from(JSON.stringify(value), 'utf8').toString('base64url');
}

describe('SessionTokenVerifier', () => {
  describe('malformed token shape (trust-boundary validation)', () => {
    it('rejects an empty token', () => {
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify('')).toThrow('malformed token');
    });

    it('rejects a token with fewer than three segments', () => {
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify('only.two')).toThrow('malformed token');
    });

    it('rejects a token with more than three segments', () => {
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify('a.b.c.d')).toThrow('malformed token');
    });

    it('throws on an invalid base64url/JSON header', () => {
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify('!!!.payload.sig')).toThrow();
    });
  });

  describe('algorithm enforcement', () => {
    it('rejects an alg:none token before signature verification', () => {
      const header = base64url({ alg: 'none', typ: 'JWT' });
      const payload = base64url({ sub: fixtures.subjects.primary, exp: FUTURE_EXP });
      const unsigned = `${header}.${payload}.`;
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify(unsigned)).toThrow('unsigned tokens are not accepted');
    });

    it('rejects a token signed by an unrelated key', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP }, otherKey.privateKey);
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify(token)).toThrow();
    });
  });

  describe('required claims', () => {
    it('rejects a token missing the subject claim', () => {
      const token = sign({ exp: FUTURE_EXP });
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify(token)).toThrow('subject required');
    });

    it('rejects a token whose expiration claim is missing', () => {
      const token = sign({ sub: fixtures.subjects.primary });
      const verifier = new SessionTokenVerifier(publicKey);
      expect(() => verifier.verify(token)).toThrow('expiration required');
    });
  });

  describe('expiration with injected clock and skew', () => {
    it('accepts a token whose expiry is within the skew window', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP });
      // now == exp + skew -> boundary, exactly not expired.
      const now = () => FUTURE_EXP + fixtures.clock.defaultSkewSeconds;
      const verifier = new SessionTokenVerifier(publicKey, now);
      expect(verifier.verify(token).subject).toBe(fixtures.subjects.primary);
    });

    it('rejects a token one second past the skew window', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP });
      const now = () => FUTURE_EXP + fixtures.clock.defaultSkewSeconds + 1;
      const verifier = new SessionTokenVerifier(publicKey, now);
      expect(() => verifier.verify(token)).toThrow('token expired');
    });

    it('honors a custom zero skew value', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP });
      const expiredNow = () => FUTURE_EXP + 1;
      expect(() => new SessionTokenVerifier(publicKey, expiredNow, 0).verify(token)).toThrow(
        'token expired'
      );

      const validNow = () => FUTURE_EXP;
      expect(new SessionTokenVerifier(publicKey, validNow, 0).verify(token).subject).toBe(
        fixtures.subjects.primary
      );
    });
  });

  describe('scope normalization', () => {
    const now = () => REAL_NOW;

    it('parses an array scope claim', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP, scope: fixtures.scopes.array });
      const result = new SessionTokenVerifier(publicKey, now).verify(token);
      expect(result.scopes).toEqual(fixtures.scopes.array);
      expect(result.expiresAt).toBe(FUTURE_EXP);
    });

    it('parses a space-delimited scope string', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP, scope: fixtures.scopes.spaceDelimited });
      const result = new SessionTokenVerifier(publicKey, now).verify(token);
      expect(result.scopes).toEqual(fixtures.scopes.spaceDelimited.split(' '));
    });

    it('returns an empty scope list when the claim is absent', () => {
      const token = sign({ sub: fixtures.subjects.primary, exp: FUTURE_EXP });
      const result = new SessionTokenVerifier(publicKey, now).verify(token);
      expect(result.scopes).toEqual([]);
    });
  });
});
