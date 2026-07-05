# Oversized Inputs

PII functions receive strings from upstream profile and statement services.
`MaskingService` currently performs simple string operations without explicit
maximum lengths. `TokenizationService` hashes the complete namespace/value pair.

Tests should document behavior for oversized inputs because PII paths often fail
through unexpected memory use, slow regexes, or truncated redaction boundaries.
Fixtures must be synthetic and should avoid realistic account or SSN values.

Coverage priorities:

- very long account identifiers
- very long display names
- long values passed to tokenization
- malformed SSNs with extra digits
- masking output length and suffix behavior for long inputs
