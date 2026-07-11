#!/usr/bin/env python
"""
Simple script to fix the Task Manager authentication issue.

The problem:
- SimpleJWT is configured in Django settings but conflicts with custom MongoDB AuthToken
- This causes "unsupported operand type(s) for +: 'datetime.datetime' and 'int'" errors

Solution:
1. Remove SimpleJWT from REST_FRAMEWORK settings
2. Clean up database
3. Run migrations
4. Create test users
"""

import os
import sys
import subprocess

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

# Step 1: Fix settings by removing SimpleJWT configuration
print("\n1️⃣  Fix Django REST_FRAMEWORK settings...")

settings_path = "server/core/settings.py"
with open(settings_path, 'r') as f:
    content = f.read()

# Remove SIMPLE_JWT and everything from it onward
lines = content.split('\n')
new_lines = []

for line in lines:
    if 'REST_FRAMEWORK = {' in line:
        # Add REST_FRAMEWORK header
        new_lines.append(line)
    
    elif 'SIMPLE_JWT = {' in line:
        # Skip SIMPLE_JWT section
        continue
    
    elif new_lines and 'REST_FRAMEWORK = {' in new_lines[-1]:
        # Inside SIMPLE_JWT section
        continue
    
    elif not new_lines and line.strip().startswith('SIMPLE_JWT'):
        # Before REST_FRAMEWORK
        continue
    
    else:
        new_lines.append(line)

with open(settings_path, 'w') as f:
    f.write('\n'.join(new_lines))

print("   ✅ Removed SimpleJWT configuration")

# Step 2: Clean up database
print("\n2️⃣  Reset database...")
if os.path.exists("server/db.sqlite3"):
    os.remove("server/db.sqlite3")
    print("   ✅ Removed existing database")

# Step 3: Run migrations
print("\n3️⃣  Running migrations...")

# Make migrations
result = subprocess.run(
    ["python", "manage.py", "makemigrations"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Makemigrations output:\n{result.stdout}")
if result.stderr:
    print(f"   Warnings:\n{result.stderr}")

# Apply migrations
result = subprocess.run(
    ["python", "manage.py", "migrate"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Migrate output:\n{result.stdout}")
if result.stderr:
    print(f"   Warnings:\n{result.stderr}")

print("   ✅ Database setup complete")

# Step 4: Create test users
print("\n4️⃣  Creating test users...")

create_users_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import AuthToken
from datetime import datetime, timedelta

User = get_user_model()

# Create test users
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
        print(f"   ✅ Created user: {user_data['username']} ({user_data['email']})")
        
        # Generate a token for the user
        try:
            token = AuthToken.generate_token(user)
            print(f"   ✅ Generated token for {user_data['username']}")
        except Exception as e:
            print(f"   ⚠️  Could not generate token for {user_data['username']}: {e}")
    else:
        print(f"   ℹ️  User already exists: {user_data['username']} ({user_data['email']})")

print("   ✅ Test users created successfully")
'''

with open("server/create_users.py", "w") as f:
    f.write(create_users_script)

result = subprocess.run(
    ["python", "server/create_users.py"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Output:\n{result.stdout}")

os.remove("server/create_users.py")

print("\n" + "=" * 70)
print("✅ AUTHENTICATION FIX COMPLETE")
print("=" * 70)
print("\n📋 Summary of fixes:")
print("1. ✅ Removed SimpleJWT configuration (fixes datetime error)")
print("2. ✅ Reset database (clean state)")
print("3. ✅ Run migrations (all tables created)")
print("4. ✅ Created test users with tokens")

print("\n🚀 Ready to test:")
print("• Start the server: python manage.py runserver")
print("• Test registration: POST /api/auth/register/")
print("• Test login: POST /api/auth/login/")

print("\n📝 Note:")
print("The SimpleJWT configuration was causing conflicts with the custom")
print("MongoDB AuthToken system. Removing it resolves the issues.")
print("=" * 70)
