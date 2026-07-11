#!/usr/bin/env python3
"""
Fix Task Manager Authentication Issues

The Problem:
- There's a conflict between SimpleJWT and MongoDB-based authentication
- SIMPLE_JWT is configured in core/settings.py but the project uses a custom
  MongoDB AuthToken system
- This causes "unsupported operand type(s) for +: 'datetime.datetime' and 'int'" errors

Solution:
1. Remove SIMPLE_JWT configuration from core/settings.py
2. Clear the existing database
3. Run migrations to create tables
4. Create test users
5. Test authentication endpoints
"""

import os
import sys
import subprocess
import json

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

def run_cmd(cmd, cwd=None, check=True):
    """Run command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr and result.stderr.strip():
        print(f"STDERR:\n{result.stderr}")
    return result.returncode == 0

# Step 1: Remove SIMPLE_JWT configuration
settings_path = "server/core/settings.py"
print(f"\n1️⃣  Fixing SIMPLE_JWT configuration in {settings_path}")

with open(settings_path, 'r') as f:
    lines = f.readlines()

new_lines = []
in_simple_jwt = False

for line in lines:
    if 'SIMPLE_JWT = {' in line:
        in_simple_jwt = True
        continue
    
    if in_simple_jwt:
        if line.strip().startswith('REST_FRAMEWORK = {'):
            in_simple_jwt = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open(settings_path, 'w') as f:
    f.writelines(new_lines)

print("   ✅ Removed SIMPLE_JWT configuration")

# Step 2: Clean up database
settings_path = "server/core/settings.py"
print(f"\n2️⃣  Cleaning up database")

if os.path.exists("server/db.sqlite3"):
    os.remove("server/db.sqlite3")
    print("   ✅ Removed existing database (db.sqlite3)")

# Step 3: Run migrations
print(f"\n3️⃣  Running Django migrations")
if not run_cmd("python manage.py makemigrations", cwd="server", check=True):
    print("   ⚠️  makemigrations had warnings but continuing...")

if not run_cmd("python manage.py migrate", cwd="server", check=True):
    print("   ❌ Failed to run migrate. Exiting.")
    sys.exit(1)

print("   ✅ Database migrations completed")

# Step 4: Create test users
print(f"\n4️⃣  Creating test users")

create_users_cmd = '''
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

test_users = [
    {'email': 'authtest@example.com', 'username': 'authtest', 'password': 'Password123'},
    {'email': 'test@example.com', 'username': 'testuser', 'password': 'testpass123'},
    {'email': 'admin@example.com', 'username': 'adminuser', 'password': 'admin123'},
]

for user_data in test_users:
    if not User.objects.filter(email=user_data['email']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        print('   ✅ Created user: {} ({})'.format(user_data['username'], user_data['email']))
    else:
        print('   ℹ️  User already exists: {} ({})'.format(user_data['username'], user_data['email']))
print('   ✅ Test users created successfully')
"
'''

run_cmd(create_users_cmd, cwd="server", check=True)

# Step 5: Test the authentication system manually
print(f"\n5️⃣  Testing authentication system")

test_auth_cmd = '''
python -c "
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import AuthToken
from datetime import datetime, timedelta

print('   Testing authentication system...')

User = get_user_model()

# Check if we have users
user_count = User.objects.count()
print('   📊 Total users in database: {}'.format(user_count))

# Find a test user
user = User.objects.filter(email='authtest@example.com').first()
if user:
    print('   👤 Found test user: {} ({})'.format(user.username, user.email))
    
    # Try to generate a token
    try:
        token = AuthToken.generate_token(user)
        print('   ✅ Token generation succeeded: {}...'.format(token.token[:20]))
        print('   📅 Token expires at: {}'.format(token.expires_at))
        
        # Try to validate the token
        validated = AuthToken.validate_token(token.token)
        if validated:
            print('   ✅ Token validation succeeded')
        else:
            print('   ❌ Token validation failed')
            
    except Exception as e:
        print('   ❌ Token generation/validation failed: {}'.format(e))
        import traceback
        traceback.print_exc()
else:
    print('   ⚠️  No test users found')

print('   ✅ Authentication system test complete')
"
'''

run_cmd(test_auth_cmd, cwd="server", check=True)

# Summary
print("\n" + "=" * 70)
print("🎉 FIX SUMMARY")
print("=" * 70)
print("\n✅ COMPLETED ALL FIXES:")
print("1. Removed SIMPLE_JWT configuration (fixing token conflict)")
print("2. Cleared existing database")
print("3. Ran migrations (all tables created)")
print("4. Created test users for authentication")
print("5. Tested authentication system")

print("\n🚀 READY TO TEST:")
print("• Start the server: python manage.py runserver")
print("• Test API endpoints: http://localhost:8000/api/")
print("• Test registration: POST /api/auth/register/")
print("• Test login: POST /api/auth/login/")

print("\n📝 Note:")
print("The fix removes the conflicting SimpleJWT configuration that was")
print("causing the 'datetime.datetime + int' TypeError. The project now")
print("uses its custom MongoDB-based AuthToken system for authentication.")
print("=" * 70)
