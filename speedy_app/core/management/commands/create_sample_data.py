from django.core.management.base import BaseCommand
from speedy_app.core.models import Zone, Hotel, Car, CarType, Rate


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # 1. Create CarTypes first
        car_types_data = [
            {'code': 'SEDAN', 'name': 'Sedan', 'description': 'Economy sedan car', 'max_capacity': 4},
            {'code': 'SUV', 'name': 'SUV', 'description': 'Mid-size SUV', 'max_capacity': 6},
            {'code': 'VAN', 'name': 'Van', 'description': 'Standard van', 'max_capacity': 8},
            {'code': 'SPRINTER', 'name': 'Sprinter', 'description': 'Large sprinter van', 'max_capacity': 12},
            {'code': 'BUS', 'name': 'Bus', 'description': 'Mini bus', 'max_capacity': 20},
        ]
        
        for type_data in car_types_data:
            car_type, created = CarType.objects.get_or_create(
                code=type_data['code'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'✅ Created CarType: {car_type.name}')
            else:
                self.stdout.write(f'ℹ️  CarType already exists: {car_type.name}')
        
        # 2. Create zones
        zones_data = [
            {'name': 'Puerto Vallarta', 'description': 'Main tourist area'},
            {'name': 'Nuevo Vallarta', 'description': 'Resort area'},
            {'name': 'Bucerias', 'description': 'Beach town'},
        ]
        
        created_zones = {}
        for zone_data in zones_data:
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            created_zones[zone_data['name']] = zone
            if created:
                self.stdout.write(f'✅ Created zone: {zone.name}')
            else:
                self.stdout.write(f'ℹ️  Zone already exists: {zone.name}')
        
        # 3. Create hotels
        hotels_data = [
            {'name': 'Hotel Marriott', 'zone': 'Puerto Vallarta'},
            {'name': 'Grand Velas', 'zone': 'Nuevo Vallarta'},
            {'name': 'Barceló', 'zone': 'Bucerias'},
            {'name': 'Hotel Riu', 'zone': 'Puerto Vallarta'},
        ]
        
        for hotel_data in hotels_data:
            zone = created_zones[hotel_data['zone']]
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={'zone': zone}
            )
            if created:
                self.stdout.write(f'✅ Created hotel: {hotel.name}')
            else:
                self.stdout.write(f'ℹ️  Hotel already exists: {hotel.name}')
        
        # 4. Create cars
        cars_data = [
            {'name': 'Economy Sedan', 'car_type_code': 'SEDAN', 'max': 4},
            {'name': 'Standard SUV', 'car_type_code': 'SUV', 'max': 6},
            {'name': 'Comfort Van', 'car_type_code': 'VAN', 'max': 8},
            {'name': 'Luxury Sprinter', 'car_type_code': 'SPRINTER', 'max': 12},
            {'name': 'Group Bus', 'car_type_code': 'BUS', 'max': 20},
        ]
        
        created_cars = {}
        for car_data in cars_data:
            car_type = CarType.objects.get(code=car_data['car_type_code'])
            car, created = Car.objects.get_or_create(
                name=car_data['name'],
                defaults={
                    'car_type': car_type,
                    'max': car_data['max']
                }
            )
            created_cars[car_data['name']] = car
            if created:
                self.stdout.write(f'✅ Created car: {car.name} ({car.car_type.name})')
            else:
                self.stdout.write(f'ℹ️  Car already exists: {car.name}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Sample data created successfully!')
        )
        
        # Summary
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'  - CarTypes: {CarType.objects.count()}')
        self.stdout.write(f'  - Zones: {Zone.objects.count()}')
        self.stdout.write(f'  - Hotels: {Hotel.objects.count()}')
        self.stdout.write(f'  - Cars: {Car.objects.count()}')
