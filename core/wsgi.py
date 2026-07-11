import os
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

logger = logging.getLogger(__name__)

import django
django.setup()

try:
    from django.core.management import call_command
    from django.conf import settings

    db_config = settings.DATABASES['default']
    if 'sqlite' in db_config['ENGINE']:
        db_path = db_config.get('NAME', '')
        if db_path and not os.path.exists(db_path):
            logger.info("SQLite DB not found at %s, running migrate...", db_path)
            call_command('migrate', '--run-syncdb', verbosity=0)
            logger.info("Migrate completed.")
except Exception as e:
    logger.exception("DB init error: %s", str(e))

from django.core.wsgi import get_wsgi_application

django_app = get_wsgi_application()

ALLOWED_ORIGINS = [
    'https://task-manager-client-feih.vercel.app',
    'https://task-manager-client-feih-git-main-sheik-saims-projects.vercel.app',
    'https://task-manager-client-tff6-sable.vercel.app',
    'http://localhost:3000',
    'http://localhost:5173',
]

CORS_HEADERS = [
    ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS'),
    ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept, Origin'),
    ('Access-Control-Max-Age', '86400'),
]


class CORSMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        origin = environ.get('HTTP_ORIGIN', '')
        request_method = environ.get('REQUEST_METHOD', '')

        allowed_origin = origin if origin in ALLOWED_ORIGINS else ALLOWED_ORIGINS[0]

        cors_headers = list(CORS_HEADERS)
        cors_headers.append(('Access-Control-Allow-Origin', allowed_origin))

        if request_method == 'OPTIONS':
            start_response('200 OK', cors_headers + [('Content-Length', '0')])
            return [b'']

        def custom_start_response(status, headers, exc_info=None):
            existing_headers = [(k.lower(), k, v) for k, v in headers]
            has_acao = any(k == 'access-control-allow-origin' for k, _, _ in existing_headers)

            if not has_acao:
                for hk, hv in cors_headers:
                    headers.append((hk, hv))

            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)


application = CORSMiddleware(django_app)
