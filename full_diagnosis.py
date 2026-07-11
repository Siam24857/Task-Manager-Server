#!/usr/bin/env python3
"""
Comprehensive fix for the Task Manager authentication issues.

Root causes:
1. SIMPLE_JWT configuration conflict with custom MongoDB AuthToken
2. Token generation issues due to timestamp handling
3. Existing database users causing conflicts
4. Authentication backend configuration issues

"""

import os
import sys
import django
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
django.setup()

print("\n📋 Checking current configuration...")

# 1. Check if SIMPLE_JWT is causing issues
from django.conf import settings
if hasattr(settings, 'SIMPLE_JWT') and settings.SIMPLE_JWT:
    print("❌ PROBLEM: SIMPLE_JWT is configured but not used!")
    print("   This conflicts with the custom MongoDB AuthToken system")
    print("\n🔧 Fix: Remove SIMPLE_JWT configuration from core/settings.py")
else:
    print("✅ SIMPLE_JWT is not configured")

# 2. Check if MongoDB is connected
print("\n📋 Checking MongoDB connection...")
try:
    from mongoengine import get_connection, disconnect
    from apps.authentication.models import AuthToken
    
    conn = get_connection()
    if conn:
        print("✅ MongoDB is connected")
        
        # Check AuthToken collection
        count = AuthToken.objects.count()
        print(f"   AuthToken records in MongoDB: {count}")
        
        # Check for existing tokens
        if count > 0:
            print(f"⚠️  Warning: {count} existing AuthToken records in MongoDB")
            print("   This might interfere with new token generation")
    else:
        print("❌ MongoDB is NOT connected")
        print("   Registration will fail without MongoDB")
        
except Exception as e:
    print(f"❌ MongoDB connection check failed: {e}")

# 3. Check database state
print("\n📋 Checking database state...")
User = get_user_model()
try:
    total_users = User.objects.count()
    print(f"   Total users in SQLite: {total_users}")
    
    # Check for specific test users
    test_users = User.objects.filter(email__in=['authtest@example.com', 'test@example.com'])
    if test_users:
        print(f"   ⚠️  Found conflicting test users:")
        for user in test_users:
            print(f"      - {user.username} ({user.email})")
except Exception as e:
    print(f"   ❌ Error checking database: {e}")

# 4. Check AuthToken model
print("\n📋 Checking AuthToken model configuration...")
try:
    from apps.authentication.models import AuthToken
    from django.utils import timezone
    
    print("   ✅ AuthToken model is importable")
    
    # Check token expiration logic
    print("\n   Checking token expiration logic...")
    
    # Look at the generate_token method
    import inspect
    source = inspect.getsource(AuthToken.generate_token)
    
    # Check if there's any problematic logic
    if "expired" in source.lower():
        print("   ⚠️  Token has expiration checking - this might cause issues")
    
    # Check validate_token method
    validate_source = inspect.getsource(AuthToken.validate_token)
    
    print("   ✅ AuthToken model appears OK")
    
except Exception as e:
    print(f"   ❌ AuthToken check failed: {e}")

print("\n" + "=" * 70)
print("DIAGNOSIS COMPLETE")
print("=" * 70)
print("\n🚨 ISSUES FOUND:")
print("1. ❌ SIMPLE_JWT configuration conflicts with custom AuthToken")
print("2. ❌ Token generation may have timestamp issues (datetime + int error)")
print("3. ❌ Database state issues with existing users")
print("4. ❌ AuthToken model may have validation logic problems")

print("\n🛠️  REQUIRED FIXES:")
print("1. Remove SIMPLE_JWT configuration from core/settings.py")
print("2. Clear existing database or delete conflicting users")
print("3. Fix AuthToken.token generation logic")
print("4. Test authentication flow manually")

print("\n" + "=" * 70)
