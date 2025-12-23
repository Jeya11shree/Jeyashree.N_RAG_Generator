# PRD: Signup Flow

## Overview
The Signup feature allows unauthenticated users to register for an account using email and password, with optional email verification. The flow is designed to be simple, secure, and resilient to common failure modes (duplicate accounts, weak passwords, expired verification tokens).

## Goals
- Allow new users to create accounts with email + password.
- Enforce password policy and provide clear inline validation.
- Prevent duplicate accounts for the same email.
- Send verification email with single-use token and expiry.
- Provide resend verification with throttling.

## Stakeholders
- Product: onboarding conversion
- Engineering: backend, email service, security
- QA: test coverage for happy/negative/boundary cases

## User Stories
- As an unauthenticated user, I can create an account using my email and a password so I can access the product.
- As a user, I should receive a verification email and verify my address before sensitive flows.
- As a user, I should see inline validation for password requirements.
- As an admin, I can control resend rate and token expiry via configuration.

## Acceptance Criteria
- POST `/signup` accepts `email`, `password`, optional `name` and returns 201 with a non-sensitive profile and `verification_sent: true` if email sending enabled.
- Duplicate email returns 409 with code `EMAIL_EXISTS`.
- Weak passwords return 400 with code `WEAK_PASSWORD` and explanation.
- Verification token link expires after configured TTL (default: 24 hours).
- Resend verification limited to 5 attempts per hour per email by default.

## Password Policy
- Minimum 8 characters
- At least one uppercase letter, one lowercase letter, one digit, and one symbol
- Not in common-passwords blacklist

## Error Messages (user-facing)
- "Email already exists" (on duplicate)
- "Password does not meet complexity requirements" (with inline hints)
- "Verification token invalid or expired" (on verification link)

## Redirects & Post-Signup Behavior
- After successful signup, user may be:
	- shown an "Check your email" confirmation page (default) or
	- automatically logged in (if email verification is optional in env)
- If auto-login is enabled, the response includes a short-lived session token.

## Flows
### Happy path
1. User opens Signup page
2. User enters email and strong password
3. User submits form
4. Server returns 201 and sends verification email
5. User clicks verification link and account becomes active

### Negative Cases
- Duplicate email -> 409
- Invalid email format -> 400
- Weak password -> 400
- Resend abuse -> 429 (too many requests)

## Observability & Metrics
- Signup attempts per minute
- Successful signups per hour
- Verification emails sent / failed
- Resend rate per email

## Implementation Notes
- Use server-side validation in addition to client-side checks.
- Tokens must be single-use and stored hashed in DB.
- Use a templated email with domain allowance checks.

## Data Schema (simplified)
- User: id, email (unique), password_hash, is_verified (bool), created_at, verification_sent_at

## Test Considerations
- Positive flows for create + verify
- Negative: duplicate, weak password, invalid token, expired token
- Boundary: max email length, max name length