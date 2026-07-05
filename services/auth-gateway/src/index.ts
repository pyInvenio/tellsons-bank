import express from 'express';
import { buildAuthRouter } from './AuthRouter';
import { SessionTokenVerifier } from './SessionTokenVerifier';

const publicKey = process.env.AUTH_PUBLIC_KEY ?? 'synthetic-public-key';
const app = express();
app.use('/auth', buildAuthRouter(new SessionTokenVerifier(publicKey)));

export { app };
