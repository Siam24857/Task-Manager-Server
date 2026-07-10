from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Annotation
from .serializers import AnnotationSerializer


@method_decorator(csrf_exempt, name='dispatch')
class AnnotationListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_queryset(self):
        image_id = self.request.query_params.get('image_id', None)
        queryset = Annotation.objects.filter(user_id=self.request.user.id)
        if image_id:
            queryset = queryset.filter(image_id=image_id)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AnnotationSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = AnnotationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class AnnotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_object(self):
        annotation_id = self.kwargs.get('pk')
        return Annotation.objects.get(id=annotation_id, user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        annotation = self.get_object()
        serializer = AnnotationSerializer(annotation)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        annotation = self.get_object()
        serializer = AnnotationSerializer(annotation, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        annotation = self.get_object()
        annotation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
