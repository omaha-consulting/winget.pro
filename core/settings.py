from django.conf import global_settings
from core.util import get_bool_from_env
from pathlib import Path

import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or \
             'django-insecure-n$m*a%3#nqpl5=(sp7v+!6r98mld#o4*(24!dawoma2i5(%lh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool_from_env('DEBUG', True)

ALLOWED_HOSTS = []

if os.getenv('HOST_NAME'):
    ALLOWED_HOSTS.append(os.getenv('HOST_NAME'))

if os.getenv('ALT_HOST_NAMES'):
    for host_name in os.getenv('ALT_HOST_NAMES').split(' '):
        assert host_name, f'Invalid format for ALT_HOST_NAMES.'
        ALLOWED_HOSTS.append(host_name)

INSTALLED_APPS = [
    'suit',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tenants',
    'winget',
    'rest_framework'
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

# Optional settings for serving files from S3 with django-storages:
DEFAULT_FILE_STORAGE = os.getenv('DEFAULT_FILE_STORAGE') or \
                       global_settings.DEFAULT_FILE_STORAGE

if DEFAULT_FILE_STORAGE == 'storages.backends.s3boto3.S3Boto3Storage':
    AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
    AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_S3_HOST = os.getenv('AWS_S3_HOST') or 's3.amazonaws.com'
    AWS_S3_ENDPOINT_URL = 'https://' + AWS_S3_HOST
    AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL')
    AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    # It's crazy that this isn't the default. It is for FileSystemStorage:
    AWS_S3_FILE_OVERWRITE = False
    if os.getenv('AWS_S3_PROXIES'):
        AWS_S3_PROXIES = json.loads(os.getenv('AWS_S3_PROXIES'))

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
        {'label': 'Users', 'icon': 'icon-user', 'permissions': 'auth.view_user',
         'models': ('auth.user', 'tenants.tenant')}
    ),
    'CONFIRM_UNSAVED_CHANGES': False
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ]
}

# Make sure Django returns https:// URLs when invoked over https.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'timestamp'
        }
    },
    'formatters': {
        'timestamp': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        }
    },
    'loggers': {
        'django': {
            # Ensure that we see server errors in Gunicorn's log output:
            'handlers': ['console']
        },
        'django.request': {
            'level': 'ERROR' # Avoid "WARNING django.request Forbidden ..." etc.
        }
    }
}