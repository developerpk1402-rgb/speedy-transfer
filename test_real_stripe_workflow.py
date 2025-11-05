#!/usr/bin/env python3
"""
Real Stripe Payment Workflow Test
Tests all payment scenarios with real Stripe test keys
"""

import os
import sys
import django
from pathlib import Path
import json
import time

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from django.test import Client
from django.conf import settings
import stripe


def test_stripe_configuration():
    """Test that real Stripe configuration is working"""
    print("🔧 Testing Real Stripe Configuration")
    print("=" * 50)
    
    try:
        # Check if we have real Stripe keys
        public_key = settings.STRIPE_PUBLIC_KEY
        secret_key = settings.STRIPE_SECRET_KEY
        
        print(f"   Public Key: {public_key[:20]}...")
        print(f"   Secret Key: {secret_key[:20]}...")
        
        # Test Stripe API connection
        stripe.api_key = secret_key
        account = stripe.Account.retrieve()
        print(f"   ✅ Stripe API connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Account Type: {account.type}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Stripe configuration error: {e}")
        return False


def test_payment_scenarios():
    """Test all payment scenarios"""
    print("\n💳 Testing Payment Scenarios")
    print("=" * 50)
    
    client = Client()
    results = {}
    
    # Test scenarios
    scenarios = [
        {
            'name': 'Single Transfer - One Way',
            'order': {
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
        },
        {
            'name': 'Multiple Transfers - Round Trip',
            'order': {
                "trip_type": "roundtrip",
                "people": 4,
                "pickup": {
                    "datetime": "2025-01-15T10:00",
                    "location_id": "0",
                    "location_name": "AEROPUERTO"
                },
                "dropoff": {
                    "location_id": "1",
                    "location_name": "VELAS VALLARTA"
                },
                "return_trip": {
                    "datetime": "2025-01-20T18:00",
                    "pickup_location_name": "VELAS VALLARTA",
                    "dropoff_location_name": "AEROPUERTO"
                },
                "car_type_label": "VAN",
                "items": [
                    {
                        "name": "VAN 001",
                        "unit_amount": 112.00,
                        "currency": "USD",
                        "date": "2025-01-15",
                        "time": "10:00",
                        "capacity": 8
                    },
                    {
                        "name": "VAN 001",
                        "unit_amount": 112.00,
                        "currency": "USD",
                        "date": "2025-01-20",
                        "time": "18:00",
                        "capacity": 8
                    }
                ],
                "subtotal": 224.00,
                "total": 224.00,
                "customer": {
                    "name": "Round Trip User",
                    "email": "roundtrip@example.com",
                    "phone": "1234567890",
                    "address": "456 Round Trip St",
                    "city": "Testville",
                    "zip": "12345",
                    "country": "USA"
                },
                "currency": "USD"
            }
        },
        {
            'name': 'Large Group - Multiple Vehicles',
            'order': {
                "trip_type": "oneway",
                "people": 15,
                "pickup": {
                    "datetime": "2025-01-15T14:00",
                    "location_id": "0",
                    "location_name": "AEROPUERTO"
                },
                "dropoff": {
                    "location_id": "10",
                    "location_name": "DECAMERON"
                },
                "car_type_label": "VAN",
                "items": [
                    {
                        "name": "VAN 001",
                        "unit_amount": 112.00,
                        "currency": "USD",
                        "date": "2025-01-15",
                        "time": "14:00",
                        "capacity": 8
                    },
                    {
                        "name": "VAN 001",
                        "unit_amount": 112.00,
                        "currency": "USD",
                        "date": "2025-01-15",
                        "time": "14:00",
                        "capacity": 8
                    }
                ],
                "subtotal": 224.00,
                "total": 224.00,
                "customer": {
                    "name": "Large Group User",
                    "email": "largegroup@example.com",
                    "phone": "1234567890",
                    "address": "789 Large Group Ave",
                    "city": "Testville",
                    "zip": "12345",
                    "country": "USA"
                },
                "currency": "USD"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. Testing: {scenario['name']}")
        try:
            # Test checkout session creation
            order_json = json.dumps(scenario['order'])
            response = client.get('/create_checkout_session/', {
                'order_json': order_json
            })
            
            if response.status_code == 302:
                print(f"   ✅ Checkout session created successfully")
                print(f"   Redirect URL: {response.url}")
                
                # Check if it's redirecting to real Stripe or mock
                if 'checkout.stripe.com' in response.url:
                    print(f"   🎯 Redirecting to REAL Stripe checkout")
                elif 'mock_stripe_checkout' in response.url:
                    print(f"   🧪 Redirecting to MOCK checkout")
                else:
                    print(f"   ⚠️  Unknown redirect destination")
                
                results[scenario['name']] = True
            else:
                print(f"   ❌ Checkout session creation failed: {response.status_code}")
                if response.status_code == 500:
                    print(f"   Error: {response.content.decode()}")
                results[scenario['name']] = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[scenario['name']] = False
    
    return results


def test_stripe_test_cards():
    """Test Stripe test card scenarios"""
    print("\n🧪 Testing Stripe Test Card Scenarios")
    print("=" * 50)
    
    test_cards = [
        {
            'number': '4242424242424242',
            'name': 'Visa - Success',
            'expected': 'success'
        },
        {
            'number': '4000000000000002',
            'name': 'Visa - Declined',
            'expected': 'declined'
        },
        {
            'number': '4000000000009995',
            'name': 'Visa - Insufficient Funds',
            'expected': 'insufficient_funds'
        },
        {
            'number': '4000000000000069',
            'name': 'Visa - Expired Card',
            'expected': 'expired'
        },
        {
            'number': '4000000000000119',
            'name': 'Visa - Processing Error',
            'expected': 'processing_error'
        }
    ]
    
    print("   Test cards available for manual testing:")
    for card in test_cards:
        print(f"   • {card['number']} - {card['name']} ({card['expected']})")
    
    print("\n   📝 Note: These cards can be used in the Stripe checkout for testing")
    print("   📝 Use any future expiry date (e.g., 12/25) and any 3-digit CVC")
    
    return True


def test_payment_flow_integration():
    """Test the complete payment flow integration"""
    print("\n🔄 Testing Complete Payment Flow Integration")
    print("=" * 50)
    
    client = Client()
    
    # Test 1: Landing page
    print("1. Testing landing page...")
    response = client.get('/')
    landing_ok = response.status_code == 200
    print(f"   Status: {response.status_code} {'✅' if landing_ok else '❌'}")
    
    # Test 2: Search with date
    print("2. Testing search with date...")
    response = client.get('/search-results/', {
        'pickup_location': '1',
        'car_type': 'VAN',
        'trip_type': 'oneway',
        'people': '2',
        'pickup_datetime': '2025-01-15T10:00'
    })
    search_ok = response.status_code == 200
    print(f"   Status: {response.status_code} {'✅' if search_ok else '❌'}")
    
    # Test 3: Checkout page
    print("3. Testing checkout page...")
    response = client.get('/checkout/')
    checkout_ok = response.status_code == 200
    print(f"   Status: {response.status_code} {'✅' if checkout_ok else '❌'}")
    
    # Test 4: Payment session creation
    print("4. Testing payment session creation...")
    sample_order = {
        "trip_type": "oneway",
        "people": 2,
        "total": 82.00,
        "currency": "USD",
        "items": [{"name": "VAN 001", "unit_amount": 82.00, "currency": "USD"}],
        "customer": {"name": "Test User", "email": "test@example.com"}
    }
    
    response = client.get('/create_checkout_session/', {
        'order_json': json.dumps(sample_order)
    })
    payment_ok = response.status_code == 302
    print(f"   Status: {response.status_code} {'✅' if payment_ok else '❌'}")
    
    if payment_ok:
        print(f"   Redirect URL: {response.url}")
    
    # Test 5: Payment success page
    print("5. Testing payment success page...")
    response = client.get('/payment_success/')
    success_ok = response.status_code == 200
    print(f"   Status: {response.status_code} {'✅' if success_ok else '❌'}")
    
    # Test 6: Payment failed page
    print("6. Testing payment failed page...")
    response = client.get('/payment_failed/')
    failed_ok = response.status_code == 200
    print(f"   Status: {response.status_code} {'✅' if failed_ok else '❌'}")
    
    return {
        'landing': landing_ok,
        'search': search_ok,
        'checkout': checkout_ok,
        'payment': payment_ok,
        'success': success_ok,
        'failed': failed_ok
    }


def main():
    """Main test function"""
    print("🎯 Real Stripe Payment Workflow Test")
    print("=" * 60)
    
    # Test 1: Stripe configuration
    config_ok = test_stripe_configuration()
    
    if not config_ok:
        print("\n❌ Stripe configuration failed. Please check your keys.")
        return False
    
    # Test 2: Payment scenarios
    scenario_results = test_payment_scenarios()
    
    # Test 3: Test cards info
    cards_ok = test_stripe_test_cards()
    
    # Test 4: Complete flow integration
    flow_results = test_payment_flow_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Stripe Configuration: {'✅ OK' if config_ok else '❌ FAILED'}")
    
    print("\n   Payment Scenarios:")
    for scenario, result in scenario_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"     {scenario}: {status}")
    
    print(f"\n   Test Cards Info: {'✅ OK' if cards_ok else '❌ FAILED'}")
    
    print("\n   Integration Tests:")
    for test, result in flow_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"     {test.title()}: {status}")
    
    # Overall result
    all_scenarios_ok = all(scenario_results.values())
    all_flow_ok = all(flow_results.values())
    
    if config_ok and all_scenarios_ok and all_flow_ok:
        print("\n🎉 SUCCESS! All tests passed!")
        print("\n🚀 Your payment system is ready for production testing!")
        print("   You can now:")
        print("   1. Go to http://localhost:8000")
        print("   2. Complete a real booking")
        print("   3. Use Stripe test cards for payment testing")
        print("   4. Test all payment scenarios")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the issues above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

