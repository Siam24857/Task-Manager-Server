import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Wrap the application to handle OPTIONS requests at WSGI level
class OptionsMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-Type', 'text/plain'),
            ])
            return [b'OK']
        return self.app(environ, start_response)

application = OptionsMiddleware(get_wsgi_application())
