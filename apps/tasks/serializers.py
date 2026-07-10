from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES, default='todo')
    priority = serializers.ChoiceField(choices=Task.PRIORITY_CHOICES, default='medium')
    due_date = serializers.DateTimeField(required=False, allow_null=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=list)
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
        return Task(**validated_data).save()

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.updated_at = datetime.utcnow()
        instance.save()
        return instance
