export class RetryPolicy {
  constructor(
    private readonly maxAttempts = 3,
    private readonly baseDelayMs = 100
  ) {}

  nextDelay(attempt: number): number | null {
    if (attempt >= this.maxAttempts) {
      return null;
    }
    return this.baseDelayMs * Math.pow(2, attempt);
  }
}
