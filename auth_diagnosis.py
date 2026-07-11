#!/usr/bin/env python3
"""
Script to diagnose and fix the SimpleJWT authentication issue in the Task Manager project.
This script will identify the root cause and provide fixes.
"""

import os
import sys
import django
import subprocess

# Set Django settings module
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

print(f"{'='*70}")
print(f"🔍 Task Manager Authentication Diagnosis")
print(f"{'='*70}")

# Try to import and run the diagnostic
try:
    django.setup()
    print(f"\n✓ Django setup successful")
    
    from django.conf import settings
    print(f"\n📋 Configuration check:")
    print(f"  - DEBUG: {settings.DEBUG}")
    print(f"  - INSTALLED_APPS count: {len(settings.INSTALLED_APPS)}")
    print(f"  - AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    
    # Check authentication backends
    backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
    print(f"  - AUTHENTICATION_BACKENDS: {backends}")
    
    # Check SIMPLE_JWT
    simple_jwt = getattr(settings, 'SIMPLE_JWT', 'NOT_CONFIGURED')
    print(f"  - SIMPLE_JWT: {'CONFIGURED' if simple_jwt != 'NOT_CONFIGURED' else 'NOT_CONFIGURED'}")
    
    # Check REST_FRAMEWORK
    rest_framework = getattr(settings, 'REST_FRAMEWORK', 'NOT_CONFIGURED')
    print(f"  - REST_FRAMEWORK: {'CONFIGURED' if rest_framework != 'NOT_CONFIGURED' else 'NOT_CONFIGURED'}")
    
    if rest_framework != 'NOT_CONFIGURED':
        auth_classes = rest_framework.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        print(f"    - DEFAULT_AUTHENTICATION_CLASSES: {auth_classes}")
    
    # Check if simplejwt is in INSTALLED_APPS
    if 'rest_framework_simplejwt' in settings.INSTALLED_APPS:
        print(f"  ✅ SimpleJWT is installed")
    else:
        print(f"  ❌ SimpleJWT is NOT installed")
        
    # Check DRF's token authentication
    if hasattr(settings, 'REST_FRAMEWORK') and 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK:
        draf_auth = settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        if any('simplejwt' in str(auth).lower() for auth in draf_auth):
            print(f"  ⚠️  DRF is trying to use SimpleJWT authentication")
        else:
            print(f"  ✅ DRF is using custom authentication")
    
    print(f"\n{'='*70}")
    print(f"DIAGNOSIS COMPLETE")
    print(f"{'='*70}")
    
    # Identify the problem
    if hasattr(settings, 'SIMPLE_JWT') and settings.SIMPLE_JWT:
        print(f"\n🚨 ISSUE FOUND: SIMPLE_JWT is configured!")
        print(f"   This creates a conflict because:")
        print(f"   1. REST_FRAMEWORK uses MongoTokenAuthentication (DRF's custom auth)")
        print(f"   2. SIMPLE_JWT is configured (typically for SimpleJWT's auth)")
        print(f"   3. This causes a conflict in DRF's authentication system")
        print(f"\n🔧 SOLUTION:")
        print(f"   Remove or comment out the SIMPLE_JWT configuration in core/settings.py")
        
    elif hasattr(settings, 'REST_FRAMEWORK') and 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK:
        draf_auth = settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        if any('simplejwt' in str(auth).lower() for auth in draf_auth):
            print(f"\n⚠️  CONFLICT FOUND: DRF is configured to use SimpleJWT!")
            print(f"   But the project has a custom MongoDB-based authentication system.")
            print(f"\n🔧 SOLUTION:")
            print(f"   Replace SimpleJWT with MongoTokenAuthentication:")
            print(f"   'DEFAULT_AUTHENTICATION_CLASSES': [")
            print(f"       'apps.authentication.authentication.MongoTokenAuthentication',")
            print(f"   ]")
            
    if 'rest_framework_simplejwt' not in settings.INSTALLED_APPS:
        print(f"\n⚠️  WARNING: SimpleJWT is not in INSTALLED_APPS")
        print(f"   This might be okay if we're not using it for DRF auth.")
        print(f"\n✅ Check if simplejwt should be in INSTALLED_APPS:")
        print(f"   The project uses custom authentication, so SimpleJWT might not be needed.")
        
    print(f"\n{'='*70}")
    print(f"All checks completed")
    print(f"{'='*70}")
    
except Exception as e:
    print(f"❌ Error during diagnosis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
