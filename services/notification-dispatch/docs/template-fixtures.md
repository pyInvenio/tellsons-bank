# Template Fixtures

`TemplateRegistry` is a small in-memory registry for notification template
bodies. It validates that both template ID and body are present, then returns the
registered body by ID.

Tests should use synthetic template IDs such as `transfer-posted` or
`audit-alert`. Template bodies should avoid customer-like names, account
numbers, or realistic phone/email values unless they come from `docs/fixtures`
and are clearly synthetic.

Coverage priorities:

- missing ID and missing body rejection
- unknown template lookup
- replacement when the same ID is registered twice
- template bodies with placeholder-looking attributes
- fixture data that does not resemble real customer notifications
