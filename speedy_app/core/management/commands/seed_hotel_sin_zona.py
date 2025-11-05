from django.core.management.base import BaseCommand
from django.db import transaction

from speedy_app.core.models import Zone, Hotel, Car, CarType, Rate


class Command(BaseCommand):
    help = "Seed data to enable manual testing for 'HOTEL SIN ZONA' in the Results page."

    def add_arguments(self, parser):
        parser.add_argument(
            "--zone-name",
            default="Default Test Zone",
            help="Name of the zone to create/use for HOTEL SIN ZONA",
        )
        parser.add_argument(
            "--price-oneway",
            type=float,
            default=120.00,
            help="Price to use for one-way VAN transfers",
        )
        parser.add_argument(
            "--price-roundtrip",
            type=float,
            default=220.00,
            help="Price to use for round-trip VAN transfers",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # argparse converts dashes to underscores for option keys
        zone_name = options["zone_name"]
        price_oneway = options["price_oneway"]
        price_roundtrip = options["price_roundtrip"]

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding data for HOTEL SIN ZONA..."))

        # 1) Ensure a zone exists
        zone, created_zone = Zone.objects.get_or_create(name=zone_name)
        if created_zone:
            self.stdout.write(self.style.SUCCESS(f"Created zone: {zone.name}"))
        else:
            self.stdout.write(self.style.NOTICE(f"Using existing zone: {zone.name}"))

        # 2) Ensure a VAN car type and a VAN car exist
        van_type, _ = CarType.objects.get_or_create(code="VAN", defaults={"name": "Van", "max_capacity": 8})
        van_car, created_car = Car.objects.get_or_create(
            name="Standard-Van",
            defaults={"max": 8, "car_type": van_type},
        )
        if not created_car:
            # Make sure it's a VAN and has reasonable capacity
            if not van_car.max or van_car.max < 1:
                van_car.max = 8
            if van_car.car_type_id != van_type.id:
                van_car.car_type = van_type
            van_car.save()
        self.stdout.write(self.style.SUCCESS(f"VAN car ready: {van_car.name} (cap {van_car.max})"))

        # 3) Ensure rates for that zone and VAN exist
        r1, _ = Rate.objects.get_or_create(
            zone=zone,
            car=van_car,
            car_type=van_type,
            travel_type="ONE_WAY",
            defaults={"price": price_oneway},
        )
        if r1.price != price_oneway:
            r1.price = price_oneway
            r1.save()
        r2, _ = Rate.objects.get_or_create(
            zone=zone,
            car=van_car,
            car_type=van_type,
            travel_type="ROUND_TRIP",
            defaults={"price": price_roundtrip},
        )
        if r2.price != price_roundtrip:
            r2.price = price_roundtrip
            r2.save()
        self.stdout.write(self.style.SUCCESS(
            f"Rates ready: ONE_WAY={r1.price} ROUND_TRIP={r2.price} for zone '{zone.name}'"
        ))

        # 4) Assign HOTEL SIN ZONA to this zone (create it if missing)
        hotel, created_hotel = Hotel.objects.get_or_create(name="HOTEL SIN ZONA")
        if created_hotel:
            self.stdout.write(self.style.SUCCESS("Created hotel 'HOTEL SIN ZONA'"))
        if hotel.zone_id != zone.id:
            hotel.zone = zone
            hotel.save()
            self.stdout.write(self.style.SUCCESS(
                f"Assigned 'HOTEL SIN ZONA' to zone '{zone.name}'"
            ))
        else:
            self.stdout.write(self.style.NOTICE(
                f"'HOTEL SIN ZONA' already assigned to zone '{zone.name}'"
            ))

        self.stdout.write(self.style.SUCCESS("Seeding complete. You can now search with:"))
        self.stdout.write("- Pickup Location: HOTEL SIN ZONA")
        self.stdout.write("- Car Type: Van")
        self.stdout.write("- Trip Options: Oneway or Roundtrip")

