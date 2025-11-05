### Payment Testing Guide (No Real Cards Required)

This project integrates both Stripe (card payments) and PayPal (redirect approval) in test/sandbox mode. Follow these steps to verify payments end-to-end without using a real card.

- Stripe is used via `stripe.checkout.Session` in `create_checkout_session`
- PayPal is used via `paypalrestsdk.Payment` in `create_payment` → `execute_payment`

Key routes (see `speedy_app/core/urls.py`):
- `GET /checkout/` → checkout UI
- `GET /create_checkout_session/` → starts Stripe Checkout
- `POST /create_payment/` → starts PayPal payment (redirects to approval)
- `GET /execute_payment/` → PayPal success callback after approval
- `GET /payment_success/`, `GET /payment_failed/` → result pages

Settings (see `config/settings/settings.py`):
- `PAYPAL_CLIENT_ID`, `PAYPAL_SECRET` are configured for sandbox mode
- `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY` are test keys

The app does not depend on webhooks for success/failure; it uses frontend redirects.

---

### 1) Prerequisites

- Install dependencies and run the app
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
- Open the checkout page in your browser:
  - `http://localhost:8000/checkout/`
- Optional: For email testing during development, use the console backend so emails print to the terminal instead of sending:
```bash
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
Emails are sent by `send_booking_email` on success to the guest email (if provided in the order) and to test recipients configured in code.

---

### 2) Test via the UI

On `http://localhost:8000/checkout/`:
1. Fill the booking details and proceed to Checkout (the page builds a structured `order_json` for you).
2. Choose your test provider:
   - Click “Pay with Card (Stripe Test)” to open Stripe Checkout
   - Click “Pay with PayPal (Test)” to open the PayPal sandbox approval page

---

### 3) Stripe Testing (Test Mode)

Stripe is configured with test keys (`pk_test_...`/`sk_test_...`). In test mode, use Stripe test card numbers; never use a real card.

- Success (simple):
  - Card number: 4242 4242 4242 4242
  - Any future expiry (e.g., 12/34), any 3-digit CVC, any ZIP
- SCA/3D Secure challenge:
  - Card number: 4000 0025 0000 3155
  - You’ll be prompted for a test authentication; choose “Complete” (or “Fail” to test failure)
- Hard decline:
  - Card number: 4000 0000 0000 0002
- Insufficient funds:
  - Card number: 4000 0000 0000 9995

Flow:
1. Click “Pay with Card (Stripe Test)”.
2. On Stripe Checkout, enter a test card above and submit.
3. On success, you’ll be redirected to `/payment_success/`.
4. Verify a booking email is emitted (console or your email backend). The order details come from the checkout page’s `order_json`.
5. Verify in Stripe Dashboard (test mode): `Payments` should show the test charge.

Cancel/Failure testing:
- Use the “Cancel” button on Checkout to return to `/payment_failed/`.
- Try a declined number to see proper error handling.

---

### 4) PayPal Testing (Sandbox)

PayPal is configured in sandbox mode; the code calls `paypalrestsdk.configure({ "mode": "sandbox", ... })` and uses `PAYPAL_CLIENT_ID`/`PAYPAL_SECRET`.

Setup a sandbox buyer account:
1. Go to the PayPal Developer Dashboard (Sandbox).
2. Create a Sandbox Business (seller) and Sandbox Personal (buyer) account.
3. Note the email/password for the Sandbox Personal (buyer) account.

Flow:
1. Click “Pay with PayPal (Test)”.
2. You’ll be redirected to the PayPal sandbox approval page; log in with the Sandbox Personal (buyer) account.
3. Approve the payment.
4. You’ll be redirected to `/execute_payment/` and then to `/payment_success/`.
5. Verify a booking email is emitted (console or your email backend).
6. Verify in the PayPal Sandbox dashboard that a test transaction was created.

Cancel/Failure testing:
- Click “Cancel and return” in PayPal to be redirected to `/payment_failed/`.

---

### 5) What gets verified on success

- Redirect to `/payment_success/` renders the success page
- `send_booking_email` runs and uses the `order_json` stored in session by the checkout flow
- You’ll see structured booking details (customer info, trip, items, and total) in the email output

---

### 6) Troubleshooting

- Stripe Checkout error (JSON error from `/create_checkout_session/`):
  - Ensure `STRIPE_SECRET_KEY` is set (it is preconfigured for test in settings)
  - Ensure your server URL in the browser matches the domain used to build `success_url`/`cancel_url`
- PayPal approval page shows invalid client or 401:
  - Ensure `PAYPAL_CLIENT_ID`/`PAYPAL_SECRET` are sandbox credentials (preconfigured in settings)
  - Make sure you are using a Sandbox Personal (buyer) account to approve
- No email appears:
  - Use the console email backend for development (see above), or configure SMTP credentials in your environment
- Cancels do not show failure page:
  - Confirm the redirect URLs resolve to `/payment_failed/` in your environment

---

### 7) Advanced: Verifying without the UI

The UI already builds and passes `order_json` for you. If you must trigger the flows directly:
- Stripe: issue a GET to `/create_checkout_session/?order_json=<urlencoded-json>` and follow the redirect URL returned
- PayPal: POST to `/create_payment/` with `order_json` form data and follow the approval link

Sample `order_json` structure the app understands (built by the checkout page):
```json
{
  "customer": {"name": "Test User", "email": "test@example.com"},
  "trip_type": "oneway",
  "people": 2,
  "items": [
    {
      "name": "Transfer",
      "date": "2025-12-31",
      "time": "10:00",
      "capacity": 4,
      "unit_amount": 20.00,
      "currency": "USD"
    }
  ],
  "total": 20.00
}
```

---

### 8) What is out of scope

- Webhooks: this app’s success/failure logic is based on redirect flows, not webhooks
- Real cards: never use a real card in test; always use Stripe test cards and PayPal Sandbox buyer accounts

That’s it—you can now validate both providers end-to-end without using your own card.