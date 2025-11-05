"""
Test configuration for different environments (staging and production)
This file provides test-specific settings and utilities for payment system testing.
"""

import os
from django.conf import settings

# Test environment detection
TEST_ENVIRONMENT = os.getenv('TEST_ENVIRONMENT', 'staging').lower()

# Test data configuration
TEST_DATA = {
    'staging': {
        'stripe_keys': {
            'public_key': 'pk_test_staging_key',
            'secret_key': 'sk_test_staging_key'
        },
        'paypal_keys': {
            'client_id': 'staging_client_id',
            'secret': 'staging_secret'
        },
        'test_amounts': [10.00, 25.50, 100.00, 250.75],
        'test_currencies': ['USD', 'EUR', 'MXN'],
        'test_cards': {
            'success': '4242424242424242',
            'decline': '4000000000000002',
            'insufficient_funds': '4000000000009995',
            '3d_secure': '4000002500003155'
        }
    },
    'production': {
        'stripe_keys': {
            'public_key': 'pk_live_production_key',
            'secret_key': 'sk_live_production_key'
        },
        'paypal_keys': {
            'client_id': 'production_client_id',
            'secret': 'production_secret'
        },
        'test_amounts': [50.00, 125.00, 500.00, 1000.00],
        'test_currencies': ['USD', 'EUR', 'MXN'],
        'test_cards': {
            'success': '4242424242424242',  # Use test cards even in production tests
            'decline': '4000000000000002',
            'insufficient_funds': '4000000000009995',
            '3d_secure': '4000002500003155'
        }
    }
}

# Get current test environment configuration
CURRENT_TEST_CONFIG = TEST_DATA[TEST_ENVIRONMENT]

# Test order templates
SAMPLE_ORDERS = {
    'simple_transfer': {
        'trip_type': 'oneway',
        'people': 2,
        'pickup': {
            'datetime': '2025-08-10 10:00',
            'location_id': '1',
            'location_name': 'Hotel Test'
        },
        'dropoff': {
            'datetime': '2025-08-10 11:00',
            'location_id': '2',
            'location_name': 'Airport'
        },
        'car_type_label': 'VAN',
        'items': [
            {
                'name': 'Test Van',
                'unit_amount': 75.00,
                'currency': 'USD',
                'date': '2025-08-10',
                'time': '10:00',
                'capacity': 8
            }
        ],
        'subtotal': 75.00,
        'total': 75.00,
        'customer': {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': '123 Test St',
            'city': 'Testville',
            'zip': '12345',
        }
    },
    'round_trip': {
        'trip_type': 'roundtrip',
        'people': 4,
        'pickup': {
            'datetime': '2025-08-10 08:00',
            'location_id': '1',
            'location_name': 'Hotel Test'
        },
        'dropoff': {
            'datetime': '2025-08-10 09:00',
            'location_id': '2',
            'location_name': 'Airport'
        },
        'return_trip': {
            'datetime': '2025-08-15 18:00',
            'pickup_location_name': 'Airport',
            'dropoff_location_name': 'Hotel Test'
        },
        'car_type_label': 'SPRINTER',
        'items': [
            {
                'name': 'Test Sprinter',
                'unit_amount': 150.00,
                'currency': 'USD',
                'date': '2025-08-10',
                'time': '08:00',
                'capacity': 12
            },
            {
                'name': 'Test Sprinter',
                'unit_amount': 150.00,
                'currency': 'USD',
                'date': '2025-08-15',
                'time': '18:00',
                'capacity': 12
            }
        ],
        'subtotal': 300.00,
        'total': 300.00,
        'customer': {
            'name': 'Round Trip User',
            'email': 'roundtrip@example.com',
            'phone': '0987654321',
            'address': '456 Return St',
            'city': 'Returnville',
            'zip': '54321',
        }
    },
    'group_transfer': {
        'trip_type': 'oneway',
        'people': 8,
        'pickup': {
            'datetime': '2025-08-10 12:00',
            'location_id': '1',
            'location_name': 'Hotel Test'
        },
        'dropoff': {
            'datetime': '2025-08-10 13:00',
            'location_id': '2',
            'location_name': 'Airport'
        },
        'car_type_label': 'BUS',
        'items': [
            {
                'name': 'Test Bus',
                'unit_amount': 200.00,
                'currency': 'USD',
                'date': '2025-08-10',
                'time': '12:00',
                'capacity': 20
            }
        ],
        'subtotal': 200.00,
        'total': 200.00,
        'customer': {
            'name': 'Group Leader',
            'email': 'group@example.com',
            'phone': '5551234567',
            'address': '789 Group Ave',
            'city': 'Group City',
            'zip': '98765',
        }
    }
}

# Test payment scenarios
PAYMENT_SCENARIOS = {
    'successful_payment': {
        'description': 'Standard successful payment flow',
        'expected_status': 'success',
        'expected_emails': 2,  # Guest + test recipients
        'expected_amount': 75.00
    },
    'payment_failure': {
        'description': 'Payment failure handling',
        'expected_status': 'failed',
        'expected_emails': 0,
        'expected_amount': 75.00
    },
    'payment_cancellation': {
        'description': 'User cancels payment',
        'expected_status': 'cancelled',
        'expected_emails': 0,
        'expected_amount': 75.00
    },
    'insufficient_funds': {
        'description': 'Card with insufficient funds',
        'expected_status': 'failed',
        'expected_emails': 0,
        'expected_amount': 75.00
    },
    '3d_secure_challenge': {
        'description': '3D Secure authentication required',
        'expected_status': 'requires_action',
        'expected_emails': 0,
        'expected_amount': 75.00
    }
}

# Test validation rules
VALIDATION_RULES = {
    'email': {
        'valid': ['test@example.com', 'user.name@domain.co.uk', 'user+tag@domain.org'],
        'invalid': ['invalid-email', '@domain.com', 'user@', 'user.domain.com']
    },
    'phone': {
        'valid': ['1234567890', '+1-234-567-8900', '(123) 456-7890'],
        'invalid': ['abc', '123', '123-456-789']
    },
    'amount': {
        'valid': [0.01, 10.00, 100.50, 9999.99],
        'invalid': [-10.00, 0, 'invalid', None]
    },
    'currency': {
        'valid': ['USD', 'EUR', 'MXN', 'CAD'],
        'invalid': ['INVALID', '123', '', None]
    }
}

# Test environment utilities
def get_test_stripe_keys():
    """Get Stripe test keys for current environment"""
    return CURRENT_TEST_CONFIG['stripe_keys']

def get_test_paypal_keys():
    """Get PayPal test keys for current environment"""
    return CURRENT_TEST_CONFIG['paypal_keys']

def get_test_amounts():
    """Get test amounts for current environment"""
    return CURRENT_TEST_CONFIG['test_amounts']

def get_test_currencies():
    """Get test currencies for current environment"""
    return CURRENT_TEST_CONFIG['test_currencies']

def get_test_cards():
    """Get test card numbers for current environment"""
    return CURRENT_TEST_CONFIG['test_cards']

def create_test_order(template_name='simple_transfer', **overrides):
    """Create a test order with optional overrides"""
    order = SAMPLE_ORDERS[template_name].copy()
    order.update(overrides)
    return order

def is_staging_environment():
    """Check if current test environment is staging"""
    return TEST_ENVIRONMENT == 'staging'

def is_production_environment():
    """Check if current test environment is production"""
    return TEST_ENVIRONMENT == 'production'

# Test database configuration
TEST_DATABASE_CONFIG = {
    'staging': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
    'production': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TEST_DB_NAME', 'test_speedy_transfers'),
        'USER': os.getenv('TEST_DB_USER', 'test_user'),
        'PASSWORD': os.getenv('TEST_DB_PASSWORD', 'test_password'),
        'HOST': os.getenv('TEST_DB_HOST', 'localhost'),
        'PORT': os.getenv('TEST_DB_PORT', '5432'),
    }
}

def get_test_database_config():
    """Get database configuration for current test environment"""
    return TEST_DATABASE_CONFIG[TEST_ENVIRONMENT]

# Test email configuration
TEST_EMAIL_CONFIG = {
    'staging': {
        'BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
        'TEST_EMAILS': ['test@staging.example.com']
    },
    'production': {
        'BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'TEST_EMAILS': ['test@production.example.com']
    }
}

def get_test_email_config():
    """Get email configuration for current test environment"""
    return TEST_EMAIL_CONFIG[TEST_ENVIRONMENT]
