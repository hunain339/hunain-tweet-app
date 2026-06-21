# Tweetbar Architecture Documentation

## 1. Overview
Tweetbar is a modern social media application built with Django and PostgreSQL, utilizing a robust Service/Selector architecture to ensure scalability, maintainability, and clean separation of concerns.

## 2. Application Architecture

The application is structured using the Service/Selector pattern:
- **Views (Class-Based Views):** Handle HTTP requests, responses, and routing.
- **Services (`services/`):** Encapsulate business logic and database write operations (e.g., creating a tweet, liking a tweet).
- **Selectors (`selectors/`):** Encapsulate database read operations and query optimizations (e.g., fetching user feeds, searching tweets).
- **Models:** Define the database schema and core data constraints.

## 3. Database Relationships

The relational data model is managed by PostgreSQL:
- **User:** Extended Django user model handling authentication and profiles.
- **Tweet:** Core content entity, contains foreign keys to the author and supports image attachments.
- **Comment:** Relates to both a User (author) and a Tweet (parent).
- **Like:** A many-to-many relationship mapping Users to Tweets.

## 4. Authentication Process
- **Session-based Authentication:** Utilizes Django's robust built-in session framework.
- **Security:** Passwords are mathematically hashed (PBKDF2) by Django. Session cookies are secured with HTTPOnly and Secure flags in production.
- **Registration Flow:** Custom signup views enforcing unique emails and secure password requirements.

## 5. Storage Architecture
- **Supabase Storage:** Used for handling all user-generated media (profile pictures, tweet images).
- **Django Storages Integration:** Boto3/S3 compatibility layer connects Django's FileField directly to Supabase Storage, ensuring scalable, decoupled media management.

## 6. Deployment Architecture
- **Hosting:** Deployed as a serverless/managed service application (e.g., Vercel or Render).
- **Database:** Supabase Managed PostgreSQL.
- **Static Files:** WhiteNoise is used to serve static assets efficiently directly from the application layer.
- **Environment Management:** Configurations are driven entirely by environment variables (`.env`).
