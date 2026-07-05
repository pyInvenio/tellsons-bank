# Clock Skew

`SessionTokenVerifier` accepts an injected `nowSeconds` function and an
`allowedClockSkewSeconds` value. The default skew is 30 seconds. This makes token
expiration testable without sleeping or using the wall clock.

The verifier delegates signature and algorithm enforcement to `jsonwebtoken`,
then performs explicit checks for required claims and expiration. Tests should
use fixed clocks and synthetic tokens only.

Coverage priorities:

- token accepted when expiration is within the configured skew
- token rejected just outside the skew window
- missing or nonnumeric `exp` claim
- custom skew values, including zero
- test fixtures that avoid dependence on the current date
