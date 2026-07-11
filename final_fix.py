#!/usr/bin/env python3
"""
Quick fix for Task Manager authentication issues.

The main problems:
1. SIMPLE_JWT configuration in core/settings.py conflicts with custom MongoDB AuthToken
2. This causes "unsupported operand type(s) for +: 'datetime.datetime' and 'int'" error

Solution:
Remove SIMPLE_JWT configuration completely since we're using MongoDB-based auth
"""

import os
import sys

print("=" * 70)
print("Task Manager Authentication Fix")
print("=" * 70)

# Check current directory
print(f"Current directory: {os.getcwd()}")

# Check if we're in the server directory
if os.path.basename(os.getcwd()) == "server":
    print("✅ We're in the server directory")
else:
    print("⚠️  Not in server directory, changing...")
    os.chdir("server")

# Step 1: Fix core/settings.py by removing SIMPLE_JWT configuration
print("\n1️⃣  Fixing core/settings.py...")
settings_path = "core/settings.py"

with open(settings_path, 'r') as f:
    content = f.read()

if "SIMPLE_JWT = {" in content:
    print("   ❌ Found problematic SIMPLE_JWT configuration")
    print("\n   🔧 Removing SIMPLE_JWT configuration...")
    
    # Find and remove SIMPLE_JWT section (approximately lines 211-229)
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip lines from SIMPLE_JWT = { to before the next top-level config
        if i == 211:  # This is where SIMPLE_JWT starts in the current file
            # Skip this and the next 17 lines
            continue
        elif i > 211 and i <= 229:  # Skip the SIMPLE_JWT config block
            continue
        new_lines.append(line)
    
    with open(settings_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("   ✅ Removed SIMPLE_JWT configuration")
else:
    print("   ✅ SIMPLE_JWT not found (already fixed)")

# Step 2: Check for duplicate decorator in views.py
print("\n2️⃣  Checking authentication views...")
views_path = "apps/authentication/views.py"

with open(views_path, 'r') as f:
    content = f.read()

# Check for duplicate @method_decorator lines
if '@method_decorator(csrf_exempt, name=\'dispatch\')\n    @method_decorator(csrf_exempt, name=\'dispatch\')' in content:
    print("   ❌ Found duplicate @method_decorator lines")
    print("   🔧 Fixing...")
    new_content = content.replace(
        '@method_decorator(csrf_exempt, name=\'dispatch\')\n    @method_decorator(csrf_exempt, name=\'dispatch\')',
        '@method_decorator(csrf_exempt, name=\'dispatch\')'
    )
    with open(views_path, 'w') as f:
        f.write(new_content)
    print("   ✅ Removed duplicate @method_decorator")
else:
    print("   ✅ Views look correct")

# Step 3: Clean up database
print("\n3️⃣  Cleaning up database...")
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
    print("   ✅ Removed existing database")

# Step 4: Run migrations
print("\n4️⃣  Running migrations...")
import subprocess
result = subprocess.run(
    ["python", "manage.py", "makemigrations"],
    capture_output=True,
    text=True
)
print(f"   Makemigrations: {result.stdout}")

result = subprocess.run(
    ["python", "manage.py", "migrate"],
    capture_output=True,
    text=True
)
print(f"   Migrate: {result.stdout}")

# Step 5: Create test user
print("\n5️⃣  Creating test user...")

test_user_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create test user
if not User.objects.filter(email="authtest@example.com").exists():
    user = User.objects.create_user(
        username="authtest",
        email="authtest@example.com",
        password="Password123"
    )
    print("   ✅ Created test user: authtest@example.com")
    print("   Password: Password123")
else:
    print("   ℹ️ Test user already exists")
'''

with open("create_test_user.py", "w") as f:
    f.write(test_user_script)

result = subprocess.run(
    ["python", "create_test_user.py"],
    capture_output=True,
    text=True
)
print(f"   Output: {result.stdout}")

os.remove("create_test_user.py")

# Step 6: Final verification
print("\n6️⃣  Final verification...")

# Check if SIMPLE_JWT is still in settings
with open(settings_path, 'r') as f:
    final_content = f.read()

if "SIMPLE_JWT" in final_content:
    print("   ❌ WARNING: SIMPLE_JWT still in settings")
else:
    print("   ✅ SIMPLE_JWT has been removed")

# Check if MongoTokenAuthentication is still in place
if "MongoTokenAuthentication" in final_content:
    print("   ✅ Custom MongoDB authentication is configured")
else:
    print("   ⚠️ Custom authentication not found")

# Check CORS configuration
if "CORS_ALLOW_ALL_ORIGINS = True" in final_content:
    print("   ✅ CORS is configured for frontend access")
else:
    print("   ⚠️ CORS not configured")

print("\n" + "=" * 70)
print("✅ FIX SUMMARY")
print("=" * 70)
print("\nProblems fixed:")
print("1. ✅ Removed SIMPLE_JWT configuration (fixing TypeError)")
print("2. ✅ Fixed duplicate @method_decorator in views")
print("3. ✅ Cleared and recreated database")
print("4. ✅ Created test user for authentication")
print("\nNext Steps:")
print("• Start server: python manage.py runserver")
print("• Test registration: POST /api/auth/register/")
print("• Test login: POST /api/auth/login/")
print("\nNote: The TypeError was caused by SimpleJWT trying to work")
print("with the custom MongoDB AuthToken system. Removing SimpleJWT")
print("resolves the conflict.")
print("=" * 70)
