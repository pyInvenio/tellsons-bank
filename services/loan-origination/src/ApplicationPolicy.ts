export interface LoanApplication {
  applicationId: string;
  applicantId: string;
  requestedAmount: number;
  verifiedIncome: number;
  authenticatedSession: boolean;
}

export class ApplicationPolicy {
  decide(application: LoanApplication): 'APPROVE' | 'MANUAL_REVIEW' | 'DECLINE' {
    if (!application.applicationId.startsWith('loan_test_')) {
      throw new Error('synthetic application id required');
    }
    if (!application.authenticatedSession) {
      return 'DECLINE';
    }
    const ratio = application.requestedAmount / Math.max(application.verifiedIncome, 1);
    if (ratio > 0.45) {
      return 'MANUAL_REVIEW';
    }
    return 'APPROVE';
  }
}
