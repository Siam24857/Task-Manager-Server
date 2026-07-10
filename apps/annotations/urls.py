from django.urls import path
from .views import AnnotationListCreateView, AnnotationDetailView

urlpatterns = [
    path('', AnnotationListCreateView.as_view(), name='annotation-list-create'),
    path('<int:pk>', AnnotationDetailView.as_view(), name='annotation-detail'),
]
