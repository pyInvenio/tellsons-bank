# Routing

`AuthRouter` exposes `GET /auth/session` through `buildAuthRouter`. It reads the
`Authorization` header, strips a case-insensitive `Bearer` prefix, and returns
the verifier result as JSON. Any verifier error maps to a generic
`401 invalid_session` response.

Router tests should use a fake `SessionTokenVerifier` or a narrow mock. They
should not require real JWT signing unless the test is specifically covering
`SessionTokenVerifier`.

Coverage priorities:

- missing authorization header
- bearer prefix with mixed casing and extra whitespace
- verifier success response shape
- verifier failure maps to `401`
- no internal error message leaks in the response body
