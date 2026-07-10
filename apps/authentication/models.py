from django.contrib.auth.models import AbstractUser
from django.db import models
from mongoengine import Document, fields
import secrets
from datetime import datetime, timedelta


class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class AuthToken(Document):
    """MongoDB-based token authentication model"""
    user_id = fields.IntField(required=True)
    user_email = fields.StringField(required=True)
    token = fields.StringField(required=True, unique=True)
    created_at = fields.DateTimeField(required=True)
    expires_at = fields.DateTimeField(required=True)
    is_active = fields.BooleanField(required=True, default=True)

    meta = {
        'collection': 'auth_tokens',
        'indexes': [
            {'fields': ['token'], 'unique': True},
            {'fields': ['user_id']},
        ]
    }

    @classmethod
    def generate_token(cls, user):
        """Generate a new token for user"""
        # Generate secure random token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        # Deactivate old tokens for this user
        cls.objects.filter(user_id=user.id, is_active=True).update(is_active=False)
        
        # Create new token
        return cls.objects.create(
            user_id=user.id,
            user_email=user.email,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True
        )

    @classmethod
    def validate_token(cls, token):
        """Validate token and return user if valid"""
        try:
            auth_token = cls.objects.get(token=token, is_active=True)
            if auth_token.expires_at > datetime.utcnow():
                return auth_token
            else:
                auth_token.is_active = False
                auth_token.save()
                return None
        except cls.DoesNotExist:
            return None

    def __str__(self):
        return f"Token for {self.user_email}"
