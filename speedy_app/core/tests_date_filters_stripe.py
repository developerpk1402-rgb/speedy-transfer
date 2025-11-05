"""
Comprehensive tests for all possible date filter scenarios through Stripe payment system.
This test suite covers various date combinations and edge cases for transfer bookings.
"""

import json
import stripe
from datetime import datetime, timedelta
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch, Mock
from django.core import mail
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.conf import settings
from .models import Zone, Hotel, Car, CarType, Rate, Booking
from .views import create_checkout_session, payment_success


class DateFiltersStripeTestCase(TestCase):
    """Test all possible date filter scenarios with Stripe payments"""
    
    def setUp(self):
        """Set up test data and mock Stripe"""
        self.factory = RequestFactory()
        
        # Create test data
        self.zone = Zone.objects.create(name="Test Zone")
        self.airport_zone = Zone.objects.create(name="Airport Zone")
        
        self.hotel = Hotel.objects.create(
            name="Test Hotel", 
            zone=self.zone
        )
        self.airport = Hotel.objects.create(
            name="AEROPUERTO",
            zone=self.airport_zone
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
        
        # Create test rates
        self.rate = Rate.objects.create(
            car=self.car,
            zone=self.zone,
            travel_type="ONE_WAY",
            price=100.00
        )
        
        # Mock Stripe configuration
        self.stripe_patcher = patch('stripe.checkout.Session.create')
        self.mock_stripe_create = self.stripe_patcher.start()
        
        # Mock successful Stripe response
        mock_session = Mock()
        mock_session.url = 'https://checkout.stripe.com/test_session'
        self.mock_stripe_create.return_value = mock_session
        
        # Mock Stripe session retrieve for payment success
        self.stripe_retrieve_patcher = patch('stripe.checkout.Session.retrieve')
        self.mock_stripe_retrieve = self.stripe_retrieve_patcher.start()
        
        mock_retrieved_session = Mock()
        mock_retrieved_session.payment_status = 'paid'
        mock_retrieved_session.customer_email = 'test@example.com'
        self.mock_stripe_retrieve.return_value = mock_retrieved_session
        
        # Base order template
        self.base_order = {
            'trip_type': 'oneway',
            'people': 2,
            'pickup': {
                'location_id': str(self.airport.id),
                'location_name': 'AEROPUERTO'
            },
            'dropoff': {
                'location_id': str(self.hotel.id),
                'location_name': 'Test Hotel'
            },
            'car_type_value': 'VAN',
            'car_type_label': 'VAN',
            'items': [{
                'rate_id': str(self.rate.id),
                'car_id': str(self.car.id),
                'name': 'Test Van',
                'unit_amount': 100,
                'currency': 'USD',
                'capacity': 8,
                'image_url': '/assets/images/cars/van.jpg'
            }],
            'subtotal': 100,
            'total': 100,
            'customer': {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '1234567890',
                'address': '123 Test St',
                'city': 'Test City',
                'zip': '12345',
                'country': 'Mexico',
                'company': ''
            },
            'currency': 'USD'
        }
    
    def tearDown(self):
        """Clean up patches"""
        self.stripe_patcher.stop()
        self.stripe_retrieve_patcher.stop()
    
    def _create_order_with_dates(self, pickup_datetime, return_datetime=None, trip_type='oneway'):
        """Helper method to create order with specific dates"""
        order = self.base_order.copy()
        order['trip_type'] = trip_type
        order['pickup']['datetime'] = pickup_datetime
        
        if return_datetime and trip_type == 'roundtrip':
            order['return_trip'] = {
                'datetime': return_datetime,
                'location_id': str(self.airport.id),
                'location_name': 'AEROPUERTO'
            }
        
        # Update items with dates
        for item in order['items']:
            item['date'] = pickup_datetime.split('T')[0] if 'T' in pickup_datetime else pickup_datetime.split(' ')[0]
            item['time'] = pickup_datetime.split('T')[1] if 'T' in pickup_datetime else pickup_datetime.split(' ')[1]
        
        return order
    
    def _test_stripe_checkout_with_order(self, order_data, test_name):
        """Helper method to test Stripe checkout with specific order data"""
        with self.subTest(test_name=test_name):
            # Create request
            request = self.factory.get('/create_checkout_session/', {
                'order_json': json.dumps(order_data)
            })
            
            # Add session middleware
            middleware = SessionMiddleware(lambda req: None)
            middleware.process_request(request)
            request.session.save()
            
            # Test Stripe checkout
            with override_settings(
                STRIPE_SECRET_KEY='sk_test_valid_key',
                STRIPE_PUBLIC_KEY='pk_test_valid_key'
            ):
                response = create_checkout_session(request)
                
                # Verify response
                self.assertEqual(response.status_code, 302)
                self.assertIn('checkout.stripe.com', response['Location'])
                
                # Verify Stripe was called
                self.mock_stripe_create.assert_called()
                
                # Verify order data in Stripe call
                call_args = self.mock_stripe_create.call_args[1]
                line_items = call_args['line_items']
                
                self.assertGreater(len(line_items), 0)
                self.assertEqual(line_items[0]['price_data']['currency'], 'usd')
                self.assertEqual(line_items[0]['price_data']['unit_amount'], 10000)  # $100.00 in cents
    
    # Test 1: Current Date Scenarios
    def test_current_date_scenarios(self):
        """Test various current date scenarios"""
        now = datetime.now()
        current_date = now.strftime('%Y-%m-%dT%H:%M')
        
        # Test 1.1: Current date, morning time
        morning_time = now.replace(hour=9, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(morning_time)
        self._test_stripe_checkout_with_order(order, "Current date, morning time")
        
        # Test 1.2: Current date, afternoon time
        afternoon_time = now.replace(hour=15, minute=30).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(afternoon_time)
        self._test_stripe_checkout_with_order(order, "Current date, afternoon time")
        
        # Test 1.3: Current date, evening time
        evening_time = now.replace(hour=20, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(evening_time)
        self._test_stripe_checkout_with_order(order, "Current date, evening time")
    
    # Test 2: Future Date Scenarios
    def test_future_date_scenarios(self):
        """Test various future date scenarios"""
        future_date = datetime.now() + timedelta(days=7)
        
        # Test 2.1: One week from now
        one_week = future_date.strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(one_week)
        self._test_stripe_checkout_with_order(order, "One week from now")
        
        # Test 2.2: One month from now
        one_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(one_month)
        self._test_stripe_checkout_with_order(order, "One month from now")
        
        # Test 2.3: Three months from now
        three_months = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(three_months)
        self._test_stripe_checkout_with_order(order, "Three months from now")
    
    # Test 3: Round Trip Date Scenarios
    def test_roundtrip_date_scenarios(self):
        """Test round trip date scenarios"""
        pickup_date = datetime.now() + timedelta(days=7)
        return_date = pickup_date + timedelta(days=7)
        
        # Test 3.1: One week round trip
        pickup_str = pickup_date.strftime('%Y-%m-%dT%H:%M')
        return_str = return_date.strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(pickup_str, return_str, 'roundtrip')
        self._test_stripe_checkout_with_order(order, "One week round trip")
        
        # Test 3.2: Same day round trip
        same_day_return = pickup_date + timedelta(hours=8)
        return_str = same_day_return.strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(pickup_str, return_str, 'roundtrip')
        self._test_stripe_checkout_with_order(order, "Same day round trip")
        
        # Test 3.3: Long round trip (3 months)
        long_return = pickup_date + timedelta(days=90)
        return_str = long_return.strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(pickup_str, return_str, 'roundtrip')
        self._test_stripe_checkout_with_order(order, "Long round trip (3 months)")
    
    # Test 4: Edge Case Date Scenarios
    def test_edge_case_date_scenarios(self):
        """Test edge case date scenarios"""
        
        # Test 4.1: Leap year date (February 29)
        leap_year = datetime(2024, 2, 29, 10, 0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(leap_year)
        self._test_stripe_checkout_with_order(order, "Leap year date (Feb 29)")
        
        # Test 4.2: New Year's Eve
        new_years_eve = datetime(2024, 12, 31, 23, 30).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(new_years_eve)
        self._test_stripe_checkout_with_order(order, "New Year's Eve")
        
        # Test 4.3: New Year's Day
        new_years_day = datetime(2025, 1, 1, 1, 0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(new_years_day)
        self._test_stripe_checkout_with_order(order, "New Year's Day")
        
        # Test 4.4: Daylight Saving Time transition (Spring forward)
        dst_spring = datetime(2024, 3, 10, 2, 30).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(dst_spring)
        self._test_stripe_checkout_with_order(order, "DST Spring forward")
        
        # Test 4.5: Daylight Saving Time transition (Fall back)
        dst_fall = datetime(2024, 11, 3, 1, 30).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(dst_fall)
        self._test_stripe_checkout_with_order(order, "DST Fall back")
    
    # Test 5: Time Zone Scenarios
    def test_timezone_scenarios(self):
        """Test various time zone scenarios"""
        
        # Test 5.1: Early morning (6 AM)
        early_morning = datetime.now().replace(hour=6, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(early_morning)
        self._test_stripe_checkout_with_order(order, "Early morning (6 AM)")
        
        # Test 5.2: Late night (11 PM)
        late_night = datetime.now().replace(hour=23, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(late_night)
        self._test_stripe_checkout_with_order(order, "Late night (11 PM)")
        
        # Test 5.3: Midnight
        midnight = datetime.now().replace(hour=0, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(midnight)
        self._test_stripe_checkout_with_order(order, "Midnight")
        
        # Test 5.4: Noon
        noon = datetime.now().replace(hour=12, minute=0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(noon)
        self._test_stripe_checkout_with_order(order, "Noon")
    
    # Test 6: Weekend and Holiday Scenarios
    def test_weekend_holiday_scenarios(self):
        """Test weekend and holiday scenarios"""
        
        # Test 6.1: Saturday
        saturday = datetime(2024, 9, 14, 10, 0).strftime('%Y-%m-%dT%H:%M')  # Saturday
        order = self._create_order_with_dates(saturday)
        self._test_stripe_checkout_with_order(order, "Saturday booking")
        
        # Test 6.2: Sunday
        sunday = datetime(2024, 9, 15, 14, 0).strftime('%Y-%m-%dT%H:%M')  # Sunday
        order = self._create_order_with_dates(sunday)
        self._test_stripe_checkout_with_order(order, "Sunday booking")
        
        # Test 6.3: Christmas Day
        christmas = datetime(2024, 12, 25, 10, 0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(christmas)
        self._test_stripe_checkout_with_order(order, "Christmas Day")
        
        # Test 6.4: Independence Day (Mexico - September 16)
        independence_day = datetime(2024, 9, 16, 10, 0).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(independence_day)
        self._test_stripe_checkout_with_order(order, "Independence Day (Mexico)")
    
    # Test 7: Date Format Variations
    def test_date_format_variations(self):
        """Test different date format variations"""
        
        # Test 7.1: ISO format with seconds
        iso_with_seconds = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        order = self._create_order_with_dates(iso_with_seconds)
        self._test_stripe_checkout_with_order(order, "ISO format with seconds")
        
        # Test 7.2: Space-separated format
        space_format = datetime.now().strftime('%Y-%m-%d %H:%M')
        order = self._create_order_with_dates(space_format)
        self._test_stripe_checkout_with_order(order, "Space-separated format")
        
        # Test 7.3: Date with Z timezone
        z_timezone = datetime.now().strftime('%Y-%m-%dT%H:%MZ')
        order = self._create_order_with_dates(z_timezone)
        self._test_stripe_checkout_with_order(order, "Date with Z timezone")
    
    # Test 8: Invalid Date Scenarios (Error Handling)
    def test_invalid_date_scenarios(self):
        """Test invalid date scenarios and error handling"""
        
        # Test 8.1: Invalid date format
        invalid_order = self.base_order.copy()
        invalid_order['pickup']['datetime'] = 'invalid-date-format'
        
        request = self.factory.get('/create_checkout_session/', {
            'order_json': json.dumps(invalid_order)
        })
        
        with override_settings(
            STRIPE_SECRET_KEY='sk_test_valid_key',
            STRIPE_PUBLIC_KEY='pk_test_valid_key'
        ):
            response = create_checkout_session(request)
            # Should still work, using current datetime as fallback
            self.assertEqual(response.status_code, 302)
        
        # Test 8.2: Empty date
        empty_date_order = self.base_order.copy()
        empty_date_order['pickup']['datetime'] = ''
        
        request = self.factory.get('/create_checkout_session/', {
            'order_json': json.dumps(empty_date_order)
        })
        
        with override_settings(
            STRIPE_SECRET_KEY='sk_test_valid_key',
            STRIPE_PUBLIC_KEY='pk_test_valid_key'
        ):
            response = create_checkout_session(request)
            # Should still work, using current datetime as fallback
            self.assertEqual(response.status_code, 302)
        
        # Test 8.3: None date
        none_date_order = self.base_order.copy()
        none_date_order['pickup']['datetime'] = None
        
        request = self.factory.get('/create_checkout_session/', {
            'order_json': json.dumps(none_date_order)
        })
        
        with override_settings(
            STRIPE_SECRET_KEY='sk_test_valid_key',
            STRIPE_PUBLIC_KEY='pk_test_valid_key'
        ):
            response = create_checkout_session(request)
            # Should still work, using current datetime as fallback
            self.assertEqual(response.status_code, 302)
    
    # Test 9: Payment Success with Different Dates
    def test_payment_success_date_scenarios(self):
        """Test payment success scenarios with different dates"""
        
        # Test 9.1: Payment success with future date
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(future_date)
        
        # Simulate successful payment with proper session setup
        request = self.factory.get('/payment_success/', {
            'session_id': 'test_session_id'
        })
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.session['order_json'] = json.dumps(order)
        
        with override_settings(
            STRIPE_SECRET_KEY='sk_test_valid_key',
            STRIPE_PUBLIC_KEY='pk_test_valid_key',
            STATIC_URL='/static/'
        ):
            response = payment_success(request)
            self.assertEqual(response.status_code, 200)
        
        # Test 9.2: Payment success with round trip dates
        pickup_date = datetime.now() + timedelta(days=3)
        return_date = pickup_date + timedelta(days=7)
        pickup_str = pickup_date.strftime('%Y-%m-%dT%H:%M')
        return_str = return_date.strftime('%Y-%m-%dT%H:%M')
        order = self._create_order_with_dates(pickup_str, return_str, 'roundtrip')
        
        request = self.factory.get('/payment_success/', {
            'session_id': 'test_session_id'
        })
        
        # Add session middleware
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.session['order_json'] = json.dumps(order)
        
        with override_settings(
            STRIPE_SECRET_KEY='sk_test_valid_key',
            STRIPE_PUBLIC_KEY='pk_test_valid_key',
            STATIC_URL='/static/'
        ):
            response = payment_success(request)
            self.assertEqual(response.status_code, 200)
    
    # Test 10: Performance Test with Multiple Date Scenarios
    def test_performance_multiple_dates(self):
        """Test performance with multiple date scenarios"""
        import time
        
        start_time = time.time()
        
        # Test multiple date scenarios in sequence
        test_dates = [
            datetime.now().strftime('%Y-%m-%dT%H:%M'),
            (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M'),
        ]
        
        for i, date_str in enumerate(test_dates):
            order = self._create_order_with_dates(date_str)
            self._test_stripe_checkout_with_order(order, f"Performance test {i+1}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance should be reasonable (less than 10 seconds for 4 tests)
        self.assertLess(execution_time, 10.0, f"Performance test took too long: {execution_time:.2f} seconds")
