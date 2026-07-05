# Transfer Limits

The maximum single transfer amount is `250000.00`, enforced in
`AmountValidator`. The validator rejects negative normalized amounts and any
amount greater than the limit. It currently allows zero, which may be a policy
gap depending on the caller.

`TransferService` applies account-level checks after validation. It rejects
currency mismatch and insufficient available balance before posting a ledger
entry. Balance comparison uses the normalized `BigDecimal` value returned by the
validator.

Coverage priorities:

- exactly `250000.00` is accepted
- values just above the limit are rejected after rounding
- negative zero and small negative decimals normalize predictably
- zero-amount transfers document the current behavior
- insufficient funds compares numeric value rather than string shape
