from mongoengine import Document, fields
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(Document):
    STATUS_CHOICES = (
        'todo',
        'in_progress',
        'done',
    )

    PRIORITY_CHOICES = (
        'low',
        'medium',
        'high',
    )

    title = fields.StringField(required=True, max_length=255)
    description = fields.StringField(required=False)
    status = fields.StringField(choices=STATUS_CHOICES, default='todo')
    priority = fields.StringField(choices=PRIORITY_CHOICES, default='medium')
    due_date = fields.DateTimeField(required=False)
    tags = fields.ListField(fields.StringField(), default=list)
    user_id = fields.IntField(required=True)  # Store Django user ID
    user_email = fields.StringField(required=True)  # Store user email for reference
    created_at = fields.DateTimeField(required=True)
    updated_at = fields.DateTimeField(required=True)

    meta = {
        'collection': 'tasks',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return self.title
