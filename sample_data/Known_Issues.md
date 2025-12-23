# Known Issues

1. Duplicate account creation reported occasionally when concurrent signup requests use the same email (race condition).
	- Symptoms: two accounts created with same email in the DB; downstream systems reject one.
	- Repro steps: send two simultaneous POST /signup requests with same email.
	- Mitigation: enforce unique constraint at DB level and perform idempotent signup flow.

2. Verification emails not received sometimes due to mail provider rate limits.
	- Symptoms: delivery failures in logs, users report not receiving verification emails.
	- Mitigation: implement retry queue and circuit-breaker for external email provider.

3. Weak password accepted on client due to missing server validation in older deployments.
	- Symptoms: user accounts created with weak passwords; security concern.
	- Mitigation: ensure server-side password policy enforcement and add unit tests.

4. Resend verification spam — multiple resends within seconds.
	- Mitigation: server-side throttling (e.g., 5/hr) and client-side cooldown UI.

5. UI: mobile layout may hide CTA on small viewports.
	- Mitigation: responsive layout audit and automated screenshot tests.