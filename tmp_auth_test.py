import os
import django
import json
import urllib.request
import urllib.error

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

user, created = User.objects.get_or_create(email='authtest@example.com', defaults={'username': 'authtest'})
if created:
    user.set_password('Password123')
    user.save()
    print('Created test user')
else:
    print('Test user already exists')

for payload in [
    {'email': 'authtest@example.com', 'password': 'Password123'},
    {'username': 'authtest', 'password': 'Password123'},
    {'email': 'authtest@example.com', 'password': 'wrong'},
]:
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8000/api/auth/login/', data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as res:
            print('Payload:', payload)
            print('Status:', res.status)
            print(res.read().decode())
    except urllib.error.HTTPError as e:
        print('Payload:', payload)
        print('Status:', e.code)
        print(e.read().decode())
    except Exception as exc:
        print('Payload:', payload)
        print('EXCEPTION', type(exc).__name__, exc)
