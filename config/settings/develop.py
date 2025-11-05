import os
from dotenv import load_dotenv
from .settings import *
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
print(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, '../.env'))

DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# Try to use MySQL if available, otherwise fall back to SQLite for development
try:
    import pymysql
    pymysql.install_as_MySQLdb()
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv('DB_NAME', 'speedy'),
            'USER': os.getenv('DB_USER', 'speedy_user'),
            'PASSWORD': os.getenv('DB_PASSWORD', 'speedy_password'),
            'HOST': os.getenv('DB_HOST', '127.0.0.1'),
            'PORT': os.getenv('DB_PORT', '3306'),
        }
    }
except ImportError:
    # Fallback to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

MEDIA_ROOT = str(BASE_DIR / 'media')
#STATIC_ROOT = str(BASE_DIR / 'templates')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATIC_URL = '/assets/'
MEDIA_URL = '/media/'

# Simple in-memory caching for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

# WhiteNoise settings - in production use compressed manifest storage.
# During tests or local DEBUG runs we prefer the simple storage to avoid
# MissingManifest errors when static files haven't been collected.
import sys
if 'test' in ' '.join(sys.argv):
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Payment Configuration - Override with environment variables
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.getenv('PAYPAL_SECRET', '')

# Twilio/WhatsApp configuration (use environment variables; do NOT commit secrets)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
# Twilio WhatsApp from number in format 'whatsapp:+1415...'
TWILIO_WHATSAPP_FROM = os.getenv('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')

# Email Configuration - Override with environment variables
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', '')

# Configure SSL/TLS based on port
if EMAIL_PORT == 465:
    EMAIL_USE_SSL = True
    EMAIL_USE_TLS = False
else:
    EMAIL_USE_SSL = False
    EMAIL_USE_TLS = True

# For local development, default to the console email backend unless explicitly
# overridden in the environment. This prevents failures when no SMTP server is
# running (which causes WinError 10061 in the logs).
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')