from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Force fix database structure by recreating tables'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Force fixing database structure...')
        
        cursor = connection.cursor()
        
        # 1. Check current state
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        
        self.stdout.write(f"Current tables: {table_names}")
        
        # 2. Create core_cartype table if it doesn't exist
        if 'core_cartype' not in table_names:
            self.stdout.write("Creating core_cartype table...")
            cursor.execute("""
                CREATE TABLE core_cartype (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    code varchar(10) NOT NULL UNIQUE,
                    name varchar(50) NOT NULL,
                    description text NULL,
                    max_capacity integer unsigned NOT NULL DEFAULT 1
                )
            """)
            
            # Insert car types
            car_types = [
                ('SEDAN', 'Sedan', 'Economy sedan car', 4),
                ('SUV', 'SUV', 'Mid-size SUV', 6),
                ('VAN', 'Van', 'Standard van', 8),
                ('SPRINTER', 'Sprinter', 'Large sprinter van', 12),
                ('BUS', 'Bus', 'Mini bus', 20),
            ]
            
            for code, name, description, max_capacity in car_types:
                cursor.execute(
                    "INSERT INTO core_cartype (code, name, description, max_capacity) VALUES (?, ?, ?, ?)",
                    (code, name, description, max_capacity)
                )
            
            self.stdout.write("✅ core_cartype table created with data")
        else:
            self.stdout.write("✅ core_cartype table already exists")
        
        # 3. Fix core_car table
        if 'core_car' in table_names:
            # Check current structure
            cursor.execute("PRAGMA table_info(core_car)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            self.stdout.write(f"Current core_car columns: {column_names}")
            
            if 'car_type_id' not in column_names:
                self.stdout.write("car_type_id column missing. Recreating core_car table...")
                
                # Backup existing data
                cursor.execute("SELECT * FROM core_car")
                existing_cars = cursor.fetchall()
                self.stdout.write(f"Found {len(existing_cars)} existing cars to preserve")
                
                # Drop and recreate table
                cursor.execute("DROP TABLE core_car")
                
                cursor.execute("""
                    CREATE TABLE core_car (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name varchar(50) NOT NULL,
                        description TEXT NULL,
                        image varchar(100) NULL,
                        max integer unsigned NOT NULL DEFAULT 1,
                        car_type_id bigint NOT NULL REFERENCES core_cartype(id)
                    )
                """)
                
                # Get VAN type ID
                cursor.execute("SELECT id FROM core_cartype WHERE code = 'VAN'")
                van_id = cursor.fetchone()[0]
                
                # Restore cars with VAN type
                for car_data in existing_cars:
                    car_id, name, description, image, max_capacity = car_data[:5]
                    cursor.execute(
                        "INSERT INTO core_car (id, name, description, image, max, car_type_id) VALUES (?, ?, ?, ?, ?, ?)",
                        (car_id, name, description, image, max_capacity, van_id)
                    )
                
                self.stdout.write("✅ core_car table recreated with car_type_id column")
            else:
                self.stdout.write("✅ car_type_id column already exists")
        else:
            self.stdout.write("❌ core_car table does not exist - this is unexpected")
        
        # 4. Verify final structure
        cursor.execute("PRAGMA table_info(core_car)")
        columns = cursor.fetchall()
        
        self.stdout.write(f"\n📊 Final core_car structure:")
        for col in columns:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            pk = " (PRIMARY KEY)" if col[5] == 1 else ""
            self.stdout.write(f"  - {col[1]} ({col[2]}) {nullable}{pk}")
        
        # 5. Test the fix
        try:
            cursor.execute("SELECT COUNT(*) FROM core_car")
            car_count = cursor.fetchone()[0]
            self.stdout.write(f"\n✅ Test query successful. Cars in database: {car_count}")
        except Exception as e:
            self.stdout.write(f"\n❌ Test query failed: {e}")
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Database structure force fixed!')
        )
