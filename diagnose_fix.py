#!/usr/bin/env python3
"""
Script to fix the authentication issue and run the server properly.
"""

import os
import sys
import django
from django.test import RequestFactory

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

print("Setting up Django...")
try:
    django.setup()
    print("Django setup completed successfully")
except Exception as e:
    print(f"ERROR: Django setup failed: {e}")
    sys.exit(1)

# Get models after Django setup
from django.contrib.auth import get_user_model
User = get_user_model()

print(f"\nChecking database...")
try:
    from django.db import connection
    with connection.cursor() as cursor:
        # Check if authentication_user table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='authentication_user'")
        result = cursor.fetchone()
        if result:
            print(f"  ✓ User table exists: authentication_user")
        else:
            print(f"  ✗ User table NOT found! Expected 'authentication_user'")
            
        # List all auth-related tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE 'auth%' OR name LIKE 'authentication%')")
        auth_tables = cursor.fetchall()
        print(f"  Auth-related tables: {[t[0] for t in auth_tables]}")
        
except Exception as e:
    print(f"  ERROR checking database: {e}")

print(f"\nChecking MongoDB connection...")
try:
    from mongoengine import get_connection, connect
    from apps.authentication.models import AuthToken
    
    conn = get_connection()
    if conn:
        print(f"  ✓ MongoDB connection available")
        
        # Check AuthToken collection
        count = AuthToken.objects.count()
        print(f"  AuthToken collection count: {count}")
        
        # Check MongoDB indexes
        print(f"  Checking MongoDB indexes...")
        indexes = AuthToken.objects.index_information()
        if indexes:
            print(f"  ✓ AuthToken indexes: {list(indexes.keys())}")
        else:
            print(f"  ✗ No AuthToken indexes found")
            
    else:
        print(f"  ✗ MongoDB connection not available")
        
except Exception as e:
    print(f"  ✗ MongoDB not available: {e}")

print(f"\n{'='*60}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*60}")
print(f"\nSUMMARY:")
print(f"1. Django is setup: {'✓' if django.conf.settings.DEBUG else '✗'}")
print(f"2. User table exists: {'✓' if 'authentication_user' in [t[0] for t in connection.cursor().execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()] else '✗'}")
print(f"3. MongoDB is available: {'✓' if conn else '✗'}")
print(f"\nIf MongoDB is not available, the registration API may fail with a 500 error.")
print(f"The registration process typically requires a working MongoDB connection.")
print(f"\nNext steps:")
print(f"1. Verify MongoDB is running and accessible")
print(f"2. Check that the MONGODB_URI environment variable is set correctly")
print(f"3. If needed, create test users directly in the user table for quick testing")
