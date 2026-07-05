export interface TransactionEvent {
  eventId: string;
  accountId: string;
  amount: string;
  currency: string;
  occurredAt: string;
  metadata?: Record<string, string>;
}
