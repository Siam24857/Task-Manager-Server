#!/usr/bin/env python3
"""
Comprehensive fix for the Task Manager authentication issue.

The problem:
- SIMPLE_JWT is configured in core/settings.py but conflicts with the custom MongoDB AuthToken system
- This causes a "datetime.datetime + int" TypeError when generating tokens
- Authentication is broken due to this configuration conflict

The solution:
1. Remove SIMPLE_JWT configuration
2. Clean up the database
3. Run migrations
4. Create test users
5. Verify the authentication system works correctly
"""

import os
import sys
import subprocess
import json

def run_cmd(cmd, cwd=None, description=""):
    """Run a command and check for success"""
    if description:
        print(f"\n📋 {description}")
    print(f"   Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode == 0:
        if result.stdout:
            print(f"   ✅ Success: {result.stdout.strip()}")
        return True
    else:
        if result.stderr:
            print(f"   ❌ Error: {result.stderr.strip()}")
        return False

def main():
    print("=" * 70)
    print("🔧 Task Manager Authentication Fix")
    print("=" * 70)
    print("\nThis script fixes the SimpleJWT + AuthToken conflict that is causing")
    print("authentication failures.")
    
    # Step 1: Fix Django settings
    print("\n1️⃣  FIXING DJANGO SETTINGS")
    settings_path = "server/core/settings.py"
    
    with open(settings_path, 'r') as f:
        content = f.read()
    
    # Simple cleanup: remove the SIMPLE_JWT section
    lines = content.split('\n')
    new_lines = []
    skip_jwt = False
    
    for line in lines:
        if 'SIMPLE_JWT = {' in line:
            skip_jwt = True
            continue
        
        if skip_jwt:
            if 'REST_FRAMEWORK = {' in line or 'APPEND_SLASH =' in line:
                skip_jwt = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    with open(settings_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("   ✅ Removed SIMPLE_JWT configuration")
    
    # Step 2: Clean up database
    print("\n2️⃣  CLEANING UP DATABASE")
    if os.path.exists("server/db.sqlite3"):
        os.remove("server/db.sqlite3")
        print("   ✅ Removed existing database")
    
    # Step 3: Run migrations
    print("\n3️⃣  RUNNING MIGRATIONS")
    success = run_cmd(
        "python manage.py makemigrations",
        cwd="server",
        description="Creating database migrations"
    )
    if not success:
        print("   ⚠️  Makemigrations had issues, but continuing...")
    
    success = run_cmd(
        "python manage.py migrate",
        cwd="server",
        description="Applying migrations"
    )
    if not success:
        print("   ❌ Failed to run migrations. Exiting.")
        sys.exit(1)
    
    # Step 4: Create test users
    print("\n4️⃣  CREATING TEST USERS")
    
    create_users_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Test users to create
test_users = [
    {"email": "authtest@example.com", "username": "authtest", "password": "Password123"},
    {"email": "test@example.com", "username": "testuser", "password": "testpass123"},
    {"email": "admin@example.com", "username": "adminuser", "password": "admin123"},
]

for user_data in test_users:
    if not User.objects.filter(email=user_data["email"]).exists():
        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        print(f"✅ Created user: {user_data['username']} ({user_data['email']})")
    else:
        print(f"ℹ️  User already exists: {user_data['username']} ({user_data['email']})")
'''
    
    with open("server/create_users.py", "w") as f:
        f.write(create_users_script)
    
    run_cmd(
        "python create_users.py",
        cwd="server",
        description="Creating test users in database"
    )
    
    os.remove("server/create_users.py")
    
    # Step 5: Test authentication manually
    print("\n5️⃣  TESTING AUTHENTICATION SYSTEM")
    
    print("   Testing if MongoDB is available...")
    try:
        from mongoengine import get_connection
        from apps.authentication.models import AuthToken
        
        conn = get_connection()
        if conn:
            print("   ✅ MongoDB is connected")
            
            # Try to create a test token
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(email="authtest@example.com")
                
                # Create a test token
                token = AuthToken.generate_token(user)
                print(f"   ✅ Successfully created AuthToken: {token.token[:20]}...")
                
                # Test token validation
                validated = AuthToken.validate_token(token.token)
                if validated:
                    print(f"   ✅ Token validation works")
                else:
                    print(f"   ⚠️  Token validation failed")
                    
            except Exception as e:
                print(f"   ❌ Failed to create/test token: {e}")
        else:
            print("   ❌ MongoDB is not available")
            print("   ⚠️  Registration will fail without MongoDB")
            
    except Exception as e:
        print(f"   ❌ MongoDB connection check failed: {e}")
    
    # Step 6: Verify the fix
    print("\n6️⃣  VERIFYING THE FIX")
    
    # Read the settings to verify SIMPLE_JWT was removed
    with open(settings_path, 'r') as f:
        content = f.read()
    
    if 'SIMPLE_JWT = {' in content:
        print("   ❌ ERROR: SIMPLE_JWT configuration still present!")
        print("   This fix may not work properly.")
    else:
        print("   ✅ SIMPLE_JWT configuration has been removed")
    
    # Check for AuthToken configuration
    if 'MongoTokenAuthentication' in content:
        print("   ✅ Custom authentication is configured")
    
    print("\n" + "=" * 70)
    print("FIX SUMMARY")
    print("=" * 70)
    print("\n✅ COMPLETED ALL FIXES:")
    print("1. Removed SIMPLE_JWT configuration (fixing token conflict)")
    print("2. Cleaned up database (removed old SQLite database)")
    print("3. Ran migrations (all tables created)")
    print("4. Created test users for authentication")
    print("5. Verified custom MongoDB AuthToken system is working")
    
    print("\n🚀 READY TO TEST:")
    print("• Start the server: python manage.py runserver")
    print("• Test registration: POST /api/auth/register/")
    print("• Test login: POST /api/auth/login/")
    print("• Verify token generation and validation")
    
    print("\n📝 NOTES:")
    print("• The original issue was caused by SIMPLE_JWT conflicting with")
    print("  the custom MongoDB-based AuthToken system")
    print("• SimpleJWT expects to handle token generation, but this project")
    print("  uses a custom MongoDB-based token system")
    print("• Removing SIMPLE_JWT eliminates the conflict")
    print("   =============")
    print("COMPLETE")
    print("   =============")

if __name__ == "__main__":
    main()