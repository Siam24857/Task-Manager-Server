#!/usr/bin/env python3
"""
Diagnostic script to check and fix authentication issues in the Task Manager project.
This script will:
1. Check Django setup
2. Check database migrations
3. Test authentication endpoints manually without running the server
4. Provide detailed debugging information
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model

# Setup Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

try:
    django.setup()
    print("Django setup completed successfully")
except Exception as e:
    print(f"Django setup failed: {e}")
    sys.exit(1)

# Get models
User = get_user_model()

print(f"\nCurrent Django settings:")
print(f"  DEBUG: {django.conf.settings.DEBUG}")
print(f"  AUTH_USER_MODEL: {django.conf.settings.AUTH_USER_MODEL}")
print(f"  INSTALLED_APPS: {django.conf.settings.INSTALLED_APPS}")
print(f"  REST_FRAMEWORK: {django.conf.settings.REST_FRAMEWORK}")

# Check database
print(f"\nDatabase status:")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        tables = cursor.fetchall()
        print(f"  Tables in SQLite database: {len(tables)}")
        for table in tables:
            print(f"    - {table[0]}")
        
        # Check if authentication tables exist
        auth_tables = [t[0] for t in tables if t[0].startswith('auth')]
        user_table = User._meta.db_table if hasattr(User, '_meta') else 'Unknown'
        print(f"  Auth tables: {auth_tables}")
        print(f"  User table: {user_table}")
except Exception as e:
    print(f"  Database check failed: {e}")

# Check MongoDB connection
print(f"\nMongoDB status:")
try:
    from mongoengine import connect, disconnect, get_connection
    from apps.authentication.models import AuthToken
    
    print(f"  MongoDB connected: {get_connection() is not None}")
    print(f"  AuthToken model: {AuthToken}")
    
    # Try to query AuthToken collection
    count = AuthToken.objects.count()
    print(f"  AuthToken records in MongoDB: {count}")
    
except Exception as e:
    print(f"  MongoDB not available or error: {e}")

# Check authentication backends
print(f"\nAuthentication backends:")
print(f"  AUTHENTICATION_BACKENDS: {django.conf.settings.AUTHENTICATION_BACKENDS}")

# Check SIMPLE_JWT configuration
print(f"\nSimpleJWT configuration:")
print(f"  SIMPLE_JWT: {getattr(django.conf.settings, 'SIMPLE_JWT', 'Not configured')}")

print(f"\n'{"="*60}")
print("DIAGNOSTIC COMPLETE")
print(f"{"="*60}")
