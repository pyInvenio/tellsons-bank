import { createSign, generateKeyPairSync } from 'crypto';
import jwt from 'jsonwebtoken';
import { systemClock } from '../src/Clock';
import { SessionTokenVerifier } from '../src/SessionTokenVerifier';

function makeKeyPair() {
  const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });

  return {
    privateKeyPem: privateKey.export({ type: 'pkcs1', format: 'pem' }).toString(),
    publicKeyPem: publicKey.export({ type: 'pkcs1', format: 'pem' }).toString()
  };
}

function signToken(
  payload: Record<string, unknown>,
  privateKeyPem: string,
  header: Record<string, unknown> = { alg: 'RS256', typ: 'JWT' }
) {
  return jwt.sign(payload as any, privateKeyPem as any, {
    algorithm: 'RS256',
    header: header as any
  } as any);
}

function signRawToken(
  payload: Record<string, unknown>,
  privateKeyPem: string,
  header: Record<string, unknown> = { alg: 'RS256', typ: 'JWT' }
) {
  const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
  const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const signingInput = `${encodedHeader}.${encodedPayload}`;
  const signature = createSign('RSA-SHA256').update(signingInput).sign(privateKeyPem, 'base64url');

  return `${signingInput}.${signature}`;
}

describe('SessionTokenVerifier', () => {
  it('reads the system clock seconds', () => {
    expect(Number.isInteger(systemClock.epochSeconds())).toBe(true);
  });

  it.each(['', 'header.payload', 'header.payload.sig.extra'])(
    'rejects malformed token shape: %s',
    token => {
      const { publicKeyPem } = makeKeyPair();
      const verifier = new SessionTokenVerifier(publicKeyPem, () => 1_700_000_000);

      expect(() => verifier.verify(token)).toThrow('malformed token');
    }
  );

  it('rejects unsigned tokens before signature verification', () => {
    const { publicKeyPem } = makeKeyPair();
    const verifier = new SessionTokenVerifier(publicKeyPem, () => 1_700_000_000);
    const token = [
      Buffer.from(JSON.stringify({ alg: 'none', typ: 'JWT' })).toString('base64url'),
      Buffer.from(JSON.stringify({ sub: 'user_test', exp: 1_700_000_060 })).toString('base64url'),
      'dummy-signature'
    ].join('.');

    expect(() => verifier.verify(token)).toThrow('unsigned tokens are not accepted');
  });

  it('verifies a valid RS256 token and returns its claims', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp - 120;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds);
    const token = signToken(
      {
        sub: 'user_test',
        scope: ['read:accounts', 'write:transfers'],
        exp
      },
      privateKeyPem
    );

    expect(verifier.verify(token)).toEqual({
      subject: 'user_test',
      scopes: ['read:accounts', 'write:transfers'],
      expiresAt: exp
    });
  });

  it('rejects a missing subject claim', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const verifier = new SessionTokenVerifier(publicKeyPem, () => 1_700_000_000);
    const token = signToken({ exp: 4_000_000_000 }, privateKeyPem);

    expect(() => verifier.verify(token)).toThrow('subject required');
  });

  it('rejects a missing expiration claim', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const verifier = new SessionTokenVerifier(publicKeyPem, () => 1_700_000_000);
    const token = signToken({ sub: 'user_test' }, privateKeyPem);

    expect(() => verifier.verify(token)).toThrow('expiration required');
  });

  it('rejects a nonnumeric expiration claim', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const verifier = new SessionTokenVerifier(publicKeyPem, () => 1_700_000_000);
    const token = signToken({ sub: 'user_test', exp: 4_000_000_000 }, privateKeyPem);
    const verifySpy = jest.spyOn(jwt, 'verify').mockReturnValue({
      sub: 'user_test',
      exp: '4000000000'
    } as any);

    try {
      expect(() => verifier.verify(token)).toThrow('expiration required');
    } finally {
      verifySpy.mockRestore();
    }
  });

  it('rejects tokens that have expired beyond the default skew', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp + 31;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds);
    const token = signToken(
      {
        sub: 'user_test',
        scope: 'read:accounts',
        exp
      },
      privateKeyPem
    );

    expect(() => verifier.verify(token)).toThrow('token expired');
  });

  it('accepts a token exactly within the default skew window', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp + 30;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds);
    const token = signToken(
      {
        sub: 'user_test',
        scope: 'read:accounts write:transfers',
        exp
      },
      privateKeyPem
    );

    expect(verifier.verify(token)).toMatchObject({
      subject: 'user_test',
      scopes: ['read:accounts', 'write:transfers'],
      expiresAt: exp
    });
  });

  it('rejects a token just outside the default skew window', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp + 31;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds);
    const token = signToken(
      {
        sub: 'user_test',
        scope: 'read:accounts',
        exp
      },
      privateKeyPem
    );

    expect(() => verifier.verify(token)).toThrow('token expired');
  });

  it('supports a custom zero-second clock skew', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds, 0);
    const token = signToken(
      {
        sub: 'user_test',
        scope: ['read:accounts'],
        exp
      },
      privateKeyPem
    );

    expect(verifier.verify(token)).toEqual({
      subject: 'user_test',
      scopes: ['read:accounts'],
      expiresAt: exp
    });
  });

  it('applies the zero-skew rejection boundary', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp + 1;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds, 0);
    const token = signToken(
      {
        sub: 'user_test',
        scope: undefined,
        exp
      },
      privateKeyPem
    );

    expect(() => verifier.verify(token)).toThrow('token expired');
  });

  it('normalizes an array scope, a space-delimited scope string, and a missing scope', () => {
    const { privateKeyPem, publicKeyPem } = makeKeyPair();
    const exp = 4_000_000_000;
    const nowSeconds = exp - 10;
    const verifier = new SessionTokenVerifier(publicKeyPem, () => nowSeconds);

    expect(
      verifier.verify(
        signToken(
          {
            sub: 'user_test_array',
            scope: ['read:accounts', 123, 'cust_test_scope'],
            exp
          },
          privateKeyPem
        )
      )
    ).toMatchObject({
      scopes: ['read:accounts', '123', 'cust_test_scope']
    });

    expect(
      verifier.verify(
        signToken(
          {
            sub: 'user_test_string',
            scope: 'read:accounts write:transfers',
            exp
          },
          privateKeyPem
        )
      )
    ).toMatchObject({
      scopes: ['read:accounts', 'write:transfers']
    });

    expect(
      verifier.verify(
        signToken(
          {
            sub: 'user_test_missing_scope',
            exp
          },
          privateKeyPem
        )
      )
    ).toMatchObject({
      scopes: []
    });
  });
});
