from mongoengine import Document, fields
from django.contrib.auth import get_user_model

User = get_user_model()


class Annotation(Document):
    image_id = fields.StringField(required=True)  # MongoDB Image ID
    user_id = fields.IntField(required=True)
    user_email = fields.StringField(required=True)
    polygons = fields.ListField(fields.DictField(), default=list)
    label = fields.StringField(required=False)
    created_at = fields.DateTimeField(required=True)
    updated_at = fields.DateTimeField(required=True)

    meta = {
        'collection': 'annotations',
        'ordering': ['-created_at']
    }

    def __str__(self):
        return f'Annotation for image {self.image_id}'
