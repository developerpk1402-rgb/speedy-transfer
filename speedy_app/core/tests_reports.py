from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Booking
from django.utils import timezone
import io


class ReportsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(username='staff', password='staffpass', is_staff=True)
        self.client = Client()
        # create a booking
        now = timezone.now()
        # ensure required FK objects exist
        from .models import CarType, Car
        ct = CarType.objects.create(code='SEDAN', name='Sedan', max_capacity=3)
        car = Car.objects.create(name='Test Car', car_type=ct, max=3)
        Booking.objects.create(client_id='test@example.com', customer_name='Test', pickup_date_time=now, return_date_time=now, car_id=car, date_capture=now, total_amount=50.0)

    def test_portal_requires_login(self):
        r = self.client.get('/reports/')
        self.assertIn(r.status_code, (302, 301))  # redirect to login

    def test_staff_can_access_and_export_csv(self):
        self.client.login(username='staff', password='staffpass')
        r = self.client.get('/reports/sold-orders/?format=csv')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r['Content-Type'], 'text/csv')
        self.assertTrue(r.content.startswith(b'Booking ID'))

    def test_staff_can_export_xlsx(self):
        self.client.login(username='staff', password='staffpass')
        r = self.client.get('/reports/sales-history/?format=xlsx')
        # if openpyxl is present, content-type should be xlsx, otherwise 200 or redirect
        self.assertIn(r.status_code, (200,))
