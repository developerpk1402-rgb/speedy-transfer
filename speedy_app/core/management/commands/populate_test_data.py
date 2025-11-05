from django.core.management.base import BaseCommand
from speedy_app.core.models import Zone, Hotel, Car, CarType, Rate
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate database with comprehensive test data for Fechas section testing'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Populating database with comprehensive test data...')
        
        # 1. Create/Update Car Types
        car_types_data = [
            {'code': 'VAN', 'name': 'VAN', 'description': 'Standard van for small groups', 'max_capacity': 8},
            {'code': 'SMALL_SPRINTER', 'name': 'SMALL SPRINTER', 'description': 'Small sprinter van', 'max_capacity': 12},
            {'code': 'LARGE_SPRINTER', 'name': 'LARGE SPRINTER', 'description': 'Large sprinter van', 'max_capacity': 18},
            {'code': 'SEDAN', 'name': 'SEDAN', 'description': 'Economy sedan', 'max_capacity': 4},
            {'code': 'SUV', 'name': 'SUV', 'description': 'Mid-size SUV', 'max_capacity': 6},
            {'code': 'BUS', 'name': 'BUS', 'description': 'Mini bus', 'max_capacity': 20},
        ]
        
        created_car_types = {}
        for ct_data in car_types_data:
            car_type, created = CarType.objects.get_or_create(
                code=ct_data['code'],
                defaults={
                    'name': ct_data['name'],
                    'description': ct_data['description'],
                    'max_capacity': ct_data['max_capacity']
                }
            )
            created_car_types[ct_data['code']] = car_type
            if created:
                self.stdout.write(f'✅ Created car type: {car_type.name}')
            else:
                self.stdout.write(f'ℹ️  Car type already exists: {car_type.name}')

        # 2. Create/Update Zones
        zones_data = [
            {'name': 'AEROPUERTO', 'description': 'Airport zone'},
            {'name': 'ZONA HOTELERA NORTE', 'description': 'North Hotel Zone'},
            {'name': 'ZONA HOTELERA SUR', 'description': 'South Hotel Zone'},
            {'name': 'CENTRO', 'description': 'Downtown area'},
            {'name': 'MARINA', 'description': 'Marina area'},
        ]
        
        created_zones = {}
        for zone_data in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults={'description': zone_data['description']}
            )
            created_zones[zone_data['name']] = zone
            if created:
                self.stdout.write(f'✅ Created zone: {zone.name}')
            else:
                self.stdout.write(f'ℹ️  Zone already exists: {zone.name}')

        # 3. Create/Update Hotels
        hotels_data = [
            # Airport Zone
            {'name': 'AEROPUERTO', 'zone': 'AEROPUERTO'},
            
            # North Hotel Zone
            {'name': 'HOTEL RIU PALACE PACIFIC', 'zone': 'ZONA HOTELERA NORTE'},
            {'name': 'HOTEL RIU JALISCO', 'zone': 'ZONA HOTELERA NORTE'},
            {'name': 'HOTEL CROWN PARADISE', 'zone': 'ZONA HOTELERA NORTE'},
            {'name': 'HOTEL FIESTA AMERICANA', 'zone': 'ZONA HOTELERA NORTE'},
            {'name': 'HOTEL MARRIOTT', 'zone': 'ZONA HOTELERA NORTE'},
            
            # South Hotel Zone
            {'name': 'HOTEL VELAS VALLARTA', 'zone': 'ZONA HOTELERA SUR'},
            {'name': 'HOTEL GRAND VELAS', 'zone': 'ZONA HOTELERA SUR'},
            {'name': 'HOTEL HARD ROCK', 'zone': 'ZONA HOTELERA SUR'},
            {'name': 'HOTEL WESTIN', 'zone': 'ZONA HOTELERA SUR'},
            
            # Centro
            {'name': 'HOTEL ROSITA', 'zone': 'CENTRO'},
            {'name': 'HOTEL PLAZA VALLARTA', 'zone': 'CENTRO'},
            
            # Marina
            {'name': 'HOTEL MARINA VALLARTA', 'zone': 'MARINA'},
            {'name': 'HOTEL VELAS MARINA', 'zone': 'MARINA'},
        ]
        
        created_hotels = {}
        for hotel_data in hotels_data:
            zone = created_zones[hotel_data['zone']]
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={'zone': zone}
            )
            created_hotels[hotel_data['name']] = hotel
            if created:
                self.stdout.write(f'✅ Created hotel: {hotel.name}')
            else:
                self.stdout.write(f'ℹ️  Hotel already exists: {hotel.name}')

        # 4. Create/Update Cars - Multiple cars per type for realistic testing
        cars_data = [
            # VAN cars (multiple units)
            {'name': 'VAN 001', 'car_type_code': 'VAN', 'max': 8, 'description': 'Max 9 people per vehicle'},
            {'name': 'VAN 002', 'car_type_code': 'VAN', 'max': 8, 'description': 'Max 9 people per vehicle'},
            {'name': 'VAN 003', 'car_type_code': 'VAN', 'max': 8, 'description': 'Max 9 people per vehicle'},
            {'name': 'VAN 004', 'car_type_code': 'VAN', 'max': 8, 'description': 'Max 9 people per vehicle'},
            {'name': 'VAN 005', 'car_type_code': 'VAN', 'max': 8, 'description': 'Max 9 people per vehicle'},
            
            # SMALL SPRINTER cars (multiple units)
            {'name': 'SMALL SPRINTER 001', 'car_type_code': 'SMALL_SPRINTER', 'max': 12, 'description': 'Max 11 people per vehicle'},
            {'name': 'SMALL SPRINTER 002', 'car_type_code': 'SMALL_SPRINTER', 'max': 12, 'description': 'Max 11 people per vehicle'},
            {'name': 'SMALL SPRINTER 003', 'car_type_code': 'SMALL_SPRINTER', 'max': 12, 'description': 'Max 11 people per vehicle'},
            
            # LARGE SPRINTER cars (multiple units)
            {'name': 'LARGE SPRINTER 001', 'car_type_code': 'LARGE_SPRINTER', 'max': 18, 'description': 'Max 20 people per vehicle'},
            {'name': 'LARGE SPRINTER 002', 'car_type_code': 'LARGE_SPRINTER', 'max': 18, 'description': 'Max 20 people per vehicle'},
            {'name': 'LARGE SPRINTER 003', 'car_type_code': 'LARGE_SPRINTER', 'max': 18, 'description': 'Max 20 people per vehicle'},
            
            # SEDAN cars (multiple units)
            {'name': 'SEDAN 001', 'car_type_code': 'SEDAN', 'max': 4, 'description': 'Economy sedan for small groups'},
            {'name': 'SEDAN 002', 'car_type_code': 'SEDAN', 'max': 4, 'description': 'Economy sedan for small groups'},
            {'name': 'SEDAN 003', 'car_type_code': 'SEDAN', 'max': 4, 'description': 'Economy sedan for small groups'},
            
            # SUV cars (multiple units)
            {'name': 'SUV 001', 'car_type_code': 'SUV', 'max': 6, 'description': 'Mid-size SUV for small groups'},
            {'name': 'SUV 002', 'car_type_code': 'SUV', 'max': 6, 'description': 'Mid-size SUV for small groups'},
            {'name': 'SUV 003', 'car_type_code': 'SUV', 'max': 6, 'description': 'Mid-size SUV for small groups'},
            
            # BUS cars (multiple units)
            {'name': 'BUS 001', 'car_type_code': 'BUS', 'max': 20, 'description': 'Mini bus for large groups'},
            {'name': 'BUS 002', 'car_type_code': 'BUS', 'max': 20, 'description': 'Mini bus for large groups'},
        ]
        
        created_cars = {}
        for car_data in cars_data:
            car_type = created_car_types[car_data['car_type_code']]
            car, created = Car.objects.get_or_create(
                name=car_data['name'],
                defaults={
                    'car_type': car_type,
                    'max': car_data['max'],
                    'description': car_data['description']
                }
            )
            created_cars[car_data['name']] = car
            if created:
                self.stdout.write(f'✅ Created car: {car.name}')
            else:
                self.stdout.write(f'ℹ️  Car already exists: {car.name}')

        # 5. Create/Update Rates - Comprehensive pricing for all combinations
        rates_data = []
        
        # Define pricing structure
        pricing = {
            'AEROPUERTO': {
                'ZONA HOTELERA NORTE': {
                    'SEDAN': {'ONE_WAY': 45, 'ROUND_TRIP': 80},
                    'SUV': {'ONE_WAY': 55, 'ROUND_TRIP': 95},
                    'VAN': {'ONE_WAY': 65, 'ROUND_TRIP': 110},
                    'SMALL_SPRINTER': {'ONE_WAY': 75, 'ROUND_TRIP': 125},
                    'LARGE_SPRINTER': {'ONE_WAY': 85, 'ROUND_TRIP': 140},
                    'BUS': {'ONE_WAY': 120, 'ROUND_TRIP': 200},
                },
                'ZONA HOTELERA SUR': {
                    'SEDAN': {'ONE_WAY': 50, 'ROUND_TRIP': 85},
                    'SUV': {'ONE_WAY': 60, 'ROUND_TRIP': 100},
                    'VAN': {'ONE_WAY': 70, 'ROUND_TRIP': 115},
                    'SMALL_SPRINTER': {'ONE_WAY': 80, 'ROUND_TRIP': 130},
                    'LARGE_SPRINTER': {'ONE_WAY': 90, 'ROUND_TRIP': 145},
                    'BUS': {'ONE_WAY': 125, 'ROUND_TRIP': 205},
                },
                'CENTRO': {
                    'SEDAN': {'ONE_WAY': 40, 'ROUND_TRIP': 70},
                    'SUV': {'ONE_WAY': 50, 'ROUND_TRIP': 85},
                    'VAN': {'ONE_WAY': 60, 'ROUND_TRIP': 100},
                    'SMALL_SPRINTER': {'ONE_WAY': 70, 'ROUND_TRIP': 115},
                    'LARGE_SPRINTER': {'ONE_WAY': 80, 'ROUND_TRIP': 130},
                    'BUS': {'ONE_WAY': 110, 'ROUND_TRIP': 185},
                },
                'MARINA': {
                    'SEDAN': {'ONE_WAY': 35, 'ROUND_TRIP': 65},
                    'SUV': {'ONE_WAY': 45, 'ROUND_TRIP': 80},
                    'VAN': {'ONE_WAY': 55, 'ROUND_TRIP': 95},
                    'SMALL_SPRINTER': {'ONE_WAY': 65, 'ROUND_TRIP': 110},
                    'LARGE_SPRINTER': {'ONE_WAY': 75, 'ROUND_TRIP': 125},
                    'BUS': {'ONE_WAY': 100, 'ROUND_TRIP': 175},
                },
            }
        }
        
        # Create rates for each car type and zone combination
        for zone_name, zone_pricing in pricing.items():
            zone = created_zones[zone_name]
            
            for target_zone_name, car_pricing in zone_pricing.items():
                target_zone = created_zones[target_zone_name]
                
                for car_type_code, travel_pricing in car_pricing.items():
                    car_type = created_car_types[car_type_code]
                    
                    # Get the first car of this type for the rate
                    car = Car.objects.filter(car_type=car_type).first()
                    if not car:
                        self.stdout.write(f'⚠️  No car found for type {car_type_code}')
                        continue
                    
                    for travel_type, price in travel_pricing.items():
                        rate, created = Rate.objects.get_or_create(
                            zone=zone,
                            car=car,
                            travel_type=travel_type,
                            defaults={'price': Decimal(str(price))}
                        )
                        if created:
                            self.stdout.write(f'✅ Created rate: {zone.name} -> {target_zone.name} - {car.name} ({travel_type}): ${price}')
                        else:
                            self.stdout.write(f'ℹ️  Rate already exists: {zone.name} -> {target_zone.name} - {car.name} ({travel_type}): ${price}')

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
