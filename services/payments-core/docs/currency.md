# Currency Handling

`AmountValidator` accepts a raw decimal string and an ISO currency code. It uses
`Currency.getInstance` to validate the code and then normalizes the amount to two
decimal places using `RoundingMode.HALF_EVEN`.

The service is intentionally conservative: currencies with more than two default
fraction digits are rejected because downstream ledger records and statement
rendering expect cents-style precision. The validator currently relies on the JDK
for null or unknown currency errors, so tests should distinguish expected
business exceptions from raw platform exceptions.

Coverage priorities:

- null, blank, and unknown currency codes
- currencies with zero, two, and three fraction digits
- half-even rounding boundaries such as `10.005` and `10.015`
- amounts that round over a policy boundary
- mismatch between transfer currency and source/destination account currency
