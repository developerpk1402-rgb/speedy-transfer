from django.core.management.base import BaseCommand
from django.test import RequestFactory
from speedy_app.core.views import send_booking_email


class Command(BaseCommand):
    help = 'Test the actual booking email function to verify admin notifications'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Actual Booking Email Function...")
        self.stdout.write("=" * 50)
        
        # Test the actual send_booking_email function
        self.test_actual_booking_email_function()
        
        self.stdout.write("=" * 50)
        self.stdout.write("✅ Booking email function testing completed!")
        self.stdout.write("📬 Check these email addresses for admin notifications:")
        self.stdout.write("   - cmelendezgp@gmail.com")
        self.stdout.write("   - adolfomariscalh@hotmail.com")

    def test_actual_booking_email_function(self):
        """Test the actual send_booking_email function"""
        self.stdout.write("\n📧 Testing Actual Booking Email Function...")
        
        try:
            # Create test order data that matches what the function expects
            test_order = {
                'trip_type': 'oneway',
                'people': 4,
                'pickup': {
                    'datetime': '2025-09-01 08:00',
                    'location_name': 'Marriott Puerto Vallarta Resort & Spa'
                },
                'dropoff': {
                    'datetime': '2025-09-01 09:00',
                    'location_name': 'Lic. Gustavo Díaz Ordaz International Airport'
                },
                'car_type_label': 'VAN',
                'items': [
                    {
                        'name': 'Luxury Van',
                        'unit_amount': 180.00,
                        'currency': 'USD',
                        'date': '2025-09-01',
                        'time': '08:00',
                        'capacity': 8,
                    }
                ],
                'subtotal': 180.00,
                'total': 180.00,
                'customer': {
                    'name': 'John Smith',
                    'email': 'john.smith@example.com',
                    'phone': '+1-555-123-4567',
                    'address': '123 Main Street',
                    'city': 'New York',
                    'zip': '10001',
                }
            }
            
            # Create a simple request object
            factory = RequestFactory()
            request = factory.get('/')
            
            # Test the actual send_booking_email function
            # This should send emails to both the customer and admin recipients
            send_booking_email(test_order, request)
            
            self.stdout.write("✅ Actual booking email function executed successfully")
            self.stdout.write("📧 Customer email should be sent to: john.smith@example.com")
            self.stdout.write("📧 Admin notification emails should be sent to:")
            self.stdout.write("   - cmelendezgp@gmail.com")
            self.stdout.write("   - adolfomariscalh@hotmail.com")
            
        except Exception as e:
            self.stdout.write(f"❌ Actual booking email function failed: {e}")
            import traceback
            traceback.print_exc()
