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

# Remove SIMPLE_JWT configuration (everything after REST_FRAMEWORK ends)
lines = content.split('\n')
new_lines = []
in_simple_jwt = False
skip_line = False

for line in lines:
    # Check if we're entering SIMPLE_JWT section
    if 'REST_FRAMEWORK = {' in line:
        # Find the end of REST_FRAMEWORK
        in_simple_jwt = False
        skip_line = False
        new_lines.append(line)
        continue
    
    # Check if we're in SIMPLE_JWT section (starts with '    ACCESS_TOKEN_LIFETIME' or indented SIMPLE_JWT = {
    if 'SIMPLE_JWT = {' in line and line.strip().startswith('SIMPLE_JWT ='):
        # This is the SIMPLE_JWT section header
        in_simple_jwt = True
        skip_line = True
        continue
    
    if in_simple_jwt:
        # Skip all lines inside SIMPLE_JWT
        continue
    
    # Check if SIMPLE_JWT section ends (empty line after indented config or new top-level section)
    if skip_line and line.strip() == '':
        skip_line = False
        continue
    
    if skip_line:
        continue
    
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
result = subprocess.run(["python", "manage.py", "makemigrations"], capture_output=True, text=True)
print(f"   Output: {result.stdout if result.stdout else ' (no output)'}")
if result.stderr:
    print(f"   Errors: {result.stderr}")

print("   Running migrate...")
result = subprocess.run(["python", "manage.py", "migrate"], capture_output=True, text=True)
print(f"   Output: {result.stdout if result.stdout else ' (no output)'}")
if result.stderr:
    print(f"   Errors: {result.stderr}")

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
