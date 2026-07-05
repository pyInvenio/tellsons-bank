# Channel Routing

`DispatchMessage.channel` is one of `email`, `sms`, or `push`. The current
`Dispatcher` does not branch on channel; it forwards the full message to the
configured `NotificationClient`. Channel-specific behavior is expected to live
behind the client adapter.

Tests should treat channel as part of the message contract and verify the
dispatcher preserves it across retries. They should not call real email, SMS, or
push providers.

Coverage priorities:

- each supported channel is passed through unchanged
- recipient token is treated as opaque synthetic data
- attributes are not mutated between retries
- client errors do not leak provider details into the returned status
- unsupported channel behavior is documented at the TypeScript boundary
