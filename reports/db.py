import os

REPORTS_DATABASE = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'speedy',
        'USER': 'speedy_user',
        'PASSWORD': '71Du$1WJ>bvv]iw',
        'HOST': '45.82.72.136',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }
    }
}