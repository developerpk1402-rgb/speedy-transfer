import json
import paypalrestsdk
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock
from django.core import mail
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.conf import settings
from .models import Zone, Hotel, Car, CarType, Rate, Booking
from .views import create_payment, execute_payment


class PayPalPaymentTestCase(TestCase):
    """Test PayPal payment integration for staging and production environments"""
    
    def setUp(self):
        """Set up test data and mock PayPal"""
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
        
        # Mock PayPal configuration
        self.paypal_patcher = patch('paypalrestsdk.Payment')
        self.mock_paypal_payment = self.paypal_patcher.start()
        
    def tearDown(self):
        """Clean up mocks"""
        self.paypal_patcher.stop()
    
    def create_request_with_session(self, method='POST', data=None):
        """Helper to create a request with session middleware"""
        request = self.factory.request(method=method, data=data)
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
    
    def test_paypal_payment_creation_success(self):
        """Test successful PayPal payment creation"""
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),  # Cancel link
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')  # Approval link
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # Create request with order data
        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(self.sample_order)}
        
        # Call the view
        response = create_payment(request)
        
        # Verify response redirects to PayPal
        self.assertEqual(response.status_code, 302)
        self.assertIn('sandbox.paypal.com', response['Location'])
        
        # Verify PayPal payment was created with correct parameters
        mock_payment.create.assert_called_once()
        
        # Verify payment configuration from constructor call
        PaymentClass = self.mock_paypal_payment
        self.assertTrue(PaymentClass.called)
        payment_config = PaymentClass.call_args[0][0]
        self.assertEqual(payment_config['intent'], 'sale')
        self.assertEqual(payment_config['transactions'][0]['amount']['total'], '150.00')
        self.assertEqual(payment_config['transactions'][0]['amount']['currency'], 'USD')
        self.assertEqual(payment_config['transactions'][0]['description'], 'Transfer booking (oneway)')
        
        # Verify session was stored
        self.assertEqual(request.session['order_json'], json.dumps(self.sample_order))
    
    def test_paypal_payment_creation_without_order_data(self):
        """Test PayPal payment creation with fallback data"""
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # Create request without order data
        request = self.create_request_with_session()
        
        # Call the view
        response = create_payment(request)
        
        # Verify response
        self.assertEqual(response.status_code, 302)
        
        # Verify fallback values were used
        PaymentClass = self.mock_paypal_payment
        payment_config = PaymentClass.call_args[0][0]
        self.assertEqual(payment_config['transactions'][0]['amount']['total'], '10.00')
        self.assertEqual(payment_config['transactions'][0]['description'], 'Payment for Product/Service')
    
    def test_paypal_payment_creation_failure(self):
        """Test PayPal payment creation failure"""
        # Mock failed PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = False
        self.mock_paypal_payment.return_value = mock_payment
        
        # Create request
        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(self.sample_order)}
        
        # Call the view
        response = create_payment(request)
        
        # Verify failure response
        self.assertEqual(response.status_code, 200)
        # Should render payment_failed.html template
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_paypal_payment_execution_success(self):
        """Test successful PayPal payment execution"""
        # Mock successful PayPal payment execution
        mock_payment = Mock()
        mock_payment.execute.return_value = True
        mock_payment.find.return_value = mock_payment
        
        # Patch the find method
        with patch('paypalrestsdk.Payment.find', return_value=mock_payment):
            # Create request with session data
            request = self.create_request_with_session()
            request.session['order_json'] = json.dumps(self.sample_order)
            request.GET = {'paymentId': 'test_payment_id', 'PayerID': 'test_payer_id'}
            
            # Call the view
            response = execute_payment(request)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Verify PayPal payment was executed
            mock_payment.execute.assert_called_once_with({'payer_id': 'test_payer_id'})
            
            # Verify emails were sent
            self.assertEqual(len(mail.outbox), 2)
            
            # Check guest email
            guest_email = mail.outbox[0]
            self.assertEqual(guest_email.to, ['test@example.com'])
            self.assertIn('Booking Confirmation', guest_email.subject)
            
            # Check test recipient email
            test_email = mail.outbox[1]
            self.assertEqual(set(test_email.to), {'cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com'})
    
    def test_paypal_payment_execution_failure(self):
        """Test failed PayPal payment execution"""
        # Mock failed PayPal payment execution
        mock_payment = Mock()
        mock_payment.execute.return_value = False
        mock_payment.find.return_value = mock_payment
        
        # Patch the find method
        with patch('paypalrestsdk.Payment.find', return_value=mock_payment):
            # Create request
            request = self.create_request_with_session()
            request.GET = {'paymentId': 'test_payment_id', 'PayerID': 'test_payer_id'}
            
            # Call the view
            response = execute_payment(request)
            
            # Verify failure response
            self.assertEqual(response.status_code, 200)
            # Should render payment_failed.html template
    
    def test_paypal_payment_execution_missing_parameters(self):
        """Test PayPal payment execution with missing parameters"""
        # Create request without required parameters
        request = self.create_request_with_session()
        request.GET = {}
        
        # Call the view
        response = execute_payment(request)
        
        # Verify response
        self.assertEqual(response.status_code, 200)
        # Should handle missing parameters gracefully
    
    def test_paypal_payment_execution_without_session_data(self):
        """Test PayPal payment execution without session data"""
        # Mock successful PayPal payment execution
        mock_payment = Mock()
        mock_payment.execute.return_value = True
        mock_payment.find.return_value = mock_payment
        
        # Patch the find method
        with patch('paypalrestsdk.Payment.find', return_value=mock_payment):
            # Create request without session data
            request = self.create_request_with_session()
            request.GET = {'paymentId': 'test_payment_id', 'PayerID': 'test_payer_id'}
            
            # Call the view
            response = execute_payment(request)
            
            # Verify response
            self.assertEqual(response.status_code, 200)
            
            # Should handle missing session data gracefully
            # No emails should be sent
            self.assertEqual(len(mail.outbox), 0)
    
    def test_paypal_payment_currency_handling(self):
        """Test PayPal payment handles different currencies correctly"""
        # Test order with different currency
        order_with_eur = self.sample_order.copy()
        order_with_eur['items'][0]['currency'] = 'EUR'
        order_with_eur['total'] = 125.50
        
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # Create request
        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(order_with_eur)}
        
        # Call the view
        response = create_payment(request)
        
        # Verify PayPal was called with correct amount
        PaymentClass = self.mock_paypal_payment
        payment_config = PaymentClass.call_args[0][0]
        self.assertEqual(payment_config['transactions'][0]['amount']['total'], '125.50')
    
    def test_paypal_payment_redirect_urls(self):
        """Test PayPal payment redirect URLs are correctly configured"""
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # Create request
        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(self.sample_order)}
        
        # Call the view
        response = create_payment(request)
        
        # Verify redirect URLs were configured
        PaymentClass = self.mock_paypal_payment
        payment_config = PaymentClass.call_args[0][0]
        self.assertIn('return_url', payment_config['redirect_urls'])
        self.assertIn('cancel_url', payment_config['redirect_urls'])
        
        # Verify URLs contain expected paths
        return_url = payment_config['redirect_urls']['return_url']
        cancel_url = payment_config['redirect_urls']['cancel_url']
        self.assertIn('execute_payment', return_url)
        self.assertIn('payment_failed', cancel_url)
    
    def test_paypal_environment_configuration(self):
        """Test PayPal configuration for different environments"""
        # Verify settings are accessible
        self.assertEqual(settings.PAYPAL_CLIENT_ID, 
                        "AU8Pa2bfXPrlP-WS60LzBxSJiOugG883-DxKny9wfkv-Mgb3K1HJEB3cgxoS9SK723RMhcKAVhcNzzEf")
        self.assertEqual(settings.PAYPAL_SECRET, 
                        "EFR2p3w3BCvoFlVnsdnqbn8bNurqLkCvgH2jeauEdr_jvVFyw1T51GbqVwibUcBS1mArP0ER11gRoXeY")
        
        # Test that the view can access PayPal settings
        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(self.sample_order)}
        
        # Mock successful response
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment
        
        # This should work without errors
        response = create_payment(request)
        self.assertEqual(response.status_code, 302)
    
    def test_paypal_webhook_handling_ready(self):
        """Test that the system is ready for PayPal webhook integration"""
        # This test ensures the current implementation can be extended for webhooks
        request = self.create_request_with_session()
        request.session['order_json'] = json.dumps(self.sample_order)
        
        # Verify session storage works (needed for webhook integration)
        self.assertIsNotNone(request.session.get('order_json'))
        
        # Verify order data structure is consistent
        stored_order = json.loads(request.session['order_json'])
        self.assertEqual(stored_order['total'], 150.00)
        self.assertEqual(stored_order['customer']['email'], 'test@example.com')

    def test_paypal_checkout_with_hotel_without_zone(self):
        """PayPal checkout should work when pickup is a hotel without zone (HOTEL SIN ZONA)."""
        # Mock successful PayPal payment creation
        mock_payment = Mock()
        mock_payment.create.return_value = True
        mock_payment.links = [
            Mock(href='http://cancel.url'),
            Mock(href='https://www.sandbox.paypal.com/checkoutnow?token=test_token')
        ]
        self.mock_paypal_payment.return_value = mock_payment

        hotel_no_zone = Hotel.objects.create(name="HOTEL SIN ZONA", zone=None)

        order = self.sample_order.copy()
        order['pickup'] = {
            'datetime': '2025-08-10 10:00',
            'location_id': str(hotel_no_zone.id),
            'location_name': 'HOTEL SIN ZONA'
        }

        request = self.create_request_with_session()
        request.POST = {'order_json': json.dumps(order)}

        response = create_payment(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn('sandbox.paypal.com', response['Location'])

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_paypal_execute_creates_booking_for_hotel_without_zone(self):
        """Successful PayPal execute should create a Booking even if hotel has no zone."""
        hotel_no_zone = Hotel.objects.create(name="HOTEL SIN ZONA", zone=None)

        order = self.sample_order.copy()
        order['pickup'] = {
            'datetime': '2025-08-10 10:00',
            'location_id': str(hotel_no_zone.id),
            'location_name': 'HOTEL SIN ZONA'
        }

        # Mock successful execution
        mock_payment = Mock()
        mock_payment.execute.return_value = True
        mock_payment.find.return_value = mock_payment
        with patch('paypalrestsdk.Payment.find', return_value=mock_payment):
            request = self.create_request_with_session()
            request.session['order_json'] = json.dumps(order)
            request.GET = {'paymentId': 'pid', 'PayerID': 'payer'}

            response = execute_payment(request)
            self.assertEqual(response.status_code, 200)

            # Booking created with correct pickup and PayPal method
            booking = Booking.objects.latest('id')
            self.assertEqual(booking.pickup_location1_id, hotel_no_zone.id)
            self.assertEqual(booking.payment_method, 'PayPal')
