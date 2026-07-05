# Hash Chain

`LogChain` appends immutable `AuditRecord` values. The first record uses
`GENESIS` as `previous_hash`; later records point at the previous record hash.
The hash payload includes sequence, previous hash, message, and ISO timestamp.

`verify` accepts either the internal records or an explicit list. It checks
sequence continuity, previous-hash linkage, and recomputed hash equality.

Coverage priorities:

- empty chain verifies successfully
- first record links to `GENESIS`
- sequence gaps fail verification
- changed `previous_hash` fails verification
- tampered message or timestamp fails verification
- externally supplied record lists do not mutate internal state
