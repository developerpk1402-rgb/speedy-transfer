from django.core.management.base import BaseCommand
from speedy_app.core.models import Zone, Hotel, CarType, Car, Rate, Contact, WhatsAppConversation, WhatsAppMessage, Booking
from django.utils import timezone


class Command(BaseCommand):
    help = 'Seed the database with sample Zones, Hotels, CarTypes, Cars, Rates, Contact, Booking and WhatsApp data.'

    def handle(self, *args, **options):
        # Create Zones
        zone1, _ = Zone.objects.get_or_create(name='Airport Zone', defaults={'description': 'Area around the main airport'})
        zone2, _ = Zone.objects.get_or_create(name='Downtown', defaults={'description': 'City center hotels and attractions'})

        # Create Hotels
        hotel1, _ = Hotel.objects.get_or_create(name='Airport Hotel', defaults={'zone': zone1, 'description': 'Hotel near the airport'})
        hotel2, _ = Hotel.objects.get_or_create(name='Grand City Hotel', defaults={'zone': zone2, 'description': 'Luxury downtown hotel'})

        # Create CarTypes
        sedan_type, _ = CarType.objects.get_or_create(code='SEDAN', defaults={'name': 'Sedan', 'max_capacity': 3})
        suv_type, _ = CarType.objects.get_or_create(code='SUV', defaults={'name': 'SUV', 'max_capacity': 6})

        # Create Cars
        car1, _ = Car.objects.get_or_create(name='Toyota Corolla', defaults={'car_type': sedan_type, 'max': 3})
        car2, _ = Car.objects.get_or_create(name='Ford Explorer', defaults={'car_type': suv_type, 'max': 6})

        # Create Rates
        Rate.objects.get_or_create(zone=zone1, car=car1, travel_type='ONE_WAY', defaults={'price': '25.00'})
        Rate.objects.get_or_create(zone=zone1, car=car2, travel_type='ONE_WAY', defaults={'price': '40.00'})
        Rate.objects.get_or_create(zone=zone2, car=car1, travel_type='ROUND_TRIP', defaults={'price': '45.00'})

        # Create Contact
        contact, _ = Contact.objects.get_or_create(
            email='sample.user@example.com',
            defaults={
                'name': 'Sample User',
                'phone': '+1234567890',
                'country': 'Sampleland',
                'company': 'Example Co',
                'interested_in': 'Airport transfer',
                'message': 'I would like a sample booking',
                'whatsapp_number': '+1234567890',
                'preferred_contact_method': 'whatsapp',
                'subscribe_newsletter': True,
            }
        )

        # Create WhatsApp conversation and messages
        conv = WhatsAppConversation.objects.create(contact=contact)
        WhatsAppMessage.objects.create(conversation=conv, sender='user', content='Hello, I need a transfer', direction='inbound')
        WhatsAppMessage.objects.create(conversation=conv, sender='agent', content='Sure — what date?', direction='outbound')

        # Create Booking
        now = timezone.now()
        booking, _ = Booking.objects.get_or_create(
            client_id=contact.email,
            defaults={
                'customer_name': contact.name,
                'customer_phone': contact.phone,
                'pickup_location1': hotel1,
                'dropoff_location1': hotel2,
                'pickup_date_time': now + timezone.timedelta(days=7),
                'return_date_time': now + timezone.timedelta(days=7, hours=2),
                'car_id': car1,
                'how_people': 2,
                'one_way': True,
                'total_amount': '25.00',
                'currency': 'USD',
                'payment_method': 'CASH_ON_ARRIVAL',
                'trip_type': 'oneway',
            }
        )

        self.stdout.write(self.style.SUCCESS('Sample data seeded successfully.'))