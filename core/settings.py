import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def parse_timedelta(value, default):
    if isinstance(value, timedelta):
        return value
    if isinstance(value, int):
        return timedelta(seconds=value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        if value.isdigit():
            return timedelta(seconds=int(value))
        parts = value.split(":")
        if len(parts) == 3:
            try:
                hours, minutes, seconds = [int(p) for p in parts]
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                pass
        if len(parts) == 2:
            try:
                minutes, seconds = [int(p) for p in parts]
                return timedelta(minutes=minutes, seconds=seconds)
            except ValueError:
                pass
    return default

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = os.getenv('DEBUG', 'False') == 'True'

vercel_host = os.getenv('VERCEL_URL', '').strip().replace('https://', '').replace('http://', '')

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app']
if vercel_host:
    ALLOWED_HOSTS.append(vercel_host)
    ALLOWED_HOSTS.append(f'.{vercel_host}')

CSRF_TRUSTED_ORIGINS = [
    'https://task-manager-client-feih.vercel.app',
    'https://task-manager-client-feih-git-main-sheik-saims-projects.vercel.app',
]
if vercel_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{vercel_host}')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'mongoengine',
    'apps.authentication',
    'apps.tasks',
    'apps.images',
    'apps.annotations',
]

# Custom middleware to handle OPTIONS requests before any redirects
class OptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            origin = request.headers.get('Origin', '')
            allowed_origins = [
                'https://task-manager-client-feih.vercel.app',
                'https://task-manager-client-feih-git-main-sheik-saims-projects.vercel.app',
                'https://task-manager-client-tff6-sable.vercel.app',
            ]
            
            response = HttpResponse(status=200)
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Allow-Credentials'] = 'true'
            
            # Return specific origin if allowed
            if origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
            
            return response
        return self.get_response(request)

MIDDLEWARE = [
    'core.settings.OptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

# Disable trailing slash redirects to prevent CORS preflight issues
APPEND_SLASH = False

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Use PostgreSQL for production on Vercel
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'task_manager'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Fallback to SQLite for local development
if not os.getenv('POSTGRES_HOST'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

from mongoengine import connect

mongo_uri = os.getenv('MONGODB_URI')
if mongo_uri:
    connect(db=os.getenv('DATABASE_NAME', 'task_manager'), host=mongo_uri)

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'authentication.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': parse_timedelta(os.getenv('ACCESS_TOKEN_LIFETIME', '1 day'), timedelta(days=1)),
    'REFRESH_TOKEN_LIFETIME': parse_timedelta(os.getenv('REFRESH_TOKEN_LIFETIME', '7 days'), timedelta(days=7)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_COOKIE': 'access_token',
    'REFRESH_COOKIE': 'refresh_token',
    'AUTH_COOKIE_DOMAIN': None,
    'AUTH_COOKIE_SECURE': True,
    'AUTH_COOKIE_HTTPONLY': True,
    'AUTH_COOKIE_PATH': '/',
    'AUTH_COOKIE_SAMESITE': 'None',
    'REFRESH_COOKIE_DOMAIN': None,
    'REFRESH_COOKIE_SECURE': True,
    'REFRESH_COOKIE_HTTPONLY': True,
    'REFRESH_COOKIE_PATH': '/',
    'REFRESH_COOKIE_SAMESITE': 'None',
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://task-manager-client-feih.vercel.app",
    "https://task-manager-client-feih-git-main-sheik-saims-projects.vercel.app",
    "https://task-manager-client-tff6-sable.vercel.app",
    "https://task-manager-server-git-main-sheik-saims-projects.vercel.app",
    "https://task-manager-servers.vercel.app"
]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Secure cookie settings for production
# Temporarily relaxed for debugging - will need HTTPS for SameSite=None
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
