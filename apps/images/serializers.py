from rest_framework import serializers
from .models import Image
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class ImageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=255)
    image_url = serializers.CharField()
    user_id = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['user_id'] = request.user.id
        validated_data['user_email'] = request.user.email
        validated_data['created_at'] = datetime.utcnow()
        validated_data['updated_at'] = datetime.utcnow()
        return Image(**validated_data).save()

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.updated_at = datetime.utcnow()
        instance.save()
        return instance
