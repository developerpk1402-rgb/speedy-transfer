import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from .models import Zone, Hotel, Car, CarType, Rate, Reservation, Payment, Booking


class PaymentSuccessDisplayTestCase(TestCase):
    """Tests for payment success page display functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.factory = RequestFactory()
        
        # Create test data
        self.zone = Zone.objects.create(name="Puerto Vallarta")
        self.hotel = Hotel.objects.create(
            name="Marriott Puerto Vallarta Resort & Spa", 
            zone=self.zone
        )
        self.airport = Hotel.objects.create(
            name="Lic. Gustavo Díaz Ordaz International Airport", 
            zone=self.zone
        )
        self.car_type = CarType.objects.create(
            code="VAN",
            name="Van",
            max_capacity=8
        )
        self.car = Car.objects.create(
            name="Luxury Van",
            car_type=self.car_type,
            max=8
        )
        
        # Sample order data for testing
        self.sample_order = {
            'trip_type': 'roundtrip',
            'people': 4,
            'pickup': {
                'datetime': '2025-08-15 08:00',
                'location_id': str(self.hotel.id),
                'location_name': 'Marriott Puerto Vallarta Resort & Spa'
            },
            'dropoff': {
                'datetime': '2025-08-15 09:00',
                'location_id': str(self.airport.id),
                'location_name': 'Lic. Gustavo Díaz Ordaz International Airport'
            },
            'return_trip': {
                'datetime': '2025-08-20 16:00',
                'pickup_location_id': str(self.airport.id),
                'pickup_location_name': 'Lic. Gustavo Díaz Ordaz International Airport',
                'dropoff_location_id': str(self.hotel.id),
                'dropoff_location_name': 'Marriott Puerto Vallarta Resort & Spa'
            },
            'car_type_label': 'VAN',
            'items': [
                {
                    'name': 'Luxury Van',
                    'unit_amount': 180.00,
                    'currency': 'USD',
                    'date': '2025-08-15',
                    'time': '08:00',
                    'capacity': 8,
                    'car_id': str(self.car.id)
                }
            ],
            'subtotal': 180.00,
            'total': 180.00,
            'customer': {
                'name': 'John Smith',
                'email': 'john.smith@example.com',
                'phone': '+1-555-123-4567',
                'address': '123 Main Street',
                'city': 'New York',
                'zip': '10001',
            }
        }
    
    def create_request_with_session(self, method='GET', data=None):
        """Helper to create a request with session middleware"""
        request = self.factory.request(method=method, data=data)
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        
        return request
    
    def test_payment_success_page_loads_with_order_data(self):
        """Test that payment success page loads and displays order information"""
        # Set up session with order data
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        # Make request to payment success page
        response = self.client.get(reverse('core:payment_success'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speedy_app/payment_success.html')
        
        # Check that order information is displayed
        content = response.content.decode()
        self.assertIn('John Smith', content)
        self.assertIn('Marriott Puerto Vallarta Resort & Spa', content)
        self.assertIn('Lic. Gustavo Díaz Ordaz International Airport', content)
        self.assertIn('August 15, 2025', content)
        self.assertIn('August 20, 2025', content)
        self.assertIn('$180.00', content)
        self.assertIn('4 passengers', content)
        self.assertIn('Round Trip', content)
    
    def test_payment_success_page_handles_missing_order_data(self):
        """Test that payment success page handles missing order data gracefully"""
        # Make request without order data in session
        response = self.client.get(reverse('core:payment_success'))
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'speedy_app/payment_success.html')
        
        # Should still display success message
        content = response.content.decode()
        self.assertIn('Payment Successful', content)
        self.assertIn('Thank you for your purchase', content)
    
    def test_payment_success_page_displays_correct_trip_type(self):
        """Test that trip type is displayed correctly"""
        # Test one-way trip
        one_way_order = self.sample_order.copy()
        one_way_order['trip_type'] = 'oneway'
        del one_way_order['return_trip']
        
        session = self.client.session
        session['order_json'] = json.dumps(one_way_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        self.assertIn('One Way', content)
        self.assertNotIn('Return Trip', content)
        
        # Test round trip
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        self.assertIn('Round Trip', content)
        self.assertIn('Return Trip', content)
    
    def test_payment_success_page_displays_customer_information(self):
        """Test that customer information is displayed correctly"""
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        
        # Check customer details
        self.assertIn('John Smith', content)
        self.assertIn('john.smith@example.com', content)
        self.assertIn('+1-555-123-4567', content)
        self.assertIn('123 Main Street', content)
        self.assertIn('New York, NY 10001', content)
    
    def test_payment_success_page_displays_vehicle_information(self):
        """Test that vehicle information is displayed correctly"""
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        
        # Check vehicle details
        self.assertIn('Luxury Van', content)
        self.assertIn('8 passengers', content)
        self.assertIn('Van', content)
    
    def test_payment_success_page_formats_dates_correctly(self):
        """Test that dates are formatted correctly"""
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        
        # Check date formatting
        self.assertIn('August 15, 2025', content)
        self.assertIn('August 20, 2025', content)
        self.assertIn('8:00 AM', content)
        self.assertIn('4:00 PM', content)
    
    def test_payment_success_page_displays_pricing_information(self):
        """Test that pricing information is displayed correctly"""
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        response = self.client.get(reverse('core:payment_success'))
        content = response.content.decode()
        
        # Check pricing details
        self.assertIn('$180.00', content)
        self.assertIn('Subtotal', content)
        self.assertIn('Total', content)
    
    def test_payment_success_page_clears_session_after_display(self):
        """Test that order data is cleared from session after display"""
        session = self.client.session
        session['order_json'] = json.dumps(self.sample_order)
        session.save()
        
        # Verify order data is in session
        self.assertIsNotNone(session.get('order_json'))
        
        # Make request to payment success page
        response = self.client.get(reverse('core:payment_success'))
        
        # Check that order data is cleared
        session = self.client.session
        self.assertIsNone(session.get('order_json'))












