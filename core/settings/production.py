"""
Django production settings.

This file contains settings for production deployment.
Set DJANGO_SETTINGS_MODULE=core.settings.production in your environment.
"""

import os
import dj_database_url
import cloudinary
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Security settings - strict for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security for production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("POSTGRES_URL_NON_POOLING", "sqlite:///" + str(BASE_DIR / "db.sqlite3")),
        conn_max_age=600,
        ssl_require=True,
    )
}

# Email configuration for production 
if not os.environ.get("DEMO_MODE"):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# Cloudinary configuration for production
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

if not os.environ.get('CLOUDINARY_URL'):
    cloud_name = env('CLOUDINARY_CLOUD_NAME', default=None)
    api_key = env('CLOUDINARY_API_KEY', default=None)
    api_secret = env('CLOUDINARY_SECRET_KEY', default=None)
    if cloud_name and api_key and api_secret:
        os.environ['CLOUDINARY_URL'] = f"cloudinary://{api_key}:{api_secret}@{cloud_name}"

cloudinary.config(
    cloud_name=env('CLOUDINARY_CLOUD_NAME', default=None),
    api_key=env('CLOUDINARY_API_KEY', default=None),
    api_secret=env('CLOUDINARY_SECRET_KEY', default=None),
)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': env('CLOUDINARY_API_KEY'),
    'API_SECRET': env('CLOUDINARY_SECRET_KEY'),
}

# WhiteNoise for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cache configuration for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# If you have Redis configured, uncomment below:
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
#     }
# }

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

print("🚀 Running with PRODUCTION settings")
