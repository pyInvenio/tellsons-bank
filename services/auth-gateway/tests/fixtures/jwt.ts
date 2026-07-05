import { generateKeyPairSync } from 'crypto';
import jwt from 'jsonwebtoken';

/**
 * Synthetic JWT fixtures for auth-gateway tests.
 *
 * Keys are generated in-memory per test run; nothing is persisted and no
 * real issuer names, customer identifiers, or production keys are used.
 * All subjects use obviously-synthetic `user_test_*` identifiers.
 */
export interface SyntheticKeyPair {
  publicKey: string;
  privateKey: string;
}

export function generateSyntheticKeyPair(): SyntheticKeyPair {
  return generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
}

/**
 * Signs a synthetic RS256 token from an arbitrary claim set. No `expiresIn`
 * is injected so callers control the presence and shape of `exp` explicitly.
 */
export function signSynthetic(
  privateKey: string,
  payload: Record<string, unknown>
): string {
  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

/**
 * Builds an `alg: none` token by hand. `jsonwebtoken` refuses to emit these,
 * so we assemble the segments directly to exercise the trust-boundary guard.
 */
export function makeUnsignedToken(payload: Record<string, unknown>): string {
  const b64 = (obj: Record<string, unknown>) =>
    Buffer.from(JSON.stringify(obj)).toString('base64url');
  return `${b64({ alg: 'none', typ: 'JWT' })}.${b64(payload)}.`;
}

/** Number of seconds since the Unix epoch as an integer. */
export const SYNTHETIC_NOW = 1_700_000_000;
