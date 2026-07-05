import jwt, { JwtPayload } from 'jsonwebtoken';

export interface VerificationResult {
  subject: string;
  scopes: string[];
  expiresAt: number;
}

export class SessionTokenVerifier {
  constructor(
    private readonly publicKey: string,
    private readonly nowSeconds: () => number = () => Math.floor(Date.now() / 1000),
    private readonly allowedClockSkewSeconds = 30
  ) {}

  verify(token: string): VerificationResult {
    if (!token || token.split('.').length !== 3) {
      throw new Error('malformed token');
    }

    const header = JSON.parse(Buffer.from(token.split('.')[0], 'base64url').toString('utf8'));
    if (header.alg === 'none') {
      throw new Error('unsigned tokens are not accepted');
    }

    const decoded = jwt.verify(token, this.publicKey, {
      algorithms: ['RS256'],
      clockTolerance: this.allowedClockSkewSeconds
    }) as JwtPayload;

    if (!decoded.sub) {
      throw new Error('subject required');
    }
    if (typeof decoded.exp !== 'number') {
      throw new Error('expiration required');
    }
    if (decoded.exp + this.allowedClockSkewSeconds < this.nowSeconds()) {
      throw new Error('token expired');
    }

    const scopes = Array.isArray(decoded.scope)
      ? decoded.scope.map(String)
      : String(decoded.scope ?? '').split(' ').filter(Boolean);

    return { subject: decoded.sub, scopes, expiresAt: decoded.exp };
  }
}
