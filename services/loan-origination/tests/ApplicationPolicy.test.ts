import { ApplicationPolicy } from '../src/ApplicationPolicy';

describe('ApplicationPolicy', () => {
  it('approves low-ratio synthetic applications with authenticated sessions', () => {
    expect(new ApplicationPolicy().decide({
      applicationId: 'loan_test_001',
      applicantId: 'cust_test_001',
      requestedAmount: 1000,
      verifiedIncome: 5000,
      authenticatedSession: true
    })).toBe('APPROVE');
  });
});
