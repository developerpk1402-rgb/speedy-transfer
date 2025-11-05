"""
Mock Stripe implementation for testing
This provides a mock Stripe API that simulates real Stripe behavior
"""

import json
from datetime import datetime


class MockStripeSession:
    """Mock Stripe Checkout Session"""
    
    def __init__(self, **kwargs):
        self.id = f"cs_test_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        # Redirect to our local mock checkout page instead of Stripe
        self.url = f"http://localhost:8000/mock_stripe_checkout/?session_id={self.id}"
        self.payment_status = "unpaid"
        self.amount_total = kwargs.get('amount_total', 0)
        self.currency = kwargs.get('currency', 'usd')
        self.customer_email = kwargs.get('customer_email', '')
        self.metadata = kwargs.get('metadata', {})


class MockStripeCheckout:
    """Mock Stripe Checkout API"""
    
    class Session:
        @staticmethod
        def create(**kwargs):
            """Mock session creation"""
            return MockStripeSession(**kwargs)
        
        @staticmethod
        def retrieve(session_id):
            """Mock session retrieval"""
            return MockStripeSession(id=session_id)


class MockStripe:
    """Mock Stripe module"""
    
    def __init__(self):
        self.api_key = None
        self.checkout = MockStripeCheckout()
    
    def __getattr__(self, name):
        """Return mock objects for any Stripe API"""
        if name == 'checkout':
            return MockStripeCheckout()
        return MockStripe()


# Global mock instance
mock_stripe = MockStripe()
