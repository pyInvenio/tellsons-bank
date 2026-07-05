import { RetryPolicy } from './RetryPolicy';

export interface NotificationClient {
  send(message: DispatchMessage): Promise<void>;
}

export interface DispatchMessage {
  channel: 'email' | 'sms' | 'push';
  recipientToken: string;
  templateId: string;
  attributes: Record<string, string>;
}

export class Dispatcher {
  constructor(
    private readonly client: NotificationClient,
    private readonly policy: RetryPolicy
  ) {}

  async dispatch(message: DispatchMessage): Promise<'sent' | 'failed'> {
    let attempt = 0;
    while (true) {
      try {
        await this.client.send(message);
        return 'sent';
      } catch {
        const next = this.policy.nextDelay(attempt);
        if (next === null) {
          return 'failed';
        }
        attempt += 1;
      }
    }
  }
}
