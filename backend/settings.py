import os
from pathlib import Path

import environ
from celery.schedules import crontab
from keycloak import KeycloakAdmin
from django.conf.global_settings import DATETIME_INPUT_FORMATS

from authentication.KeycloakOpenIDExtended import KeycloakOpenIDExtended
from authentication.choices import EmailNotificationType
from keycloak_auth.KeycloakAdminExtended import KeycloakAdminExtended

env = environ.Env()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# reading .env file
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# Application definition
INSTALLED_APPS = [
    'rest_framework',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'storages',
    # 'ebhealthcheck.apps.EBHealthCheckConfig',
    'django_extensions',
    'django_filters',
    'mozilla_django_oidc',
    'colorfield',
    'drf_api_logger',
    'basic',
    'anmelde_tool.email_services',
    'anmelde_tool.event',
    'anmelde_tool.event.summary',
    'anmelde_tool.registration',
    'anmelde_tool.event.choices',
    'anmelde_tool.event.cash',
    'anmelde_tool.event.file_generator',
    'anmelde_tool.event.email',
    'anmelde_tool.attributes',
    'anmelde_tool.workshop',
    'authentication',
    'messaging',
    'keycloak_auth',
    'food',
    'notifications',
    'authentication.custom_notifications',
    'inspi'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'mozilla_django_oidc.middleware.SessionRefresh',
    'drf_api_logger.middleware.api_logger_middleware.APILoggerMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates/emails/'),
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

WSGI_APPLICATION = 'backend.wsgi.application'

if env.bool('USE_RDS_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('RDS_DB_NAME'),
            'USER': env('RDS_USERNAME'),
            'PASSWORD': env('RDS_PASSWORD'),
            'HOST': env('RDS_HOSTNAME'),
            'PORT': env('RDS_PORT'),
            'CONN_MAX_AGE': 600,
            'OPTIONS': {'sslmode': 'require'},
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(os.path.join(BASE_DIR, "db.sqlite3")),
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

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DRF_API_LOGGER_DATABASE = True

# https://testdriven.io/blog/storing-django-static-and-media-files-on-amazon-s3/#private-media-files
# Continue tutorial for uploading images
if env.bool('USE_S3'):
    # aws settings
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')

    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    # s3 static settings
    STATIC_LOCATION = 'static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
    # s3 private media settings
    PRIVATE_MEDIA_LOCATION = 'private'
    PRIVATE_MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PRIVATE_MEDIA_LOCATION}/'
    AWS_S3_REGION_NAME = 'eu-central-1'

    STORAGES = {
        "default": {
            "BACKEND": 'backend.storage_backends.PublicMediaStorage'
        },
        "staticfiles": {
            "BACKEND": 'backend.storage_backends.StaticStorage'
        },
        "private": {
            "BACKEND": 'backend.storage_backends.PrivateMediaStorage'
        },
    }
else:
    STATIC_URL = '/staticfiles/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/mediafiles/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

AUTH_USER_MODEL = 'authentication.CustomUser'

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST")
CSRF_TRUSTED_ORIGINS = env.list("CORS_ORIGIN_WHITELIST")
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 60
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SITE_ID = 1

DATETIME_INPUT_FORMATS += [
    '%Y-%m-%dT%H:%M:%S%z',
    '%Y-%m-%dT%H:%M:%S%Z'
]
SEND_MAIL = env.bool('USE_SES', False)

if SEND_MAIL:
    EMAIL_BACKEND = 'django_ses.SESBackend'
    AWS_SES_ACCESS_KEY_ID = env('AWS_SES_ACCESS_KEY_ID')
    AWS_SES_SECRET_ACCESS_KEY = env('AWS_SES_SECRET_ACCESS_KEY')
    AWS_SES_REGION_NAME = 'eu-central-1'
    AWS_SES_REGION_ENDPOINT = 'email.eu-central-1.amazonaws.com'
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    FRONT_URL = env.str('FRONT_URL')

REST_USE_JWT = True

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'djangorestframework_camel_case.render.CamelCaseJSONRenderer',
        'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'djangorestframework_camel_case.parser.CamelCaseFormParser',
        'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        'djangorestframework_camel_case.parser.CamelCaseJSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'mozilla_django_oidc.contrib.drf.OIDCAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

AUTHENTICATION_BACKENDS = (
    'backend.OIDCAuthentication.MyOIDCAB',
    'django.contrib.auth.backends.ModelBackend',
)

BASE_URI = env('BASE_URI')
BASE_REALM_URI = f'{BASE_URI}realms/{env("OIDC_RP_REALMNAME")}'
OIDC_AUTH_URI = f'{BASE_REALM_URI}/{env("OIDC_RP_CLIENT_ID")}/'
OIDC_CALLBACK_PUBLIC_URI = f'{BASE_REALM_URI}/'
OIDC_RP_CLIENT_ID = env('OIDC_RP_CLIENT_ID')
OIDC_RP_CLIENT_SECRET = env('OIDC_RP_CLIENT_SECRET_BACKEND')
OIDC_OP_TOKEN_ENDPOINT = f'{BASE_REALM_URI}/protocol/openid-connect/token'
OIDC_OP_USER_ENDPOINT = f'{BASE_REALM_URI}/protocol/openid-connect/userinfo'
OIDC_OP_AUTHORIZATION_ENDPOINT = f'{BASE_REALM_URI}/protocol/openid-connect/auth'
OIDC_STORE_ID_TOKEN = True
OIDC_CREATE_USER = True

GRAPHENE = {
    "SCHEMA": "basic.schema.schema"
}

CELERY_BROKER_URL = env('CELERY_BROKER')
CELERY_RESULT_BACKEND = env('CELERY_BROKER')
USE_CELERY = env('USE_CELERY')
CELERY_TIMEZONE = 'Europe/Berlin'
CELERY_BEAT_SCHEDULE = {
    "import_keycloak_members": {
        "task": "authentication.sync_keycloak_users.import_keycloak_members",
        "schedule": crontab(minute="*/15"),
    },
    "notifications_3h": {
        "task": "authentication.custom_notifications.email_services.hourly_notification",
        "schedule": crontab(hour="1,4,7,10,13,16,19,22", minute=0),
        'args': {EmailNotificationType.EVERY_3H}
    },
    "notifications_12h": {
        "task": "authentication.custom_notifications.email_services.hourly_notification",
        "schedule": crontab(hour="11,23", minute=0),
        'args': {EmailNotificationType.EVERY_12H}
    },
    "notifications_24h": {
        "task": "authentication.custom_notifications.email_services.hourly_notification",
        "schedule": crontab(hour="0", minute=0),
        'args': {EmailNotificationType.DAILY}
    },
    "notifications_7d": {
        "task": "authentication.custom_notifications.email_services.hourly_notification",
        "schedule": crontab(hour="23", minute=0, day_of_week="SUN"),
        'args': {EmailNotificationType.WEEKLY}
    },
}

keycloak_admin = KeycloakAdminExtended(
    server_url=env('BASE_URI'),
    client_id=env('KEYCLOAK_ADMIN_USER'),
    client_secret_key=env('KEYCLOAK_ADMIN_PASSWORD'),
    realm_name=env('KEYCLOAK_APP_REALM'),
    user_realm_name=env('KEYCLOAK_APP_REALM'),
    verify=True,
    auto_refresh_token=['get', 'put', 'post', 'delete']
)

keycloak_user = KeycloakOpenIDExtended(
    server_url=env('BASE_URI'),
    client_id=env('OIDC_RP_CLIENT_ID'),
    realm_name=env('OIDC_RP_REALMNAME'),
)

if not DEBUG:
    SERVER_EMAIL = 'error@anmelde-tool.de'
    ADMINS = [('Robert', 'robertbaggi@gmail.com'), ('Hagi', 'hagi@dpvonline.de')]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'mail_admins': {
                'class': 'django.utils.log.AdminEmailHandler',
                'level': 'ERROR',
                'include_html': True,
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            # Again, default Django configuration to email unhandled exceptions
            'django.request': {
                'handlers': ['console', 'mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
            # Might as well log any errors anywhere else in Django
            'django': {
                'handlers': ['console', 'mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }
