import { buildAuthRouter } from '../src/AuthRouter';

function getSessionHandler(router: any) {
  const layer = router.stack.find((entry: any) => entry.route?.path === '/session');

  if (!layer) {
    throw new Error('session route not found');
  }

  return layer.route.stack[0].handle;
}

function makeReq(headers: Record<string, string | undefined>) {
  return {
    header(name: string) {
      return headers[name.toLowerCase()];
    }
  };
}

function makeRes() {
  return {
    statusCode: undefined as number | undefined,
    payload: undefined as unknown,
    status(code: number) {
      this.statusCode = code;
      return this;
    },
    json(body: unknown) {
      this.payload = body;
      return this;
    }
  };
}

describe('buildAuthRouter', () => {
  it('returns a generic 401 when the authorization header is missing', () => {
    const verifier = {
      verify: jest.fn(() => {
        throw new Error('missing token');
      })
    } as any;
    const handler = getSessionHandler(buildAuthRouter(verifier));
    const req = makeReq({});
    const res = makeRes();

    handler(req, res);

    expect(verifier.verify).toHaveBeenCalledWith('');
    expect(res.statusCode).toBe(401);
    expect(res.payload).toEqual({ error: 'invalid_session' });
  });

  it('strips a mixed-case bearer prefix with extra whitespace before verification', () => {
    const verifierResult = {
      subject: 'user_test',
      scopes: ['read:accounts'],
      expiresAt: 1_700_000_060
    };
    const verifier = {
      verify: jest.fn().mockReturnValue(verifierResult)
    } as any;
    const handler = getSessionHandler(buildAuthRouter(verifier));
    const req = makeReq({ authorization: 'bEaReR     token_test_123' });
    const res = makeRes();

    handler(req, res);

    expect(verifier.verify).toHaveBeenCalledWith('token_test_123');
    expect(res.statusCode).toBeUndefined();
    expect(res.payload).toEqual(verifierResult);
  });

  it('maps verifier failures to invalid_session without leaking internal details', () => {
    const verifier = {
      verify: jest.fn(() => {
        throw new Error('internal verifier failure: secret_token_test');
      })
    } as any;
    const handler = getSessionHandler(buildAuthRouter(verifier));
    const req = makeReq({ authorization: 'Bearer token_test_failure' });
    const res = makeRes();

    handler(req, res);

    expect(verifier.verify).toHaveBeenCalledWith('token_test_failure');
    expect(res.statusCode).toBe(401);
    expect(res.payload).toEqual({ error: 'invalid_session' });
    expect(JSON.stringify(res.payload)).not.toContain('secret_token_test');
  });
});
