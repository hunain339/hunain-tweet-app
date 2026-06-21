# Tweetbar

## Project Overview
Tweetbar is a full-featured, modern social media platform built to demonstrate production-grade engineering principles. It allows users to authenticate, create tweets, upload images, search for content, and interact via likes and comments. The application is designed using a clean Service/Selector architecture to ensure scalability and maintainability.

## Features
- **Authentication:** Secure user registration, login, and session management.
- **Tweet Creation:** Post text and media content.
- **Image Uploads:** Seamless media storage powered by Supabase.
- **Search:** Query tweets and users efficiently.
- **Likes & Comments:** Interactive engagement system for user content.

## Tech Stack
- **Backend:** Python, Django
- **Database:** PostgreSQL
- **Storage:** Supabase Storage
- **Architecture:** Service/Selector pattern

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/tweet-app.git
   cd tweet-app
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *Note: Ensure you have a Supabase project set up and provide the required keys in `.env`.*

5. **Apply Migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```

## Deployment
The application is structured to be deployed easily to modern platforms like Vercel or Render. 
- Ensure `ALLOWED_HOSTS` is updated.
- Use `gunicorn` for the WSGI server in production.
- Static files are configured to use WhiteNoise.
- Media files are handled remotely by Supabase.

## Screenshots
*(Add screenshots or a GIF demonstration of the application in the `screenshots` folder.)*
