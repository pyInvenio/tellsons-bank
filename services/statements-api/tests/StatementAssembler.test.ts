import { StatementAssembler } from '../src/StatementAssembler';

describe('StatementAssembler', () => {
  it('assembles redacted synthetic statement lines', () => {
    const result = new StatementAssembler().assemble('cust_test_001', [
      { postedAt: '2026-01-01', description: 'ACH transfer', amount: '10.00', classification: 'PII_REDACTED' }
    ]);

    expect(result).toContain('ACH transfer');
  });
});
