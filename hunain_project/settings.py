"""
Django settings for hunain_project
Vercel + Supabase ready with local HTTPS dev
"""

import os
from pathlib import Path
import dj_database_url
from decouple import config
from django.core.exceptions import ImproperlyConfigured

# -----------------------------
# Base Directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Environment Detection
# -----------------------------
IS_VERCEL = "VERCEL" in os.environ

# -----------------------------
# Security
# -----------------------------
SECRET_KEY = config('SECRET_KEY', default='django-insecure-CHANGE_THIS')
DEBUG = config('DEBUG', default=not IS_VERCEL, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='localhost,127.0.0.1,.vercel.app'
).split(',')

if IS_VERCEL:
    # Add Vercel specific hosts if needed
    vercel_url = os.environ.get("VERCEL_URL")
    if vercel_url:
        ALLOWED_HOSTS.append(vercel_url)

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
    f'https://{host.lstrip(".")}' if not host.startswith('.') else f'https://*{host.lstrip(".")}'
    for host in ALLOWED_HOSTS if host not in ['localhost', '127.0.0.1']
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
    'django_extensions',
    'tweet',
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
                'tweet.context_processors.search_query',
            ],
        },
    },
]

WSGI_APPLICATION = 'hunain_project.wsgi.application'
ASGI_APPLICATION = 'hunain_project.asgi.application'

# -----------------------------
# Database Configuration
# -----------------------------
DATABASE_URL = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default=None)

if IS_VERCEL:
    if not DATABASE_URL:
        raise ImproperlyConfigured(
            "DATABASE_URL is not set. SQLite is not supported on Vercel as it is a serverless platform. "
            "Please provide a valid PostgreSQL connection string in your Vercel Environment Variables."
        )
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL, 
            conn_max_age=600, 
            ssl_require=True
        )
    }
elif DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL, 
            conn_max_age=600, 
            ssl_require=True
        )
    }
else:
    # Local development fallback
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
if not DEBUG or IS_VERCEL:
    # Vercel uses a proxy, so we need to trust the X-Forwarded-Proto header
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool) if not DEBUG else False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # HSTS settings
    if not DEBUG:
        SECURE_HSTS_SECONDS = 31536000  # 1 year
        SECURE_HSTS_INCLUDE_SUBDOMAINS = True
        SECURE_HSTS_PRELOAD = True

# -----------------------------
# Default primary key field
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------
# Optional: print HTTPS info
# -----------------------------
if USE_HTTPS_LOCAL:
    print(f"✅ Local HTTPS enabled with cert: {SSL_CERT_FILE} and key: {SSL_KEY_FILE}")