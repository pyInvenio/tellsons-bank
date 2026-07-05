import { generateKeyPairSync } from 'crypto';
import jwt, { Algorithm } from 'jsonwebtoken';

/**
 * Synthetic-only JWT helpers for auth-gateway tests.
 *
 * All keys are generated in-process at test time; no real keys, issuers, or
 * customer identifiers are used. Downstream systems are not contacted.
 */

export interface KeyPair {
  publicKey: string;
  privateKey: string;
}

export function generateRsaKeyPair(): KeyPair {
  return generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
}

export function base64url(input: object | string): string {
  const raw = typeof input === 'string' ? input : JSON.stringify(input);
  return Buffer.from(raw, 'utf8').toString('base64url');
}

/** Sign a payload with a given key and algorithm (default RS256). */
export function signToken(
  payload: Record<string, unknown>,
  privateKey: string,
  algorithm: Algorithm = 'RS256'
): string {
  // noTimestamp keeps fixtures deterministic; callers set exp explicitly.
  return jwt.sign(payload, privateKey, { algorithm, noTimestamp: true });
}

/**
 * Build a raw token whose header advertises `alg: none` with an empty
 * signature segment. Produces exactly three dot-separated segments so it
 * reaches the algorithm check rather than the malformed-shape check.
 */
export function makeAlgNoneToken(payload: Record<string, unknown>): string {
  const header = base64url({ alg: 'none', typ: 'JWT' });
  const body = base64url(payload);
  return `${header}.${body}.`;
}

/** A fixed-clock factory: returns a nowSeconds function pinned to a value. */
export function fixedClock(epochSeconds: number): () => number {
  return () => epochSeconds;
}
