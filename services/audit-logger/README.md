# Audit Logger

Python service for tamper-evident audit logging. This service intentionally has no pytest
setup, no coverage configuration, no CI job, and no test doubles. It is the bootstrap
target for the Tellson's audit coverage program.

## Expected First Test PR

Bootstrap pytest and coverage, add sink mocks, cover `LogChain` tamper/gap cases, cover
`Redactor` PII suppression, and add an audit-logger CI job without changing production code.
