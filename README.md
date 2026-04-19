# Tweetbar — Modern Django Microblog

A lightweight Twitter-like application built with Django 6 and Bootstrap 5.

Purpose
- Provide a simple social feed where users can post tweets, upload images, like posts, and comment with nested replies.

Quick Start (local)
- Create and activate a virtualenv:
  ```bash
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```
- Apply migrations and start server:
  ```bash
  python manage.py migrate
  python manage.py runserver
  ```

Where to look
- Project root: `hunain_project/`
- Main app: `tweet/` (models, views, templates)
- Global templates: `templates/`
- Static: `static/` and `staticfiles/`
- Media uploads: `media/`

Deployment notes
- Production uses PostgreSQL (Supabase) and can be deployed to Vercel/Render. Ensure `DATABASE_URL` and Supabase keys are set and migrations run during deployment.

Contributing
- Open issues or PRs for bug fixes and improvements. Run tests in `tweet/tests.py` when present.

Maintainer
- Hunain
