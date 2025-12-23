# Rate Limit Policy (Signup / Resend)

- Resend verification: max 5 attempts per rolling hour per email.
- Signup attempts: max 10 attempts per hour per IP.
- Abuse behavior: block for 1 hour after repeated violations.

Monitoring: log resend attempts and expose metric `resend_attempts_per_email` for alerting.
