# SSN Boundaries

`MaskingService.maskSsn` strips non-digits before deciding how to mask. Exactly
nine digits produce `***-**-` plus the last four digits. Other digit counts
still return a masked suffix based on whatever digits are present.

This is intentionally permissive so tests can expose edge cases. A stricter
policy may eventually reject invalid SSNs instead of masking best-effort input.

Coverage priorities:

- canonical `000-00-0000` style synthetic SSN
- input with spaces or punctuation
- fewer than four digits
- more than nine digits
- null, blank, and whitespace-only input
