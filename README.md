# Tweetbar — Production-Scale Django Microblog

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Tweetbar** is a high-performance, production-ready microblogging platform. This project was built by **Hunain** as a first major application to showcase full-stack proficiency, scalability, and modern engineering practices for an internship.

## 🚀 Key Features
- **Dynamic Feed:** Real-time-ready feed with nested comments and likes.
- **Media Support:** Integrated with **Supabase Storage** for scalable image uploads.
- **Advanced Search:** Powered by **PostgreSQL Full-Text Search** for fast, relevant results.
- **Security First:** Implements Rate Limiting, CSRF protection, and HTTPS enforcement.
- **Optimized Performance:** Database queries are tuned with eager loading to prevent N+1 issues.
- **Admin Suite:** Custom dashboard for user management and system analytics.

## 🛠 Tech Stack
- **Backend:** Django 6 (Python)
- **Database:** PostgreSQL (via Supabase)
- **Storage:** Supabase Cloud Storage
- **Frontend:** Bootstrap 5, Vanilla JS
- **Deployment:** Vercel / Render

## 📦 Quick Start
1. **Clone & Setup:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Environment:** Configure `.env` with your `DATABASE_URL` and `SUPABASE_*` keys.
3. **Run:**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## 📖 Project Documentation
For a deep dive into why this app was built and how it's structured, see:
- [Why I Created This App](WHY_I_CREATED_THIS_APP.md)
- [Project Documentation](PROJECT_DOCUMENTATION.md)

---
**Maintainer:** [Hunain](https://github.com/hunain339)
