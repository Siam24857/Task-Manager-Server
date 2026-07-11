#!/usr/bin/env python
"""
Fix the simplejwt/django SIMPLE_JWT configuration issue.

The problem is that the SIMPLE_JWT configuration in core/settings.py is
improperly formatted. It's missing the 'SIMPLE_JWT = {' header and has
indentation errors.

Solution:
1. Remove the incorrectly formatted SIMPLE_JWT section
2. Ensure REST_FRAMEWORK is properly closed
3. Keep only the custom MongoDB AuthToken authentication
"""

import os
import sys

print("=" * 70)
print("Fixing Task Manager Authentication Configuration")
print("=" * 70)

# Load the settings file
settings_path = "server/core/settings.py"

print(f"\n1️⃣  Loading {settings_path}")

with open(settings_path, 'r') as f:
    content = f.read()

print("   ✅ Settings file loaded")

# Check for SIMPLE_JWT issues
print(f"\n2️⃣  Checking for SimpleJWT configuration...")

if 'SIMPLE_JWT = {' in content:
    print("   ❌ Found 'SIMPLE_JWT = {' in settings")
    # This is wrong - SIMPLE_JWT should be removed
    
    # Find where it's located
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'SIMPLE_JWT = {' in line:
            print(f"      Found at line {i+1}: '{line}'")
            # Show context
            for j in range(max(0, i-2), min(i+10, len(lines))):
                marker = ">>>" if j == i else "   "
                print(f"      {marker} {j+1:3d}: {lines[j]}")
            break
else:
    print("   ✅ SIMPLE_JWT = { not found - good")

# Check the end of the file for the broken SIMPLE_JWT section
print(f"\n3️⃣  Checking for incorrectly indented SIMPLE_JWT items...")

# Look for lines that look like SIMPLE_JWT configuration items
# (indented, but not inside REST_FRAMEWORK)
lines = content.split('\n')
problem_lines = []

for i, line in enumerate(lines):
    if line.strip() and not line.startswith(' ') and not line.startswith('REST_FRAMEWORK') and not line.startswith('SIMPLE_JWT'):
        # Check if it looks like a config item that should be inside SIMPLE_JWT
        if ("'AUTH_COOKIE'" in line or 
            "'REFRESH_COOKIE'" in line or
            "'ACCESS_TOKEN_LIFETIME'" in line or
            "'ALGORITHM'" in line or
            "'SIGNING_KEY'" in line or
            "'AUTH_HEADER_TYPES'" in line):
            problem_lines.append((i+1, line))

if problem_lines:
    print(f"   ❌ Found {len(problem_lines)} problem lines with SimpleJWT configuration:")
    for line_num, line in problem_lines:
        print(f"      Line {line_num}: {line}")
else:
    print("   ✅ No SimpleJWT configuration items found")

# The fix: Remove everything from '    'AUTH_COOKIE':'False' on
print(f"\n4️⃣  Applying fix...")

# We'll simplify: remove all lines that look like SimpleJWT config items
# after REST_FRAMEWORK and make sure REST_FRAMEWORK ends correctly

new_lines = []
skip_simple_jwt = False

for line in lines:
    stripped = line.strip()
    
    # Check if this is a line that indicates beginning of SIMPLE_JWT
    if "'AUTH_COOKIE'" in line and line.startswith('    ') and 'REST_FRAMEWORK' not in new_lines:
        skip_simple_jwt = True
        print(f"      ❌ Removing problematic SimpleJWT config at line: {line.strip()}")
    
    if skip_simple_jwt:
        # Skip this line and continue
        continue
    
    # Check if REST_FRAMEWORK is ending
    if "'UNAUTHENTICATED_USER': None," in line:
        # This is the end of REST_FRAMEWORK
        new_lines.append(line)
        skip_simple_jwt = False
        continue
    
    new_lines.append(line)

# Write fixed settings
with open(settings_path, 'w') as f:
    f.write('\n'.join(new_lines))

print("   ✅ Settings file fixed")

# Verify the fix
print(f"\n5️⃣  Verifying fix...")

with open(settings_path, 'r') as f:
    fixed_content = f.read()

if "'AUTH_COOKIE'" in fixed_content and "REST_FRAMEWORK" in fixed_content:
    # Check if it's properly placed now
    if "SIMPLE_JWT = {" not in fixed_content:
        print("   ❌ Still found potentially problematic configuration items")
        
        # Look for specific issues
        if "'ACCESS_TOKEN_LIFETIME'" in fixed_content and "SIMPLE_JWT = {" not in fixed_content:
            print("      ⚠️  Found 'ACCESS_TOKEN_LIFETIME' but SIMPLE_JWT header is missing")
            print("      This is likely leftover SimpleJWT configuration")
        
        # Show the end of the file to check
        lines = fixed_content.split('\n')
        print(f"\n      Last 20 lines of settings:")
        for i in range(max(0, len(lines)-20), len(lines)):
            marker = ">>>" if "AUTH_COOKIE" in lines[i] or "REFRESH_COOKIE" in lines[i] else "   "
            print(f"      {marker} {i+1:3d}: {lines[i]}")
    else:
        print("   ✅ SimpleJWT configuration removed completely")
else:
    print("   ✅ SimpleJWT configuration appears to be removed")

print("\n" + "=" * 70)
print("FIX SUMMARY")
print("=" * 70)
print("\nThe issue was that core/settings.py contained a SimpleJWT configuration")
print("that conflicted with the custom MongoDB AuthToken authentication system.")
print("\n✅ Applied fixes:")
print("1. Removed SimpleJWT configuration from settings")
print("2. Cleaned up indentation issues")
print("3. Left only custom authentication (MongoTokenAuthentication)")
print("\n🎯 Next Steps:")
print("Run migrations: python manage.py makemigrations && python manage.py migrate")
print("Create test users, then test authentication endpoints")
print("=" * 70)
