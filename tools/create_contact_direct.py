import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
import django
django.setup()
from speedy_app.core.models import Contact
c = Contact.objects.create(name='Direct ORM User', email='ormtest@example.com', phone='999-888', country='Ormland', company='ORMCo', interested_in='Transfers', message='Created via ORM test')
print('Created Contact id=', c.id)
print('Name:', c.name)
print('Email:', c.email)
print('Submitted at:', c.submitted_at)
