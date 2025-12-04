"""
Django base settings for core project.

This file contains settings common to both local and production environments.
Environment-specific settings are in local.py and production.py.
"""

import os
from pathlib import Path
import environ
import cloudinary

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'blog',
    'storages',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'phonenumber_field',
    'markdownx',
]

AUTH_USER_MODEL = 'blog.CustomUser'
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    'blog.backends.EmailOrPhoneBackend',
]
ACCOUNT_ADAPTER = 'blog.adapter.CustomAccountAdapter'

ACCOUNT_FORMS = {
    'signup': 'blog.forms.CustomSignupForm',
}

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True

ACCOUNT_PASSWORD_RESET_VERIFICATION_METHOD = 'email'

ACCOUNT_SIGNUP_FIELDS = ['email*', 'username', 'phone_number', 'password1', 'password2']
ACCOUNT_LOGIN_METHODS = {"email", "username"}

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APPS': [
            {
                "client_id": os.environ.get('CLIENT_ID'),
                "secret": os.environ.get('SECRET'),
                "key": "",
                "settings": {
                    "scope": ["profile", "email"],
                    "auth_params": {"access_type": "online"},
                },
            },
        ],
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# Rate limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_RATE = '5/m'  # 5 requests per minute for authenticated views

# File upload limits
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

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

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'blog' / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
