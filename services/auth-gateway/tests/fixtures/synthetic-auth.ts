/**
 * Synthetic auth fixtures. All identifiers are obviously non-production and use
 * the mandated demo/test prefixes and documentation ranges. No real customer
 * data, secrets, or tokens are stored here.
 */
export const SYNTHETIC: {
  subject: string;
  clientId: string;
  scopesArray: string[];
  scopesString: string;
  sourceIp: string;
  emailDomain: string;
} = {
  subject: 'cust_demo_0001',
  clientId: 'client_demo_web_0001',
  scopesArray: ['accounts:read', 'statements:read'],
  scopesString: 'accounts:read statements:read',
  // Documentation IP range (RFC 5737) for any log-adjacent assertions.
  sourceIp: '203.0.113.7',
  emailDomain: 'example.test'
};
