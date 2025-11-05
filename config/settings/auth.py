# Authentication backends
AUTHENTICATION_BACKENDS = [
    'reports.auth.ReportingAuthBackend',  # Custom backend for reporting login
    'django.contrib.auth.backends.ModelBackend',  # Default backend
]