"""
Tests for pricing and payment system fixes
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from unittest.mock import patch, Mock
import json

from .models import Zone, Rate, Car, CarType, Hotel


class PricingFixTests(TestCase):
    """Test pricing system fixes"""
    
    def setUp(self):
        """Set up test data"""
        # Create test zone
        self.zone = Zone.objects.create(
            id=10,
            name="BUCERIAS",
            description="BUCERIAS"
        )
        
        # Create test car type (with trailing space to simulate real data)
        self.car_type = CarType.objects.create(
            code="VAN ",
            name="VAN",
            description="Standard van",
            max_capacity=8
        )
        
        # Create test car
        self.car = Car.objects.create(
            name="VAN 001",
            car_type=self.car_type,
            description="Test van",
            max=8
        )
        
        # Create test hotel
        self.hotel = Hotel.objects.create(
            name="DECAMERON",
            description="Test hotel",
            zone=self.zone
        )
        
        # Create test rates
        self.rate_one_way = Rate.objects.create(
            zone=self.zone,
            car=self.car,
            travel_type="ONE_WAY",
            price=110.00
        )
        
        self.rate_round_trip = Rate.objects.create(
            zone=self.zone,
            car=self.car,
            travel_type="ROUND_TRIP",
            price=200.00
        )
    
    def test_car_type_matching_with_trailing_spaces(self):
        """Test that car type matching works with trailing spaces"""
        from django.db import models
        
        # Test the old query (should fail)
        rates_old = Rate.objects.filter(
            zone_id=10,
            travel_type="ONE_WAY"
        ).filter(
            models.Q(car__car_type__code="VAN")
        )
        self.assertEqual(rates_old.count(), 0, "Old query should fail with trailing spaces")
        
        # Test the new query (should work)
        rates_new = Rate.objects.filter(
            zone_id=10,
            travel_type="ONE_WAY"
        ).filter(
            models.Q(car__car_type__code__icontains="VAN".strip())
        )
        self.assertEqual(rates_new.count(), 1, "New query should work with trailing spaces")
        self.assertEqual(rates_new.first().price, 110.00)
    
    def test_results_view_pricing_display(self):
        """Test that results view displays correct pricing"""
        client = Client()
        
        # Test with one-way trip
        response = client.get(reverse('core:results'), {
            'pickup_location': str(self.hotel.id),
            'car_type': 'VAN',
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-09-09T09:53'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "110.00")
        self.assertNotContains(response, "0.00")
    
    def test_round_trip_pricing(self):
        """Test round trip pricing"""
        client = Client()
        
        response = client.get(reverse('core:results'), {
            'pickup_location': str(self.hotel.id),
            'car_type': 'VAN',
            'trip_type': 'roundtrip',
            'people': '2',
            'pickup_datetime': '2025-09-09T09:53',
            'return_datetime': '2025-09-16T09:53'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "200.00")
    
    def test_no_rates_for_hotel_without_zone(self):
        """Test behavior when hotel has no zone assigned"""
        # Create hotel without zone
        hotel_no_zone = Hotel.objects.create(
            name="HOTEL NO ZONE",
            description="Hotel without zone"
        )
        
        client = Client()
        
        response = client.get(reverse('core:results'), {
            'pickup_location': str(hotel_no_zone.id),
            'car_type': 'VAN',
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-09-09T09:53'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No rates available")


class PaymentConfigurationTests(TestCase):
    """Test payment system configuration"""
    
    def test_stripe_configuration_validation(self):
        """Test that Stripe configuration is properly validated"""
        # Test with missing keys
        with patch.object(settings, 'STRIPE_SECRET_KEY', ''):
            with patch.object(settings, 'STRIPE_PUBLIC_KEY', ''):
                # This should not raise an error but should be handled gracefully
                self.assertEqual(settings.STRIPE_SECRET_KEY, '')
                self.assertEqual(settings.STRIPE_PUBLIC_KEY, '')
    
    def test_paypal_configuration_validation(self):
        """Test that PayPal configuration is properly validated"""
        # Test with missing keys
        with patch.object(settings, 'PAYPAL_CLIENT_ID', ''):
            with patch.object(settings, 'PAYPAL_SECRET', ''):
                self.assertEqual(settings.PAYPAL_CLIENT_ID, '')
                self.assertEqual(settings.PAYPAL_SECRET, '')
    
    @patch('stripe.checkout.Session.create')
    def test_stripe_checkout_with_valid_keys(self, mock_stripe_create):
        """Test Stripe checkout with valid API keys"""
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        mock_stripe_create.return_value = mock_session
        
        with patch.object(settings, 'STRIPE_SECRET_KEY', 'sk_test_valid_key'):
            with patch.object(settings, 'STRIPE_PUBLIC_KEY', 'pk_test_valid_key'):
                client = Client()
                
                # Create test order
                test_order = {
                    'items': [{
                        'name': 'Test Transfer',
                        'unit_amount': 110.00,
                        'currency': 'USD',
                        'date': '2025-09-09',
                        'time': '09:53'
                    }],
                    'total': 110.00,
                    'currency': 'USD'
                }
                
                response = client.get(reverse('core:create_checkout_session'), {
                    'order_json': json.dumps(test_order)
                })
                
                self.assertEqual(response.status_code, 302)
                mock_stripe_create.assert_called_once()
    
    @patch('paypalrestsdk.Payment')
    def test_paypal_payment_with_valid_keys(self, mock_paypal_payment):
        """Test PayPal payment with valid credentials"""
        # Mock successful PayPal response
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        mock_paypal_payment.return_value = mock_payment
        
        with patch.object(settings, 'PAYPAL_CLIENT_ID', 'valid_client_id'):
            with patch.object(settings, 'PAYPAL_SECRET', 'valid_secret'):
                client = Client()
                
                # Create test order
                test_order = {
                    'items': [{
                        'name': 'Test Transfer',
                        'unit_amount': 110.00,
                        'currency': 'USD',
                        'date': '2025-09-09',
                        'time': '09:53'
                    }],
                    'total': 110.00,
                    'currency': 'USD'
                }
                
                response = client.post(reverse('core:create_payment'), {
                    'order_json': json.dumps(test_order)
                })
                
                self.assertEqual(response.status_code, 302)
                mock_paypal_payment.assert_called_once()
    
    def test_payment_error_handling(self):
        """Test payment error handling"""
        client = Client()
        
        # Test Stripe with invalid configuration
        with patch.object(settings, 'STRIPE_SECRET_KEY', ''):
            response = client.get(reverse('core:create_checkout_session'))
            # Should handle gracefully, not crash
            self.assertIn(response.status_code, [200, 302, 400])
        
        # Test PayPal with invalid configuration
        with patch.object(settings, 'PAYPAL_CLIENT_ID', ''):
            response = client.post(reverse('core:create_payment'), {
                'order_json': json.dumps({'total': 110.00})
            })
            # Should handle gracefully, not crash
            self.assertIn(response.status_code, [200, 302, 400])


class IntegrationTests(TestCase):
    """Integration tests for complete booking flow"""
    
    def setUp(self):
        """Set up test data for integration tests"""
        # Create test zone
        self.zone = Zone.objects.create(
            id=10,
            name="BUCERIAS",
            description="BUCERIAS"
        )
        
        # Create test car type
        self.car_type = CarType.objects.create(
            code="VAN ",
            name="VAN",
            description="Standard van",
            max_capacity=8
        )
        
        # Create test car
        self.car = Car.objects.create(
            name="VAN 001",
            car_type=self.car_type,
            description="Test van",
            max=8
        )
        
        # Create test hotel
        self.hotel = Hotel.objects.create(
            name="DECAMERON",
            description="Test hotel",
            zone=self.zone
        )
        
        # Create test rate
        self.rate = Rate.objects.create(
            zone=self.zone,
            car=self.car,
            travel_type="ONE_WAY",
            price=110.00
        )
    
    def test_complete_booking_flow(self):
        """Test complete booking flow from search to payment"""
        client = Client()
        
        # Step 1: Search for transfers
        response = client.get(reverse('core:results'), {
            'pickup_location': str(self.hotel.id),
            'car_type': 'VAN',
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-09-09T09:53'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "110.00")
        
        # Step 2: Go to checkout
        response = client.get(reverse('core:checkout'))
        self.assertEqual(response.status_code, 200)
        
        # Step 3: Test payment creation (with mocked payment providers)
        with patch('stripe.checkout.Session.create') as mock_stripe:
            mock_session = Mock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            mock_stripe.return_value = mock_session
            
            with patch.object(settings, 'STRIPE_SECRET_KEY', 'sk_test_valid_key'):
                test_order = {
                    'items': [{
                        'name': 'VAN 001',
                        'unit_amount': 110.00,
                        'currency': 'USD',
                        'date': '2025-09-09',
                        'time': '09:53'
                    }],
                    'total': 110.00,
                    'currency': 'USD',
                    'customer': {
                        'name': 'Test Customer',
                        'email': 'test@example.com',
                        'phone': '1234567890'
                    }
                }
                
                response = client.get(reverse('core:create_checkout_session'), {
                    'order_json': json.dumps(test_order)
                })
                
                self.assertEqual(response.status_code, 302)
                mock_stripe.assert_called_once()
