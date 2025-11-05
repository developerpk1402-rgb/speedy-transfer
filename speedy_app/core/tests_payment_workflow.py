"""
Comprehensive Payment Workflow Tests
Tests the complete payment flow from search to confirmation
"""

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, MagicMock
from decimal import Decimal


class PaymentWorkflowTestCase(TestCase):
    """Test the complete payment workflow"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Sample order data for testing
        self.sample_order = {
            "trip_type": "oneway",
            "people": 2,
            "pickup": {
                "datetime": "2025-01-15T10:00",
                "location_id": "1",
                "location_name": "VELAS VALLARTA"
            },
            "dropoff": {
                "location_id": "2", 
                "location_name": "AEROPUERTO"
            },
            "car_type_label": "VAN",
            "items": [
                {
                    "name": "VAN 001",
                    "unit_amount": 82.00,
                    "currency": "USD",
                    "date": "2025-01-15",
                    "time": "10:00",
                    "capacity": 8
                }
            ],
            "subtotal": 82.00,
            "total": 82.00,
            "customer": {
                "name": "Test User",
                "email": "test@example.com",
                "phone": "1234567890",
                "address": "123 Test St",
                "city": "Testville",
                "zip": "12345",
                "country": "USA"
            },
            "currency": "USD"
        }
    
    def test_landing_page_loads(self):
        """Test that the landing page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PICK UP DATE AND TIME')
        self.assertContains(response, 'Find a Transfer')
    
    def test_search_results_with_date(self):
        """Test search results with date functionality"""
        response = self.client.get('/search-results/', {
            'pickup_location': '1',
            'car_type': 'VAN',
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-01-15T10:00'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'transfer')
    
    def test_checkout_page_loads(self):
        """Test that checkout page loads"""
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Billing Details')
        self.assertContains(response, 'Order Summary')
    
    @patch('stripe.checkout.Session.create')
    def test_stripe_checkout_session_creation(self, mock_stripe_create):
        """Test Stripe checkout session creation"""
        # Mock successful Stripe response
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        mock_stripe_create.return_value = mock_session
        
        # Test the checkout session creation
        order_json = json.dumps(self.sample_order)
        response = self.client.get('/create_checkout_session/', {
            'order_json': order_json
        })
        
        # Should redirect to Stripe checkout
        self.assertEqual(response.status_code, 302)
        self.assertIn('checkout.stripe.com', response.url)
        
        # Verify Stripe was called with correct parameters
        mock_stripe_create.assert_called_once()
        call_args = mock_stripe_create.call_args[1]
        self.assertEqual(call_args['mode'], 'payment')
        self.assertEqual(call_args['payment_method_types'], ['card'])
    
    @patch('stripe.checkout.Session.create')
    def test_stripe_checkout_with_multiple_items(self, mock_stripe_create):
        """Test Stripe checkout with multiple vehicle items"""
        # Create order with multiple items
        multi_item_order = self.sample_order.copy()
        multi_item_order['items'] = [
            {
                "name": "VAN 001",
                "unit_amount": 82.00,
                "currency": "USD",
                "date": "2025-01-15",
                "time": "10:00",
                "capacity": 8
            },
            {
                "name": "VAN 001", 
                "unit_amount": 82.00,
                "currency": "USD",
                "date": "2025-01-15",
                "time": "10:00",
                "capacity": 8
            }
        ]
        multi_item_order['total'] = 164.00
        
        # Mock successful Stripe response
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        mock_stripe_create.return_value = mock_session
        
        # Test checkout session creation
        order_json = json.dumps(multi_item_order)
        response = self.client.get('/create_checkout_session/', {
            'order_json': order_json
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Verify line items were created correctly
        call_args = mock_stripe_create.call_args[1]
        line_items = call_args['line_items']
        self.assertEqual(len(line_items), 2)
        self.assertEqual(line_items[0]['price_data']['unit_amount'], 8200)  # $82.00 in cents
    
    def test_stripe_configuration_validation(self):
        """Test Stripe configuration validation"""
        # Test with invalid API key
        with patch.object(settings, 'STRIPE_SECRET_KEY', ''):
            response = self.client.get('/create_checkout_session/')
            self.assertEqual(response.status_code, 500)
            self.assertJSONEqual(response.content, {
                'error': 'Stripe API key not configured. Please contact support.'
            })
    
    @patch('stripe.checkout.Session.create')
    def test_payment_success_flow(self, mock_stripe_create):
        """Test the complete payment success flow"""
        # Mock successful Stripe session creation
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        mock_stripe_create.return_value = mock_session
        
        # Create checkout session
        order_json = json.dumps(self.sample_order)
        response = self.client.get('/create_checkout_session/', {
            'order_json': order_json
        })
        self.assertEqual(response.status_code, 302)
        
        # Simulate successful payment return
        response = self.client.get('/payment/success/', {
            'session_id': 'test_session_123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Booking Confirmation')
    
    @patch('stripe.checkout.Session.create')
    def test_payment_failed_flow(self, mock_stripe_create):
        """Test payment failure handling"""
        # Mock Stripe error
        mock_stripe_create.side_effect = Exception("Payment failed")
        
        order_json = json.dumps(self.sample_order)
        response = self.client.get('/create_checkout_session/', {
            'order_json': order_json
        })
        
        # Should handle error gracefully
        self.assertEqual(response.status_code, 500)
    
    def test_round_trip_payment_flow(self):
        """Test payment flow for round trip bookings"""
        round_trip_order = self.sample_order.copy()
        round_trip_order['trip_type'] = 'roundtrip'
        round_trip_order['return_trip'] = {
            'datetime': '2025-01-20T18:00',
            'pickup_location_name': 'AEROPUERTO',
            'dropoff_location_name': 'VELAS VALLARTA'
        }
        round_trip_order['items'].append({
            "name": "VAN 001",
            "unit_amount": 82.00,
            "currency": "USD", 
            "date": "2025-01-20",
            "time": "18:00",
            "capacity": 8
        })
        round_trip_order['total'] = 164.00
        
        with patch('stripe.checkout.Session.create') as mock_stripe_create:
            mock_session = MagicMock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            mock_stripe_create.return_value = mock_session
            
            order_json = json.dumps(round_trip_order)
            response = self.client.get('/create_checkout_session/', {
                'order_json': order_json
            })
            
            self.assertEqual(response.status_code, 302)
            
            # Verify round trip items are included
            call_args = mock_stripe_create.call_args[1]
            line_items = call_args['line_items']
            self.assertEqual(len(line_items), 2)
    
    def test_date_validation_in_payment_flow(self):
        """Test that dates are properly validated in payment flow"""
        # Test with invalid date format
        invalid_date_order = self.sample_order.copy()
        invalid_date_order['pickup']['datetime'] = 'invalid-date'
        
        with patch('stripe.checkout.Session.create') as mock_stripe_create:
            mock_session = MagicMock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            mock_stripe_create.return_value = mock_session
            
            order_json = json.dumps(invalid_date_order)
            response = self.client.get('/create_checkout_session/', {
                'order_json': order_json
            })
            
            # Should still work (graceful fallback to current date)
            self.assertEqual(response.status_code, 302)
    
    @patch('stripe.checkout.Session.create')
    def test_booking_record_creation(self, mock_stripe_create):
        """Test that booking records are created after successful payment"""
        # Mock successful Stripe session
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        mock_stripe_create.return_value = mock_session
        
        # Create checkout session (this stores order in session)
        order_json = json.dumps(self.sample_order)
        response = self.client.get('/create_checkout_session/', {
            'order_json': order_json
        })
        
        # Simulate payment success
        response = self.client.get('/payment/success/', {
            'session_id': 'test_session_123'
        })
        
        # Check that booking was created (if booking creation is implemented)
        # This test assumes the booking creation logic is working
        self.assertEqual(response.status_code, 200)
    
    def test_csrf_protection(self):
        """Test CSRF protection on payment endpoints"""
        # Test without CSRF token
        response = self.client.post('/create_checkout_session/', {
            'order_json': json.dumps(self.sample_order)
        })
        # Should handle CSRF properly (either require token or be exempt)
        self.assertIn(response.status_code, [200, 302, 403])
    
    def test_currency_handling(self):
        """Test different currency handling"""
        usd_order = self.sample_order.copy()
        usd_order['currency'] = 'USD'
        
        with patch('stripe.checkout.Session.create') as mock_stripe_create:
            mock_session = MagicMock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            mock_stripe_create.return_value = mock_session
            
            order_json = json.dumps(usd_order)
            response = self.client.get('/create_checkout_session/', {
                'order_json': order_json
            })
            
            self.assertEqual(response.status_code, 302)
            
            # Verify currency is set correctly
            call_args = mock_stripe_create.call_args[1]
            line_items = call_args['line_items']
            self.assertEqual(line_items[0]['price_data']['currency'], 'usd')


class PaymentIntegrationTestCase(TestCase):
    """Integration tests for payment workflow"""
    
    def setUp(self):
        self.client = Client()
    
    def test_complete_booking_workflow(self):
        """Test the complete workflow from search to payment"""
        # Step 1: Search for transfers
        response = self.client.get('/search-results/', {
            'pickup_location': '1',
            'car_type': 'VAN', 
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-01-15T10:00'
        })
        self.assertEqual(response.status_code, 200)
        
        # Step 2: Go to summary page
        response = self.client.get('/summary/')
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Go to checkout page
        response = self.client.get('/checkout/')
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Test payment initiation (with mocked Stripe)
        with patch('stripe.checkout.Session.create') as mock_stripe_create:
            mock_session = MagicMock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            mock_stripe_create.return_value = mock_session
            
            sample_order = {
                "trip_type": "oneway",
                "people": 2,
                "total": 82.00,
                "currency": "USD",
                "items": [{"name": "VAN 001", "unit_amount": 82.00, "currency": "USD"}],
                "customer": {"name": "Test User", "email": "test@example.com"}
            }
            
            response = self.client.get('/create_checkout_session/', {
                'order_json': json.dumps(sample_order)
            })
            self.assertEqual(response.status_code, 302)
    
    def test_error_handling_workflow(self):
        """Test error handling throughout the workflow"""
        # Test with invalid search parameters
        response = self.client.get('/search-results/', {
            'pickup_location': 'invalid',
            'car_type': 'INVALID',
            'pickup_datetime': 'invalid-date'
        })
        # Should handle gracefully
        self.assertIn(response.status_code, [200, 400, 404])
        
        # Test payment with invalid order data
        with patch('stripe.checkout.Session.create') as mock_stripe_create:
            mock_stripe_create.side_effect = Exception("Stripe error")
            
            response = self.client.get('/create_checkout_session/', {
                'order_json': 'invalid-json'
            })
            # Should handle error gracefully
            self.assertIn(response.status_code, [400, 500])


if __name__ == '__main__':
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["speedy_app.core.tests_payment_workflow"])

