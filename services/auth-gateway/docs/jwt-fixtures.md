# JWT Fixtures

Authentication tests should use synthetic JWT fixtures with generated keys. Do
not use production-like issuer names, customer identifiers, or real public keys.
The service only needs enough fixture data to exercise parser and claim logic:
header, subject, expiration, and optional scopes.

`SessionTokenVerifier` rejects malformed token shape before calling
`jsonwebtoken`. It also rejects `alg: none` before signature verification. Those
branches are important because they represent input-validation behavior at the
trust boundary.

Coverage priorities:

- malformed token with fewer or more than three segments
- invalid base64url header
- `alg: none` rejection
- missing `sub` and missing `exp`
- scope as a space-delimited string and as an array
