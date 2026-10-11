import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('LAMBDA_TASK_ROOT'))

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-your-secret-key-here')
# Default DEBUG to False in serverless/production environments; True for local dev
DEBUG = os.getenv('DEBUG', 'False' if is_serverless else 'True').lower() in ('true', '1', 't')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.vercel.app', 'skillrecommender.vercel.app', '*']
CSRF_TRUSTED_ORIGINS = [
    'https://skillrecommender.vercel.app',
    'https://*.vercel.app',
    'http://localhost',
    'http://127.0.0.1',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recommender.apps.RecommenderConfig',
]

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


ROOT_URLCONF = 'skill_recommender.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'skill_recommender.wsgi.application'

# Production-grade Relational Database Configuration:
# Defaults to robust persistent SQLite for zero-config local development,
# and switches to PostgreSQL automatically when DATABASE_URL or DB_NAME is set.
# In serverless environments (e.g. Vercel), writable directory is /tmp.
is_serverless = bool(os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') or os.environ.get('LAMBDA_TASK_ROOT'))

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    ssl_req = 'localhost' not in DATABASE_URL and '127.0.0.1' not in DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=ssl_req,
        )
    }
elif os.environ.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    db_path = Path('/tmp') / 'db.sqlite3' if is_serverless else BASE_DIR / 'db.sqlite3'
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(db_path),
        }
    }


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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

LOGIN_REDIRECT_URL = 'profile'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'logout'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
WHITENOISE_USE_FINDERS = True


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')

# Startup check for environment variables (Log clear warnings without exposing secret values)
import logging
startup_logger = logging.getLogger(__name__)

_missing_vars = []
if not os.getenv('SECRET_KEY') or os.getenv('SECRET_KEY') == 'django-insecure-your-secret-key-here':
    _missing_vars.append('SECRET_KEY (using default insecure fallback key)')
if not os.getenv('GROQ_API_KEY'):
    _missing_vars.append('GROQ_API_KEY (AI assessment and recommendation engine will use fallback mode)')
if is_serverless and not os.getenv('DATABASE_URL') and not os.getenv('DB_NAME'):
    _missing_vars.append('DATABASE_URL (serverless deployment detected; SQLite in /tmp will be ephemeral)')

for _var in _missing_vars:
    startup_logger.warning("[CONFIG WARNING] Environment variable notice: %s", _var)

