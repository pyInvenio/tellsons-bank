# Bootstrap Target

`audit-logger` is intentionally missing test infrastructure. There is no pytest
configuration, no coverage command, no CI lane, and no established mocks for
file sinks. This makes it the clearest service for proving test-infrastructure
bootstrap work.

Production code should not change during a coverage-only remediation PR. The
first acceptable PR should add tests, fixtures, coverage reporting, and CI wiring
while preserving current runtime behavior.

Coverage priorities:

- add pytest and coverage configuration
- mock or temp-file `FileAuditSink` writes
- cover `LogChain.verify` success and failure paths
- cover `Redactor` PII suppression
- add an audit-logger CI job matching repository workflow conventions
