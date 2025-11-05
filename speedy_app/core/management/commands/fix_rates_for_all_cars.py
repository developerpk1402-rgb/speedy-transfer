from django.core.management.base import BaseCommand
from django.db import connection
from speedy_app.core.models import Car, CarType, Rate, Zone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create rates for ALL cars of each type, not just the first one'

    def handle(self, *args, **options):
        self.stdout.write('🔄 Creating rates for ALL cars of each type...')
        
        with connection.cursor() as cursor:
            # Get all zones
            cursor.execute("SELECT id, name FROM core_zone")
            zones = {name: id for id, name in cursor.fetchall()}
            
            # Get all car types
            cursor.execute("SELECT id, code FROM core_cartype")
            car_types = {code: id for id, code in cursor.fetchall()}
            
            # Define pricing structure
            pricing = {
                'SEDAN': 45,
                'SUV': 55, 
                'VAN': 65,
                'SMALL_SPRINTER': 75,
                'LARGE_SPRINTER': 85,
                'BUS': 120,
            }
            
            # Get airport zone
            airport_zone_id = zones.get('AEROPUERTO')
            if not airport_zone_id:
                self.stdout.write('❌ Airport zone not found')
                return
            
            # For each car type, create rates for ALL cars of that type
            for car_type_code, car_type_id in car_types.items():
                if car_type_code not in pricing:
                    continue
                    
                base_price = pricing[car_type_code]
                
                # Get ALL cars of this type
                cursor.execute("SELECT id, name FROM core_car WHERE car_type_id = %s", [car_type_id])
                cars = cursor.fetchall()
                
                self.stdout.write(f'\n🚗 Processing {car_type_code}: {len(cars)} cars')
                
                for car_id, car_name in cars:
                    self.stdout.write(f'  📝 Creating rates for {car_name}')
                    
                    # Create rates for each target zone
                    for target_zone_name in ['ZONA HOTELERA NORTE', 'ZONA HOTELERA SUR', 'CENTRO', 'MARINA']:
                        target_zone_id = zones.get(target_zone_name)
                        if target_zone_id:
                            # Create ONE_WAY rate
                            cursor.execute("""
                                INSERT IGNORE INTO core_rate (zone_id, car_id, travel_type, price)
                                VALUES (%s, %s, %s, %s)
                            """, [airport_zone_id, car_id, 'ONE_WAY', base_price])
                            
                            # Create ROUND_TRIP rate (1.5x price)
                            cursor.execute("""
                                INSERT IGNORE INTO core_rate (zone_id, car_id, travel_type, price)
                                VALUES (%s, %s, %s, %s)
                            """, [airport_zone_id, car_id, 'ROUND_TRIP', base_price * 1.5])
                            
                            self.stdout.write(f'    ✅ Created rates for {car_name} to {target_zone_name}')

        self.stdout.write('\n🎉 Rate creation completed!')
        
        # Show summary
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM core_rate")
            total_rates = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT ct.code, COUNT(DISTINCT c.id) as car_count, COUNT(r.id) as rate_count
                FROM core_cartype ct
                LEFT JOIN core_car c ON ct.id = c.car_type_id
                LEFT JOIN core_rate r ON c.id = r.car_id
                GROUP BY ct.id, ct.code
                ORDER BY ct.code
            """)
            
            self.stdout.write(f'\n📊 Summary:')
            self.stdout.write(f'  Total rates: {total_rates}')
            self.stdout.write(f'  Rates per car type:')
            
            for car_type_code, car_count, rate_count in cursor.fetchall():
                self.stdout.write(f'    {car_type_code}: {car_count} cars, {rate_count} rates')
