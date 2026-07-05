import express from 'express';
import { SessionTokenVerifier } from './SessionTokenVerifier';

export function buildAuthRouter(verifier: SessionTokenVerifier): express.Router {
  const router = express.Router();
  router.get('/session', (req, res) => {
    const authorization = req.header('authorization') ?? '';
    const token = authorization.replace(/^Bearer\s+/i, '');
    try {
      res.json(verifier.verify(token));
    } catch {
      res.status(401).json({ error: 'invalid_session' });
    }
  });
  return router;
}
