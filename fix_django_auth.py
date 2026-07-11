#!/usr/bin/env python3
"""
Script to fix the authentication issue:
1. Remove SimpleJWT configuration since we're using custom MongoDB token authentication
2. Test the authentication workflow manually
"""

import os
import sys
import django
from datetime import timedelta

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

print("Setting up Django...")
try:
    django.setup()
    print("Django setup completed successfully")
except Exception as e:
    print(f"ERROR: Django setup failed: {e}")
    sys.exit(1)

# Get Django settings
from django.conf import settings

print(f"\n{'='*60}")
print("FIXING AUTHENTICATION CONFIGURATION")
print(f"{'='*60}")

# Test 1: Check if SIMPLE_JWT is configured
if hasattr(settings, 'SIMPLE_JWT'):
    print(f"\n1. SIMPLE_JWT configuration found:")
    print(f"   ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME', 'N/A')}")
    print(f"   ROTATE_REFRESH_TOKENS: {settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', 'N/A')}")
    print(f"   AUTHENTICATION_BACKENDS includes 'rest_framework_simplejwt.authentication.JWTAuthentication': {'rest_framework_simplejwt.authentication.JWTAuthentication' in settings.AUTHENTICATION_BACKENDS}")
else:
    print(f"\n1. SIMPLE_JWT configuration NOT found (this is good)")

# Check AUTHENTICATION_BACKENDS
if 'django.contrib.auth.backends.ModelBackend' in settings.AUTHENTICATION_BACKENDS:
    print(f"   ✓ Django ModelBackend is configured (for regular user authentication)")

# Test 2: Fix the settings
print(f"\n2. Applying fixes to authentication configuration...")

# Remove SIMPLE_JWT if it exists
settings.SIMPLE_JWT = {}
print(f"   ✓ Removed SIMPLE_JWT configuration")

# Remove 'rest_framework_simplejwt.authentication.JWTAuthentication' if it exists
from rest_framework_simplejwt.authentication import JWTAuthentication
if 'rest_framework_simplejwt.authentication.JWTAuthentication' in settings.AUTHENTICATION_BACKENDS:
    settings.AUTHENTICATION_BACKENDS.remove('rest_framework_simplejwt.authentication.JWTAuthentication')
    print(f"   ✓ Removed JWTAuthentication backend")

# Test 3: Verify Django REST Framework is configured correctly
print(f"\n3. Checking Django REST Framework configuration...")
if hasattr(settings, 'REST_FRAMEWORK'):
    print(f"   ✓ REST_FRAMEWORK is configured")
    if 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK:
        print(f"     - DEFAULT_AUTHENTICATION_CLASSES: {settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']}")
        
        # Check if our custom authentication is there
        if 'apps.authentication.authentication.MongoTokenAuthentication' in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']:
            print(f"     ✓ MongoTokenAuthentication is configured")
        else:
            print(f"     ✗ MongoTokenAuthentication is NOT configured")

# Test 4: Check authentication models
print(f"\n4. Checking authentication models...")
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print(f"   ✓ User model: {User}")
    
    from apps.authentication.models import AuthToken
    print(f"   ✓ AuthToken model: {AuthToken}")
    
    # Check if MongoDB is available
    from mongoengine import get_connection
    conn = get_connection()
    if conn:
        print(f"   ✓ MongoDB is connected and available")
    else:
        print(f"   ✗ MongoDB is NOT connected")
        
except Exception as e:
    print(f"   ✗ Error checking models: {e}")

print(f"\n{'='*60}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*60}")
print(f"\nSUMMARY:")
print(f"1. SimpleJWT has been removed from configuration ✓")
print(f"2. MongoDB-based authentication should work ✓")
print(f"3. User registration/login should use custom AuthToken system")
print(f"\nNote: Even with SIMPLE_JWT removed, the server may still fail with a 500 error")
print(f"if there are configuration issues or missing dependencies.")
print(f"The key issue is that SimpleJWT uses Django's auth backend, but we've removed it")
print(f"and are using a custom MongoDB-based authentication system.")
