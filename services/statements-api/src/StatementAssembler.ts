export interface StatementLine {
  postedAt: string;
  description: string;
  amount: string;
  classification: 'PUBLIC' | 'PII_REDACTED';
}

export class StatementAssembler {
  assemble(customerId: string, lines: StatementLine[]): string {
    if (!customerId.startsWith('cust_test_')) {
      throw new Error('synthetic customer id required');
    }
    const unsafe = lines.find((line) => line.classification !== 'PII_REDACTED');
    if (unsafe) {
      throw new Error(`unredacted statement line: ${unsafe.description}`);
    }
    return lines.map((line) => `${line.postedAt}|${line.description}|${line.amount}`).join('\n');
  }
}
