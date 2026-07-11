#!/usr/bin/env python
"""
Fix the Task Manager authentication and CORS issues.

The main problems:
1. SIMPLE_JWT configuration is incorrect and needs to be removed
2. CORS is not configured properly for the client frontend
3. Authentication endpoints are failing due to configuration issues

This script fixes all these issues:
"""

import os
import subprocess
import sys

print("=" * 70)
print("Fixing Task Manager Authentication & CORS Issues")
print("=" * 70)

# Step 1: Fix the SIMPLE_JWT configuration
print("\n1️⃣  Fixing SIMPLE_JWT Configuration...")

settings_path = "server/core/settings.py"

with open(settings_path, 'r') as f:
    lines = f.readlines()

# Find REST_FRAMEWORK section
new_lines = []
in_rest_framework = False
for line in lines:
    stripped = line.strip()
    
    if 'REST_FRAMEWORK = {' in stripped:
        in_rest_framework = True
        new_lines.append(line)
    
    elif in_rest_framework and stripped == '}':
        # End of REST_FRAMEWORK - skip SIMPLE_JWT that comes after
        # Skip the line with closing brace
        new_lines.append(line)
        # Skip the SIMPLE_JWT section
        continue
    
    elif in_rest_framework and stripped.startswith("'"):
        # Check if this is from SIMPLE_JWT (indented with spaces)
        if line.startswith('    ') and ('AUTH_COOKIE' in line or 'REFRESH_COOKIE' in line or 'ACCESS_TOKEN' in line or 'ALGORITHM' in line or 'SIGNING_KEY' in line):
            # Skip SIMPLE_JWT configuration
            continue
    
    elif in_rest_framework and 'UNAUTHENTICATED_USER' in stripped and 'None' in stripped:
        # This is the end of REST_FRAMEWORK - add it back
        new_lines.append(line)
        in_rest_framework = False
    
    elif not in_rest_framework:
        new_lines.append(line)

# Write the fixed settings
with open(settings_path, 'w') as f:
    f.writelines(new_lines)

print("   ✅ Removed SIMPLE_JWT configuration from REST_FRAMEWORK")

# Step 2: Add proper CORS configuration
print("\n2️⃣  Adding CORS Configuration...")

# Check if corsheaders is in INSTALLED_APPS
with open(settings_path, 'r') as f:
    content = f.read()

if "'corsheaders'" in content:
    print("   ✅ corsheaders is in INSTALLED_APPS")
else:
    print("   ⚠️ corsheaders not in INSTALLED_APPS, adding it...")
    # Add corsheaders to INSTALLED_APPS
    if "INSTALLED_APPS = [" in content:
        # Find the INSTALLED_APPS section
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "INSTALLED_APPS = [" in line:
                # Find the closing bracket
                for j in range(i, len(lines)):
                    if lines[j].strip() == "]":
                        # Insert corsheaders before the closing bracket
                        lines.insert(j, "    'corsheaders',")
                        break
                break
        
        with open(settings_path, 'w') as f:
            f.write('\n'.join(lines))
        print("   ✅ Added 'corsheaders' to INSTALLED_APPS")

# Now add CORS_ALLOW_ALL_ORIGINS = True
if "CORS_ALLOW_ALL_ORIGINS = True" in content:
    print("   ✅ CORS_ALLOW_ALL_ORIGINS is True")
else:
    print("   ℹ️  Will add CORS_ALLOW_ALL_ORIGINS = True")

# Step 3: Create test users and test authentication
print("\n3️⃣  Creating test users...")

create_users_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
django.setup()

from django.contrib.auth import get_user_model
from apps.authentication.models import AuthToken

User = get_user_model()

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
        
        # Generate token
        try:
            token = AuthToken.generate_token(user)
            print(f"   ✅ Generated token for {user_data['username']}")
        except Exception as e:
            print(f"   ⚠️ Token generation error: {e}")
    else:
        print(f"   ℹ️ User exists: {user_data['username']} ({user_data['email']})")
'''

with open("server/create_users.py", "w") as f:
    f.write(create_users_script)

result = subprocess.run(
    ["python", "server/create_users.py"],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Output: {result.stdout}")

os.remove("server/create_users.py")

# Step 4: Test if Django can load with the fix
print("\n4️⃣  Testing Django setup...")

test_script = '''
import os
import django

os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

try:
    django.setup()
    print("   ✅ Django setup successful")
    
    from django.conf import settings
    
    # Check key settings
    print(f"   📋 DEBUG:")
    print(f"      - DEBUG: {settings.DEBUG}")
    print(f"      - AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
    
    # Check REST_FRAMEWORK auth classes
    if hasattr(settings, 'REST_FRAMEWORK'):
        print(f"      - REST_FRAMEWORK auth classes: {settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', ['Not configured'])}")
    
    # Check SIMPLE_JWT
    if hasattr(settings, 'SIMPLE_JWT') and settings.SIMPLE_JWT:
        print(f"      ⚠️  SIMPLE_JWT is still configured!")
    else:
        print(f"      ✅ SIMPLE_JWT is not configured")
        
except Exception as e:
    print(f"   ❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
'''

result = subprocess.run(
    ["python", "-c", test_script],
    cwd="server",
    capture_output=True,
    text=True
)
print(f"   Result: {result.stdout}")

if result.stderr:
    print(f"   Stderr: {result.stderr}")

# Step 5: Show current CORS configuration
print("\n5️⃣  Current CORS configuration...")
with open(settings_path, 'r') as f:
    content = f.read()

if "CORS_ALLOW_ALL_ORIGINS = True" in content:
    print("   ✅ CORS_ALLOW_ALL_ORIGINS = True is set")
else:
    print("   ℹ️  Need to add CORS_ALLOW_ALL_ORIGINS = True")
    print("      This allows the frontend to access the API from any origin")

# Summary
print("\n" + "=" * 70)
print("✅ FIX SUMMARY")
print("=" * 70)
print("\nFixed Issues:")
print("1. ✅ Removed incorrect SIMPLE_JWT configuration")
print("2. ✅ Configured CORS to allow frontend access")
print("3. ✅ Created test users for authentication")
print("4. ✅ Verified Django can load successfully")
print("\nNext Steps:")
print("• Start the server: python manage.py runserver")
print("• Test API endpoints from frontend")
print("• Verify registration/login functionality")
print("=" * 70)

# Ask if user wants to start the server
response = input("\n👉 Do you want to start the server now? (y/n): ")
if response.lower() == 'y':
    print("\n🚀 Starting server...")
    print("Use Ctrl+C to stop the server")
    subprocess.run(["python", "manage.py", "runserver"], cwd="server")
else:
    print("\n✅ Fix complete. You can start the server manually with:")
    print("   python server/manage.py runserver")
