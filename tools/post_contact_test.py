import os
import sys

# Ensure project root is on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Set Django settings module (matches manage.py default)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')

import django
django.setup()

from django.test import Client
from speedy_app.core.models import Contact

client = Client()
print('Submitting test contact...')
payload = {
    'name': 'Automated Test User',
    'email': 'autotest@example.com',
    'phone': '555-1234',
    'country': 'Testland',
    'company': 'TestCo',
    'interested': 'Transfers',
    'additional': 'This is an automated test.'
}
resp = client.post('/contact/', payload, follow=True)

print('POST status code:', resp.status_code)
# Debug info to understand redirects/response
try:
    print('Response redirected to:', resp.redirect_chain)
except Exception:
    pass
print('Response content (first 400 bytes):')
print(resp.content[:400])

count = Contact.objects.count()
print('Total Contact rows:', count)

latest = Contact.objects.order_by('-submitted_at').first()
if latest:
    print('Latest Contact:')
    print('id =', latest.id)
    print('name =', latest.name)
    print('email =', latest.email)
    print('phone =', latest.phone)
    print('country =', latest.country)
    print('company =', latest.company)
    print('interested_in =', latest.interested_in)
    print('message =', latest.message)
else:
    print('No Contact rows found')
