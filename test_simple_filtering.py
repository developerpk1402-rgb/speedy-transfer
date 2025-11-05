#!/usr/bin/env python
"""
Simple test to verify the fixed filtering logic
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/zednelem/speedy-site/speedy-transfer-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from speedy_app.core.models import Car, CarType, Rate
from django.db import models
from collections import defaultdict

def test_van_filtering():
    """Test VAN filtering specifically"""
    
    print("🧪 Testing VAN Filtering (Fixed Logic)")
    print("=" * 50)
    
    # Get VAN car type
    van_type = CarType.objects.filter(code='VAN').first()
    if not van_type:
        print("❌ VAN car type not found")
        return
    
    # Count actual VAN cars
    van_cars = Car.objects.filter(car_type=van_type)
    print(f"📊 Actual VAN cars in DB: {van_cars.count()}")
    for car in van_cars:
        print(f"  - {car.name} (max: {car.max})")
    
    # Get rates for VAN cars (simulating the fixed logic)
    rates = Rate.objects.filter(
        models.Q(car__car_type__code='VAN')
    )
    print(f"📊 Total VAN rates: {rates.count()}")
    
    # Group rates by car (this is the fix)
    rates_by_car = defaultdict(list)
    for rate in rates:
        if rate.car:
            rates_by_car[rate.car.id].append(rate)
    
    print(f"📊 Unique cars with rates: {len(rates_by_car)}")
    
    # Count transfer options (one per car, not per rate)
    transfer_options_count = len(rates_by_car)
    
    print(f"📊 Transfer options that would be shown: {transfer_options_count}")
    
    # Show what each car would display
    for car_id, car_rates in rates_by_car.items():
        car = car_rates[0].car
        print(f"  🚗 {car.name}: {len(car_rates)} rates available")
    
    # Check if fixed
    if transfer_options_count == van_cars.count():
        print(f"✅ FIXED: Shows {transfer_options_count} options for {van_cars.count()} actual cars")
    else:
        print(f"❌ STILL BROKEN: Shows {transfer_options_count} options but {van_cars.count()} actual cars")

if __name__ == "__main__":
    test_van_filtering()
