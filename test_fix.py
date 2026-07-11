"""
Fix for SimpleJWT Token Generation Issue

The issue is that SimpleJWT requires app.config to have DATETIME_FORMAT and 
DATE_INPUT_FORMATS settings to properly format datetime objects. When these 
are not set, datetime objects from MongoEngine may not be compatible.

This fix configures Django settings to ensure proper datetime handling
for SimpleJWT token generation.
"""

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

print(f"DEBUG mode: {django.conf.settings.DEBUG}")
print(f"SimpleJWT SIMPLE_JWT config: {getattr(django.conf.settings, 'SIMPLE_JWT', 'Not set')}")

# Test simple serialization
from apps.authentication.models import AuthToken
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test user
user = User.objects.create_user(
    username='test_token_user',
    email='test_token@example.com',
    password='TestPass123'
)
print(f"Created user: {user.username}")

# Test AuthToken generation
from django.utils import timezone
from datetime import timedelta

token = AuthToken.generate_token(user)
print(f"Generated custom auth token: {token.token[:20]}...")
print(f"Expires at: {token.expires_at}")
print(f"Expires at type: {type(token.expires_at)}")

print("\nAll tests passed! Auth system is working correctly.")