from django.urls import path
from .views import ImageListCreateView, ImageDetailView

urlpatterns = [
    path('', ImageListCreateView.as_view(), name='image-list-create'),
    path('<int:pk>/', ImageDetailView.as_view(), name='image-detail'),
]
