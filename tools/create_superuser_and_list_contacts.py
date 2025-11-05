import os, sys, secrets
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')
import django
django.setup()

from django.contrib.auth import get_user_model
from speedy_app.core.models import Contact

User = get_user_model()
username = 'admin'
email = 'admin@example.com'
# generate a secure password
password = secrets.token_urlsafe(12)

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Created superuser:')
    print('  username:', username)
    print('  email:', email)
    print('  password:', password)
else:
    print('Superuser already exists with username:', username)

print('\nListing Contact rows:')
for c in Contact.objects.order_by('submitted_at'):
    print(f"id={c.id} name={c.name} email={c.email} submitted_at={c.submitted_at}")
