import os
from django.utils.log import DEFAULT_LOGGING

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


DATA_DIR = os.getenv('IRON_DATA_DIR', PROJECT_ROOT)
WEBROOT_DIR = os.getenv('IRON_WEBROOT_DIR', os.path.join(PROJECT_ROOT, 'webroot/'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('IRON_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('IRON_DEBUG_IN_PRODUCTION', 'False') == 'True'

ALLOWED_HOSTS = list(filter(lambda x: x, map(lambda x: x.strip(),
                                             os.getenv('IRON_ALLOWED_HOSTS', '').split(','))))
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Application definition

INSTALLED_APPS = [
    'pl_sugar',  # must be inserted before admin so that we can override some admin templates
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'iron',
]

ROOT_URLCONF = 'django_project.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'templates/')],
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

WSGI_APPLICATION = 'django_project.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.getenv('IRON_DB_ENGINE',
                            'django.db.backends.sqlite3'),
        'USER': os.getenv('IRON_DB_USER', 'iron'),
        'PASSWORD': os.getenv('IRON_DB_PASSWORD', 'password'),
        'HOST': os.getenv('IRON_DB_HOST', ''),
        'PORT': os.getenv('IRON_DB_PORT', ''),
    }
}

if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
    DATABASES['default']['NAME'] = os.getenv('IRON_DB_PATH',
                                             os.path.join(DATA_DIR, 'db.sqlite3'))
else:
    DATABASES['default']['NAME'] = os.getenv('IRON_DB_NAME', 'iron')

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = os.getenv('IRON_STATIC_URL', '/static/')
STATIC_ROOT = os.path.join(WEBROOT_DIR, 'static/')

# CELERY
BROKER_URL = os.getenv('BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

REST_FRAMEWORK = {
    'PAGE_SIZE': 50,
    'DEFAULT_PAGINATION_CLASS': 'pl_sugar.rest_framework.pagination.LinkHeaderPagination',
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

# configure logging
LOG_LEVEL = os.getenv('IRON_LOG_LEVEL', 'INFO')
LOGGING = DEFAULT_LOGGING.copy()
LOGGING['loggers']['django']['level'] = LOG_LEVEL
LOGGING['loggers']['celery'] = {
    'handlers': ['console'],
    'level': LOG_LEVEL
}


if os.getenv('IRON_SENTRY_DSN', None):
    import raven
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {
        'dsn': os.getenv('IRON_SENTRY_DSN'),
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
        'environment': os.getenv('ENV_NAME', None),
    }

    # Sentry logging with celery is a real pain in the ass
    # https://github.com/getsentry/sentry/issues/4565
    CELERYD_HIJACK_ROOT_LOGGER = False
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler'
    }
    LOGGING['loggers']['celery.task'] = {
        'level': LOG_LEVEL,
        'handlers': ['console', 'sentry']
    }
