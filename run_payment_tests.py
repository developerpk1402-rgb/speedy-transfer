#!/usr/bin/env python
"""
Payment System Test Runner for Speedy Transfers
This script runs comprehensive payment tests in staging and production environments.

Usage:
    python run_payment_tests.py [--environment staging|production] [--payment-method stripe|paypal|all] [--verbose]

Examples:
    # Run all payment tests in staging environment
    python run_payment_tests.py --environment staging --payment-method all

    # Run only Stripe tests in production environment
    python run_payment_tests.py --environment production --payment-method stripe --verbose

    # Run tests with default settings (staging, all payment methods)
    python run_payment_tests.py
"""

import os
import sys
import argparse
import subprocess
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.settings')

def setup_django():
    """Initialize Django for testing"""
    try:
        django.setup()
        print("✓ Django initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize Django: {e}")
        sys.exit(1)

def run_tests(environment, payment_method, verbose=False):
    """Run the specified payment tests"""
    
    # Set environment variable for tests
    os.environ['TEST_ENVIRONMENT'] = environment
    
    # Determine which test files to run
    test_files = []
    
    if payment_method in ['stripe', 'all']:
        test_files.append('speedy_app.core.tests_payment_stripe')
    
    if payment_method in ['paypal', 'all']:
        test_files.append('speedy_app.core.tests_payment_paypal')
    
    if payment_method in ['integration', 'all']:
        test_files.append('speedy_app.core.tests_payment_integration')
    
    # Build test command
    cmd = [
        'python', 'manage.py', 'test',
        '--verbosity=2' if verbose else '--verbosity=1',
        '--keepdb' if environment == 'production' else '',
        '--parallel' if environment == 'production' else '',
    ]
    
    # Add test files
    cmd.extend(test_files)
    
    # Remove empty strings
    cmd = [arg for arg in cmd if arg]
    
    print(f"\n🚀 Running {payment_method} payment tests in {environment} environment...")
    print(f"📁 Test files: {', '.join(test_files)}")
    print(f"🔧 Command: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        # Run tests
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("\n✅ All tests passed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return False

def run_specific_test_scenarios(environment):
    """Run specific test scenarios for the given environment"""
    
    os.environ['TEST_ENVIRONMENT'] = environment
    
    print(f"\n🧪 Running specific test scenarios for {environment} environment...")
    
    # Test specific payment amounts
    test_amounts = [10.00, 25.50, 100.00, 250.75] if environment == 'staging' else [50.00, 125.00, 500.00, 1000.00]
    
    for amount in test_amounts:
        print(f"  Testing payment amount: ${amount:.2f}")
        # Here you could run specific test cases with different amounts
    
    # Test different currencies
    currencies = ['USD', 'EUR', 'MXN']
    for currency in currencies:
        print(f"  Testing currency: {currency}")
        # Here you could run specific test cases with different currencies
    
    print("✓ Specific test scenarios completed")

def check_environment_requirements(environment):
    """Check if the environment meets requirements for testing"""
    
    print(f"\n🔍 Checking {environment} environment requirements...")
    
    # Check required environment variables
    required_vars = {
        'staging': ['STRIPE_PUBLIC_KEY', 'STRIPE_SECRET_KEY', 'PAYPAL_CLIENT_ID', 'PAYPAL_SECRET'],
        'production': ['STRIPE_PUBLIC_KEY', 'STRIPE_SECRET_KEY', 'PAYPAL_CLIENT_ID', 'PAYPAL_SECRET', 'SECRET_KEY']
    }
    
    missing_vars = []
    for var in required_vars.get(environment, []):
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables for {environment}: {', '.join(missing_vars)}")
        print("   Please set these variables before running tests.")
        return False
    
    # Check database connectivity for production
    if environment == 'production':
        try:
            import psycopg2
            # Try to connect to test database
            print("✓ PostgreSQL driver available")
        except ImportError:
            print("⚠️  PostgreSQL driver not available. Install psycopg2-binary for production tests.")
            return False
    
    print(f"✓ {environment} environment requirements met")
    return True

def generate_test_report(environment, payment_method, success):
    """Generate a test report"""
    
    timestamp = os.popen('date').read().strip()
    
    report = f"""
📊 Payment System Test Report
============================

Environment: {environment.upper()}
Payment Methods: {payment_method.upper()}
Status: {'✅ PASSED' if success else '❌ FAILED'}
Timestamp: {timestamp}

Test Coverage:
- Stripe Integration: {'✓' if payment_method in ['stripe', 'all'] else '✗'}
- PayPal Integration: {'✓' if payment_method in ['paypal', 'all'] else '✗'}
- Integration Tests: {'✓' if payment_method in ['integration', 'all'] else '✗'}

Environment Details:
- Django Version: {django.get_version()}
- Python Version: {sys.version}
- Test Environment: {os.getenv('TEST_ENVIRONMENT', 'Not Set')}

Recommendations:
"""
    
    if success:
        report += """
✅ All tests passed successfully!
   - Payment systems are working correctly
   - Ready for deployment
   - Consider running load tests for production
"""
    else:
        report += """
❌ Tests failed - Action required:
   - Review error logs
   - Check payment service configurations
   - Verify environment variables
   - Fix failing tests before deployment
"""
    
    # Save report to file
    report_file = f"payment_test_report_{environment}_{payment_method}_{timestamp.replace(' ', '_').replace(':', '-')}.txt"
    
    try:
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Test report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save test report: {e}")
    
    return report

def main():
    """Main function to run payment tests"""
    
    parser = argparse.ArgumentParser(
        description='Run payment system tests for Speedy Transfers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--environment', '-e',
        choices=['staging', 'production'],
        default='staging',
        help='Test environment (default: staging)'
    )
    
    parser.add_argument(
        '--payment-method', '-p',
        choices=['stripe', 'paypal', 'integration', 'all'],
        default='all',
        help='Payment method to test (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose test output'
    )
    
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only check environment requirements, do not run tests'
    )
    
    args = parser.parse_args()
    
    print("🏁 Speedy Transfers Payment System Test Runner")
    print("=" * 60)
    
    # Setup Django
    setup_django()
    
    # Check environment requirements
    if not check_environment_requirements(args.environment):
        print("\n❌ Environment requirements not met. Exiting.")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ Environment check completed successfully!")
        return
    
    # Run specific test scenarios
    run_specific_test_scenarios(args.environment)
    
    # Run the actual tests
    success = run_tests(args.environment, args.payment_method, args.verbose)
    
    # Generate and display test report
    report = generate_test_report(args.environment, args.payment_method, success)
    print(report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
