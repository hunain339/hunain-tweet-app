Security Audit (OWASP) Checklist
--------------------------------

High-level checklist
- Ensure proper authentication & session handling.
- Validate and sanitize all user inputs.
- Use parameterized queries (ORM default) and avoid raw SQL.
- Enforce strong password rules and rate-limit authentication endpoints.
- Ensure HTTPS everywhere; set `SECURE_*` settings.
- Configure Content Security Policy (CSP) for templates.
- Review permissions on file uploads and storage (Supabase).
- Run dependency vulnerability scans (`safety`, `bandit`).

Next steps
- Run `bandit` across the repo and fix high severity findings.
- Audit third-party packages and remove unused ones.
