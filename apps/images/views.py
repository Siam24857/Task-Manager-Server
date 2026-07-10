from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Image
from .serializers import ImageSerializer


@method_decorator(csrf_exempt, name='dispatch')
class ImageListCreateView(generics.ListCreateAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_queryset(self):
        return Image.objects.filter(user_id=self.request.user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ImageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = ImageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class ImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_object(self):
        image_id = self.kwargs.get('pk')
        return Image.objects.get(id=image_id, user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        image = self.get_object()
        serializer = ImageSerializer(image)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        image = self.get_object()
        serializer = ImageSerializer(image, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        image = self.get_object()
        serializer = ImageSerializer(image, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        image = self.get_object()
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
