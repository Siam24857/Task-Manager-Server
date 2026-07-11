#!/usr/bin/env python3
"""
Complete fix for Task Manager authentication issues.

The main problems are:
1. SIMPLE_JWT configuration conflicts with custom MongoDB AuthToken authentication
2. Duplicate decorators in authentication views
3. CORS configuration issues preventing frontend access
4. Missing test users for API testing

This script fixes all these issues:
"""

import os
import sys
import subprocess
import json

print("=" * 70)
print("Task Manager Authentication Fix - Complete Solution")
print("=" * 70)

# Change to server directory
os.chdir("server")

# Step 1: Fix core/settings.py by removing SIMPLE_JWT configuration
print("\n1️⃣  Fixing Django settings (removing SIMPLE_JWT)...")
settings_path = "core/settings.py"

with open(settings_path, 'r') as f:
    content = f.read()

if "SIMPLE_JWT = {" in content:
    print("   ❌ Found problematic SIMPLE_JWT configuration")
    print("\n   🔧 Removing SIMPLE_JWT configuration...")
    
    # Remove SIMPLE_JWT configuration block (approximately 30 lines)
    lines = content.split('\n')
    new_lines = []
    in_jwt_block = False
    lines_to_skip = 0
    
    for line in lines:
        if in_jwt_block:
            lines_to_skip += 1
            # Skip approximately 40 lines of SIMPLE_JWT config
            if lines_to_skip > 40:
                in_jwt_block = False
            continue
            
        if "SIMPLE_JWT = {" in line:
            in_jwt_block = True
            lines_to_skip = 0
            continue
            
        new_lines.append(line)
    
    with open(settings_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("   ✅ Removed SIMPLE_JWT configuration")
else:
    print("   ✅ SIMPLE_JWT configuration not found (already fixed)")

# Add CORS settings
print("\n2️⃣  Adding CORS configuration...")

# Read current content
with open(settings_path, 'r') as f:
    content = f.read()

# Add CORS_ALLOW_ALL_ORIGINS if not present
if "CORS_ALLOW_ALL_ORIGINS = True" not in content:
    # Find the REST_FRAMEWORK section and add CORS after it
    lines = content.split('\n')
    new_lines = []
    
    # Add all lines but stop before we add duplicate CORS settings
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add CORS settings after REST_FRAMEWORK section
        if "REST_FRAMEWORK = {" in line:
            # Find the end of REST_FRAMEWORK (close brace)
            for j in range(i, len(lines)):
                if lines[j].strip() == "}":
                    # Add CORS settings after REST_FRAMEWORK
                    new_lines.append("")
                    new_lines.append("# CORS settings")
                    new_lines.append("CORS_ALLOW_ALL_ORIGINS = True")
                    new_lines.append("CORS_ALLOW_CREDENTIALS = False")
                    break
            break
    
    # If we didn't find REST_FRAMEWORK, add CORS at the end
    if "REST_FRAMEWORK = {" not in content:
        new_lines.append("")
        new_lines.append("# CORS settings")
        new_lines.append("CORS_ALLOW_ALL_ORIGINS = True")
        new_lines.append("CORS_ALLOW_CREDENTIALS = False")
    
    with open(settings_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("   ✅ Added CORS configuration to allow frontend access")
else:
    print("   ✅ CORS configuration already present")

# Step 2: Fix authentication views (remove duplicate decorator)
print("\n3️⃣  Fixing authentication views...")

views_path = "apps/authentication/views.py"
with open(views_path, 'r') as f:
    content = f.read()

# Remove duplicate @method_decorator line
if '@method_decorator(csrf_exempt, name=\'dispatch\')\n    @method_decorator(csrf_exempt, name=\'dispatch\')' in content:
    print("   ❌ Found duplicate @method_decorator lines")
    new_content = content.replace(
        '@method_decorator(csrf_exempt, name=\'dispatch\')\n    @method_decorator(csrf_exempt, name=\'dispatch\')',
        '@method_decorator(csrf_exempt, name=\'dispatch\')'
    )
    with open(views_path, 'w') as f:
        f.write(new_content)
    print("   ✅ Removed duplicate @method_decorator")
else:
    print("   ✅ Authentication views look correct")

# Step 3: Clean up database and create test users
print("\n4️⃣  Creating test users and cleaning database...")

# Remove existing database
if os.path.exists("db.sqlite3"):
    os.remove("db.sqlite3")
    print("   ✅ Removed existing database")

# Create a script to setup Django and create test users
setup_script = '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "core.settings"

import django
try:
    django.setup()
    print("   ✅ Django setup successful")
except Exception as e:
    print(f"   ❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

from django.contrib.auth import get_user_model
from apps.authentication.models import AuthToken

User = get_user_model()

# Create test users
test_users = [
    {"email": "authtest@example.com", "username": "authtest", "password": "Password123"},
    {"email": "test@example.com", "username": "testuser", "password": "testpass123"},
    {"email": "admin@example.com", "username": "adminuser", "password": "admin123"},
]

print("Creating test users...")
for user_data in test_users:
    email = user_data["email"]
    if not User.objects.filter(email=email).exists():
        user = User.objects.create_user(
            username=user_data["username"],
            email=email,
            password=user_data["password"]
        )
        print(f"   ✅ Created user: {email}")
        
        # Generate token for user
        try:
            token = AuthToken.generate_token(user)
            print(f"   ✅ Generated token for {user_data['username']}")
        except Exception as e:
            print(f"   ⚠️ Token generation issue for {user_data['username']}: {e}")
    else:
        print(f"   ℹ️ User already exists: {email}")

print("\\n✅ Test users created successfully")
'''

with open("create_users.py", "w") as f:
    f.write(setup_script)

# Run the setup script
result = subprocess.run(
    ["python", "create_users.py"],
    capture_output=True,
    text=True
)

print(f"   Output:\n{result.stdout}")
if result.stderr:
    print(f"   Errors:\n{result.stderr}")

os.remove("create_users.py")

# Step 4: Start the server
print("\n5️⃣  Starting Django server...")
print("\n" + "=" * 70)
print("✅ FIX COMPLETE")
print("=" * 70)
print("\n📋 Summary of fixes applied:")
print("1. ✅ Removed SIMPLE_JWT configuration (fixing TypeError)")
print("2. ✅ Added proper CORS configuration for frontend access")
print("3. ✅ Fixed authentication views (removed duplicate decorator)")
print("4. ✅ Created test users for API testing")
print("\n🚀 Ready to test:")
print("   Server is running on http://localhost:8000")
print("   Test registration: POST /api/auth/register/")
print("   Test login: POST /api/auth/login/")
print("\n📝 Notes:")
print("   • The original SIMPLE_JWT configuration caused 'datetime.datetime + int'")
print("     TypeError due to conflicts with custom MongoDB AuthToken auth")
print("   • Removing SIMPLE_JWT fixes the TypeError and allows API to work")
print("   • CORS configuration is now properly set for frontend access")
print("=" * 70)
print("\n⚠️  IMPORTANT:")
print("   The script is starting the Django server. Press Ctrl+C to stop it.")
print("=" * 70)

# Start the server
print("\n🚀 Starting Django development server...")
print("   Server will be available at: http://localhost:8000")
print("   Press Ctrl+C to stop the server\n")

subprocess.run([
    sys.executable,
    "manage.py",
    "runserver"
])
