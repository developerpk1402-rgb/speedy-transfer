# Payment System Testing Guide

This guide explains how to test the payment systems in both staging and production environments for the Speedy Transfers application.

## 🎯 Overview

The payment system includes:
- **Stripe Integration**: Credit card payments via Stripe Checkout
- **PayPal Integration**: PayPal payments via redirect flow
- **Email Notifications**: Booking confirmation emails
- **Session Management**: Order data persistence during payment flow

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
# Install test requirements
pip install -r requirements-test.txt

# Or install specific packages
pip install pytest pytest-django pytest-cov stripe paypalrestsdk
```

### 2. Run All Payment Tests

```bash
# Run all tests in staging environment (default)
python run_payment_tests.py

# Run all tests in production environment
python run_payment_tests.py --environment production

# Run only Stripe tests
python run_payment_tests.py --payment-method stripe

# Run only PayPal tests
python run_payment_tests.py --payment-method paypal

# Run with verbose output
python run_payment_tests.py --verbose
```

### 3. Run Tests with Django

```bash
# Run all payment tests
python manage.py test speedy_app.core.tests_payment_stripe
python manage.py test speedy_app.core.tests_payment_paypal
python manage.py test speedy_app.core.tests_payment_integration

# Run with coverage
python manage.py test --with-coverage speedy_app.core.tests_payment_stripe
```

## 🧪 Test Structure

### Test Files

1. **`tests_payment_stripe.py`** - Stripe payment integration tests
2. **`tests_payment_paypal.py`** - PayPal payment integration tests  
3. **`tests_payment_integration.py`** - End-to-end payment flow tests
4. **`test_config.py`** - Test configuration and utilities
5. **`run_payment_tests.py`** - Test runner script

### Test Categories

- **Unit Tests**: Individual payment method functionality
- **Integration Tests**: Complete payment flows
- **Error Handling**: Payment failures and edge cases
- **Data Validation**: Order data integrity
- **Environment Testing**: Staging vs production configurations

## 🔧 Environment Configuration

### Staging Environment

```bash
export TEST_ENVIRONMENT=staging
export STRIPE_PUBLIC_KEY=pk_test_your_staging_key
export STRIPE_SECRET_KEY=sk_test_your_staging_key
export PAYPAL_CLIENT_ID=your_staging_client_id
export PAYPAL_SECRET=your_staging_secret
```

### Production Environment

```bash
export TEST_ENVIRONMENT=production
export STRIPE_PUBLIC_KEY=pk_live_your_production_key
export STRIPE_SECRET_KEY=sk_live_your_production_key
export PAYPAL_CLIENT_ID=your_production_client_id
export PAYPAL_SECRET=your_production_secret
export SECRET_KEY=your_django_secret_key
```

### Environment Variables

| Variable | Staging | Production | Description |
|----------|---------|------------|-------------|
| `TEST_ENVIRONMENT` | `staging` | `production` | Test environment identifier |
| `STRIPE_PUBLIC_KEY` | `pk_test_...` | `pk_live_...` | Stripe public key |
| `STRIPE_SECRET_KEY` | `sk_test_...` | `sk_live_...` | Stripe secret key |
| `PAYPAL_CLIENT_ID` | Sandbox ID | Live ID | PayPal client ID |
| `PAYPAL_SECRET` | Sandbox secret | Live secret | PayPal secret |
| `SECRET_KEY` | Optional | Required | Django secret key |

## 🧪 Test Scenarios

### Stripe Test Scenarios

1. **Successful Payment**
   - Test card: `4242 4242 4242 4242`
   - Any future expiry, any CVC, any ZIP

2. **3D Secure Challenge**
   - Test card: `4000 0025 0000 3155`
   - Choose "Complete" for success

3. **Payment Decline**
   - Test card: `4000 0000 0000 0002`
   - Tests proper error handling

4. **Insufficient Funds**
   - Test card: `4000 0000 0000 9995`
   - Tests declined payment handling

### PayPal Test Scenarios

1. **Sandbox Accounts**
   - Create sandbox business and personal accounts
   - Use personal account for testing payments

2. **Payment Flow**
   - Create payment → Redirect to PayPal → Approve → Execute
   - Tests complete payment lifecycle

3. **Cancellation**
   - Cancel payment during PayPal flow
   - Tests proper cancellation handling

### Integration Test Scenarios

1. **Complete Payment Flow**
   - Order creation → Payment → Success → Email confirmation

2. **Error Handling**
   - Network failures, API errors, validation failures

3. **Data Persistence**
   - Session management, order data integrity

4. **Multi-currency Support**
   - USD, EUR, MXN currency handling

## 📊 Test Coverage

### What's Tested

✅ **Payment Creation**
- Stripe checkout session creation
- PayPal payment creation
- Order data validation
- Amount and currency handling

✅ **Payment Processing**
- Stripe payment flow
- PayPal payment execution
- Error handling and fallbacks
- Session management

✅ **Post-Payment**
- Email notifications
- Order confirmation
- Session cleanup
- Data persistence

✅ **Edge Cases**
- Invalid order data
- Payment failures
- Network errors
- Missing parameters

### Coverage Reports

```bash
# Generate coverage report
python manage.py test --with-coverage --cover-package=speedy_app.core

# Generate HTML coverage report
coverage run --source='.' manage.py test
coverage html
open htmlcov/index.html
```

## 🚨 Common Issues & Solutions

### 1. Environment Variables Not Set

```bash
# Error: Missing environment variables
export STRIPE_PUBLIC_KEY=pk_test_your_key
export STRIPE_SECRET_KEY=sk_test_your_key
```

### 2. Database Connection Issues

```bash
# For production tests, ensure PostgreSQL is running
sudo systemctl start postgresql
sudo -u postgres createdb test_speedy_transfers
```

### 3. Payment Service API Errors

```bash
# Check API keys are correct
# Verify sandbox vs live environment
# Check network connectivity
```

### 4. Test Data Issues

```bash
# Ensure test models are created
python manage.py migrate
python manage.py shell
# Create test Zone, Hotel, Car objects
```

## 🔍 Debugging Tests

### Verbose Output

```bash
# Run with detailed output
python run_payment_tests.py --verbose

# Django test verbosity
python manage.py test --verbosity=2
```

### Debug Specific Tests

```bash
# Run single test method
python manage.py test speedy_app.core.tests_payment_stripe.StripePaymentTestCase.test_stripe_checkout_session_creation_success

# Run with pdb debugger
python -m pytest --pdb
```

### Log Analysis

```bash
# Check Django logs
tail -f server.log

# Check test output
python run_payment_tests.py > test_output.log 2>&1
```

## 📈 Performance Testing

### Load Testing

```bash
# Run tests in parallel
python manage.py test --parallel

# Use pytest-xdist for parallel execution
pytest -n auto
```

### Benchmark Testing

```bash
# Install benchmark plugin
pip install pytest-benchmark

# Run benchmark tests
pytest --benchmark-only
```

## 🔒 Security Testing

### Vulnerability Scanning

```bash
# Install security tools
pip install bandit safety

# Run security checks
bandit -r speedy_app/
safety check
```

### Payment Security

- Test with invalid payment data
- Verify API key security
- Check for sensitive data exposure
- Test authentication and authorization

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Payment Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
      - name: Run payment tests
        run: |
          python run_payment_tests.py --environment staging
        env:
          STRIPE_PUBLIC_KEY: ${{ secrets.STRIPE_TEST_KEY }}
          STRIPE_SECRET_KEY: ${{ secrets.STRIPE_TEST_SECRET }}
          PAYPAL_CLIENT_ID: ${{ secrets.PAYPAL_TEST_CLIENT_ID }}
          PAYPAL_SECRET: ${{ secrets.PAYPAL_TEST_SECRET }}
```

### Docker Testing

```bash
# Run tests in Docker
docker-compose -f docker-compose.test.yml up --build

# Or run tests in existing container
docker exec -it speedy_app python run_payment_tests.py
```

## 📋 Test Checklist

### Before Running Tests

- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Test dependencies installed
- [ ] Payment service accounts configured
- [ ] Test data created

### After Running Tests

- [ ] All tests pass
- [ ] Coverage report generated
- [ ] Test report saved
- [ ] Issues documented
- [ ] Performance metrics recorded

## 🆘 Getting Help

### Documentation

- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Stripe Testing](https://stripe.com/docs/testing)
- [PayPal Testing](https://developer.paypal.com/docs/api-basics/sandbox/)

### Support

- Check test logs for error details
- Verify environment configuration
- Ensure payment service accounts are active
- Test with minimal data first

## 📝 Test Reports

Test reports are automatically generated and saved with timestamps:

```
payment_test_report_staging_all_2025-01-27_14-30-45.txt
payment_test_report_production_stripe_2025-01-27_15-45-12.txt
```

Reports include:
- Test results summary
- Environment details
- Coverage information
- Recommendations
- Error details (if any)

---

**Remember**: Always test in staging environment first before running production tests!
