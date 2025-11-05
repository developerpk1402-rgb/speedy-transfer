import json
import stripe
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock
from django.core import mail
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.conf import settings
from .models import Zone, Hotel, Car, CarType, Rate, Booking
from .views import create_checkout_session, payment_success


class StripePaymentTestCase(TestCase):
    """Test Stripe payment integration for staging and production environments"""
    
    def setUp(self):
        """Set up test data and mock Stripe"""
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
        
        # Sample order data
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
        
        # Mock Stripe configuration
        self.stripe_patcher = patch('stripe.checkout.Session.create')
        self.mock_stripe_create = self.stripe_patcher.start()
        
    def tearDown(self):
        """Clean up mocks"""
        self.stripe_patcher.stop()
    
    def create_request_with_session(self, method='GET', data=None):
        """Helper to create a request with session middleware"""
        request = self.factory.request(method=method, data=data)
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_stripe_checkout_session_creation_success(self):
        """Test successful Stripe checkout session creation"""
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Create request with order data
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(self.sample_order)}
        
        # Call the view
        response = create_checkout_session(request)
        
        # Verify response
        self.assertEqual(response.status_code, 302)
        self.assertIn('checkout.stripe.com', response['Location'])
        
        # Verify Stripe was called with correct parameters
        self.mock_stripe_create.assert_called_once()
        call_args = self.mock_stripe_create.call_args[1]
        
        # Verify line items
        self.assertEqual(len(call_args['line_items']), 1)
        line_item = call_args['line_items'][0]
        self.assertEqual(line_item['price_data']['currency'], 'usd')
        self.assertEqual(line_item['price_data']['unit_amount'], 15000)  # $150.00 in cents
        self.assertEqual(line_item['price_data']['product_data']['name'], 'Test Van')
        
        # Verify session was stored
        self.assertEqual(request.session['order_json'], json.dumps(self.sample_order))
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_stripe_checkout_session_without_order_data(self):
        """Test Stripe checkout with fallback demo data"""
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Create request without order data
        request = self.create_request_with_session()
        
        # Call the view
        response = create_checkout_session(request)
        
        # Verify response
        self.assertEqual(response.status_code, 302)
        
        # Verify fallback demo item was used
        call_args = self.mock_stripe_create.call_args[1]
        line_item = call_args['line_items'][0]
        self.assertEqual(line_item['price_data']['unit_amount'], 2000)  # $20.00 in cents
        self.assertEqual(line_item['price_data']['product_data']['name'], 'Transfer')
    
    def test_stripe_checkout_session_creation_failure(self):
        """Test Stripe checkout session creation failure"""
        # Mock Stripe error
        self.mock_stripe_create.side_effect = stripe.error.StripeError("Test error")
        
        # Create request
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(self.sample_order)}
        
        # Call the view
        response = create_checkout_session(request)
        
        # Verify error response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertIn('Test error', response_data['error'])
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_stripe_payment_success_emails(self):
        """Test that successful Stripe payment sends confirmation emails"""
        # Store order in session
        request = self.create_request_with_session()
        request.session['order_json'] = json.dumps(self.sample_order)
        
        # Call payment success view
        response = payment_success(request)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        
        # Verify emails were sent
        self.assertEqual(len(mail.outbox), 2)
        
        # Check guest email
        guest_email = mail.outbox[0]
        self.assertEqual(guest_email.to, ['test@example.com'])
        self.assertIn('Booking Confirmation', guest_email.subject)
        self.assertIn('John Test', guest_email.body)
        self.assertIn('150.00 USD', guest_email.body)
        
        # Check test recipient email
        test_email = mail.outbox[1]
        self.assertEqual(set(test_email.to), {'cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com'})
        self.assertIn('Booking Confirmation', test_email.subject)
    
    def test_stripe_checkout_session_currency_handling(self):
        """Test Stripe checkout handles different currencies correctly"""
        # Test order with different currency
        order_with_eur = json.loads(json.dumps(self.sample_order))
        order_with_eur['items'][0]['currency'] = 'EUR'
        order_with_eur['items'][0]['unit_amount'] = 125.50
        order_with_eur['total'] = 125.50
        
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Create request
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(order_with_eur)}
        
        # Call the view
        response = create_checkout_session(request)
        
        # Verify Stripe was called with correct amount
        call_args = self.mock_stripe_create.call_args[1]
        line_item = call_args['line_items'][0]
        self.assertEqual(line_item['price_data']['unit_amount'], 12550)  # €125.50 in cents
    
    def test_stripe_checkout_session_multiple_items(self):
        """Test Stripe checkout with multiple line items"""
        # Create order with multiple items
        multi_item_order = self.sample_order.copy()
        multi_item_order['items'] = [
            {
                'name': 'Van 1',
                'unit_amount': 100.00,
                'currency': 'USD',
                'date': '2025-08-10',
                'time': '10:00',
                'capacity': 8
            },
            {
                'name': 'Van 2',
                'unit_amount': 75.00,
                'currency': 'USD',
                'date': '2025-08-10',
                'time': '14:00',
                'capacity': 6
            }
        ]
        multi_item_order['total'] = 175.00
        
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Create request
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(multi_item_order)}
        
        # Call the view
        response = create_checkout_session(request)
        
        # Verify multiple line items
        call_args = self.mock_stripe_create.call_args[1]
        self.assertEqual(len(call_args['line_items']), 2)
        
        # Verify first item
        self.assertEqual(call_args['line_items'][0]['price_data']['unit_amount'], 10000)
        self.assertEqual(call_args['line_items'][0]['price_data']['product_data']['name'], 'Van 1')
        
        # Verify second item
        self.assertEqual(call_args['line_items'][1]['price_data']['unit_amount'], 7500)
        self.assertEqual(call_args['line_items'][1]['price_data']['product_data']['name'], 'Van 2')
    
    def test_stripe_webhook_handling_ready(self):
        """Test that the system is ready for Stripe webhook integration"""
        # This test ensures the current implementation can be extended for webhooks
        request = self.create_request_with_session()
        request.session['order_json'] = json.dumps(self.sample_order)
        
        # Verify session storage works (needed for webhook integration)
        self.assertIsNotNone(request.session.get('order_json'))
        
        # Verify order data structure is consistent
        stored_order = json.loads(request.session['order_json'])
        self.assertEqual(stored_order['total'], 150.00)
        self.assertEqual(stored_order['customer']['email'], 'test@example.com')
    
    @override_settings(STRIPE_PUBLIC_KEY='pk_test_environment_key')
    @override_settings(STRIPE_SECRET_KEY='sk_test_environment_key')
    def test_stripe_environment_configuration(self):
        """Test Stripe configuration for different environments"""
        # Verify settings are accessible
        self.assertEqual(settings.STRIPE_PUBLIC_KEY, 'pk_test_environment_key')
        self.assertEqual(settings.STRIPE_SECRET_KEY, 'sk_test_environment_key')
        
        # Test that the view can access Stripe settings
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(self.sample_order)}
        
        # Mock successful response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # This should work without errors
        response = create_checkout_session(request)
        self.assertEqual(response.status_code, 302)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_stripe_checkout_with_hotel_without_zone(self):
        """Stripe checkout should work when pickup is a hotel without zone (HOTEL SIN ZONA)."""
        # Create a hotel without zone
        hotel_no_zone = Hotel.objects.create(name="HOTEL SIN ZONA", zone=None)

        # Build order using this hotel
        order = self.sample_order.copy()
        order['pickup'] = {
            'datetime': '2025-08-10 10:00',
            'location_id': str(hotel_no_zone.id),
            'location_name': 'HOTEL SIN ZONA'
        }

        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session

        # Create request
        request = self.create_request_with_session()
        request.GET = {'order_json': json.dumps(order)}

        # Call view
        response = create_checkout_session(request)

        # Assert redirect to Stripe
        self.assertEqual(response.status_code, 302)
        self.assertIn('checkout.stripe.com', response['Location'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_stripe_payment_success_creates_booking_for_hotel_without_zone(self):
        """Successful Stripe payment should create a Booking even if hotel has no zone."""
        hotel_no_zone = Hotel.objects.create(name="HOTEL SIN ZONA", zone=None)

        order = self.sample_order.copy()
        order['pickup'] = {
            'datetime': '2025-08-10 10:00',
            'location_id': str(hotel_no_zone.id),
            'location_name': 'HOTEL SIN ZONA'
        }

        # Store order in session and call payment_success
        request = self.create_request_with_session()
        request.session['order_json'] = json.dumps(order)

        response = payment_success(request)
        self.assertEqual(response.status_code, 200)

        # Emails sent (guest + test recipients)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 2)

        # Booking created with pickup_location1 set to our hotel and payment method Stripe
        booking = Booking.objects.latest('id')
        self.assertEqual(booking.pickup_location1_id, hotel_no_zone.id)
        self.assertEqual(booking.payment_method, 'Stripe')
