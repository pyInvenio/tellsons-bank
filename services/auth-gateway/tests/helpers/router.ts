import express from 'express';
import type { AddressInfo } from 'net';
import type { Server } from 'http';
import { buildAuthRouter, AuthRouterOptions } from '../../src/AuthRouter';
import type { SessionTokenVerifier } from '../../src/SessionTokenVerifier';

export interface RunningRouter {
  baseUrl: string;
  close: () => Promise<void>;
}

/**
 * Mounts the auth router on an ephemeral-port express app so tests can drive it
 * over real HTTP without a fixed port or wall-clock sleeps. No downstream
 * network calls are made; the verifier is always a caller-supplied fake.
 */
export async function startAuthRouter(
  verifier: Pick<SessionTokenVerifier, 'verify'>,
  options?: AuthRouterOptions
): Promise<RunningRouter> {
  const app = express();
  // Omit options entirely when unset so the router's default-parameter branch
  // is exercised alongside the explicit-options paths.
  const router =
    options === undefined
      ? buildAuthRouter(verifier as SessionTokenVerifier)
      : buildAuthRouter(verifier as SessionTokenVerifier, options);
  app.use('/auth', router);
  const server: Server = await new Promise((resolve) => {
    const s = app.listen(0, () => resolve(s));
  });
  const { port } = server.address() as AddressInfo;
  return {
    baseUrl: `http://127.0.0.1:${port}`,
    close: () =>
      new Promise<void>((resolve, reject) =>
        server.close((err) => (err ? reject(err) : resolve()))
      )
  };
}
