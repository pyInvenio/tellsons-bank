# Redaction

`Redactor` suppresses SSNs matching `000-00-0000` style patterns and account IDs
matching `acct_` plus six or more alphanumeric/underscore characters. It returns
the redacted message string for later formatting and sink writes.

Tests should use synthetic account IDs and fake SSNs only. They should include
negative cases so reviewers can see exactly what the regex does and does not
catch.

Coverage priorities:

- single and multiple SSNs in one line
- account IDs surrounded by punctuation
- messages containing both SSN and account ID
- near misses that should remain unchanged
- empty strings and messages without PII
