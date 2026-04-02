# 🐦 Tweetbar - Modern Django Twitter Clone

Tweetbar is a feature-rich, high-performance social media application built with **Django 6.0** and **Bootstrap 5.3**. It features a stunning dark-mode aesthetic with vibrant orange accents, providing a premium user experience.

---

## 🚀 Key Features

- **User Authentication**: Secure Login, Register, and Logout functionality with polished Bootstrap UI cards.
- **Tweet Management**: Create, Edit, and Delete tweets (with image support).
- **Social Interactions**:
  - **❤️ Like System**: Like and unlike tweets with real-time counters.
  - **💬 Comments**: Add and view replies on any tweet.
- **User Profiles**: View specific user profiles showing their join date, tweet count, and cumulative likes.
- **Real-time Search**: Search tweets by content or username directly from the navbar.
- **Pagination**: Smooth navigation through the feed with 10 tweets per page.
- **Flash Messages**: Interactive "Toast" style notifications for all user actions.
- **Responsive Design**: Fully mobile-friendly layout built on a modern grid system.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Django 6.0
- **Database**: SQLite (Default)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Vanilla CSS, Bootstrap 5.3
- **Media**: Pillow (for image handling)

---

## 📦 Local Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd django_2/hunain_project
```

### 2. Set up Virtual Environment
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/macOS
# or
myenv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install django pillow sqlparse autopep8
```

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

---

## 📁 Project Structure

- `hunain_project/`: Project configuration and root URLs.
- `tweet/`: Main application logic.
  - `models.py`: Database schema (Tweet, Comment).
  - `views.py`: Application logic and route handling.
  - `forms.py`: Django model forms for tweets and users.
  - `templates/`: HTML templates for the app views.
- `static/`: Static assets (CSS, JS).
- `media/`: User-uploaded images.
- `templates/`: Global base templates (layout, registration).

---

## 👨‍💻 Author
**Hunain** - *Lead Developer*

---

> [!TIP]
> Make sure to upload actual images when creating tweets to see the beautiful card layout in action!
