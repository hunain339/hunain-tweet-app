Deployment & DevOps Recommendations
-----------------------------------

Checklist for production deploys
- Use a managed Postgres (Supabase) with automated backups and read replicas if needed.
- Run schema migrations during maintenance window or use `CREATE INDEX CONCURRENTLY` for indexes.
- Use Redis for caching and ephemeral session store; enable persistence depending on needs.
- Configure observability: Prometheus + Grafana, Sentry for error tracking, and slow query logging.
- CI: run smoke test step that installs `requirements-prod.txt` and runs `manage.py check` + key tests.

Runbook for index creation
- Create index with `CONCURRENTLY` and monitor `pg_stat_activity` and locks.
- If downtime unacceptable, add index on a replica and promote.
