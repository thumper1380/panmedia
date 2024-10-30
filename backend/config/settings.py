"""
Django settings for Pandemia project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from django.conf.global_settings import PASSWORD_HASHERS as DEFAULT_PASSWORD_HASHERS  # Preferably at the same place where you import your other modules
from sentry_sdk.integrations.django import DjangoIntegration
import sentry_sdk
from celery.schedules import crontab
import environ
from datetime import timedelta
import os
from django.utils.translation import gettext_lazy as _
ROOT_DIR = environ.Path(__file__) - 2

# Load operating system environment variables and then prepare to use them
env = environ.Env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'admin_volt.apps.AdminVoltConfig',
    'django.contrib.admin',
    'django.contrib.humanize'
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'django_extensions',
    'django_celery_beat',
    'polymorphic',
    'mptt',
    'django_countries',
    'djmoney',
    'phonenumber_field',
    'djangoql',
    'fsm_admin',
    'django_fsm_log',
    'nested_admin',
    'django_jsonform',
    'djsingleton',
    'mathfilters',
    'drf_spectacular',
    'django_filters',
    'corsheaders'
]

LOCAL_APPS = [
    'apps.users',
    'apps.affiliate',
    'apps.traffic_distribution',
    'apps.leads_conversions',
    'apps.trafficdata',
    'apps.offer',
    'apps.settings',
    'apps.utils',
    'apps.telegrambot',
    'apps.chatgpt',
    'apps.sms',
    'apps.emails',
    'apps.finance',
    'apps.notification',
    'apps.webauth',
]


GRAPH_MODELS = {
    'all_applications': True,
    'group_models': True,
}


# FSM
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
)


# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # 'config.middleware.DomainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ALLOW_ALL_ORIGINS = True


# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY', default="Gt=4Hwc|%*gJF|U3w}*P5MLLDBWWQcjqmh]I}Nr*ha^NT@9=z+")

# ADMIN URL
# ------------------------------------------------------------------------------
ADMIN_URL = env.str('ADMIN_URL', default='admin/')


# DOMAINS
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
DOMAIN = env.str('DOMAIN', default=False)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_PORT = env.int('EMAIL_PORT', default='1025')
EMAIL_HOST = env.str('EMAIL_HOST', default='mailhog')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = [
    ('Admin', ''),
]

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB', default="panmedia_db"),
        'USER': env.str('POSTGRES_USER', default="postgres"),
        'PASSWORD': env.str('POSTGRES_PASSWORD', default="123456789"),
        'HOST': 'localhost',
        'PORT': 5432,
    },
}

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.

TIME_ZONE = 'Asia/Jerusalem'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = False

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = False

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))


# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/staticfiles/'


# LANDER_PATH = 'lander'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [
    str(ROOT_DIR('static')),
    # BASE_DIR + '/templates',
]

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(ROOT_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': STATICFILES_DIRS,
        'OPTIONS': {
            'debug': DEBUG,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# PASSWORD STORAGE SETTINGS
# ------------------------------------------------------------------------------
# See https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]

# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [

    'django.contrib.auth.backends.ModelBackend',
]

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'


# DJANGO REST FRAMEWORK
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'UPLOADED_FILES_USE_URL': False,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser'
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_THROTTLE_RATES': {
        'affiliate_api': '60/minute',
    }
}

# OPEN-API CONFIGURATION
# ------------------------------------------------------------------------------
TG_SUPPORT_USER = 'example'
SPECTACULAR_SETTINGS = {
    'TITLE': 'Affiliate API',
    "DESCRIPTION": "## Authentication\n"
                   "Our API uses JWT (JSON Web Token) authentication for secure access to endpoints. This authentication method requires clients to include a valid JWT token in the `Authorization` header of their requests. The token should be prefixed with the keyword `Bearer`, followed by a space.\n"
                   "Example of an Authorization header with JWT:\n\n"
                   "    Authorization: Bearer <your_jwt_token>\n\n",
    'VERIFYING_KEY': True,
    'VERSION': '1.0.2',
    # 'SERVE_INCLUDE_SCHEMA': False,
    'AUTHENTICATION_WHITELIST': [
    ],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "JWT Auth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Affiliate JWT Auth"
            }
        }
    },
    "SECURITY": [{"JWT Auth": []}],
    "REDOC_UI_SETTINGS": {
        "disableSearch": True,
        "expandResponses": "200,201",
        "hideDownloadButton": True,
        "hideHostname": True,
        # "hideRequestPayloadSample": True,
        # "hideSecuritySection": True,
        # "showObjectSchemaExamples": True,

    },
}


# SIMPLE JWT CONFIGURATION
# ------------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}


# CELERY CONFIGURATION
# ------------------------------------------------------------------------------
CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


CELERY_BEAT_SCHEDULE = {
    'pull_lead_statuses': {
        'task': 'apps.traffic_distribution.tasks.pull_leads_statuses',
        'schedule': crontab(minute='*/1'),
    },
    'pull_conversions': {
        'task': 'apps.traffic_distribution.tasks.pull_conversions',
        'schedule': crontab(minute='*/1'),
    },
    # every day at 00:00 reset all caps
    'reset_caps': {
        'task': 'apps.traffic_distribution.tasks.reset_caps',
        'schedule': crontab(minute=0, hour=0),
    },
    'summarize-conversations': {
        'task': 'apps.chatgpt.tasks.summarize_conversations',
        'schedule': crontab(minute='*/5'),
        'description': 'Summarize conversations',
    },
}


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# TELEGRAM BOT CONFIGURATION
# ------------------------------------------------------------------------------
TELEGRAM_API_KEY = env.str('TELEGRAM_API_KEY', default=False)


# CHAT GPT CONFIGURATION
# ------------------------------------------------------------------------------
OPENAI_API_KEY = env.str('OPENAI_API_KEY', default=False)


# NEUTRINO CONFIGURATION
# ------------------------------------------------------------------------------
NEUTRINO_USER_ID = env.str('NEUTRINO_USER_ID', default=False)
NEUTRINO_API_KEY = env.str('NEUTRINO_API_KEY', default=False)
NEUTRINO_BASE_URL = env.str('NEUTRINO_BASE_URL', default=False)


# SENTRY CONFIGURATION
# ------------------------------------------------------------------------------
SENTRY_DSN = env.str('SENTRY_DSN', default=False)
sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)


# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
# EMAIL_BACKEND = 'apps.settings.models.CustomEmailBackend'


CACHE_BACKEND = 'django_redis.cache.RedisCache'

# Configure the Redis cache settings
CACHES = {
    'default': {
        'BACKEND': CACHE_BACKEND,
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}

# Optional: Configure cache prefix
CACHE_PREFIX = os.getenv('CACHE_PREFIX', 'django')  # Set your own cache prefix
CACHE_MIDDLEWARE_KEY_PREFIX = CACHE_PREFIX


CORS_ORIGIN_ALLOW_ALL = True  # If you want to allow all origins

# Or if you want to whitelist certain origins
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "http://localhost:5500",
    "http://trc.domain.com"
]


NUMEXPR_MAX_THREADS = 4


# ------------------------------------------------------------------------------
# MFA CONFIGURATION
# ------------------------------------------------------------------------------
WEBAUTH_RP_ID = "localhost"
WEBAUTH_RP_NAME = "Example Site"
WEBAUTH_ORIGIN = "http://localhost:8000"
WEBAUTH_VERIFY_URL = "/webauth/verify/"


# ------------------------------------------------------------------------------
# PLATFORM CONFIGURATION
# ------------------------------------------------------------------------------
# CLICK_IDENTIFIER_PARAMETER_NAME
CLICK_ID_PARAMETER_NAME = env.str('CLICK_ID_PARAMETER_NAME', default='p')
REDIRECT_URL_PARAMETER_NAME = env.str('REDIRECT_URL_PARAMETER_NAME', default='r')
DEFAULT_ADVERTISER_TEST_AUTOL_OGIN_URL= env.str('DEFAULT_ADVERTISER_TEST_AUTOL_OGIN_URL', default='https://example.com')
#
