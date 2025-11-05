# -*- coding: utf-8 -*-

from django.urls import path

from .views import LandingView, ResultsView, SummaryView, contact_form_view,\
    CheckoutView, create_payment, execute_payment, payment_failed, create_checkout_session, payment_success,\
    mock_stripe_checkout, mock_payment_success, twilio_whatsapp_webhook, send_whatsapp_endpoint
from .views_reports import reports_portal, sold_orders_report, sales_history_report

app_name = 'core'

urlpatterns = [
    path('', LandingView.as_view(), name="home_view"),
    path('search-results/', ResultsView.as_view(), name="results_view"),
    path('summary/', SummaryView.as_view(), name="summary_view"),
    path('checkout/', CheckoutView.as_view(), name="checkout_view"),
    path('contact/', contact_form_view, name='contact-form'),
    path('create_payment/', create_payment, name='create_payment'),
    path('create_checkout_session/', create_checkout_session, name='create_checkout_session'),
    path('execute_payment/', execute_payment, name='execute_payment'),
    path('payment_failed/', payment_failed, name='payment_failed'),
    path('payment_success/', payment_success, name='payment_success'),
    # Backwards-compatible aliases expected by some tests
    path('payment/failed/', payment_failed),
    path('payment/success/', payment_success),
    path('mock_stripe_checkout/', mock_stripe_checkout, name='mock_stripe_checkout'),
    path('mock_payment_success/', mock_payment_success, name='mock_payment_success'),
    # Twilio WhatsApp endpoints
    path('twilio/whatsapp/webhook/', twilio_whatsapp_webhook, name='twilio_whatsapp_webhook'),
    path('twilio/whatsapp/send/', send_whatsapp_endpoint, name='twilio_whatsapp_send'),
    # Reporting portal (staff only)
    path('reports/', reports_portal, name='reports_portal'),
    path('reports/sold-orders/', sold_orders_report, name='reports_sold_orders'),
    path('reports/sales-history/', sales_history_report, name='reports_sales_history'),
    #path('paypal/create/', PaypalPaymentView.as_view(), name='ordercreate'),
    #path('paypal/validate/', PaypalValidatePaymentView.as_view(), name='paypalvalidate'),   
]
