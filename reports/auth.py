from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import connections
from .db import REPORTS_DATABASE
import os

User = get_user_model()

class ReportingAuthBackend(ModelBackend):
    """
    Custom authentication backend for the reporting system.
    Uses specific database credentials for reporting portal authentication.
    """
    def __init__(self):
        super().__init__()
        # Ensure we have a reports database connection
        if 'reports' not in connections.databases:
            connections.databases['reports'] = REPORTS_DATABASE['default']

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        try:
            # Use the reports database connection
            using_db = 'reports'
            # Try to fetch the user from reports database
            user = User.objects.using(using_db).get(username=username)
            
            # Check if user is staff and validate password
            if user.is_staff and user.check_password(password):
                return user
                
        except User.DoesNotExist:
            return None
            
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None