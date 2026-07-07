from rest_framework import serializers
from .models import Annotation
from django.contrib.auth import get_user_model

User = get_user_model()


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'image', 'user', 'polygons', 'label', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
