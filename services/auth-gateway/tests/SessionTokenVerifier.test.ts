import { SessionTokenVerifier } from '../src/SessionTokenVerifier';
import {
  newSyntheticKeyPair,
  signSyntheticToken,
  rawTokenWithHeader,
  fixedClock,
  SyntheticKeyPair
} from './helpers/tokens';
import { SYNTHETIC } from './fixtures/synthetic-auth';

/**
 * `jsonwebtoken` validates `exp` against the real system clock, so tokens are
 * always signed with an `exp` that is valid relative to real time. The
 * verifier's own expiry/skew branch is then driven purely by the injected
 * `nowSeconds` clock, which is what these tests exercise deterministically.
 */
describe('SessionTokenVerifier', () => {
  let keys: SyntheticKeyPair;
  let baseNow: number;

  beforeAll(() => {
    keys = newSyntheticKeyPair();
    baseNow = Math.floor(Date.now() / 1000);
  });

  // Injected clock defaults to "real now" unless a test needs to advance it.
  const verifier = (skew?: number, injectedNow: number = baseNow): SessionTokenVerifier =>
    new SessionTokenVerifier(keys.publicKey, fixedClock(injectedNow), skew);

  const futureExp = (): number => baseNow + 3600;

  describe('token shape validation (trust boundary)', () => {
    it('rejects an empty token as malformed', () => {
      expect(() => verifier().verify('')).toThrow('malformed token');
    });

    it('rejects a token with fewer than three segments', () => {
      expect(() => verifier().verify('only.two')).toThrow('malformed token');
    });

    it('rejects a token with more than three segments', () => {
      expect(() => verifier().verify('a.b.c.d')).toThrow('malformed token');
    });

    it('propagates an error for an invalid base64url header', () => {
      // Three segments so the shape check passes, but the header is not JSON.
      expect(() => verifier().verify('%%%.payload.sig')).toThrow();
    });

    it('rejects tokens advertising alg: none before signature verification', () => {
      const token = rawTokenWithHeader({ alg: 'none', typ: 'JWT' }, { sub: SYNTHETIC.subject });
      expect(() => verifier().verify(token)).toThrow('unsigned tokens are not accepted');
    });
  });

  describe('signature and algorithm enforcement', () => {
    it('rejects a token signed by a different (synthetic) key', () => {
      const other = newSyntheticKeyPair();
      const token = signSyntheticToken({
        privateKey: other.privateKey,
        payload: { sub: SYNTHETIC.subject, exp: futureExp() }
      });
      expect(() => verifier().verify(token)).toThrow();
    });
  });

  describe('claim validation', () => {
    it('rejects a token missing the sub claim', () => {
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { exp: futureExp() }
      });
      expect(() => verifier().verify(token)).toThrow('subject required');
    });

    it('rejects a token missing the exp claim', () => {
      // No exp is signed, so jsonwebtoken performs no expiry check and the
      // verifier's own `typeof exp !== number` guard is what fires.
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject }
      });
      expect(() => verifier().verify(token)).toThrow('expiration required');
    });
  });

  describe('expiration and clock skew (injected clock)', () => {
    it('accepts a token whose expiry is comfortably in the future', () => {
      const exp = futureExp();
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp }
      });
      const result = verifier().verify(token);
      expect(result.subject).toBe(SYNTHETIC.subject);
      expect(result.expiresAt).toBe(exp);
    });

    it('rejects via the skew branch when the injected clock is past exp + skew', () => {
      const exp = futureExp();
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp }
      });
      // Advance the injected clock well beyond exp + default 30s skew.
      expect(() => verifier(30, exp + 31).verify(token)).toThrow('token expired');
    });

    it('honors a custom skew of zero (rejects one second past exp)', () => {
      const exp = futureExp();
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp }
      });
      expect(() => verifier(0, exp + 1).verify(token)).toThrow('token expired');
    });

    it('uses the default system clock when none is injected', () => {
      // Constructed without a clock so the default `nowSeconds` is exercised;
      // a far-future exp keeps the assertion independent of the wall clock.
      const defaultClockVerifier = new SessionTokenVerifier(keys.publicKey);
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp: baseNow + 86_400 }
      });
      expect(defaultClockVerifier.verify(token).subject).toBe(SYNTHETIC.subject);
    });

    it('accepts a token exactly inside a custom skew window', () => {
      const exp = futureExp();
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp }
      });
      // exp + 10 is not less than the injected now (exp + 10) -> still valid.
      expect(verifier(10, exp + 10).verify(token).subject).toBe(SYNTHETIC.subject);
    });
  });

  describe('scope normalization', () => {
    it('accepts scope provided as an array', () => {
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp: futureExp(), scope: SYNTHETIC.scopesArray }
      });
      expect(verifier().verify(token).scopes).toEqual(SYNTHETIC.scopesArray);
    });

    it('accepts scope provided as a space-delimited string', () => {
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp: futureExp(), scope: SYNTHETIC.scopesString }
      });
      expect(verifier().verify(token).scopes).toEqual(SYNTHETIC.scopesArray);
    });

    it('yields an empty scope list when the scope claim is absent', () => {
      const token = signSyntheticToken({
        privateKey: keys.privateKey,
        payload: { sub: SYNTHETIC.subject, exp: futureExp() }
      });
      expect(verifier().verify(token).scopes).toEqual([]);
    });
  });
});
