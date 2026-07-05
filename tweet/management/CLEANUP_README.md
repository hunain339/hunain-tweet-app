This document describes safe steps to remove unwanted comments/posts from production and how to seed clean tweets for the recruiter demo.

Prerequisites
- Access to the production Postgres database (connection string or via psql).
- Or the ability to run Django management commands against production by setting `DATABASE_URL`.

Option A — Run the management command against production DB

1. On your workstation (or CI runner), set `DATABASE_URL` to point at the production database. Example:

```bash
export DATABASE_URL="postgres://db_user:REDACTED@db-host:5432/dbname"
```

2. From the project root, run the dry-run first to see what would be deleted:

```bash
/sandbox_venv/bin/python manage.py clean_production_content \
  --delete-text "The dark mode is stunning! Very easy on the eyes. 🌑" \
  --dry-run
```

3. If the output looks correct, run the same command without `--dry-run` to perform deletion:

```bash
/sandbox_venv/bin/python manage.py clean_production_content \
  --delete-text "The dark mode is stunning! Very easy on the eyes. 🌑"
```

4. (Optional) Create seed tweets to reach desired feed size:

```bash
/sandbox_venv/bin/python manage.py clean_production_content --seed-count 50 --seed-user your_seed_username
```

Option B — Run SQL directly against Postgres (psql or Supabase SQL editor)

- Delete comments with exact text (one-liner):

```sql
-- preview
SELECT id, user_id, text FROM tweet_comment WHERE text = 'The dark mode is stunning! Very easy on the eyes. 🌑';

-- delete (run only after preview)
DELETE FROM tweet_comment WHERE text = 'The dark mode is stunning! Very easy on the eyes. 🌑';
```

- Delete comments matching a regex (Postgres ~* is case-insensitive regex):

```sql
-- preview
SELECT id, user_id, text FROM tweet_comment WHERE text ~* 'dark mode|The UI is really smooth|upload images|asdasd|test';

-- delete
DELETE FROM tweet_comment WHERE text ~* 'dark mode|The UI is really smooth|upload images|asdasd|test';
```

Verification
- After running changes, fetch the production page and re-scan HTML:

```bash
curl -sL https://hunain-gujjar-tweet-prod.vercel.app/tweet/ | grep -iE "The dark mode is stunning|The UI is really smooth|upload images|test|asdasd"
```

Notes and safety
- Always run dry-run / preview queries first.
- If running against Supabase, use the SQL editor or connect with `psql`.
- For `manage.py` runs, ensure your virtualenv has project deps and `DATABASE_URL` points to production.

If you want, provide the production DB connection string (or run the provided commands yourself) and I will run the cleanup and re-verify the site.