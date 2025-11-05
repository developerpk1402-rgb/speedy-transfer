from django.core.management.base import BaseCommand
from speedy_app.core.models import Zone, Hotel, Car, CarType, Rate


class Command(BaseCommand):
    help = 'Restore expanded hotels and car types that were lost during migration'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Restoring expanded data...')
        
        # 1. Create expanded CarTypes
        expanded_car_types = [
            {'code': 'SEDAN', 'name': 'Sedan', 'description': 'Economy sedan car', 'max_capacity': 4},
            {'code': 'SUV', 'name': 'SUV', 'description': 'Mid-size SUV', 'max_capacity': 6},
            {'code': 'VAN', 'name': 'Van', 'description': 'Standard van', 'max_capacity': 8},
            {'code': 'SPRINTER', 'name': 'Sprinter', 'description': 'Large sprinter van', 'max_capacity': 12},
            {'code': 'BUS', 'name': 'Bus', 'description': 'Mini bus', 'max_capacity': 20},
            {'code': 'LUXURY_SEDAN', 'name': 'Luxury Sedan', 'description': 'Premium sedan with luxury features', 'max_capacity': 4},
            {'code': 'LUXURY_SUV', 'name': 'Luxury SUV', 'description': 'Premium SUV with luxury amenities', 'max_capacity': 6},
            {'code': 'LUXURY_VAN', 'name': 'Luxury Van', 'description': 'Premium van with luxury features', 'max_capacity': 8},
            {'code': 'LUXURY_SPRINTER', 'name': 'Luxury Sprinter', 'description': 'Premium sprinter with luxury amenities', 'max_capacity': 12},
            {'code': 'LUXURY_BUS', 'name': 'Luxury Bus', 'description': 'Premium mini bus with luxury features', 'max_capacity': 20},
            {'code': 'EXECUTIVE_SPRINTER', 'name': 'Executive Sprinter', 'description': 'Executive class sprinter for business', 'max_capacity': 12},
            {'code': 'PARTY_BUS', 'name': 'Party Bus', 'description': 'Entertainment bus for parties and events', 'max_capacity': 25},
            {'code': 'TOUR_BUS', 'name': 'Tour Bus', 'description': 'Comfortable bus for tours and groups', 'max_capacity': 30},
            {'code': 'LUXURY_LIMOUSINE', 'name': 'Luxury Limousine', 'description': 'Premium limousine service', 'max_capacity': 8},
            {'code': 'STRETCH_LIMOUSINE', 'name': 'Stretch Limousine', 'description': 'Extended limousine for special occasions', 'max_capacity': 10},
            {'code': 'HUMMER_LIMO', 'name': 'Hummer Limousine', 'description': 'Luxury Hummer limousine', 'max_capacity': 12},
            {'code': 'CHARTER_BUS', 'name': 'Charter Bus', 'description': 'Large charter bus for groups', 'max_capacity': 50},
        ]
        
        created_car_types = {}
        for type_data in expanded_car_types:
            car_type, created = CarType.objects.get_or_create(
                code=type_data['code'],
                defaults=type_data
            )
            created_car_types[type_data['code']] = car_type
            if created:
                self.stdout.write(f'✅ Created CarType: {car_type.name}')
            else:
                self.stdout.write(f'ℹ️  CarType already exists: {car_type.name}')
        
        # 2. Create expanded zones
        expanded_zones = [
            {'name': 'Puerto Vallarta', 'description': 'Main tourist area with beaches and nightlife'},
            {'name': 'Nuevo Vallarta', 'description': 'Resort area with luxury hotels'},
            {'name': 'Bucerias', 'description': 'Charming beach town with local culture'},
            {'name': 'Punta Mita', 'description': 'Exclusive resort area with luxury properties'},
            {'name': 'Sayulita', 'description': 'Surf town with bohemian vibe'},
            {'name': 'San Pancho', 'description': 'Quiet beach town perfect for relaxation'},
            {'name': 'Riviera Nayarit', 'description': 'Coastal region with multiple destinations'},
            {'name': 'Airport Zone', 'description': 'Puerto Vallarta International Airport area'},
        ]
        
        created_zones = {}
        for zone_data in expanded_zones:
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            created_zones[zone_data['name']] = zone
            if created:
                self.stdout.write(f'✅ Created zone: {zone.name}')
            else:
                self.stdout.write(f'ℹ️  Zone already exists: {zone.name}')
        
        # 3. Create expanded hotels
        expanded_hotels = [
            # Puerto Vallarta
            {'name': 'Hotel Marriott Puerto Vallarta', 'zone': 'Puerto Vallarta'},
            {'name': 'Hotel Riu Palace Pacifico', 'zone': 'Puerto Vallarta'},
            {'name': 'Casa Velas', 'zone': 'Puerto Vallarta'},
            {'name': 'Garza Blanca Preserve Resort', 'zone': 'Puerto Vallarta'},
            {'name': 'Villa del Palmar Beach Resort', 'zone': 'Puerto Vallarta'},
            {'name': 'Hyatt Ziva Puerto Vallarta', 'zone': 'Puerto Vallarta'},
            {'name': 'Secrets Vallarta Bay', 'zone': 'Puerto Vallarta'},
            {'name': 'Now Amber Puerto Vallarta', 'zone': 'Puerto Vallarta'},
            {'name': 'Dreams Puerto Vallarta', 'zone': 'Puerto Vallarta'},
            {'name': 'Villa Premiere Boutique Hotel', 'zone': 'Puerto Vallarta'},
            
            # Nuevo Vallarta
            {'name': 'Grand Velas Riviera Nayarit', 'zone': 'Nuevo Vallarta'},
            {'name': 'Marival Residences Luxury Resort', 'zone': 'Nuevo Vallarta'},
            {'name': 'Hard Rock Hotel Vallarta', 'zone': 'Nuevo Vallarta'},
            {'name': 'Paradisus Playa Mujeres', 'zone': 'Nuevo Vallarta'},
            {'name': 'Secrets Bahia Mita', 'zone': 'Nuevo Vallarta'},
            {'name': 'Now Jade Riviera Cancun', 'zone': 'Nuevo Vallarta'},
            {'name': 'Dreams Riviera Cancun', 'zone': 'Nuevo Vallarta'},
            {'name': 'Hyatt Ziva Riviera Cancun', 'zone': 'Nuevo Vallarta'},
            {'name': 'Valentin Imperial Riviera Maya', 'zone': 'Nuevo Vallarta'},
            {'name': 'Excellence Riviera Cancun', 'zone': 'Nuevo Vallarta'},
            
            # Bucerias
            {'name': 'Barceló Bucerías', 'zone': 'Bucerias'},
            {'name': 'Hotel Villa del Palmar Flamingos', 'zone': 'Bucerias'},
            {'name': 'Casa de Mita', 'zone': 'Bucerias'},
            {'name': 'Hotel Mousai', 'zone': 'Bucerias'},
            {'name': 'Villa La Estancia Riviera Nayarit', 'zone': 'Bucerias'},
            {'name': 'Marival Residences Luxury Resort', 'zone': 'Bucerias'},
            {'name': 'Grand Velas Riviera Nayarit', 'zone': 'Bucerias'},
            {'name': 'Hard Rock Hotel Vallarta', 'zone': 'Bucerias'},
            
            # Punta Mita
            {'name': 'Four Seasons Resort Punta Mita', 'zone': 'Punta Mita'},
            {'name': 'St. Regis Punta Mita Resort', 'zone': 'Punta Mita'},
            {'name': 'W Punta de Mita', 'zone': 'Punta Mita'},
            {'name': 'Conrad Punta de Mita', 'zone': 'Punta Mita'},
            {'name': 'Punta Mita Golf Club', 'zone': 'Punta Mita'},
            
            # Sayulita
            {'name': 'Hotel Playa Escondida', 'zone': 'Sayulita'},
            {'name': 'Villa Amor', 'zone': 'Sayulita'},
            {'name': 'Hotelito Los Sueños', 'zone': 'Sayulita'},
            {'name': 'Casa de los Sueños', 'zone': 'Sayulita'},
            {'name': 'Hotelito Casa Escondida', 'zone': 'Sayulita'},
            
            # San Pancho
            {'name': 'Hotel Cielo Rojo', 'zone': 'San Pancho'},
            {'name': 'Casa Obelisco', 'zone': 'San Pancho'},
            {'name': 'Hotel La Perla', 'zone': 'San Pancho'},
            {'name': 'Casa San Pancho', 'zone': 'San Pancho'},
            
            # Airport Zone
            {'name': 'Puerto Vallarta International Airport', 'zone': 'Airport Zone'},
            {'name': 'Hotel Aeropuerto', 'zone': 'Airport Zone'},
            {'name': 'Fiesta Inn Aeropuerto', 'zone': 'Airport Zone'},
        ]
        
        for hotel_data in expanded_hotels:
            zone = created_zones[hotel_data['zone']]
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                defaults={'zone': zone}
            )
            if created:
                self.stdout.write(f'✅ Created hotel: {hotel.name}')
            else:
                self.stdout.write(f'ℹ️  Hotel already exists: {hotel.name}')
        
        # 4. Create expanded cars
        expanded_cars = [
            # Economy/Standard vehicles
            {'name': 'Economy Sedan', 'car_type_code': 'SEDAN', 'max': 4, 'description': 'Basic sedan for budget-conscious travelers'},
            {'name': 'Standard SUV', 'car_type_code': 'SUV', 'max': 6, 'description': 'Reliable SUV for small groups'},
            {'name': 'Comfort Van', 'car_type_code': 'VAN', 'max': 8, 'description': 'Standard van with comfortable seating'},
            {'name': 'Standard Sprinter', 'car_type_code': 'SPRINTER', 'max': 12, 'description': 'Large van for medium groups'},
            {'name': 'Group Bus', 'car_type_code': 'BUS', 'max': 20, 'description': 'Mini bus for large groups'},
            
            # Luxury vehicles
            {'name': 'Luxury Sedan', 'car_type_code': 'LUXURY_SEDAN', 'max': 4, 'description': 'Premium sedan with luxury amenities'},
            {'name': 'Luxury SUV', 'car_type_code': 'LUXURY_SUV', 'max': 6, 'description': 'High-end SUV with premium features'},
            {'name': 'Luxury Van', 'car_type_code': 'LUXURY_VAN', 'max': 8, 'description': 'Premium van with luxury seating'},
            {'name': 'Luxury Sprinter', 'car_type_code': 'LUXURY_SPRINTER', 'max': 12, 'description': 'Premium sprinter with luxury amenities'},
            {'name': 'Luxury Bus', 'car_type_code': 'LUXURY_BUS', 'max': 20, 'description': 'Premium mini bus with luxury features'},
            
            # Special vehicles
            {'name': 'Executive Sprinter', 'car_type_code': 'EXECUTIVE_SPRINTER', 'max': 12, 'description': 'Business class sprinter for executives'},
            {'name': 'Party Bus', 'car_type_code': 'PARTY_BUS', 'max': 25, 'description': 'Entertainment bus with party features'},
            {'name': 'Tour Bus', 'car_type_code': 'TOUR_BUS', 'max': 30, 'description': 'Comfortable bus for sightseeing tours'},
            {'name': 'Luxury Limousine', 'car_type_code': 'LUXURY_LIMOUSINE', 'max': 8, 'description': 'Premium limousine service'},
            {'name': 'Stretch Limousine', 'car_type_code': 'STRETCH_LIMOUSINE', 'max': 10, 'description': 'Extended limousine for special occasions'},
            {'name': 'Hummer Limousine', 'car_type_code': 'HUMMER_LIMO', 'max': 12, 'description': 'Luxury Hummer limousine'},
            {'name': 'Charter Bus', 'car_type_code': 'CHARTER_BUS', 'max': 50, 'description': 'Large charter bus for big groups'},
        ]
        
        created_cars = {}
        for car_data in expanded_cars:
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
        
        # 5. Create sample rates for each zone and car type
        self.stdout.write('\n💰 Creating sample rates...')
        
        # Base prices for different car types
        base_prices = {
            'SEDAN': {'one_way': 80, 'round_trip': 150},
            'SUV': {'one_way': 100, 'round_trip': 180},
            'VAN': {'one_way': 120, 'round_trip': 220},
            'SPRINTER': {'one_way': 150, 'round_trip': 280},
            'BUS': {'one_way': 200, 'round_trip': 380},
            'LUXURY_SEDAN': {'one_way': 120, 'round_trip': 220},
            'LUXURY_SUV': {'one_way': 150, 'round_trip': 280},
            'LUXURY_VAN': {'one_way': 180, 'round_trip': 320},
            'LUXURY_SPRINTER': {'one_way': 220, 'round_trip': 400},
            'LUXURY_BUS': {'one_way': 280, 'round_trip': 520},
            'EXECUTIVE_SPRINTER': {'one_way': 250, 'round_trip': 450},
            'PARTY_BUS': {'one_way': 350, 'round_trip': 650},
            'TOUR_BUS': {'one_way': 300, 'round_trip': 550},
            'LUXURY_LIMOUSINE': {'one_way': 200, 'round_trip': 380},
            'STRETCH_LIMOUSINE': {'one_way': 250, 'round_trip': 450},
            'HUMMER_LIMO': {'one_way': 300, 'round_trip': 550},
            'CHARTER_BUS': {'one_way': 400, 'round_trip': 750},
        }
        
        rates_created = 0
        for zone in created_zones.values():
            for car in created_cars.values():
                car_type_code = car.car_type.code
                if car_type_code in base_prices:
                    prices = base_prices[car_type_code]
                    
                    # One way rate
                    rate, created = Rate.objects.get_or_create(
                        zone=zone,
                        car=car,
                        travel_type='ONE_WAY',
                        defaults={'price': prices['one_way']}
                    )
                    if created:
                        rates_created += 1
                    
                    # Round trip rate
                    rate, created = Rate.objects.get_or_create(
                        zone=zone,
                        car=car,
                        travel_type='ROUND_TRIP',
                        defaults={'price': prices['round_trip']}
                    )
                    if created:
                        rates_created += 1
        
        self.stdout.write(f'✅ Created {rates_created} rates')
        
        # 6. Summary
        self.stdout.write('\n📊 Summary:')
        self.stdout.write(f'  - Car Types: {CarType.objects.count()}')
        self.stdout.write(f'  - Zones: {Zone.objects.count()}')
        self.stdout.write(f'  - Hotels: {Hotel.objects.count()}')
        self.stdout.write(f'  - Cars: {Car.objects.count()}')
        self.stdout.write(f'  - Rates: {Rate.objects.count()}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Expanded data restored successfully!')
        )
