"""
Django settings for hunain_project
Vercel + Supabase ready with local HTTPS dev
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

# -----------------------------
# Base Directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Security
# -----------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-CHANGE_THIS')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,hunain-gujjar-tweet-prod.vercel.app'
).split(',')

# -----------------------------
# Local HTTPS dev
# -----------------------------
USE_HTTPS_LOCAL = config('USE_HTTPS_LOCAL', default=True, cast=bool)
if USE_HTTPS_LOCAL:
    SSL_CERT_FILE = BASE_DIR / 'certs' / '127.0.0.1+localhost.pem'
    SSL_KEY_FILE = BASE_DIR / 'certs' / '127.0.0.1+localhost-key.pem'

# -----------------------------
# CSRF Configuration
# -----------------------------
CSRF_TRUSTED_ORIGINS = [
    f'https://{host}' for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
]
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# -----------------------------
# Installed Applications
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',  # for runserver_plus
    'tweet',  # your app
]

# -----------------------------
# Middleware
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# -----------------------------
# URL configuration
# -----------------------------
ROOT_URLCONF = 'hunain_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tweet.context_processors.search_query',  # custom processor
            ],
        },
    },
]

WSGI_APPLICATION = 'hunain_project.wsgi.application'
ASGI_APPLICATION = 'hunain_project.asgi.application'

# -----------------------------
# Database (Supabase or local fallback)
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if "127.0.0.1" in DATABASE_URL:
        # Local Supabase: no SSL
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
        }
    else:
        # Production Supabase Cloud: SSL required
        DATABASES = {
            'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True)
        }
else:
    # Fallback: local SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -----------------------------
# Authentication
# -----------------------------
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/tweet/'
LOGOUT_REDIRECT_URL = '/tweet/'

# -----------------------------
# Password validation
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# -----------------------------
# Internationalization
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# Static files
# -----------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -----------------------------
# Media files
# -----------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# -----------------------------
# Production security (Vercel)
# -----------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = False  # Vercel handles SSL
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# -----------------------------
# Default primary key field
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Optional: print HTTPS info
# -----------------------------
if USE_HTTPS_LOCAL:
    print(f"✅ Local HTTPS enabled with cert: {SSL_CERT_FILE} and key: {SSL_KEY_FILE}")