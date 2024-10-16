"""
Django settings for crowdsourcing project.

Generated by 'django-admin startproject' using Django 3.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
from django.contrib import messages
from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
from django.contrib.messages import constants as messages
load_dotenv(find_dotenv())

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# 0 => False
# 1 => True

ALLOWED_HOSTS = ['*']

# ALLOWED_HOSTS = [] if DEBUG else os.environ.get("DJANGO_ALLOWED_HOSTS").split(',')
# CSRF_TRUSTED_ORIGINS = ['*']


# Application definition

INSTALLED_APPS = [
    'daphne',
    'django_truncate',
    'channels',
    'corsheaders',
    'django_cleanup.apps.CleanupConfig',
    'jazzmin',
    'django_countries',
    'mathfilters',
    'ckeditor',
    'import_export',
    'core',
    'accounts',
    'chat',
    'crispy_forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumbers',
    'phonenumber_field',
    'django_celery_beat',
    'django_celery_results',
    'social_django',
    
]

MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware'
]



# CORS Config
CORS_ORIGIN_ALLOW_ALL = True
# CORS_ALLOW_CREDENTIALS = False

ROOT_URLCONF = 'crowdsourcing.urls'

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
                'social_django.context_processors.backends',
                'core.context_processor.universal_content',
            ],
        },
    },
]


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
        },
}

# For SOCIAL-AUTH
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',
]


SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET')

WSGI_APPLICATION = 'crowdsourcing.wsgi.application'
ASGI_APPLICATION = 'crowdsourcing.asgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'TEST': {
            'NAME': BASE_DIR / 'db.sqlite3',
            },
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': f"{os.environ.get('POSTGRES_DB')}",
#         'USER': 'postgres',
#         'PASSWORD': f"{os.environ.get('POSTGRES_PASSWORD')}",
#         'HOST': 'localhost',
#         'PORT': '5432'
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]


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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Lagos' # UTC

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


STATIC_URL = '/static/'
MEDIA_URL = '/media/'


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR / 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.BaseUser'

# SMTP CONFIGS
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = '465'
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'CrowdsourceIt Team <noreply@crowdsourceit.com>'


MESSAGE_TAGS = {
        messages.DEBUG: 'alert-secondary',
        messages.INFO: 'alert-info',
        messages.SUCCESS: 'alert-success',
        messages.WARNING: 'alert-warning',
        messages.ERROR: 'alert-danger',
 }

LOGIN_URL = 'accounts:innovator_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/'
LOGOUT_REDIRECT_URL = 'accounts:innovator_login'


# SOCIAL_AUTH_URL_NAMESPACE = 'social'

# SOCIAL_AUTH_EMAIL_FORM_HTML = 'demo/email_signup.html'
# SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'

SOCIAL_AUTH_PIPELINE = (
'social.pipeline.social_auth.social_details',
'social.pipeline.social_auth.social_uid',
'social.pipeline.social_auth.auth_allowed',
'social.pipeline.social_auth.social_user',
'social.pipeline.user.get_username',
# "common.pipeline.require_email",
# "common.pipeline.require_country",
# "common.pipeline.require_city",
# "social_core.pipeline.mail.mail_validation",
'accounts.pipeline.get_username',
'social.pipeline.user.create_user',
'accounts.pipeline.save_profile',
'social.pipeline.social_auth.associate_user',
'social.pipeline.social_auth.load_extra_data',
'social.pipeline.user.user_details'
)




SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/user.phonenumbers.read']
SOCIAL_AUTH_GOOGLE_OAUTH2_FIELD_SELECTORS = {
    'name': 'names(displayName, familyName, givenName, middleName)',
    'phone': 'phoneNumbers(value)',}


# SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = os.environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY')
# SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = os.environ.get('SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET')



# # Add email to requested authorizations.
# SOCIAL_AUTH_LINKEDIN_OAUTH2_SCOPE = ['r_liteprofile', 'r_emailaddress']
# # Add the fields so they will be requested from linkedin.
# SOCIAL_AUTH_LINKEDIN_OAUTH2_FIELD_SELECTORS = ['emailAddress']
# # Arrange to add the fields to UserSocialAuth.extra_data
# SOCIAL_AUTH_LINKEDIN_OAUTH2_EXTRA_DATA = [('id', 'id'),
#                                           ('firstName', 'first_name'),
#                                           ('lastName', 'last_name'),
#                                           ('emailAddress', 'email_address')]

SOCIAL_AUTH_USER_FIELDS=['first_name', 'last_name', 'password', 'email', 'username']



# Set the session engine to 'django.contrib.sessions.backends.signed_cookies'
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# Set the session cookie age to a reasonable duration (e.g., 2 weeks)
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds

# Set the session cookie secure to True if using HTTPS on production
# SESSION_COOKIE_SECURE = False

# Set SESSION_COOKIE_HTTPONLY to True for added security
# SESSION_COOKIE_HTTPONLY = True

# SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# JAZZMIN
JAZZMIN_SETTINGS = {
    "site_title": "Chat App",
    "site_header": "Chat App",
    "copyright": "toshiro.tech"
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-success",
    "accent": "accent-teal",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    "sidebar": "sidebar-dark-info",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "cyborg",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

DJANGORESIZED_DEFAULT_SIZE = [1024, 768]
DJANGORESIZED_DEFAULT_QUALITY = 75
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = True



DATA_UPLOAD_MAX_NUMBER_FIELDS = None # higher than the count of fields

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': 'full',
    },
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

if os.getcwd() == "/app":
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True 

PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')

THOUSAND_SEPARATOR = True

# CELERY
CELERY_BROKER_USER = os.environ.get('BROKER_USER')
CELERY_BROKER_PASSWORD = os.environ.get('BROKER_PASSWORD')
CELERY_BROKER_URL = f'amqp://{os.environ.get("RABBITMQ_USER")}:{os.environ.get("RABBITMQ_PASS")}@rabbit:5672/rabbit'
# CELERY_RESULT_BACKEND = 'django-db'
CELERY_BROKER_BACKEND = "rpc://"