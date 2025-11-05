import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')

import django
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from speedy_app.core.views import contact_form_view
from speedy_app.core.models import Contact

rf = RequestFactory()
req = rf.post('/contact/', data={
    'name': 'Direct Call User',
    'email': 'directcall@example.com',
    'phone': '000-111',
    'country': 'Directland',
    'company': 'DirectCo',
    'interested': 'Transfers',
    'additional': 'Direct call test'
})
# Apply session middleware
session_mw = SessionMiddleware()
session_mw.process_request(req)
req.session.save()
# Apply messages middleware
msg_mw = MessageMiddleware()
msg_mw.process_request(req)

# Call the view
resp = contact_form_view(req)
print('View returned:', type(resp), getattr(resp, 'status_code', None))

print('Contacts count:', Contact.objects.count())
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
