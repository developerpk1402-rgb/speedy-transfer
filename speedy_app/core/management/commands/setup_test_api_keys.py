from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Set up test API keys for Stripe and PayPal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--stripe-secret',
            type=str,
            help='Stripe secret key (sk_test_...)',
        )
        parser.add_argument(
            '--stripe-public',
            type=str,
            help='Stripe public key (pk_test_...)',
        )
        parser.add_argument(
            '--paypal-client-id',
            type=str,
            help='PayPal client ID',
        )
        parser.add_argument(
            '--paypal-secret',
            type=str,
            help='PayPal secret',
        )

    def handle(self, *args, **options):
        self.stdout.write('🔑 Setting up test API keys...')
        
        # Set environment variables
        if options['stripe_secret']:
            os.environ['STRIPE_SECRET_KEY'] = options['stripe_secret']
            self.stdout.write('✅ Stripe secret key set')
        
        if options['stripe_public']:
            os.environ['STRIPE_PUBLIC_KEY'] = options['stripe_public']
            self.stdout.write('✅ Stripe public key set')
        
        if options['paypal_client_id']:
            os.environ['PAYPAL_CLIENT_ID'] = options['paypal_client_id']
            self.stdout.write('✅ PayPal client ID set')
        
        if options['paypal_secret']:
            os.environ['PAYPAL_SECRET'] = options['paypal_secret']
            self.stdout.write('✅ PayPal secret set')
        
        # Show current configuration
        self.stdout.write('\n📊 Current configuration:')
        self.stdout.write(f'  STRIPE_SECRET_KEY: {os.getenv("STRIPE_SECRET_KEY", "NOT_SET")[:20]}...')
        self.stdout.write(f'  STRIPE_PUBLIC_KEY: {os.getenv("STRIPE_PUBLIC_KEY", "NOT_SET")[:20]}...')
        self.stdout.write(f'  PAYPAL_CLIENT_ID: {os.getenv("PAYPAL_CLIENT_ID", "NOT_SET")[:20]}...')
        self.stdout.write(f'  PAYPAL_SECRET: {os.getenv("PAYPAL_SECRET", "NOT_SET")[:20]}...')
        
        self.stdout.write('\n💡 To make these permanent, add them to your .env file or environment')
