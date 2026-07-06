import express from 'express';
import request from 'supertest';
import { buildAuthRouter, AuthRouterOptions } from '../src/AuthRouter';
import { SessionTokenVerifier, VerificationResult } from '../src/SessionTokenVerifier';

function makeApp(
  verifyResult: VerificationResult | Error,
  options: AuthRouterOptions = {}
): express.Express {
  const verifier = {
    verify: jest.fn(() => {
      if (verifyResult instanceof Error) throw verifyResult;
      return verifyResult;
    }),
  } as unknown as SessionTokenVerifier;
  const app = express();
  app.use(buildAuthRouter(verifier, options));
  return app;
}

const VALID_SESSION: VerificationResult = {
  subject: 'cust_test_0001',
  scopes: ['read', 'write'],
  expiresAt: 9999999999,
};

describe('AuthRouter /session', () => {
  describe('without requireClientId', () => {
    it('returns session details when token is valid', async () => {
      const app = makeApp(VALID_SESSION);
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc');
      expect(res.status).toBe(200);
      expect(res.body.subject).toBe('cust_test_0001');
      expect(res.body.scopes).toEqual(['read', 'write']);
    });

    it('returns 401 for invalid token', async () => {
      const app = makeApp(new Error('malformed token'));
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer bad_token');
      expect(res.status).toBe(401);
      expect(res.body.error).toBe('invalid_session');
    });

    it('omits clientId from response when header is absent', async () => {
      const app = makeApp(VALID_SESSION);
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc');
      expect(res.body.clientId).toBeUndefined();
    });

    it('includes clientId in response when header is provided', async () => {
      const app = makeApp(VALID_SESSION);
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc')
        .set('x-tellsons-client-id', 'client_test_web_01');
      expect(res.status).toBe(200);
      expect(res.body.clientId).toBe('client_test_web_01');
    });

    it('does not reject missing client id when requireClientId is off', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: false });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc');
      expect(res.status).toBe(200);
    });
  });

  describe('with requireClientId enabled', () => {
    it('returns 400 when x-tellsons-client-id header is missing', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc');
      expect(res.status).toBe(400);
      expect(res.body.error).toBe('client_id_required');
    });

    it('returns 400 when x-tellsons-client-id header is empty string', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc')
        .set('x-tellsons-client-id', '');
      expect(res.status).toBe(400);
      expect(res.body.error).toBe('client_id_required');
    });

    it('returns 400 when x-tellsons-client-id is whitespace only', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc')
        .set('x-tellsons-client-id', '   ');
      expect(res.status).toBe(400);
      expect(res.body.error).toBe('client_id_required');
    });

    it('succeeds with valid client id and valid token', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc')
        .set('x-tellsons-client-id', 'client_test_mobile_02');
      expect(res.status).toBe(200);
      expect(res.body.subject).toBe('cust_test_0001');
      expect(res.body.clientId).toBe('client_test_mobile_02');
    });

    it('trims whitespace from client id before using it', async () => {
      const app = makeApp(VALID_SESSION, { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer test_token_abc')
        .set('x-tellsons-client-id', '  client_test_padded  ');
      expect(res.status).toBe(200);
      expect(res.body.clientId).toBe('client_test_padded');
    });

    it('still returns 401 for invalid token even with valid client id', async () => {
      const app = makeApp(new Error('token expired'), { requireClientId: true });
      const res = await request(app)
        .get('/session')
        .set('Authorization', 'Bearer expired_token')
        .set('x-tellsons-client-id', 'client_test_web_01');
      expect(res.status).toBe(401);
      expect(res.body.error).toBe('invalid_session');
    });
  });
});
