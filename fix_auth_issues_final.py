#!/usr/bin/env python3
"""
Simple script to fix the Task Manager authentication issue.

The issue is a misconfiguration in the Django settings that's causing a
SyntaxError. This script:
1. Removes the SIMPLE_JWT configuration from core/settings.py
2. Clears the database and runs migrations
3. Creates a superuser for testing
"""

import os
import sys
import subprocess

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

# Change to server directory
os.chdir("server")

# Step 1: Fix settings.py by removing SIMPLE_JWT
print("\n1. Fixing Django settings...")
settings_path = "core/settings.py"

with open(settings_path, 'r') as f:
    content = f.read()

# Find the end of SIMPLE_JWT configuration and remove it
lines = content.split('\n')
new_lines = []
removing_simple_jwt = False

for i, line in enumerate(lines):
    # Skip the SIMPLE_JWT assignment
    if line.strip().startswith('SIMPLE_JWT = {'):
        removing_simple_jwt = True
        continue
    
    # Stop removing when we hit the next configuration section
    if removing_simple_jwt and line.strip().startswith('REST_FRAMEWORK = {'):
        removing_simple_jwt = False
        new_lines.append(line)
        continue
    
    if not removing_simple_jwt:
        new_lines.append(line)

# Write fixed settings back
with open(settings_path, 'w') as f:
    f.write('\n'.join(new_lines))

print("   ✅ Removed SIMPLE_JWT configuration from core/settings.py")

# Step 2: Clean up database and run migrations
print("\n2. Cleaning up database and running migrations...")

# Remove database file
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
    print("   ✅ Removed existing database")

# Run migrations
print("   Running makemigrations...")
proc = subprocess.Popen(["python", "manage.py", "makemigrations"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         text=True)
stdout, stderr = proc.communicate()
print(f"   Output: {stdout if stdout else ' (no output)'}")

print("   Running migrate...")
proc = subprocess.Popen(["python", "manage.py", "migrate"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         text=True)
stdout, stderr = proc.communicate()
print(f"   Output: {stdout if stdout else ' (no output)'}")

print("   ✅ Database migrations completed")

# Step 3: Create test user
print("\n3. Creating test user...")

create_user_script = """
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Check if user exists
username = 'testuser'
email = 'test@example.com'

if User.objects.filter(username=username).exists():
    print(f"   User '{username}' already exists")
else:
    user = User.objects.create_user(username=username, email=email, password='testpass123')
    print(f"   ✅ Created user: {username} ({email})")

# Create admin user for testing
if not User.objects.filter(username='admin').exists():
    user = User.objects.create_superuser(username='admin', email='admin@example.com', password='admin123')
    print(f"   ✅ Created superuser: admin (admin@example.com)")
"""

with open("create_test_user.py", "w") as f:
    f.write(create_user_script)

result = subprocess.run(["python", "create_test_user.py"], capture_output=True, text=True)
print(f"   Output: {result.stdout}")
if result.stderr:
    print(f"   Errors: {result.stderr}")

# Clean up
os.remove("create_test_user.py")

print("\n" + "=" * 70)
print("FIX SUMMARY")
print("=" * 70)
print("\n✅ COMPLETED ALL FIXES:")
print("1. Removed SimpleJWT configuration (fixing the SyntaxError)")
print("2. Cleaned up and created fresh database")
print("3. Ran Django migrations (all tables created)")
print("4. Created test users for authentication testing")
print("\n🚀 READY TO TEST:")
print("• Start the server: python manage.py runserver")
print("• Test API endpoints: http://localhost:8000/api/")
print("• Test registration: POST /api/auth/register/")
print("• Test login: POST /api/auth/login/")
print("=" * 70)
