import os
from pathlib import Path

from core.util import get_bool_from_env

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY') or \
             'django-insecure-n$m*a%3#nqpl5=(sp7v+!6r98mld#o4*(24!dawoma2i5(%lh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_from_env('DEBUG', True)

ALLOWED_HOSTS = []

if os.getenv('HOST_NAME'):
    ALLOWED_HOSTS.append(os.getenv('HOST_NAME'))

INSTALLED_APPS = [
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tenants',
    'winget'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('SQLITE_DB_FILE') or (BASE_DIR / 'db.sqlite3'),
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

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ADMINS = []

if os.getenv('ADMIN_EMAIL'):
    ADMINS.append(('', os.getenv('ADMIN_EMAIL')))

# Email settings

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 25
EMAIL_USE_SSL = False
EMAIL_USE_TLS = False

EMAIL_SUBJECT_PREFIX = ''

if os.getenv('SMTP_FROM'):
    SERVER_EMAIL = os.getenv('SMTP_FROM')

SUIT_CONFIG = {
    'ADMIN_NAME': 'winget.Pro Admin',
    'MENU': (
        {'app': 'winget', 'icon': 'icon-refresh'},
        {'label': 'Users', 'icon': 'icon-user', 'permissions': 'auth.add_user',
         'models': ('auth.user', 'tenants.tenant')}
    ),
    'CONFIRM_UNSAVED_CHANGES': False
}
