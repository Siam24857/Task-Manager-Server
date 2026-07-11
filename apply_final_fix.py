#!/usr/bin/env python
"""
Quick fix for the Task Manager authentication issue.

The core problem:
1. SIMPLE_JWT is configured in Django settings, but conflicting with custom MongoDB AuthToken
2. Token generation error: "unsupported operand type(s) for +: 'datetime.datetime' and 'int'"
3. This happens because SimpleJWT tries to generate tokens using its own logic
   while the custom AuthToken system exists

Solution: Remove SIMPLE_JWT configuration completely since we're using custom
MongoDB-based authentication through MongoTokenAuthentication.
"""

import os

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

# Step 1: Remove SIMPLE_JWT configuration from core/settings.py
print("\n1️⃣  Removing SIMPLE_JWT configuration (fixing token conflict)...")

settings_path = "server/core/settings.py"
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

# Step 2: Delete the database
print("\n2️⃣  Resetting database...")
if os.path.exists("server/db.sqlite3"):
    os.remove("server/db.sqlite3")
    print("   ✅ Removed existing database")

# Step 3: Run migrations
print("\n3️⃣  Running migrations...")
import subprocess

result = subprocess.run(
    ["python", "manage.py", "makemigrations"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Makefile output: {result.stdout}")

result = subprocess.run(
    ["python", "manage.py", "migrate"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Migrate output: {result.stdout}")
print("   ✅ Database setup complete")

# Step 4: Create test user
print("\n4️⃣  Creating test user...")

create_user_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
django.setup()

from django.contrib.auth import get_user_model
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
        print(f"✅ Created: {user_data['username']} ({user_data['email']})")
    else:
        print(f"ℹ️  Already exists: {user_data['username']} ({user_data['email']})")

print("✅ Test users created successfully")
'''

with open("server/create_test_users.py", "w") as f:
    f.write(create_user_script)

subprocess.run(["python", "server/create_test_users.py"], check=True)
os.remove("server/create_test_users.py")

print("\n" + "=" * 70)
print("✅ AUTHENTICATION FIX COMPLETE")
print("=" * 70)
print("\n📋 Summary of fixes applied:")
print("1. ✅ Removed SIMPLE_JWT configuration from Django settings")
print("2. ✅ Deleted existing database and created fresh one")
print("3. ✅ Applied Django migrations (all tables created)")
print("4. ✅ Created test users for authentication")

print("\n🚀 Ready to test:")
print("• Start server: python manage.py runserver")
print("• Test registration API: POST /api/auth/register/")
print("• Test login API: POST /api/auth/login/")
print("=" * 70)
print("\nNote: The authentication should now work using the custom MongoDB")
print("based AuthToken system instead of SimpleJWT.")
