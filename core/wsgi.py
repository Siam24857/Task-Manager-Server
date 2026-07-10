import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Wrap the application to handle OPTIONS requests at WSGI level
class OptionsMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            # Get the origin from the request
            origin = environ.get('HTTP_ORIGIN', '')
            allowed_origins = [
                'https://task-manager-client-feih.vercel.app',
                'https://task-manager-client-feih-git-main-sheik-saims-projects.vercel.app',
                'https://task-manager-client-tff6-sable.vercel.app',
            ]
            
            headers = [
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Content-Type', 'text/plain'),
            ]
            
            # Return specific origin if allowed, otherwise don't set it
            if origin in allowed_origins:
                headers.insert(0, ('Access-Control-Allow-Origin', origin))
            
            start_response('200 OK', headers)
            return [b'OK']
        return self.app(environ, start_response)

application = OptionsMiddleware(get_wsgi_application())
