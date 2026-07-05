# Sink Contract

`FileAuditSink.write` appends one formatted line to a UTF-8 file and creates the
parent directory if needed. `AuditFormatter.format` serializes sequence,
previous hash, current hash, timestamp, and message using pipe separators.

Tests should use temporary directories or mocks. They should not write to shared
paths or depend on a pre-existing local file. Formatter tests should use fixed
`AuditRecord` values so output is deterministic.

Coverage priorities:

- parent directory creation
- append behavior across multiple writes
- newline termination
- formatter field order
- sink exceptions for unwritable paths, where the platform allows simulation
