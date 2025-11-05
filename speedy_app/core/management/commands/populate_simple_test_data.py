from django.core.management.base import BaseCommand
from django.db import connection
from speedy_app.core.models import Zone, Hotel, Car, CarType, Rate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with simple test data for Fechas section testing'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Populating database with simple test data...')
        
        # 1. Create Car Types using direct SQL to avoid auto-increment issues
        car_types_data = [
            ('VAN', 'VAN', 'Standard van for small groups', 8),
            ('SMALL_SPRINTER', 'SMALL SPRINTER', 'Small sprinter van', 12),
            ('LARGE_SPRINTER', 'LARGE SPRINTER', 'Large sprinter van', 18),
            ('SEDAN', 'SEDAN', 'Economy sedan', 4),
            ('SUV', 'SUV', 'Mid-size SUV', 6),
            ('BUS', 'BUS', 'Mini bus', 20),
        ]
        
        with connection.cursor() as cursor:
            for code, name, description, max_capacity in car_types_data:
                cursor.execute("""
                    INSERT IGNORE INTO core_cartype (code, name, description, max_capacity)
                    VALUES (%s, %s, %s, %s)
                """, [code, name, description, max_capacity])
                self.stdout.write(f'✅ Created/Updated car type: {name}')

        # 2. Create Zones
        zones_data = [
            ('AEROPUERTO', 'Airport zone'),
            ('ZONA HOTELERA NORTE', 'North Hotel Zone'),
            ('ZONA HOTELERA SUR', 'South Hotel Zone'),
            ('CENTRO', 'Downtown area'),
            ('MARINA', 'Marina area'),
        ]
        
        with connection.cursor() as cursor:
            for name, description in zones_data:
                cursor.execute("""
                    INSERT IGNORE INTO core_zone (name, description)
                    VALUES (%s, %s)
                """, [name, description])
                self.stdout.write(f'✅ Created/Updated zone: {name}')

        # 3. Create Hotels
        hotels_data = [
            ('AEROPUERTO', 'AEROPUERTO'),
            ('HOTEL RIU PALACE PACIFIC', 'ZONA HOTELERA NORTE'),
            ('HOTEL RIU JALISCO', 'ZONA HOTELERA NORTE'),
            ('HOTEL CROWN PARADISE', 'ZONA HOTELERA NORTE'),
            ('HOTEL FIESTA AMERICANA', 'ZONA HOTELERA NORTE'),
            ('HOTEL MARRIOTT', 'ZONA HOTELERA NORTE'),
            ('HOTEL VELAS VALLARTA', 'ZONA HOTELERA SUR'),
            ('HOTEL GRAND VELAS', 'ZONA HOTELERA SUR'),
            ('HOTEL HARD ROCK', 'ZONA HOTELERA SUR'),
            ('HOTEL WESTIN', 'ZONA HOTELERA SUR'),
            ('HOTEL ROSITA', 'CENTRO'),
            ('HOTEL PLAZA VALLARTA', 'CENTRO'),
            ('HOTEL MARINA VALLARTA', 'MARINA'),
            ('HOTEL VELAS MARINA', 'MARINA'),
        ]
        
        with connection.cursor() as cursor:
            for hotel_name, zone_name in hotels_data:
                # Get zone ID
                cursor.execute("SELECT id FROM core_zone WHERE name = %s", [zone_name])
                zone_result = cursor.fetchone()
                if zone_result:
                    zone_id = zone_result[0]
                    cursor.execute("""
                        INSERT IGNORE INTO core_hotel (name, zone_id)
                        VALUES (%s, %s)
                    """, [hotel_name, zone_id])
                    self.stdout.write(f'✅ Created/Updated hotel: {hotel_name}')

        # 4. Create Cars - Multiple cars per type
        cars_data = [
            # VAN cars (5 units)
            ('VAN 001', 'VAN', 8, 'Max 9 people per vehicle'),
            ('VAN 002', 'VAN', 8, 'Max 9 people per vehicle'),
            ('VAN 003', 'VAN', 8, 'Max 9 people per vehicle'),
            ('VAN 004', 'VAN', 8, 'Max 9 people per vehicle'),
            ('VAN 005', 'VAN', 8, 'Max 9 people per vehicle'),
            
            # SMALL SPRINTER cars (3 units)
            ('SMALL SPRINTER 001', 'SMALL_SPRINTER', 12, 'Max 11 people per vehicle'),
            ('SMALL SPRINTER 002', 'SMALL_SPRINTER', 12, 'Max 11 people per vehicle'),
            ('SMALL SPRINTER 003', 'SMALL_SPRINTER', 12, 'Max 11 people per vehicle'),
            
            # LARGE SPRINTER cars (3 units)
            ('LARGE SPRINTER 001', 'LARGE_SPRINTER', 18, 'Max 20 people per vehicle'),
            ('LARGE SPRINTER 002', 'LARGE_SPRINTER', 18, 'Max 20 people per vehicle'),
            ('LARGE SPRINTER 003', 'LARGE_SPRINTER', 18, 'Max 20 people per vehicle'),
            
            # SEDAN cars (3 units)
            ('SEDAN 001', 'SEDAN', 4, 'Economy sedan for small groups'),
            ('SEDAN 002', 'SEDAN', 4, 'Economy sedan for small groups'),
            ('SEDAN 003', 'SEDAN', 4, 'Economy sedan for small groups'),
            
            # SUV cars (3 units)
            ('SUV 001', 'SUV', 6, 'Mid-size SUV for small groups'),
            ('SUV 002', 'SUV', 6, 'Mid-size SUV for small groups'),
            ('SUV 003', 'SUV', 6, 'Mid-size SUV for small groups'),
            
            # BUS cars (2 units)
            ('BUS 001', 'BUS', 20, 'Mini bus for large groups'),
            ('BUS 002', 'BUS', 20, 'Mini bus for large groups'),
        ]
        
        with connection.cursor() as cursor:
            for car_name, car_type_code, max_capacity, description in cars_data:
                # Get car type ID
                cursor.execute("SELECT id FROM core_cartype WHERE code = %s", [car_type_code])
                car_type_result = cursor.fetchone()
                if car_type_result:
                    car_type_id = car_type_result[0]
                    cursor.execute("""
                        INSERT IGNORE INTO core_car (name, car_type_id, max, description)
                        VALUES (%s, %s, %s, %s)
                    """, [car_name, car_type_id, max_capacity, description])
                    self.stdout.write(f'✅ Created/Updated car: {car_name}')

        # 5. Create Rates - Simple pricing structure
        with connection.cursor() as cursor:
            # Get zone and car IDs
            cursor.execute("SELECT id, name FROM core_zone")
            zones = {name: id for id, name in cursor.fetchall()}
            
            cursor.execute("SELECT id, name FROM core_cartype")
            car_types = {name: id for id, name in cursor.fetchall()}
            
            # Create rates for airport to hotel zones
            airport_zone_id = zones.get('AEROPUERTO')
            if airport_zone_id:
                for target_zone_name in ['ZONA HOTELERA NORTE', 'ZONA HOTELERA SUR', 'CENTRO', 'MARINA']:
                    target_zone_id = zones.get(target_zone_name)
                    if target_zone_id:
                        # Get first car of each type
                        for car_type_name in ['VAN', 'SMALL_SPRINTER', 'LARGE_SPRINTER', 'SEDAN', 'SUV', 'BUS']:
                            car_type_id = car_types.get(car_type_name)
                            if car_type_id:
                                cursor.execute("""
                                    SELECT id FROM core_car WHERE car_type_id = %s LIMIT 1
                                """, [car_type_id])
                                car_result = cursor.fetchone()
                                if car_result:
                                    car_id = car_result[0]
                                    
                                    # Define prices based on car type and distance
                                    base_prices = {
                                        'SEDAN': 45, 'SUV': 55, 'VAN': 65,
                                        'SMALL_SPRINTER': 75, 'LARGE_SPRINTER': 85, 'BUS': 120
                                    }
                                    price = base_prices.get(car_type_name, 50)
                                    
                                    # Create ONE_WAY rate
                                    cursor.execute("""
                                        INSERT IGNORE INTO core_rate (zone_id, car_id, travel_type, price)
                                        VALUES (%s, %s, %s, %s)
                                    """, [airport_zone_id, car_id, 'ONE_WAY', price])
                                    
                                    # Create ROUND_TRIP rate (1.5x price)
                                    cursor.execute("""
                                        INSERT IGNORE INTO core_rate (zone_id, car_id, travel_type, price)
                                        VALUES (%s, %s, %s, %s)
                                    """, [airport_zone_id, car_id, 'ROUND_TRIP', price * 1.5])
                                    
                                    self.stdout.write(f'✅ Created rates for {car_type_name} from Airport to {target_zone_name}')

        self.stdout.write('\n🎉 Database population completed!')
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  - Car Types: {CarType.objects.count()}')
        self.stdout.write(f'  - Cars: {Car.objects.count()}')
        self.stdout.write(f'  - Zones: {Zone.objects.count()}')
        self.stdout.write(f'  - Hotels: {Hotel.objects.count()}')
        self.stdout.write(f'  - Rates: {Rate.objects.count()}')
        
        self.stdout.write('\n🧪 Test Scenarios Available:')
        self.stdout.write('  - Filter by VAN: Should show 5 different VAN options')
        self.stdout.write('  - Filter by SMALL SPRINTER: Should show 3 different SMALL SPRINTER options')
        self.stdout.write('  - Filter by LARGE SPRINTER: Should show 3 different LARGE SPRINTER options')
        self.stdout.write('  - Filter by SEDAN: Should show 3 different SEDAN options')
        self.stdout.write('  - Filter by SUV: Should show 3 different SUV options')
        self.stdout.write('  - Filter by BUS: Should show 2 different BUS options')
        self.stdout.write('\n💡 Each car type now has multiple real vehicles in the database!')
