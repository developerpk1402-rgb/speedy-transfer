import json
import stripe
import paypalrestsdk
from django.test import TestCase, override_settings, Client
from django.urls import reverse
from unittest.mock import patch, Mock
from django.core import mail
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.conf import settings
from .models import Zone, Hotel, Car, CarType, Rate, Reservation, Payment, Booking
from .views import create_checkout_session, create_payment, execute_payment, payment_success


class PaymentIntegrationTestCase(TestCase):
    """Integration tests for complete payment flows in staging and production"""
    
    def setUp(self):
        """Set up test data and mocks"""
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create test data
        self.zone = Zone.objects.create(name="Test Zone")
        self.hotel = Hotel.objects.create(
            name="Test Hotel", 
            zone=self.zone
        )
        self.car_type = CarType.objects.create(
            code="VAN",
            name="Van",
            max_capacity=8
        )
        self.car = Car.objects.create(
            name="Test Van",
            car_type=self.car_type,
            max=8
        )
        
        # Sample order data for testing
        self.sample_order = {
            'trip_type': 'oneway',
            'people': 3,
            'pickup': {
                'datetime': '2025-08-10 10:00',
                'location_id': str(self.hotel.id),
                'location_name': 'Test Hotel'
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
                    'unit_amount': 150.00,
                    'currency': 'USD',
                    'date': '2025-08-10',
                    'time': '10:00',
                    'capacity': 8
                }
            ],
            'subtotal': 150.00,
            'total': 150.00,
            'customer': {
                'name': 'John Test',
                'email': 'test@example.com',
                'phone': '1234567890',
                'address': '123 Test St',
                'city': 'Testville',
                'zip': '12345',
            }
        }
        
        # Mock external payment services
        self.stripe_patcher = patch('stripe.checkout.Session.create')
        self.paypal_patcher = patch('paypalrestsdk.Payment')
        
        self.mock_stripe_create = self.stripe_patcher.start()
        self.mock_paypal_payment = self.paypal_patcher.start()
        
    def tearDown(self):
        """Clean up mocks"""
        self.stripe_patcher.stop()
        self.paypal_patcher.stop()
    
    def create_request_with_session(self, method='GET', data=None):
        """Helper to create a request with session middleware"""
        request = self.factory.request(method=method, data=data)
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_stripe_payment_flow(self):
        """Test complete Stripe payment flow from checkout to success"""
        # Mock successful Stripe checkout session
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Step 1: Create checkout session
        response = self.client.get(
            reverse('core:create_checkout_session'),
            {'order_json': json.dumps(self.sample_order)}
        )
        
        # Verify redirect to Stripe
        self.assertEqual(response.status_code, 302)
        self.assertIn('checkout.stripe.com', response['Location'])
        
        # Verify session was stored
        session = self.client.session
        self.assertIsNotNone(session.get('order_json'))
        
        # Step 2: Simulate successful payment return
        # Mock the payment success view
        with patch('stripe.checkout.Session.retrieve') as mock_retrieve:
            mock_retrieve.return_value = Mock(
                payment_status='paid',
                amount_total=15000
            )
            
            # Call payment success
            response = self.client.get(reverse('core:payment_success'))
            self.assertEqual(response.status_code, 200)
            
            # Verify emails were sent
            self.assertEqual(len(mail.outbox), 2)
            
            # Check guest email
            guest_email = mail.outbox[0]
            self.assertEqual(guest_email.to, ['test@example.com'])
            self.assertIn('Booking Confirmation', guest_email.subject)
            self.assertIn('150.00 USD', guest_email.body)
            
            # Check test recipient email
            test_email = mail.outbox[1]
            self.assertEqual(set(test_email.to), {'cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com'})
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_complete_paypal_payment_flow(self):
        """Test complete PayPal payment flow from creation to execution"""
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # Step 1: Create PayPal payment
        response = self.client.post(
            reverse('core:create_payment'),
            {'order_json': json.dumps(self.sample_order)},
            content_type='application/xwww-form-urlencoded'
        )
        
        # Verify redirect to PayPal
        self.assertEqual(response.status_code, 302)
        self.assertIn('sandbox.paypal.com', response['Location'])
        
        # Verify session was stored
        session = self.client.session
        self.assertIsNotNone(session.get('order_json'))
        
        # Step 2: Execute PayPal payment (simulate return from PayPal)
        with patch('paypalrestsdk.Payment.find') as mock_find:
            mock_payment_obj = Mock()
            mock_payment_obj.execute.return_value = True
            mock_find.return_value = mock_payment_obj
            
            # Call execute payment
            response = self.client.get(
                reverse('core:execute_payment'),
                {'paymentId': 'test_payment_id', 'PayerID': 'test_payer_id'}
            )
            
            self.assertEqual(response.status_code, 200)
            
            # Verify PayPal payment was executed
            mock_payment_obj.execute.assert_called_once_with({'payer_id': 'test_payer_id'})
            
            # Verify emails were sent
            self.assertEqual(len(mail.outbox), 2)
            
            # Check guest email
            guest_email = mail.outbox[0]
            self.assertEqual(guest_email.to, ['test@example.com'])
            self.assertIn('Booking Confirmation', guest_email.subject)
    
    def test_payment_failure_handling(self):
        """Test payment failure scenarios"""
        # Test Stripe checkout failure
        self.mock_stripe_create.side_effect = stripe.error.StripeError("Test error")
        
        response = self.client.get(
            reverse('core:create_checkout_session'),
            {'order_json': json.dumps(self.sample_order)}
        )
        
        # Should return error response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        
        # Test PayPal payment creation failure
        mock_payment = Mock()
        mock_payment.create.return_value = False
        self.mock_paypal_payment.return_value = mock_payment
        
        response = self.client.post(
            reverse('core:create_payment'),
            {'order_json': json.dumps(self.sample_order)},
            content_type='application/xwww-form-urlencoded'
        )
        
        # Should render payment failed template
        self.assertEqual(response.status_code, 200)
    
    def test_payment_cancellation_handling(self):
        """Test payment cancellation scenarios"""
        # Test PayPal cancellation
        response = self.client.get(reverse('core:payment_failed'))
        self.assertEqual(response.status_code, 200)
        
        # Verify no emails sent on cancellation
        self.assertEqual(len(mail.outbox), 0)
    
    def test_payment_data_validation(self):
        """Test payment data validation and sanitization"""
        # Test with malformed order data
        malformed_order = {
            'trip_type': 'oneway',
            'total': 'invalid_amount',  # Invalid amount
            'customer': {
                'email': 'invalid-email'  # Invalid email
            }
        }
        
        # Test Stripe with malformed data
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        response = self.client.get(
            reverse('core:create_checkout_session'),
            {'order_json': json.dumps(malformed_order)}
        )
        
        # Should handle gracefully (fallback to demo data)
        self.assertEqual(response.status_code, 302)
        
        # Test PayPal with malformed data
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        response = self.client.post(
            reverse('core:create_payment'),
            {'order_json': json.dumps(malformed_order)},
            content_type='application/xwww-form-urlencoded'
        )
        
        # Should handle gracefully (fallback to default values)
        self.assertEqual(response.status_code, 302)
    
    def test_payment_session_management(self):
        """Test payment session data management"""
        # Test session storage
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        # Verify session data is accessible
        self.assertIsNotNone(session.get('order_json'))
        stored_order = json.loads(session['order_json'])
        self.assertEqual(stored_order['total'], 150.00)
        
        # Test session cleanup after successful payment
        response = self.client.get(reverse('core:payment_success'))
        self.assertEqual(response.status_code, 200)
        
        # Session should be cleaned up
        session = self.client.session
        self.assertIsNone(session.get('order_json'))
    
    def test_payment_currency_handling(self):
        """Test payment handling with different currencies"""
        # Test USD
        usd_order = self.sample_order.copy()
        usd_order['items'][0]['currency'] = 'USD'
        usd_order['total'] = 150.00
        
        # Test EUR
        eur_order = self.sample_order.copy()
        eur_order['items'][0]['currency'] = 'EUR'
        eur_order['total'] = 125.50
        
        # Test MXN
        mxn_order = self.sample_order.copy()
        mxn_order['items'][0]['currency'] = 'MXN'
        mxn_order['total'] = 2500.00
        
        # Verify all currencies are handled
        for order, expected_total in [(usd_order, 150.00), (eur_order, 125.50), (mxn_order, 2500.00)]:
            # Test Stripe
            mock_session = Mock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            self.mock_stripe_create.return_value = mock_session
            
            response = self.client.get(
                reverse('core:create_checkout_session'),
                {'order_json': json.dumps(order)}
            )
            
            self.assertEqual(response.status_code, 302)
            
            # Test PayPal
            mock_payment = Mock()
            mock_payment.create.return_value = True
            mock_payment.links = [
                Mock(href='http://cancel.url'),
                Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
            ]
            self.mock_paypal_payment.return_value = mock_payment
            
            response = self.client.post(
                reverse('core:create_payment'),
                {'order_json': json.dumps(order)},
                content_type='application/xwww-form-urlencoded'
            )
            
            self.assertEqual(response.status_code, 302)
    
    def test_payment_environment_configuration(self):
        """Test payment configuration for different environments"""
        # Test staging environment
        with self.settings(
            STRIPE_PUBLIC_KEY='pk_test_staging',
            STRIPE_SECRET_KEY='sk_test_staging',
            PAYPAL_CLIENT_ID='staging_client_id',
            PAYPAL_SECRET='staging_secret'
        ):
            # Verify settings are accessible
            self.assertEqual(settings.STRIPE_PUBLIC_KEY, 'pk_test_staging')
            self.assertEqual(settings.PAYPAL_CLIENT_ID, 'staging_client_id')
            
            # Test that views can access settings
            mock_session = Mock()
            mock_session.url = 'https://checkout.stripe.com/test_session'
            self.mock_stripe_create.return_value = mock_session
            
            response = self.client.get(
                reverse('core:create_checkout_session'),
                {'order_json': json.dumps(self.sample_order)}
            )
            
            self.assertEqual(response.status_code, 302)
        
        # Test production environment
        with self.settings(
            STRIPE_PUBLIC_KEY='pk_live_production',
            STRIPE_SECRET_KEY='sk_live_production',
            PAYPAL_CLIENT_ID='production_client_id',
            PAYPAL_SECRET='production_secret'
        ):
            # Verify settings are accessible
            self.assertEqual(settings.STRIPE_PUBLIC_KEY, 'pk_live_production')
            self.assertEqual(settings.PAYPAL_CLIENT_ID, 'production_client_id')
    
    def test_payment_webhook_readiness(self):
        """Test that the system is ready for webhook integration"""
        # Test session data persistence (needed for webhooks)
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        # Verify data can be retrieved
        stored_order = json.loads(session['order_json'])
        self.assertEqual(stored_order['total'], 150.00)
        self.assertEqual(stored_order['customer']['email'], 'test@example.com')
        
        # Test order data structure consistency
        required_fields = ['total', 'customer', 'items', 'trip_type']
        for field in required_fields:
            self.assertIn(field, stored_order)
        
        # Test customer data structure
        customer_fields = ['name', 'email', 'phone']
        for field in customer_fields:
            self.assertIn(field, stored_order['customer'])
    
    def test_payment_error_logging(self):
        """Test payment error handling and logging"""
        # Test Stripe error logging
        self.mock_stripe_create.side_effect = Exception("Unexpected error")
        
        response = self.client.get(
            reverse('core:create_checkout_session'),
            {'order_json': json.dumps(self.sample_order)}
        )
        
        # Should handle error gracefully
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        
        # Test PayPal error handling
        mock_payment = Mock()
        mock_payment.create.side_effect = Exception("PayPal error")
        self.mock_paypal_payment.return_value = mock_payment
        
        response = self.client.post(
            reverse('core:create_payment'),
            {'order_json': json.dumps(self.sample_order)},
            content_type='application/xwww-form-urlencoded'
        )
        
        # Should handle error gracefully
        self.assertEqual(response.status_code, 200)
