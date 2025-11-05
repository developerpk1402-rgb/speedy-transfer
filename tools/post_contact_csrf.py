import os, sys, re
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.develop')

import django
django.setup()

import requests
from bs4 import BeautifulSoup

BASE = 'http://127.0.0.1:8000'
s = requests.Session()
# Fetch homepage to retrieve CSRF token
r = s.get(BASE + '/')
if r.status_code != 200:
    print('Failed to GET homepage:', r.status_code)
    print(r.text[:500])
    sys.exit(1)

# parse token
soup = BeautifulSoup(r.text, 'html.parser')
csrf = soup.find('input', attrs={'name':'csrfmiddlewaretoken'})
if not csrf:
    print('No CSRF token found on homepage; trying contact page')
    r = s.get(BASE + '/contact/')
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf = soup.find('input', attrs={'name':'csrfmiddlewaretoken'})
if not csrf:
    print('No CSRF token found; aborting')
    sys.exit(1)

token = csrf['value']
print('CSRF token found')

payload = {
    'name': 'HTTP POST User',
    'email': 'httppost@example.com',
    'phone': '321-654',
    'country': 'HTTPland',
    'company': 'HTTPCo',
    'interested': 'Transfers',
    'additional': 'Sent by requests with CSRF',
    'csrfmiddlewaretoken': token
}

headers = {'Referer': BASE + '/'}
post = s.post(BASE + '/contact/', data=payload, headers=headers)
print('POST status', post.status_code)
print('Response text (first 300 chars):')
print(post.text[:300])

# Check DB
from speedy_app.core.models import Contact
print('Total Contact rows after POST:', Contact.objects.count())
latest = Contact.objects.order_by('-submitted_at').first()
if latest:
    print('Latest contact id:', latest.id, 'name:', latest.name, 'email:', latest.email)
else:
    print('No contact rows found')
