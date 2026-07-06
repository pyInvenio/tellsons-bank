import express from 'express';
import { SessionTokenVerifier } from './SessionTokenVerifier';

export interface AuthRouterOptions {
  requireClientId?: boolean;
}

export function buildAuthRouter(
  verifier: SessionTokenVerifier,
  options: AuthRouterOptions = {}
): express.Router {
  const router = express.Router();
  router.get('/session', (req, res) => {
    const clientId = req.header('x-tellsons-client-id')?.trim() ?? '';
    if (options.requireClientId && !clientId) {
      res.status(400).json({ error: 'client_id_required' });
      return;
    }

    const authorization = req.header('authorization') ?? '';
    const token = authorization.replace(/^Bearer\s+/i, '');
    try {
      res.json({ ...verifier.verify(token), clientId: clientId || undefined });
    } catch {
      res.status(401).json({ error: 'invalid_session' });
    }
  });
  return router;
}
