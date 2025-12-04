"""
Django local development settings.

This file contains settings for local development.
Run with: python manage.py runserver --settings=core.settings.local
Or set DJANGO_SETTINGS_MODULE=core.settings.local in your environment.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '*']

# Security settings - relaxed for local development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = False
SECURE_CONTENT_TYPE_NOSNIFF = False
X_FRAME_OPTIONS = 'SAMEORIGIN'
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Database - use SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email - use console backend for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For testing with actual email, uncomment below and comment above:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
# DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Static and media files - serve locally
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Optional: Use Cloudinary even in local if configured
# Uncomment below to use Cloudinary in local development:
# if env('CLOUDINARY_CLOUD_NAME', default=None):
#     import cloudinary
#     DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
#     cloudinary.config(
#         cloud_name=env('CLOUDINARY_CLOUD_NAME'),
#         api_key=env('CLOUDINARY_API_KEY'),
#         api_secret=env('CLOUDINARY_SECRET_KEY'),
#     )
#     CLOUDINARY_STORAGE = {
#         'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME'),
#         'API_KEY': env('CLOUDINARY_API_KEY'),
#         'API_SECRET': env('CLOUDINARY_SECRET_KEY'),
#     }

# Debug toolbar (optional - install django-debug-toolbar if you want this)
# INSTALLED_APPS += ['debug_toolbar']
# MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
# INTERNAL_IPS = ['127.0.0.1']

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

print("🚀 Running with LOCAL settings")
