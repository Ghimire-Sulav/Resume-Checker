# Production Readiness Assessment

## Completed

- Upload size restriction and supported-extension allowlist.
- In-memory parsing; no uploaded resume files or separate full-text copies are written to disk (structured analysis may repeat extracted details).
- Server-side API key configuration.
- Structured AI response validation and labeled demo fallback.
- SQLite persistence for analysis output and limited metadata.
- Automated tests for core local functionality.
- User-facing privacy and limitation notes.

## Incomplete / risks

- **Not production-ready for public or multi-user access.** Routes have no authentication or ownership checks; analysis IDs are guessable.
- Forms have no CSRF protection, endpoints have no rate limiting, and operational monitoring is minimal.
- The default development secret must be replaced with a strong environment secret; do not run Flask's development server in production.
- SQLite is suitable for local testing, not necessarily concurrent institutional use. No backup, retention, or deletion workflow is implemented.
- Gemini receives resume content when enabled. Institutional privacy review, vendor terms review, consent, and retention controls are required.
- Bootstrap and fonts load from third-party CDNs. Self-host assets or adopt a reviewed content security policy for stricter environments.
- Resume parser safety is limited to format libraries, file size caps, and in-memory handling; run in a restricted environment and keep dependencies updated.
- There is no automated PDF text-positive extraction test or browser-level accessibility audit.

## Recommended before deployment

1. Add login, role-based authorization, per-user record ownership, and non-guessable public identifiers.
2. Add CSRF protection, secure cookie flags, HTTPS, CSP, security headers, rate limiting, and request timeouts.
3. Set a strong secret, production WSGI server, structured privacy-safe logging, and monitored error handling.
4. Define consent and data-retention/deletion policies; review Gemini terms and institutional requirements before sending resumes externally.
5. Use managed database backups, migrations, and operational recovery procedures.
6. Add malware scanning or isolated parsing, dependency scanning, representative PDF tests, accessibility checks, and load tests.

## Final assessment

Suitable as a local educational prototype. Not suitable for public production deployment or processing real student data at scale until the incomplete safeguards are addressed.
