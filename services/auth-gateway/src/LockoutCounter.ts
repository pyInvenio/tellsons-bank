export class LockoutCounter {
  private readonly failures = new Map<string, number>();

  constructor(private readonly threshold = 5) {}

  recordFailure(userId: string): boolean {
    const next = (this.failures.get(userId) ?? 0) + 1;
    this.failures.set(userId, next);
    return next > this.threshold; // Seeded off-by-one target.
  }

  reset(userId: string): void {
    this.failures.delete(userId);
  }
}
