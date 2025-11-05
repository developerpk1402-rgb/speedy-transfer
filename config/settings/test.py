from .settings import *  # noqa

# Use in-memory SQLite DB for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Fast email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Ensure allowed hosts for test client
ALLOWED_HOSTS = ["*"]

# Avoid external live reload during tests
MIDDLEWARE = [mw for mw in MIDDLEWARE if mw != "livereload.middleware.LiveReloadScript"]

# Minimal static settings to satisfy templates during tests
STATIC_URL = "/static/"
import os
from .settings import *

DEBUG = True

SECRET_KEY = 'test-secret-key'

# Minimal apps for tests (exclude jet and livereload)
INSTALLED_APPS = [
	"django.contrib.admin",
	"django.contrib.auth",
	"django.contrib.contenttypes",
	"django.contrib.sessions",
	"django.contrib.messages",
	"django.contrib.staticfiles",
	"speedy_app.core",
]

# Minimal middleware (exclude livereload)
MIDDLEWARE = [
	"django.middleware.security.SecurityMiddleware",
	"django.contrib.sessions.middleware.SessionMiddleware",
	"django.middleware.common.CommonMiddleware",
	"django.middleware.csrf.CsrfViewMiddleware",
	"django.contrib.auth.middleware.AuthenticationMiddleware",
	"django.contrib.messages.middleware.MessageMiddleware",
	"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Disable migrations for local app to avoid MySQL-specific SQL in tests
MIGRATION_MODULES = {
	"core": None,
}

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'test_db.sqlite3'),
	}
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
DEFAULT_FROM_EMAIL = 'test@example.com'

PASSWORD_HASHERS = [
	'django.contrib.auth.hashers.MD5PasswordHasher',
]

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
	}
}