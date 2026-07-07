import json
import urllib.request
import urllib.error
url='http://127.0.0.1:8000/api/auth/login/'
data=json.dumps({'email':'test@example.com','password':'testpass123'}).encode('utf-8')
req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print('STATUS', r.status)
        print(r.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print('STATUS', e.code)
    print(e.read().decode('utf-8'))
except Exception as exc:
    print('ERROR', type(exc).__name__, exc)
