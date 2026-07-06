import { generateKeyPairSync } from 'crypto';
import jwt, { Algorithm } from 'jsonwebtoken';

/**
 * Synthetic RS256 key pair generated per test run. No real or production keys
 * are ever stored in fixtures; the private key lives only in test memory.
 */
export interface SyntheticKeyPair {
  publicKey: string;
  privateKey: string;
}

export function newSyntheticKeyPair(): SyntheticKeyPair {
  const { publicKey, privateKey } = generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  return { publicKey, privateKey };
}

export interface SyntheticTokenOptions {
  privateKey: string;
  payload?: Record<string, unknown>;
  algorithm?: Algorithm;
  header?: Record<string, unknown>;
}

/** Signs a synthetic JWT with the provided (synthetic) private key. */
export function signSyntheticToken(options: SyntheticTokenOptions): string {
  const { privateKey, payload = {}, algorithm = 'RS256', header } = options;
  return jwt.sign(payload, privateKey, {
    algorithm,
    ...(header ? { header: { alg: algorithm, typ: 'JWT', ...header } } : {})
  });
}

/**
 * Builds a raw three-segment token with an arbitrary decoded header object,
 * used to exercise header-inspection branches (e.g. `alg: none`) that never
 * survive a real signature check.
 */
export function rawTokenWithHeader(header: Record<string, unknown>, payload: Record<string, unknown> = {}): string {
  const encode = (obj: Record<string, unknown>): string =>
    Buffer.from(JSON.stringify(obj), 'utf8').toString('base64url');
  return `${encode(header)}.${encode(payload)}.${encode({ sig: 'synthetic' })}`;
}

/** Deterministic clock factory so token-expiry branches never touch the wall clock. */
export function fixedClock(epochSeconds: number): () => number {
  return () => epochSeconds;
}
