# Token Lifecycle

`TokenizationService.tokenize` creates deterministic synthetic tokens by hashing
`namespace:value` with SHA-256 and returning a `tok_` prefix plus the first 24
hex characters. The same namespace and value should always produce the same
token; changing either input should produce a different token.

The token is not reversible and should be treated as an identifier, not a secret.
Tests should avoid asserting the full hash algorithm everywhere, but they should
pin enough behavior to detect accidental namespace loss.

Coverage priorities:

- namespace required
- value required
- deterministic output for repeated calls
- different namespaces for the same value
- output prefix and length
