from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch
from django.core import mail
import json


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PaymentEmailTests(TestCase):
    def setUp(self):
        self.order = {
            'trip_type': 'oneway',
            'people': 3,
            'pickup': {
                'datetime': '2025-08-10 10:00',
                'location_id': '1',
                'location_name': 'Hotel A'
            },
            'dropoff': {
                'location_id': '2',
                'location_name': 'Airport'
            },
            'car_type_label': 'VAN',
            'items': [
                {'name': 'Van A', 'unit_amount': 100.0, 'currency': 'USD', 'date': '2025-08-10', 'time': '10:00', 'capacity': 10},
            ],
            'subtotal': 100.0,
            'total': 100.0,
            'customer': {
                'name': 'John Tester',
                'email': 'guest@example.com',
                'phone': '1234567890',
                'address': '123 Test St',
                'city': 'Testville',
                'zip': '12345',
            }
        }

    @patch('stripe.checkout.Session.create')
    def test_stripe_checkout_sends_emails_on_success(self, mock_create):
        mock_create.return_value = type('obj', (), {'url': '/fake-stripe'})
        # Start checkout (stores order in session)
        resp = self.client.get(reverse('core:create_checkout_session'), {'order_json': json.dumps(self.order)})
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/fake-stripe', resp['Location'])

        # Simulate success callback which should send emails
        resp2 = self.client.get(reverse('core:payment_success'))
        self.assertEqual(resp2.status_code, 200)

        # Two messages sent: one to guest, one to test recipients (2 addresses)
        self.assertEqual(len(mail.outbox), 2)
        # Guest
        self.assertEqual(mail.outbox[0].to, ['guest@example.com'])
        # Test recipients
        self.assertEqual(set(mail.outbox[1].to), set(['cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com']))

    @patch('paypalrestsdk.Payment.create')
    def test_paypal_checkout_sends_emails_on_execute(self, mock_create):
        # Mock creation returning True
        mock_create.return_value = True
        # Mock the Payment.links with approval url at index 1
        with patch('paypalrestsdk.Payment') as MockPayment:
            instance = MockPayment.return_value
            instance.links = [type('link', (), {'href': '/link0'}), type('link', (), {'href': '/paypal-redirect'})]

            # Create payment (store session)
            resp = self.client.post(
                reverse('core:create_payment'),
                {'order_json': json.dumps(self.order)},
                content_type='application/x-www-form-urlencoded'
            )
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/paypal-redirect', resp['Location'])

        # Ensure session contains order for execute step (some middlewares may not persist in test)
        session = self.client.session
        session['order_json'] = json.dumps(self.order)
        session.save()

        # Mock execute flow
        with patch('paypalrestsdk.Payment.find') as MockFind:
            payment_obj = MockFind.return_value
            payment_obj.execute.return_value = True
            resp2 = self.client.get(reverse('core:execute_payment'), {'paymentId': 'pid', 'PayerID': 'payer'})
            self.assertEqual(resp2.status_code, 200)

        # Two messages sent: one to guest, one to test recipients
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ['guest@example.com'])
        self.assertEqual(set(mail.outbox[1].to), set(['cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com']))
