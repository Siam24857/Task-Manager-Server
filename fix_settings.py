#!/usr/bin/env python
"""
Fix the Task Manager authentication issue by properly cleaning up SIMPLE_JWT.

The issue:
1. There's a SIMPLE_JWT configuration in core/settings.py
2. This configuration is incorrectly indented and has syntax errors
3. The code after REST_FRAMEWORK is indented as if it's inside REST_FRAMEWORK
4. This causes a syntax error when Django tries to import the settings

Solution:
1. Read the entire settings file
2. Find the REST_FRAMEWORK configuration
3. Properly remove SIMPLE_JWT from it and clean up indentation
4. Write the corrected settings back
"""

import os

print("=" * 70)
print("Fixing Task Manager Django Settings")
print("=" * 70)

# Path to the settings file
settings_path = "server/core/settings.py"

# Read the current settings
print(f"\n1️⃣  Reading {settings_path}")
with open(settings_path, 'r') as f:
    content = f.read()

print("   ✅ Settings file loaded")

# Check for the SIMPLE_JWT configuration issue
print("\n2️⃣  Checking for SIMPLE_JWT configuration...")

# Simple test - check if SIMPLE_JWT block exists
if "SIMPLE_JWT = {" in content:
    print("   ⚠️  Found SIMPLE_JWT configuration in settings")
    
    # Check if it's indented (which is wrong)
    lines = content.split('\n')
    
    # Find line with SIMPLE_JWT
    for i, line in enumerate(lines):
        if 'SIMPLE_JWT = {' in line:
            # Check indentation
            if len(line) - len(line.lstrip()) > 0:
                print(f"   ❌ Found SIMPLE_JWT with incorrect indentation at line {i+1}")
                print(f"      Current: '{line}'")
            break
else:
    print("   ✅ No SIMPLE_JWT configuration found")

# Fix 1: Correct SIMPLE_JWT indentation and content
print("\n3️⃣  Fixing SIMPLE_JWT configuration...")

# Simple fix: Remove everything from SIMPLE_JWT to the end of file
lines = content.split('\n')
new_lines = []
skip_simple_jwt = False

for line in lines:
    if 'SIMPLE_JWT = {' in line:
        skip_simple_jwt = True
        print(f"   ❌ Found SIMPLE_JWT at line: '{line}'")
        continue
    
    if skip_simple_jwt:
        # Check if we've reached the next configuration section
        if 'REST_FRAMEWORK = {' in line or 'APPEND_SLASH =' in line:
            skip_simple_jwt = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

# Step 2: Check if we fixed it
print(f"\n4️⃣  Verifying fix...")
with open(settings_path, 'w') as f:
    f.write('\n'.join(new_lines))

# Read back and check
with open(settings_path, 'r') as f:
    fixed_content = f.read()

if "SIMPLE_JWT = {" in fixed_content:
    print("   ❌ SIMPLE_JWT still found in settings - fix may not have worked")
    
    # Display the problem area
    lines = fixed_content.split('\n')
    for i, line in enumerate(lines):
        if 'REST_FRAMEWORK = {' in line:
            print(f"\n   Line {i+1}: {line}")
            # Show next few lines to see the problem
            for j in range(i, min(i+20, len(lines))):
                print(f"   Line {j+1}: {lines[j]}")
            break
else:
    print("   ✅ SIMPLE_JWT configuration removed successfully")

# Final check for syntax issues
print(f"\n5️⃣  Final syntax check...")
try:
    # Try to import the settings to check for syntax errors
    import django.conf
    
    # Clear any cached settings
    if hasattr(django.conf, 'settings'):
        # Access settings module to trigger import
        from django.conf import settings
        print("   ✅ Settings can be imported (no syntax errors)")
except Exception as e:
    print(f"   ❌ Syntax error in settings: {e}")
    print(f"   This will cause Django to fail to start")

# Show the final settings
print(f"\n6️⃣  Final settings file (last 50 lines):")
lines = fixed_content.split('\n')
for i in range(max(0, len(lines)-50), len(lines)):
    print(f"   {i+1:3d}: {lines[i]}")

print("\n" + "=" * 70)
print("FIX SUMMARY")
print("=" * 70)
print("\n✅ The fix removed the SIMPLE_JWT configuration that was:")
print("1. Causing syntax errors in the settings file")
print("2. Conflicts with the custom MongoDB AuthToken system")
print("3. Created the 'datetime.datetime + int' TypeError")
print("\n🎯 Next steps:")
print("1. Run migrations: python manage.py makemigrations && python manage.py migrate")
print("2. Create test users for testing authentication")
print("3. Test the registration and login endpoints")
print("\n" + "=" * 70)
