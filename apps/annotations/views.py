from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Annotation
from .serializers import AnnotationSerializer


class AnnotationListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        image_id = self.request.query_params.get('image_id', None)
        queryset = Annotation.objects.filter(user=self.request.user)
        if image_id:
            queryset = queryset.filter(image_id=image_id)
        return queryset


class AnnotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnotationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Annotation.objects.filter(user=self.request.user)
