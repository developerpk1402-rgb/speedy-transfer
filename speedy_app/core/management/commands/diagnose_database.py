from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Diagnose database structure issues'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Diagnosing database structure...')
        
        cursor = connection.cursor()
        
        # 1. Check all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        self.stdout.write(f"\n📋 Tables in database:")
        for table in tables:
            self.stdout.write(f"  - {table[0]}")
        
        # 2. Check if core_car table exists
        if ('core_car',) in tables:
            self.stdout.write(f"\n✅ core_car table exists")
            
            # Check core_car structure
            cursor.execute("PRAGMA table_info(core_car)")
            columns = cursor.fetchall()
            
            self.stdout.write(f"\n📊 core_car table structure:")
            for col in columns:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                pk = " (PRIMARY KEY)" if col[5] == 1 else ""
                self.stdout.write(f"  - {col[1]} ({col[2]}) {nullable}{pk}")
            
            # Check if car_type_id exists
            column_names = [col[1] for col in columns]
            if 'car_type_id' in column_names:
                self.stdout.write(f"\n✅ car_type_id column exists")
            else:
                self.stdout.write(f"\n❌ car_type_id column MISSING")
                
        else:
            self.stdout.write(f"\n❌ core_car table does NOT exist")
        
        # 3. Check if core_cartype table exists
        if ('core_cartype',) in tables:
            self.stdout.write(f"\n✅ core_cartype table exists")
            
            # Check core_cartype structure
            cursor.execute("PRAGMA table_info(core_cartype)")
            columns = cursor.fetchall()
            
            self.stdout.write(f"\n📊 core_cartype table structure:")
            for col in columns:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                pk = " (PRIMARY KEY)" if col[5] == 1 else ""
                self.stdout.write(f"  - {col[1]} ({col[2]}) {nullable}{pk}")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM core_cartype")
            count = cursor.fetchone()[0]
            self.stdout.write(f"\n📈 Records in core_cartype: {count}")
            
            if count > 0:
                cursor.execute("SELECT code, name FROM core_cartype")
                types = cursor.fetchall()
                self.stdout.write(f"   Types available:")
                for code, name in types:
                    self.stdout.write(f"     - {code}: {name}")
        else:
            self.stdout.write(f"\n❌ core_cartype table does NOT exist")
        
        # 4. Check Django migrations
        cursor.execute("SELECT app, name FROM django_migrations WHERE app = 'core' ORDER BY id")
        migrations = cursor.fetchall()
        
        self.stdout.write(f"\n📦 Applied core migrations:")
        for app, name in migrations:
            self.stdout.write(f"  - {name}")
        
        # 5. Check if there are any cars
        if ('core_car',) in tables:
            cursor.execute("SELECT COUNT(*) FROM core_car")
            car_count = cursor.fetchone()[0]
            self.stdout.write(f"\n🚗 Cars in database: {car_count}")
            
            if car_count > 0:
                cursor.execute("SELECT id, name FROM core_car LIMIT 5")
                cars = cursor.fetchall()
                self.stdout.write(f"   Sample cars:")
                for car_id, name in cars:
                    self.stdout.write(f"     - {car_id}: {name}")
        
        self.stdout.write(f"\n" + "="*50)
        self.stdout.write(f"🎯 DIAGNOSIS COMPLETE")
        self.stdout.write(f"="*50)
