#!/usr/bin/env python3
"""
Test 10 Complete Stripe Payment Workflows
Tests the complete payment flow from checkout to booking creation
"""

import os
import sys
import django
from pathlib import Path
import json
import time
import random
from datetime import datetime, timedelta

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from django.test import Client
from django.conf import settings
from speedy_app.core.models import Booking


def generate_test_order(test_number):
    """Generate a unique test order for each test"""
    # Random trip data
    trip_types = ['oneway', 'roundtrip']
    car_types = ['VAN', 'SEDAN', 'SUV']
    locations = [
        {'id': '0', 'name': 'AEROPUERTO'},
        {'id': '1', 'name': 'VELAS VALLARTA'},
        {'id': '2', 'name': 'HOTEL ZONE'},
        {'id': '108', 'name': 'DECAMERON'}
    ]
    
    trip_type = random.choice(trip_types)
    car_type = random.choice(car_types)
    pickup_location = random.choice(locations)
    dropoff_location = random.choice([loc for loc in locations if loc['id'] != pickup_location['id']])
    people = random.randint(1, 8)
    
    # Generate future datetime
    future_date = datetime.now() + timedelta(days=random.randint(1, 30))
    pickup_datetime = future_date.strftime('%Y-%m-%dT%H:%M')
    
    # Generate customer data
    customers = [
        {'name': 'John Smith', 'email': 'john.smith@example.com', 'phone': '555-0101'},
        {'name': 'Maria Garcia', 'email': 'maria.garcia@example.com', 'phone': '555-0102'},
        {'name': 'David Johnson', 'email': 'david.johnson@example.com', 'phone': '555-0103'},
        {'name': 'Sarah Wilson', 'email': 'sarah.wilson@example.com', 'phone': '555-0104'},
        {'name': 'Carlos Rodriguez', 'email': 'carlos.rodriguez@example.com', 'phone': '555-0105'},
        {'name': 'Lisa Brown', 'email': 'lisa.brown@example.com', 'phone': '555-0106'},
        {'name': 'Michael Davis', 'email': 'michael.davis@example.com', 'phone': '555-0107'},
        {'name': 'Ana Martinez', 'email': 'ana.martinez@example.com', 'phone': '555-0108'},
        {'name': 'Robert Taylor', 'email': 'robert.taylor@example.com', 'phone': '555-0109'},
        {'name': 'Elena Lopez', 'email': 'elena.lopez@example.com', 'phone': '555-0110'}
    ]
    
    customer = customers[test_number % len(customers)]
    
    # Calculate price based on car type and distance
    base_prices = {'VAN': 82, 'SEDAN': 65, 'SUV': 95}
    base_price = base_prices.get(car_type, 82)
    total = base_price * (1 if people <= 4 else 2)  # Multiple vehicles for large groups
    
    order = {
        "trip_type": trip_type,
        "people": people,
        "pickup": {
            "datetime": pickup_datetime,
            "location_id": pickup_location['id'],
            "location_name": pickup_location['name']
        },
        "dropoff": {
            "location_id": dropoff_location['id'],
            "location_name": dropoff_location['name']
        },
        "car_type_value": car_type,
        "car_type_label": car_type,
        "items": [
            {
                "rate_id": str(random.randint(1, 50)),
                "car_id": "1",
                "name": f"{car_type} 001",
                "unit_amount": total,
                "currency": "USD",
                "date": future_date.strftime('%Y-%m-%d'),
                "time": future_date.strftime('%H:%M'),
                "capacity": 8 if car_type == 'VAN' else 4,
                "image_url": f"/assets/images/cars/{car_type.lower()}_dark.jpg"
            }
        ],
        "subtotal": total,
        "total": total,
        "customer": {
            "name": customer['name'],
            "email": customer['email'],
            "phone": customer['phone'],
            "address": f"{random.randint(100, 999)} Test Street",
            "city": "Puerto Vallarta",
            "zip": f"{random.randint(48000, 48999)}",
            "country": "Mexico",
            "company": ""
        },
        "currency": "USD"
    }
    
    # Add return trip for roundtrip
    if trip_type == 'roundtrip':
        return_datetime = future_date + timedelta(days=random.randint(1, 7))
        order["return_trip"] = {
            "datetime": return_datetime.strftime('%Y-%m-%dT%H:%M'),
            "location_id": dropoff_location['id'],
            "location_name": dropoff_location['name']
        }
        order["total"] = total * 2
        order["subtotal"] = total * 2
    
    return order


def test_single_payment_workflow(test_number):
    """Test a single complete payment workflow"""
    print(f"\n🔄 Test #{test_number + 1}: Complete Payment Workflow")
    print("=" * 60)
    
    client = Client()
    
    # Generate test order
    test_order = generate_test_order(test_number)
    
    print(f"📋 Order Details:")
    print(f"   Customer: {test_order['customer']['name']} ({test_order['customer']['email']})")
    print(f"   Trip: {test_order['trip_type'].upper()} - {test_order['people']} people")
    print(f"   Route: {test_order['pickup']['location_name']} → {test_order['dropoff']['location_name']}")
    print(f"   Vehicle: {test_order['car_type_label']} - ${test_order['total']} {test_order['currency']}")
    print(f"   Date: {test_order['pickup']['datetime']}")
    
    try:
        # Step 1: Create checkout session
        print(f"\n1️⃣ Creating Stripe checkout session...")
        response = client.get('/create_checkout_session/', {
            'order_json': json.dumps(test_order)
        })
        
        if response.status_code == 302:
            print(f"   ✅ Checkout session created successfully")
            print(f"   Redirect URL: {response.url}")
            
            # Check if it's a real Stripe URL or mock
            if 'checkout.stripe.com' in response.url:
                print(f"   🎯 Real Stripe checkout detected")
                stripe_session_id = response.url.split('/')[-1]
            else:
                print(f"   🧪 Mock Stripe checkout detected")
                stripe_session_id = f"cs_test_{test_number}_{int(time.time())}"
            
            # Step 2: Simulate payment success
            print(f"\n2️⃣ Simulating payment success...")
            success_response = client.get('/payment_success/', {
                'session_id': stripe_session_id
            })
            
            if success_response.status_code == 200:
                print(f"   ✅ Payment success page loaded")
                
                # Step 3: Check if booking was created
                print(f"\n3️⃣ Verifying booking creation...")
                
                # Wait a moment for booking creation
                time.sleep(1)
                
                # Check for recent bookings
                recent_bookings = Booking.objects.filter(
                    customer_name=test_order['customer']['name'],
                    customer_email=test_order['customer']['email']
                ).order_by('-id')
                
                if recent_bookings.exists():
                    booking = recent_bookings.first()
                    print(f"   ✅ Booking created successfully!")
                    print(f"   Booking ID: {booking.id}")
                    print(f"   Customer: {booking.customer_name}")
                    print(f"   Total: ${booking.total_amount} {booking.currency}")
                    print(f"   Trip Type: {'One Way' if booking.one_way else 'Round Trip'}")
                    print(f"   Pickup: {booking.pickup_date_time}")
                    
                    return {
                        'success': True,
                        'booking_id': booking.id,
                        'customer_name': booking.customer_name,
                        'total': float(booking.total_amount),
                        'currency': booking.currency,
                        'trip_type': 'oneway' if booking.one_way else 'roundtrip'
                    }
                else:
                    print(f"   ❌ No booking found in database")
                    return {'success': False, 'error': 'Booking not created'}
            else:
                print(f"   ❌ Payment success page failed: {success_response.status_code}")
                return {'success': False, 'error': f'Payment success page failed: {success_response.status_code}'}
        else:
            print(f"   ❌ Checkout session creation failed: {response.status_code}")
            if hasattr(response, 'content'):
                print(f"   Response: {response.content.decode()[:200]}...")
            return {'success': False, 'error': f'Checkout session failed: {response.status_code}'}
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def main():
    """Run 10 complete payment workflow tests"""
    print("🎯 STRIPE PAYMENT WORKFLOW TEST SUITE")
    print("=" * 80)
    print(f"Testing 10 complete payment workflows with real Stripe integration")
    print(f"Server: {settings.ALLOWED_HOSTS}")
    print(f"Stripe Keys: {'✅ Configured' if settings.STRIPE_SECRET_KEY else '❌ Missing'}")
    print("=" * 80)
    
    results = []
    successful_tests = 0
    total_revenue = 0
    
    for i in range(10):
        result = test_single_payment_workflow(i)
        results.append(result)
        
        if result['success']:
            successful_tests += 1
            total_revenue += result.get('total', 0)
        
        # Small delay between tests
        if i < 9:  # Don't delay after the last test
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"Total Tests: 10")
    print(f"Successful: {successful_tests} ✅")
    print(f"Failed: {10 - successful_tests} ❌")
    print(f"Success Rate: {(successful_tests/10)*100:.1f}%")
    print(f"Total Revenue Tested: ${total_revenue:.2f}")
    
    print(f"\n📋 Individual Test Results:")
    for i, result in enumerate(results, 1):
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        if result['success']:
            print(f"   Test {i:2d}: {status} - {result['customer_name']} - ${result['total']} {result['currency']} - Booking ID: {result['booking_id']}")
        else:
            print(f"   Test {i:2d}: {status} - Error: {result.get('error', 'Unknown error')}")
    
    # Check database for all bookings
    print(f"\n🗄️ Database Verification:")
    total_bookings = Booking.objects.count()
    recent_bookings = Booking.objects.order_by('-id')[:10]
    print(f"   Total bookings in database: {total_bookings}")
    print(f"   Recent 10 bookings:")
    for booking in recent_bookings:
        print(f"     ID: {booking.id} - {booking.customer_name} - ${booking.total_amount} - {booking.pickup_date_time}")
    
    if successful_tests == 10:
        print(f"\n🎉 ALL TESTS PASSED! 🎉")
        print(f"   ✅ Payment system is fully functional")
        print(f"   ✅ Booking creation working perfectly")
        print(f"   ✅ Database integration working")
        print(f"   ✅ Ready for production use!")
        return True
    elif successful_tests >= 8:
        print(f"\n⚠️ MOSTLY SUCCESSFUL ({successful_tests}/10)")
        print(f"   System is working but has some issues to investigate")
        return False
    else:
        print(f"\n❌ MULTIPLE FAILURES ({successful_tests}/10)")
        print(f"   System needs significant fixes before production")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

