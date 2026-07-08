from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'message': 'BotLeague API Server',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth/',
            'tasks': '/api/tasks/',
            'images': '/api/images/',
            'annotations': '/api/annotations/',
        }
    })

urlpatterns = [
    path('', api_root),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/images/', include('apps.images.urls')),
    path('api/annotations/', include('apps.annotations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
