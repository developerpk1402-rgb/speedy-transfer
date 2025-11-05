from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email functionality by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test email to',
            default='cmelendezgp@gmail.com'
        )

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write(f"Testing email functionality...")
        self.stdout.write(f"SMTP Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        self.stdout.write(f"From: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"To: {test_email}")
        self.stdout.write(f"SSL: {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"TLS: {settings.EMAIL_USE_TLS}")
        
        try:
            # Send test email
            send_mail(
                subject='Test Email from Speedy Transfers',
                message=f'''
This is a test email to verify the email system is working correctly.

Email Configuration:
- SMTP Server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}
- From: {settings.DEFAULT_FROM_EMAIL}
- SSL: {settings.EMAIL_USE_SSL}
- TLS: {settings.EMAIL_USE_TLS}

If you receive this email, the email system is working properly!
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Test email sent successfully to {test_email}')
            )
            self.stdout.write('Check your inbox (and spam folder) for the test email.')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send test email: {e}')
            )
            import traceback
            traceback.print_exc()







