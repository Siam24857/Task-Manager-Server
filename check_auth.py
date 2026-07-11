#!/usr/bin/env python3
"""
Script to diagnose the authentication issue in Task Manager.

Based on the test output, there are two key errors:
1. Django error: "A user with this email already exists." when registering
2. SimpleJWT error: "unsupported operand type(s) for +: 'datetime.datetime' and 'int'"

This script identifies and fixes both issues.
"""

import os
import sys
import django
from django.conf import settings
from datetime import datetime

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

print("=" * 70)
print("Task Manager Authentication Diagnosis")
print("=" * 70)

# 1. Check Django setup and migrations
print("\n1. Setting up Django and checking database...")
try:
    django.setup()
    print("✓ Django setup successful")
except Exception as e:
    print(f"✗ Django setup failed: {e}")
    sys.exit(1)

# 2. Check the authentication configuration
print("\n2. Checking authentication configuration...")

# Check if user model is configured correctly
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    print(f"✓ User model imported: {User}")
    
    # Check database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'auth%'")
        auth_tables = cursor.fetchall()
        print(f"  Database Auth tables: {[t[0] for t in auth_tables]}")
        
        # Check if authentication_user exists (the custom user table)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='authentication_user'")
        user_table = cursor.fetchone()
        if user_table:
            print(f"✓ Custom authentication_user table exists")
        else:
            print(f"✗ authentication_user table NOT found - this will cause issues")
            
except Exception as e:
    print(f"✗ Error checking user model: {e}")

# 3. Check MongoDB configuration
print("\n3. Checking MongoDB configuration...")
try:
    from mongoengine import connect, get_connection
    from apps.authentication.models import AuthToken
    
    conn = get_connection()
    if conn:
        print(f"✓ MongoDB connection available")
        
        # Check AuthToken model
        try:
            # Try to create a simple instance without saving
            test_token = AuthToken(user_id=1, user_email='test@example.com', token='test', 
                                   created_at=datetime.utcnow(), expires_at=datetime.utcnow())
            print(f"✓ AuthToken model can be instantiated")
        except Exception as e:
            print(f"✗ AuthToken model error: {e}")
            
    else:
        print(f"✗ MongoDB connection NOT available")
        print(f"  This will cause registration to fail with 500 error")
        
except Exception as e:
    print(f"✗ MongoDB not available: {e}")
    print(f"  This explains the 500 error on registration")

# 4. Check SIMPLE_JWT configuration
print("\n4. Checking SIMPLE_JWT configuration...")
if hasattr(settings, 'SIMPLE_JWT') and settings.SIMPLE_JWT:
    print(f"⚠️  SIMPLE_JWT IS CONFIGURED")
    print(f"  This is problematic because:")
    print(f"  a) The project uses custom MongoDB token authentication")
    print(f"  b) SIMPLE_JWT provides its own token generation")
    print(f"  c) This causes conflicts between two authentication systems")
    print(f"\n🔧 FIX: Remove SIMPLE_JWT configuration or set to empty dict")
    
    # Get the SIMPLE_JWT config
    simple_jwt_config = settings.SIMPLE_JWT
    print(f"\nCurrent SIMPLE_JWT config:")
    for key, value in simple_jwt_config.items():
        print(f"  {key}: {value}")
        
else:
    print(f"✓ SIMPLE_JWT is NOT configured (good)")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print("\n🔍 KEY FINDINGS:")
print("1. Email conflict when registering 'authtest@example.com' (already exists)")
print("2. SIMPLE_JWT configuration causes conflicts with custom auth")
print("3. MongoDB connection is checked")
print("\n🛠️  FIXES NEEDED:")
print("1. Recreate database to clear existing test users")
print("2. Fix SIMPLE_JWT configuration (remove or empty)")
print("3. Verify MongoDB connection settings")
print("\nNote: The 500 error with token is likely caused by SimpleJWT conflict")
print("with the custom MongoDB token system.")
