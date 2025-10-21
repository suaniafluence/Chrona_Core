# Security Hardening

This document tracks security hardening tasks and current measures for the Chrona backend.

## Implemented

- Security headers middleware (FastAPI):
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: no-referrer`
  - `Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=()`
  - `Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' 'unsafe-eval'`
  - Optional HSTS via `ENABLE_HSTS=true` (enable only behind HTTPS/ingress)

## TODO

- Rate limiting for sensitive endpoints (e.g., `/auth/token`, `/punch/validate`)
- Brute-force protection / lockout policy on authentication
- Password policy & strength checks on registration
- Secrets scanning in CI (e.g., Gitleaks) and a pre-commit hook
- Dependency vulnerability gating (Safety, npm audit thresholds)
- Audit logs alerting integration (SIEM/webhook)
- Review CSP for backoffice/kiosk in production

## Configuration

- `ENABLE_HSTS`: `true` to enable `Strict-Transport-Security` header in production (requires HTTPS). Default: `false`.

