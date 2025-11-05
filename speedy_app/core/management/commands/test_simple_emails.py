from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test simple email functionality by sending test emails to admin addresses'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Simple Email Functionality...")
        self.stdout.write("=" * 50)
        
        # Test 1: Simple test email
        self.test_simple_email()
        
        # Test 2: Admin notification email
        self.test_admin_notification_email()
        
        # Test 3: Booking confirmation email
        self.test_booking_confirmation_email()
        
        self.stdout.write("=" * 50)
        self.stdout.write("✅ Simple email testing completed!")
        self.stdout.write("📬 Check these email addresses for test emails:")
        self.stdout.write("   - cmelendezgp@gmail.com")
        self.stdout.write("   - adolfomariscalh@hotmail.com")

    def test_simple_email(self):
        """Test basic email functionality"""
        self.stdout.write("\n📧 Testing Basic Email Functionality...")
        
        try:
            # Send simple test email
            send_mail(
                subject='Test Email from Speedy Transfers - Basic Test',
                message='''
This is a basic test email to verify the email system is working correctly.

Email Configuration:
- SMTP Server: {host}:{port}
- From: {from_email}
- SSL: {ssl}
- TLS: {tls}

If you receive this email, the basic email system is working properly!

Best regards,
Speedy Transfers Team
                '''.format(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    ssl=settings.EMAIL_USE_SSL,
                    tls=settings.EMAIL_USE_TLS
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cmelendezgp@gmail.com'],
                fail_silently=False,
            )
            
            self.stdout.write("✅ Basic test email sent successfully to cmelendezgp@gmail.com")
            
        except Exception as e:
            self.stdout.write(f"❌ Basic test email failed: {e}")
            import traceback
            traceback.print_exc()

    def test_admin_notification_email(self):
        """Test admin notification email"""
        self.stdout.write("\n📧 Testing Admin Notification Email...")
        
        try:
            # Send admin notification email
            send_mail(
                subject='Admin Notification: New Booking Received - Test',
                message='''
ADMIN NOTIFICATION - NEW BOOKING

A new booking has been received through the Speedy Transfers system.

Booking Details:
- Customer: Test User (test@example.com)
- Trip Type: One-Way
- Passengers: 4
- Pickup: Marriott Puerto Vallarta Resort & Spa
- Dropoff: Lic. Gustavo Díaz Ordaz International Airport
- Date: September 1, 2025
- Time: 8:00 AM
- Vehicle: Luxury Van
- Total Amount: $180.00 USD

This is a test notification to verify admin emails are working.

Please log into the admin panel to view full booking details.

Best regards,
Speedy Transfers System
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cmelendezgp@gmail.com', 'adolfomariscalh@hotmail.com'],
                fail_silently=False,
            )
            
            self.stdout.write("✅ Admin notification email sent successfully to both admin addresses")
            
        except Exception as e:
            self.stdout.write(f"❌ Admin notification email failed: {e}")
            import traceback
            traceback.print_exc()

    def test_booking_confirmation_email(self):
        """Test booking confirmation email"""
        self.stdout.write("\n📧 Testing Booking Confirmation Email...")
        
        try:
            # Send booking confirmation email
            send_mail(
                subject='Booking Confirmation: Round-Trip Transfer - Test',
                message='''
BOOKING CONFIRMATION

Thank you for your booking with Speedy Transfers!

Booking Reference: TEST-2025-001
Customer: Maria Garcia (maria.garcia@example.com)

TRIP DETAILS:
- Trip Type: Round-Trip
- Passengers: 6
- Vehicle: Luxury SUV
- Total Amount: $250.00 USD

OUTBOUND TRIP:
- Date: September 2, 2025
- Pickup: 10:00 AM from Marriott Puerto Vallarta Resort & Spa
- Dropoff: 11:00 AM at Lic. Gustavo Díaz Ordaz International Airport

RETURN TRIP:
- Date: September 5, 2025
- Pickup: 4:00 PM from Lic. Gustavo Díaz Ordaz International Airport
- Dropoff: 5:00 PM at Marriott Puerto Vallarta Resort & Spa

IMPORTANT INFORMATION:
- Please be ready 15 minutes before pickup time
- Driver will contact you 30 minutes before pickup
- Cancellation policy: 24 hours notice required

This is a test confirmation email to verify the email system.

For questions, contact: soporte@vittapp.com

Best regards,
Speedy Transfers Team
                ''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['cmelendezgp@gmail.com'],
                fail_silently=False,
            )
            
            self.stdout.write("✅ Booking confirmation email sent successfully to cmelendezgp@gmail.com")
            
        except Exception as e:
            self.stdout.write(f"❌ Booking confirmation email failed: {e}")
            import traceback
            traceback.print_exc()







