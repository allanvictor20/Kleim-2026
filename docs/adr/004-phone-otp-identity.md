# ADR-004: Phone number with SMS one-time code as primary identity

- **Status:** Accepted
- **Date:** [project start]
- **Related:** SDD §21, AUTH-01; Implementation Plan M1

## Context

Most users in Kampala identify by phone number, pay by mobile money and are reached by SMS. Many do not use email regularly. Passwords are often forgotten and reused.

## Decision

Users sign up and log in with a phone number verified by a 6-digit SMS code. Email is optional for customers and recommended for sellers. Tokens: 15-minute access token and 30-day rotating refresh token.

## Consequences

- Positive: familiar, fast sign-up; the verified number doubles as the delivery and payment contact.
- Negative: SMS costs money per login and depends on the SMS provider; SIM swap is a risk.
- Follow-up: rate limits on OTP requests (API Specification §2.7); re-verify the phone before changing payout numbers.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| Email and password | Poor fit for the audience; password resets add support load |
| Google sign-in only | Not universal among target users; still need a verified phone |
