#!/usr/bin/env python
"""
Test script to verify Fechas section filtering by car type.
This script simulates the filtering logic from the ResultsView to ensure
that each car type shows the correct number of real vehicles from the database.
"""

import os
import sys
import django

# Setup Django
sys.path.append('/Users/zednelem/speedy-site/speedy-transfer-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
django.setup()

from speedy_app.core.models import Car, CarType, Hotel, Rate, Zone
from django.db import models


def test_car_type_filtering():
    """Test the car type filtering logic from ResultsView"""
    
    print("🧪 Testing Fechas Section Car Type Filtering")
    print("=" * 50)
    
    # Get all car types
    car_types = CarType.objects.all()
    print(f"Found {car_types.count()} car types in database")
    
    # Test each car type
    for car_type in car_types:
        print(f"\n🔍 Testing Car Type: {car_type.code} ({car_type.name})")
        print("-" * 30)
        
        # Count actual cars of this type in database
        actual_cars = Car.objects.filter(car_type=car_type)
        print(f"  📊 Actual cars in DB: {actual_cars.count()}")
        for car in actual_cars:
            print(f"    - {car.name} (max: {car.max})")
        
        # Simulate the filtering logic from ResultsView
        # This is the same logic used in lines 206-211 of views.py
        rates = Rate.objects.filter(
            models.Q(car__car_type__code=car_type.code)
        )
        
        print(f"  📊 Rates found: {rates.count()}")
        
        # Count unique cars in rates
        unique_cars_in_rates = set()
        for rate in rates:
            if rate.car:
                unique_cars_in_rates.add(rate.car.id)
        
        print(f"  📊 Unique cars in rates: {len(unique_cars_in_rates)}")
        
        # Simulate the transfer options generation (lines 355-377 in views.py)
        transfer_options = []
        for rate in rates:
            car = rate.car
            if car:
                # Create one transfer option per rate (simplified version)
                transfer_options.append({
                    'id': f"{rate.id}",
                    'car_name': car.name,
                    'car_capacity': car.max,
                    'price': rate.price,
                    'travel_type': rate.travel_type,
                })
        
        print(f"  📊 Transfer options generated: {len(transfer_options)}")
        
        # Show what would be displayed to user
        if transfer_options:
            print(f"  🎯 What user would see:")
            for i, option in enumerate(transfer_options[:5], 1):  # Show first 5
                print(f"    {i}. {option['car_name']} - Max {option['car_capacity']} people - ${option['price']} ({option['travel_type']})")
            if len(transfer_options) > 5:
                print(f"    ... and {len(transfer_options) - 5} more options")
        else:
            print(f"  ❌ No transfer options would be shown to user")
        
        # Check if the issue is resolved
        if len(transfer_options) == actual_cars.count():
            print(f"  ✅ CORRECT: Shows {len(transfer_options)} options for {actual_cars.count()} actual cars")
        else:
            print(f"  ⚠️  ISSUE: Shows {len(transfer_options)} options but only {actual_cars.count()} actual cars")
            print(f"      This suggests the filtering logic is creating duplicate options")


def test_specific_scenario():
    """Test a specific scenario that was problematic"""
    
    print(f"\n🎯 Testing Specific VAN Scenario")
    print("=" * 50)
    
    # Get VAN car type
    van_type = CarType.objects.filter(code='VAN').first()
    if not van_type:
        print("❌ VAN car type not found")
        return
    
    print(f"VAN Car Type: {van_type.name} (max capacity: {van_type.max_capacity})")
    
    # Get all VAN cars
    van_cars = Car.objects.filter(car_type=van_type)
    print(f"VAN Cars in database: {van_cars.count()}")
    for car in van_cars:
        print(f"  - {car.name} (max: {car.max})")
    
    # Get rates for VAN cars
    van_rates = Rate.objects.filter(car__car_type__code='VAN')
    print(f"VAN Rates in database: {van_rates.count()}")
    
    # Group by car
    cars_with_rates = {}
    for rate in van_rates:
        car_name = rate.car.name if rate.car else 'Unknown'
        if car_name not in cars_with_rates:
            cars_with_rates[car_name] = []
        cars_with_rates[car_name].append(rate)
    
    print(f"VAN Cars with rates: {len(cars_with_rates)}")
    for car_name, rates in cars_with_rates.items():
        print(f"  - {car_name}: {len(rates)} rates")
        for rate in rates:
            print(f"    * {rate.zone.name} - {rate.travel_type}: ${rate.price}")


if __name__ == "__main__":
    test_car_type_filtering()
    test_specific_scenario()
    
    print(f"\n🎉 Testing Complete!")
    print("=" * 50)
    print("If you see 'CORRECT' for all car types, the filtering issue is resolved.")
    print("If you see 'ISSUE', there may still be duplicate options being generated.")
