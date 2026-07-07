from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskBulkUpdateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('bulk-update/', TaskBulkUpdateView.as_view(), name='task-bulk-update'),
]
