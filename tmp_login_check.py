import os
import django
import json
import urllib.request
import urllib.error

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

url = 'http://127.0.0.1:8000/api/auth/login/'
data = json.dumps({'email': 'authtest@example.com', 'password': 'Password123'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req) as res:
        print('status', res.status)
        print('body', res.read().decode())
except urllib.error.HTTPError as e:
    print('status', e.code)
    print('body', e.read().decode())
except Exception as ex:
    print('EXCEPTION', type(ex).__name__, ex)
