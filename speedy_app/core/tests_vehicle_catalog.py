from django.test import TestCase, RequestFactory
from django.urls import reverse

from speedy_app.core.models import Zone, Hotel


class VehicleCatalogTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_cartype_catalog_exists_and_can_be_created(self):
        # Import lazily to avoid import errors before implementation
        from speedy_app.core.models import CarType

        # Create five basic types if not present
        defaults = [
            ("SEDAN", "Sedan"),
            ("SUV", "SUV"),
            ("VAN", "Van"),
            ("SPRINTER", "Sprinter"),
            ("BUS", "Bus"),
        ]
        for code, name in defaults:
            CarType.objects.get_or_create(code=code, defaults={"name": name})

        codes = set(CarType.objects.values_list("code", flat=True))
        for code, _ in defaults:
            self.assertIn(code, codes)

    def test_rate_relates_to_cartype_and_results_view_filters_by_code(self):
        from speedy_app.core.models import CarType, Car, Rate
        from speedy_app.core.views import ResultsView

        # Setup zone, hotel, type and rate
        zone = Zone.objects.create(name="Test Zone")
        hotel = Hotel.objects.create(name="Hotel A", zone=zone)
        van_type = CarType.objects.create(code="VAN", name="Van")
        van = Car.objects.create(name="Test Van", car_type=van_type, max=8)
        Rate.objects.create(zone=zone, car=van, travel_type="ONE_WAY", price=123.45)

        # Build request
        url = reverse("core:results_view")
        request = self.factory.get(
            url,
            {
                "pickup_location": str(hotel.id),
                "dropoff_location": str(hotel.id),
                "car_type": "VAN",
                "trip_type": "oneway",
                "people": "4",
                "pickup_datetime": "2025-09-01T10:00",
            },
        )

        response = ResultsView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        options = context.get("transfer_options") or []
        self.assertTrue(len(options) >= 1)
        self.assertEqual(float(options[0]["price"]), 123.45)
        self.assertEqual(options[0]["travel_type"], "ONE_WAY")

    # Booking continues to reference a specific Car unit; catalog linkage is ensured via Rate
    # so we don't require Booking to have a CarType FK


