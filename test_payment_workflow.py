#!/usr/bin/env python3
"""
Simple Payment Workflow Test
Tests the payment flow without requiring a test database
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from django.test import Client
from django.conf import settings
import json


def test_payment_workflow():
    """Test the complete payment workflow"""
    print("🧪 Testing Payment Workflow")
    print("=" * 50)
    
    client = Client()
    results = {}
    
    # Test 1: Landing page loads
    print("1. Testing landing page...")
    try:
        response = client.get('/')
        results['landing_page'] = response.status_code == 200
        print(f"   Status: {response.status_code} {'✅' if results['landing_page'] else '❌'}")
    except Exception as e:
        results['landing_page'] = False
        print(f"   Error: {e} ❌")
    
    # Test 2: Search results with date
    print("2. Testing search results with date...")
    try:
        response = client.get('/search-results/', {
            'pickup_location': '1',
            'car_type': 'VAN',
            'trip_type': 'oneway',
            'people': '2',
            'pickup_datetime': '2025-01-15T10:00'
        })
        results['search_results'] = response.status_code == 200
        print(f"   Status: {response.status_code} {'✅' if results['search_results'] else '❌'}")
    except Exception as e:
        results['search_results'] = False
        print(f"   Error: {e} ❌")
    
    # Test 3: Checkout page
    print("3. Testing checkout page...")
    try:
        response = client.get('/checkout/')
        results['checkout_page'] = response.status_code == 200
        print(f"   Status: {response.status_code} {'✅' if results['checkout_page'] else '❌'}")
    except Exception as e:
        results['checkout_page'] = False
        print(f"   Error: {e} ❌")
    
    # Test 4: Stripe configuration
    print("4. Testing Stripe configuration...")
    try:
        results['stripe_config'] = bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLIC_KEY)
        print(f"   Keys configured: {'✅' if results['stripe_config'] else '❌'}")
        print(f"   Public Key: {settings.STRIPE_PUBLIC_KEY[:20]}...")
        print(f"   Secret Key: {settings.STRIPE_SECRET_KEY[:20]}...")
    except Exception as e:
        results['stripe_config'] = False
        print(f"   Error: {e} ❌")
    
    # Test 5: Payment session creation
    print("5. Testing payment session creation...")
    try:
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
        results['payment_session'] = response.status_code == 302
        print(f"   Status: {response.status_code} {'✅' if results['payment_session'] else '❌'}")
        
        if response.status_code == 302:
            print(f"   Redirect URL: {response.url}")
        elif response.status_code == 500:
            print(f"   Error: {response.content.decode()}")
            
    except Exception as e:
        results['payment_session'] = False
        print(f"   Error: {e} ❌")
    
    # Test 6: Payment success page
    print("6. Testing payment success page...")
    try:
        response = client.get('/payment_success/')
        results['payment_success'] = response.status_code == 200
        print(f"   Status: {response.status_code} {'✅' if results['payment_success'] else '❌'}")
    except Exception as e:
        results['payment_success'] = False
        print(f"   Error: {e} ❌")
    
    # Test 7: Payment failed page
    print("7. Testing payment failed page...")
    try:
        response = client.get('/payment_failed/')
        results['payment_failed'] = response.status_code == 200
        print(f"   Status: {response.status_code} {'✅' if results['payment_failed'] else '❌'}")
    except Exception as e:
        results['payment_failed'] = False
        print(f"   Error: {e} ❌")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Payment workflow is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return False


def test_date_functionality():
    """Test date functionality specifically"""
    print("\n📅 Testing Date Functionality")
    print("=" * 50)
    
    client = Client()
    test_dates = [
        "2025-01-15T10:00",
        "2025-06-15T14:30", 
        "2025-12-25T08:00",
        "2025-02-29T12:00"  # Leap year
    ]
    
    results = {}
    
    for i, test_date in enumerate(test_dates, 1):
        print(f"{i}. Testing date: {test_date}")
        try:
            response = client.get('/search-results/', {
                'pickup_location': '1',
                'car_type': 'VAN',
                'trip_type': 'oneway',
                'people': '2',
                'pickup_datetime': test_date
            })
            results[test_date] = response.status_code == 200
            print(f"   Status: {response.status_code} {'✅' if results[test_date] else '❌'}")
        except Exception as e:
            results[test_date] = False
            print(f"   Error: {e} ❌")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nDate functionality: {passed}/{total} tests passed")
    
    return passed == total


def main():
    """Main test function"""
    print("🎯 Speedy Transfers - Payment Workflow Test")
    print("=" * 60)
    
    # Test payment workflow
    workflow_ok = test_payment_workflow()
    
    # Test date functionality
    date_ok = test_date_functionality()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏁 Final Results:")
    print(f"   Payment Workflow: {'✅ WORKING' if workflow_ok else '❌ ISSUES'}")
    print(f"   Date Functionality: {'✅ WORKING' if date_ok else '❌ ISSUES'}")
    
    if workflow_ok and date_ok:
        print("\n🎉 SUCCESS! Your payment system is ready for testing!")
        print("   You can now:")
        print("   1. Go to http://localhost:8000")
        print("   2. Search for transfers with dates")
        print("   3. Complete the checkout process")
        print("   4. Test the 'Pay with Card (Stripe Test)' button")
    else:
        print("\n⚠️  Some issues detected. Please review the test results above.")
    
    return workflow_ok and date_ok


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
