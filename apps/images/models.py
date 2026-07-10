from mongoengine import Document, fields
from django.contrib.auth import get_user_model

User = get_user_model()


class Image(Document):
    title = fields.StringField(required=True, max_length=255)
    image_url = fields.StringField(required=True)  # Store image URL instead of file
    user_id = fields.IntField(required=True)
    user_email = fields.StringField(required=True)
    created_at = fields.DateTimeField(required=True)
    updated_at = fields.DateTimeField(required=True)

    meta = {
        'collection': 'images',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return self.title
