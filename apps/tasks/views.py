from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Task
from .serializers import TaskSerializer


@method_decorator(csrf_exempt, name='dispatch')
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_queryset(self):
        queryset = Task.objects.filter(user_id=self.request.user.id)
        status_filter = self.request.query_params.get('status', None)
        priority_filter = self.request.query_params.get('priority', None)
        search = self.request.query_params.get('search', None)
        due_date = self.request.query_params.get('due_date', None)

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if search:
            queryset = queryset.filter(title__icontains=search)
        if due_date:
            queryset = queryset.filter(due_date__date=due_date)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_object(self):
        task_id = self.kwargs.get('pk')
        return Task.objects.get(id=task_id, user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = TaskSerializer(task, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(csrf_exempt, name='dispatch')
class TaskBulkUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def put(self, request, *args, **kwargs):
        tasks_data = request.data.get('tasks', [])
        updated_tasks = []

        for task_data in tasks_data:
            task_id = task_data.get('id')
            if task_id:
                try:
                    task = Task.objects.get(id=task_id, user_id=request.user.id)
                    serializer = TaskSerializer(task, data=task_data, partial=True, context={'request': request})
                    if serializer.is_valid():
                        serializer.save()
                        updated_tasks.append(serializer.data)
                except Task.DoesNotExist:
                    continue

        return Response(updated_tasks, status=status.HTTP_200_OK)
